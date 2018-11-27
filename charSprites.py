import pygame, math

size = width, height = 1024, 768
screen = pygame.display.set_mode(size)

pygame.init()


# spawns a new sprite in front of the player
class Weapon(pygame.sprite.Sprite):
    def __init__(self, stickLen, charHeight, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((stickLen, charHeight))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


# class for the detection field
class Field(pygame.sprite.Sprite):
    def __init__(self, length, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((length, length))
        self.rect = self.image.get_rect()
        self.rect.center = location


# class for bullets
class Projectile(pygame.sprite.Sprite):
    def __init__(self, velocity, spawnLocation):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((15, 15))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = spawnLocation
        self.velocity = velocity  # to move a different direction, make it negative
        self.outOfBounds = False

    def update(self):
        if self.rect.left <= 0 or self.rect.left >= 12026:
            self.outOfBounds = True
        self.rect.left -= self.velocity


# from https://www.pygame.org/docs/ref/sprite.html
class CharSprites(pygame.sprite.Sprite):
    # class for each character's functions, specifically the player
    def __init__(self, fileName, location):
        pygame.sprite.Sprite.__init__(self)
        # display
        self.width, self.height = 73, 162
        self.image = pygame.image.load(fileName)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.tempRect = self.rect.left
        self.imageSurface = pygame.Surface([self.rect.left, self.rect.top])

        # movement
        self.jumpState = False
        self.velocity = 35
        self.velocityX = 15
        self.gravity = 5
        self.blocked = False
        self.obstacleCheck = 0

        # weapons
        self.equipped = False
        self.weapon = []
        self.weaponLeft = []
        self.weaponRight = []
        self.tempWeapon = []
        self.attackState = False
        self.angle = 0  # angle for weapon attacking
        self.weaponDown = False
        self.stickLen = 0
        self.durability = 10

        # update
        self.health = 3
        self.alive = True
        self.cooldown = 100
        self.left = False
        self.right = True  # starts facing right


    def charDisplay(self):
        if 11491 >= self.rect.left > 480:
            self.tempRect = 481
            screen.blit(self.image, (self.tempRect, self.rect.top, 73, 162))
        elif self.rect.left > 11491:
            screen.blit(self.image, (self.tempRect, self.rect.top, 73, 162))
        else:
            self.tempRect = self.rect.left
            screen.blit(self.image, self.rect)

    def moveRight(self):
        self.right = True
        self.left = False
        if not self.blocked:
            self.rect.left += self.velocityX
            if self.equipped and self.tempRect < 481:
                self.weapon = [(self.weapon[0][0] + self.velocityX, self.weapon[0][1]),
                               (self.weapon[1][0] + self.velocityX, self.weapon[1][1])]
                self.weaponLeft = [(self.weaponLeft[0][0] + self.velocityX, self.weaponLeft[0][1]),
                                   (self.weaponLeft[1][0] + self.velocityX, self.weaponLeft[1][1])]
                self.weaponRight = [(self.weaponRight[0][0] + self.velocityX, self.weaponRight[0][1]),
                                    (self.weaponRight[1][0] + self.velocityX, self.weaponRight[1][1])]
            elif self.rect.left > 11491:
                self.tempRect += self.velocityX
                if self.equipped:
                    self.weapon = [(self.weapon[0][0] + self.velocityX, self.weapon[0][1]),
                                   (self.weapon[1][0] + self.velocityX, self.weapon[1][1])]
                    self.weaponLeft = [(self.weaponLeft[0][0] + self.velocityX, self.weaponLeft[0][1]),
                                       (self.weaponLeft[1][0] + self.velocityX, self.weaponLeft[1][1])]
                    self.weaponRight = [(self.weaponRight[0][0] + self.velocityX, self.weaponRight[0][1]),
                                        (self.weaponRight[1][0] + self.velocityX, self.weaponRight[1][1])]
            elif self.equipped and self.tempRect == 481:
                self.weapon = self.weapon

    def moveLeft(self):
        self.right = False
        self.left = True
        self.rect.left -= self.velocityX
        if self.equipped and self.tempRect < 481:
            self.weapon = [(self.weapon[0][0] - self.velocityX, self.weapon[0][1]),
                           (self.weapon[1][0] - self.velocityX, self.weapon[1][1])]
            self.weaponLeft = [(self.weaponLeft[0][0] - self.velocityX, self.weaponLeft[0][1]),
                               (self.weaponLeft[1][0] - self.velocityX, self.weaponLeft[1][1])]
            self.weaponRight = [(self.weaponRight[0][0] - self.velocityX, self.weaponRight[0][1]),
                                (self.weaponRight[1][0] - self.velocityX, self.weaponRight[1][1])]
        elif self.rect.left > 11491:
            self.tempRect -= self.velocityX
            if self.equipped:
                self.weapon = [(self.weapon[0][0] - self.velocityX, self.weapon[0][1]),
                               (self.weapon[1][0] - self.velocityX, self.weapon[1][1])]
                self.weaponLeft = [(self.weaponLeft[0][0] - self.velocityX, self.weaponLeft[0][1]),
                                   (self.weaponLeft[1][0] - self.velocityX, self.weaponLeft[1][1])]
                self.weaponRight = [(self.weaponRight[0][0] - self.velocityX, self.weaponRight[0][1]),
                                    (self.weaponRight[1][0] - self.velocityX, self.weaponRight[1][1])]
        elif self.equipped and self.tempRect == 481:
            self.weapon = self.weapon

    def jump(self):
        if not self.jumpState:
            self.velocity = 35
            self.jumpState = True

    def attack(self, enemyList):
        print(self.health)
        self.durability -= 1
        if self.durability <= 0:
            self.equipped = False
            self.weapon = []
            self.weaponLeft = []
            self.weaponRight = []
            self.durability = 10
            self.attackState = False
        else:
            if not self.attackState:
                self.attackState = True
                # creates a hitbox to check for collision with monsters
            if self.right:
                weapon = Weapon(self.stickLen, self.height,
                                (self.rect.left + self.width / 2, self.rect.top))
            elif self.left:
                weapon = Weapon(self.stickLen, self.height,
                                (self.rect.left + self.width / 2 - self.stickLen, self.rect.top))
            # check for collisions
            for enemy in enemyList:
                if pygame.sprite.collide_rect(weapon, enemy):
                    enemy.health -= 1

    def attackAnimation(self):
        # animation
        if self.equipped and self.right:
            if self.angle <= -math.pi / 3 or self.weaponDown:
                self.angle += 0.4
                self.weaponDown = True
            else:
                self.angle -= 0.4
            self.weapon = [self.weapon[0],
                           (self.weapon[0][0] + self.stickLen * math.cos(self.angle),
                            self.weapon[0][1] + self.stickLen * math.sin(self.angle))]
            if self.angle >= 0:
                self.weapon = [self.weapon[0],
                               (self.weapon[0][0] + self.stickLen * math.cos(0),
                                self.weapon[0][1] + self.stickLen * math.sin(0))]
                self.weaponRight = [self.weapon[0],
                                    (self.weapon[0][0] + self.stickLen * math.cos(0),
                                     self.weapon[0][1] + self.stickLen * math.sin(0))]
                self.weaponLeft = [self.weapon[0],
                                   (self.weapon[0][0] - self.stickLen * math.cos(0),
                                    self.weapon[0][1] - self.stickLen * math.sin(0))]
                self.attackState = False
        elif self.equipped and self.left:
            if self.angle >= math.pi / 3 or self.weaponDown:
                self.angle -= 0.4
                self.weaponDown = True
            else:
                self.angle += 0.4
            self.weapon = [self.weapon[0],
                           (self.weapon[0][0] - self.stickLen * math.cos(self.angle),
                            self.weapon[0][1] - self.stickLen * math.sin(self.angle))]
            if self.angle <= 0:
                self.weapon = [self.weapon[0],
                               (self.weapon[0][0] - self.stickLen * math.cos(0),
                                self.weapon[0][1] - self.stickLen * math.sin(0))]
                self.weaponRight = [self.weapon[0],
                                    (self.weapon[0][0] + self.stickLen * math.cos(0),
                                     self.weapon[0][1] + self.stickLen * math.sin(0))]
                self.weaponLeft = [self.weapon[0],
                                   (self.weapon[0][0] - self.stickLen * math.cos(0),
                                    self.weapon[0][1] - self.stickLen * math.sin(0))]
                self.attackState = False

    def update(self, enemyList, obstacles):
        if self.cooldown <= 0:
            self.cooldown = 0
        else:
            self.cooldown -= 1
        # check for player's health
        if self.health <= 0:
            self.alive = False
        # check if player gets hit or not
        # enemies collide check
        if self.cooldown == 0:
            for enemy in enemyList:
                if enemy.alive and pygame.sprite.collide_rect(self, enemy):
                    self.health -= 1
                    self.cooldown = 100
                if isinstance(enemy, BlueBlob) and len(enemy.bullets) >= 1:
                    for bullet in enemy.bullets:
                        if pygame.sprite.collide_rect(self, bullet):
                            try:
                                enemy.bullets.remove(bullet)
                            except:
                                pass
                            self.health -= 1
                            self.cooldown = 100
        for obstacle in obstacles:
            if pygame.sprite.collide_rect(self, obstacle):
                if not obstacle.destroyed:
                    self.blocked = True
            else:
                self.obstacleCheck += 1
        if self.obstacleCheck == len(obstacles):
            self.blocked = False
        self.obstacleCheck = 0

    def equip(self, stick):
        self.durability = 10
        diffX = stick.stickPoints[1][0] - stick.stickPoints[0][0]
        diffY = stick.stickPoints[1][1] - stick.stickPoints[0][1]
        self.weaponRight = [(self.tempRect + self.width/2,
                             self.rect.top + 100),
                            (self.tempRect + self.width/2 + diffX,
                             self.rect.top + 100 + diffY)]
        self.weaponLeft = [(self.tempRect + self.width/2,
                            self.rect.top + 100),
                           (self.tempRect + self.width/2 - diffX,
                            self.rect.top + 100 + diffY)]
        if self.right:
            self.weapon = self.weaponRight
        else:
            self.weapon = self.weaponLeft
        self.equipped = True
        self.stickLen = stick.stickLen


class RedBlob(CharSprites):
    # class for monster A
    def __init__(self, fileName, location, radius, velocity):
        super().__init__(fileName, location)
        self.locationX, self.locationY = location[0], location[1]
        self.width, self.height = 110, 113
        self.velocityX = velocity
        self.health = 3
        self.alive = True
        self.radius = radius

    def update(self):
        if self.health <= 0:
            self.alive = False
        if self.alive:
            if self.rect.left + self.width / 2 + self.velocityX >= self.locationX + self.radius:
                self.velocityX = -self.velocityX
            elif self.rect.left - self.width / 2 \
                    + self.velocityX <= self.locationX - self.radius:
                self.velocityX = -self.velocityX
            self.rect.left += self.velocityX


class BlueBlob(RedBlob):
    # class for monster B
    # this monster does not move
    def __init__(self, fileName, location, radius, velocity):
        super().__init__(fileName, location, radius, velocity)
        # radius for detecting players
        self.detectionRad = radius
        # velocity for bullet velocity
        self.bulletVelocity = velocity
        self.detection = Field(radius, location)
        self.time = 100
        self.bullets = pygame.sprite.Group()
        self.rect.center = location
        self.left = True
        self.right = False
        self.health = 5

    def fire(self, player):
        if self.time <= 0:
            self.time = 0
        else:
            self.time -= 1
        if self.time == 0:
            if pygame.sprite.collide_rect(self.detection, player) and player.rect.left <= self.rect.center[0]:
                self.left = True
                self.right = False
                bullet = Projectile(self.bulletVelocity, (self.rect.center[0], self.rect.center[1] + 50))
                self.bullets.add(bullet)
                self.time = 100
            elif pygame.sprite.collide_rect(self.detection, player) and player.rect.left >= self.rect.center[0]:
                self.left = False
                self.right = True
                bullet = Projectile(-self.bulletVelocity, (self.rect.center[0], self.rect.center[1] + 50))
                self.bullets.add(bullet)
                self.time = 100

    def update(self):
        if self.health <= 0:
            self.alive = False


class Obstacles(pygame.sprite.Sprite):
    # class for obstacles
    # blocks would also be in this class
    def __init__(self, fileName, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(fileName)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.destroyed = False
