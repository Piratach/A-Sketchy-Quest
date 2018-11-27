import pygame

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
        self.location = location
        self.image = pygame.Surface(location)
        self.image.fill(black)
        self.rect = self.image.get_rect()
        self.fallen = False  # if object has reached the ground


class Stick():
    def __init__(self, location, stickLen, stickFallen):
        self.stickPoints = location
        self.stickLen = stickLen  # length of each stick
        self.fallen = stickFallen

    def update(self):
        if len(self.stickPoints) == 2:
            diff = abs(self.stickLen - (getDistance(self.stickPoints[0], self.stickPoints[1])))
            if 100 <= self.stickLen <= 250:  # only allow sticks of reasonable length
                pygame.draw.lines(screen, black, True, (self.stickPoints[0], self.stickPoints[1]), 6)
            # make these sticks fall
            if self.stickPoints[0][1] >= self.stickPoints[1][1]:
                if self.stickPoints[0][1] <= 600:
                    self.stickPoints[0] = (self.stickPoints[0][0], self.stickPoints[0][1] + gravity)
                if self.stickPoints[1][1] <= 600:
                    self.stickPoints[1] = (self.stickPoints[1][0] + diff, self.stickPoints[1][1] + gravity)
            else:
                if self.stickPoints[1][1] <= 600:
                    self.stickPoints[1] = (self.stickPoints[1][0], self.stickPoints[1][1] + gravity)
                if self.stickPoints[0][1] <= 600:
                    self.stickPoints[0] = (self.stickPoints[0][0] - diff, self.stickPoints[0][1] + gravity)
            # making sure the point on the left is index 0
            if self.stickPoints[1][0] < self.stickPoints[0][0]:
                self.stickPoints = [self.stickPoints[1], self.stickPoints[0]]
            # checking if it has reached the ground
            if self.stickPoints[0][1] >= 580:
                self.fallen = True


class Bomb(SketchedObjects):
    def __init__(self, location, bombPoints, realPoints, radius, explosionRadius):
        SketchedObjects.__init__(self, location)
        self.explosionRadius = explosionRadius
        self.bombPoints = bombPoints
        self.realPoints = realPoints
        self.radius = radius
        self.fuse = 0
        self.explosion = pygame.image.load("boom!.png")
        self.explosionRect = self.explosion.get_rect()

    def draw(self):
        pygame.draw.circle(screen, black, self.bombPoints, self.radius, 0)

    def explode(self, enemyList, obstacles, player):
        explosion = BombExplosion(self.realPoints, self.explosionRadius)
        # kills both enemies and player
        for enemy in enemyList:
            if pygame.sprite.collide_rect(explosion, enemy):
                enemy.health -= 5
        if pygame.sprite.collide_rect(explosion, player):
            player.health -= 5
        # destroys obstacles
        for obstacle in obstacles:
            if pygame.sprite.collide_rect(explosion, obstacle):
                obstacle.destroyed = True
        self.bombPoints = (0, 0)
        self.fuse = 0
        self.fallen = False


class Block(pygame.sprite.Sprite):
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)
        self.location = location
        self.image = pygame.Surface((100, 300))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.timer = 150
        self.fallen = False
        self.gone = True

    def draw(self):
        pygame.draw.rect(screen, black, self.rect, 0)

    def update(self):
        if self.timer <= 0:
            self.timer = 0
            self.gone = True
        else:
            self.timer -= 1
