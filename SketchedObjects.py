import pygame
from charSprites import BlueBlob

size = width, height = 1024, 768
screen = pygame.display.set_mode(size)

black = 0, 0, 0
white = 255, 255, 255
gravity = 8

pygame.init()

def getDistance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5


# spawns a new sprite around the bomb radius
class BombExplosion(pygame.sprite.Sprite):
    def __init__(self, centre, explosion):
        pygame.sprite.Sprite.__init__(self)
        self.centre = centre
        self.explosion = 2*explosion
        self.image = pygame.Surface((self.explosion, self.explosion))
        self.rect = self.image.get_rect()
        self.rect.center = self.centre


class SketchedObjects(pygame.sprite.Sprite):
    # class for things like bombs and blocks
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)
        self.colour = black
        self.location = location
        self.image = pygame.Surface(location)
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        self.fallen = False  # if object has reached the ground


class Stick():
    def __init__(self, location, stickLen, stickFallen):
        self.stickPoints = location
        self.stickLen = stickLen  # length of each stick
        self.fallen = stickFallen
        self.colour = black

    def update(self):
        if len(self.stickPoints) == 2:
            diff = abs(self.stickLen - (getDistance(self.stickPoints[0],
                                                    self.stickPoints[1])))
            if 100 <= self.stickLen <= 250:
                # only allow sticks of reasonable length
                pygame.draw.lines(screen, self.colour, True,
                                  (self.stickPoints[0], self.stickPoints[1]), 6)
            # make these sticks fall
            if self.stickPoints[0][1] >= self.stickPoints[1][1]:
                if self.stickPoints[0][1] <= 600:
                    self.stickPoints[0] = (self.stickPoints[0][0],
                                           self.stickPoints[0][1] + gravity)
                if self.stickPoints[1][1] <= 600:
                    self.stickPoints[1] = (self.stickPoints[1][0]
                                           + diff, self.stickPoints[1][1]
                                           + gravity)
            else:
                if self.stickPoints[1][1] <= 600:
                    self.stickPoints[1] = (self.stickPoints[1][0],
                                           self.stickPoints[1][1] + gravity)
                if self.stickPoints[0][1] <= 600:
                    self.stickPoints[0] = (self.stickPoints[0][0] - diff,
                                           self.stickPoints[0][1] + gravity)
            # making sure the point on the left is index 0
            if self.stickPoints[1][0] < self.stickPoints[0][0]:
                self.stickPoints = [self.stickPoints[1], self.stickPoints[0]]
            # checking if it has reached the ground
            if self.stickPoints[0][1] >= 580:
                self.fallen = True


class Bomb(SketchedObjects):
    def __init__(self, location, bombPoints, realPoints,
                 radius, explosionRadius):
        SketchedObjects.__init__(self, location)
        self.explosionRadius = explosionRadius
        self.bombPoints = bombPoints
        self.realPoints = realPoints
        self.radius = radius
        self.fuse = 0
        self.explosion = pygame.image.load("boom!.png")
        self.explosionRect = self.explosion.get_rect()
        self.colour = black

    def draw(self):
        pygame.draw.circle(screen, self.colour, self.bombPoints, self.radius, 0)

    def explode(self, enemyList, obstacles, player, dragon):
        explosion = BombExplosion(self.realPoints, self.explosionRadius)
        # kills both enemies and player
        for enemy in enemyList:
            if pygame.sprite.collide_rect(explosion, enemy):
                enemy.health -= 5
        if pygame.sprite.collide_rect(explosion, player):
            player.health -= 5
        if pygame.sprite.collide_rect(explosion, dragon):
            dragon.health -= 1  # dragon is sort of immune to bombs
        # destroys obstacles
        for obstacle in obstacles:
            if pygame.sprite.collide_rect(explosion, obstacle):
                obstacle.destroyed = True
        self.bombPoints = (0, 0)
        self.fuse = 0
        self.fallen = False


class Block(pygame.sprite.Sprite):
    def __init__(self, location, realLocation):
        pygame.sprite.Sprite.__init__(self)
        self.location = location
        self.width, self.height = 100, 300
        self.image = pygame.Surface((self.width, self.height))
        self.tempRect = self.image.get_rect()
        self.tempRect.left, self.tempRect.top = location
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = realLocation
        self.timer = 150
        self.fallen = False
        self.destroyed = True
        self.colour = black

    def draw(self):
        pygame.draw.rect(screen, self.colour, self.tempRect, 0)

    def time(self):
        if self.timer <= 0:
            self.timer = 0
            self.destroyed = True
        else:
            self.timer -= 1

    def checkCollision(self, gameState, enemyList):
        for enemy in enemyList:
            if enemy.alive and enemy.stage == gameState:
                if pygame.sprite.collide_rect(self, enemy):
                    self.destroyed = True
                elif isinstance(enemy, BlueBlob) and len(enemy.bullets) >= 1:
                        for bullet in enemy.bullets:
                            if bullet.gameState == gameState and\
                                    pygame.sprite.collide_rect(self, bullet):
                                self.destroyed = True
                                try:
                                    enemy.bullets.remove(bullet)
                                except:
                                    pass
