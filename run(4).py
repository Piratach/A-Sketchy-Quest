import pygame, math

from pygamegam import PygameGame
from charSprites import CharSprites, Weapon, RedBlob, Obstacles
from SketchedObjects import Stick, Bomb

size = width, height = 1024, 768
screen = pygame.display.set_mode(size)  # my surface
allMonsters = pygame.sprite.Group()
allObstacles = pygame.sprite.Group()

black = 0, 0, 0
white = 255, 255, 255
gravity = 8

pygame.mixer.init(48000, -16, 1, 1024)  # initializing sound

def getDistance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5


pygame.init()

#  pygame.mixer.music.load('titleTheme?.mp3')
#  pygame.mixer.music.play(0)


def isCircle(tempPoints):
    if len(tempPoints) <= 10:  # drawing circles make a lot more points
        return [False]
    count = 0
    for i in range(len(tempPoints)):
        for j in range(len(tempPoints)):
            if abs(i - j) <= 10:  # each point compared must be at least 11 points apart
                continue
            elif abs(tempPoints[i][0] - tempPoints[j][0]) <= 40 and abs(tempPoints[i][1] - tempPoints[j][1]) <= 40:
                count += 1
            if count >= 6:  # at least 10 such points must be close to one another
                return [True, tempPoints[i]]
    return [False]


def withinBounds(tempPoints):
    for i in range(len(tempPoints)):
        if tempPoints[i][1] > 600:
            return False
    return True


class SketchyQuest(PygameGame):
    def __init__(self):
        # screen
        self.title = "A Sketchy Quest"
        self.screen = pygame.display.set_mode(size)  # my surface
        self.screenWidth, self.screenHeight = 1024, 768
        self.fps = 50
        self.timerCalls = 0
        self.maxDistance = 0

        # stage
        self.tempPoints = []  # shows sketch
        self.scrollX = 0
        self.scrollSpeed = 0
        self.rubble = Obstacles("rubble.png", (11000, 210))
        allObstacles.add(self.rubble)

        # main character
        self.ground = 465  # we will work on ground/platforming
        self.mainChar = CharSprites("characterDude(COLOURED).png", (21, self.ground))

        # monsterA - can only move around
        self.redblob1 = RedBlob("monster1.png", (3000, 499), 600, -5)
        self.redblob2 = RedBlob("monster1.png", (5000, 499), 600, 5)
        self.redblob3 = RedBlob("monster1.png", (7000, 499), 600, 10)
        allMonsters.add(self.redblob1, self.redblob2, self.redblob3)

        # monsterB - can attack with projectiles

        # boss - can breathe fire

        # music
        self.titleScreenBGM = False
        self.gameBGM = False
        self.bossBGM = False

        # sticks
        self.stickFallen = False  # if stick has reached the ground
        self.stickPoints = []  # actual stick drawn
        self.stickLen = 0  # length of each stick
        self.stick = Stick(self.stickPoints, self.stickLen, self.stickFallen)

        # bombs
        self.bomb = Bomb((0, 0), (0, 0), (0, 0), 1, 1)  # initializing
        self.exploded = False
        self.explosionDelay = 0
        self.explosionPoint = self.bomb.bombPoints

        # states
        self.gameState = "start"  # starts at the title state

        # title states
        self.title1 = True
        self.title2 = False
        self.title3 = False
        self.titleScreen = pygame.image.load("aSketchyQuestTitleScreen.png")
        self.titleScreenRect = self.titleScreen.get_rect()
        self.titleScreen2 = pygame.image.load("aSketchyQuestTitleScreen2.png")
        self.titleScreen2Rect = self.titleScreen.get_rect()
        self.titleScreen3 = pygame.image.load("aSketchyQuestTitleScreen3.png")
        self.titleScreen3Rect = self.titleScreen.get_rect()

        # game states
        self.gameScreen = pygame.image.load("finalStage.png")
        self.gameScreenRect = self.gameScreen.get_rect()
        self.gameScreenLen = 12026

        # game over state
        self.gameOverScreen = pygame.image.load("Game Over!!.png")
        self.gameOverScreenRect = self.gameOverScreen.get_rect()

    def mousePressed(self, x, y):
        # no mousePressed is needed for title screen
        if self.gameState == "game":
            print((x, y))
            self.tempPoints += [(x, y)]

    def mouseReleased(self):
        if self.gameState == "game":
            if withinBounds(self.tempPoints):
                try:
                    # bombs
                    if isCircle(self.tempPoints)[0]:  # isCircle returns a list of truth value and a point
                        centreX = isCircle(self.tempPoints)[1][0]
                        centreY = isCircle(self.tempPoints)[1][1]
                        bombPoints = (centreX, centreY)
                        radius = 40
                        explosionRadius = 200
                        self.tempPoints = []
                        self.bomb = Bomb((centreX - radius, centreY - radius), bombPoints,
                                         (bombPoints[0] + self.scrollX, bombPoints[1]),
                                         radius, explosionRadius)
                        self.bomb.fallen = False
                        self.bomb.fuse = 0
                    # sticks
                    else:
                        self.stickPoints = [self.tempPoints[0], self.tempPoints[-1]]  # adding a permanent stick
                        self.stickLen = getDistance(self.stickPoints[0], self.stickPoints[1])
                        self.tempPoints = []  # removing sketches
                        self.stickFallen = False
                        self.stick = Stick(self.stickPoints, self.stickLen, self.stickFallen)

                        if self.mainChar.equipped:
                            self.mainChar.equipped = False
                            self.mainChar.weapon = []
                            self.mainChar.weaponLeft = []
                            self.mainChar.weaponRight = []

                except:
                    pass
            else:
                self.tempPoints = []

    def keyPressed(self, currKey):
        # for title screen
        if self.gameState == "start":
            if self.title1:
                if currKey == "return":
                    self.gameState = "game"
                    self.title1 = False
                    self.title2 = False
                    self.title3 = False
                elif currKey == "s":
                    self.title1 = False
                    self.title2 = True
            elif self.title2:
                if currKey == "w":
                    self.title2 = False
                    self.title1 = True
                elif currKey == "s":
                    self.title2 = False
                    self.title3 = True
            else:
                if currKey == "w":
                    self.title3 = False
                    self.title2 = True

        # for the game screen
        elif self.gameState == "game":
            #  move left and right has been implemented in the run function
            if currKey == "d":
                self.mainChar.weapon = self.mainChar.weaponRight
            elif currKey == "a":
                self.mainChar.weapon = self.mainChar.weaponLeft
            elif currKey == "space":
                self.mainChar.jump()
            elif currKey == "w":  # equip sticks
                # can only equip if near and stick has fallen
                if len(self.stick.stickPoints) == 2 and \
                        abs(self.mainChar.tempRect - self.stick.stickPoints[0][0]) <= 200 and self.stick.fallen:
                    self.mainChar.equip(self.stick)
                    self.stick = Stick([], 0, False)

            # equipped state
            if self.mainChar.equipped:
                if not self.mainChar.attackState and currKey == "s":  # attack
                    self.mainChar.attackState = True
                    self.mainChar.angle = 0
                    self.mainChar.weaponDown = False
                    self.mainChar.attack(allMonsters)

    def timerFired(self, dt):
        if self.gameState == "game":
            self.timerCalls += 1
            # bombs
            if self.bomb.fallen:
                self.bomb.fuse += 1  # start counting after bomb has fallen
                if self.bomb.fuse % 50 == 0:
                    self.explosionPoint = (self.bomb.bombPoints[0] - 200,
                                           self.bomb.bombPoints[1] - 200)
                    self.bomb.explode(allMonsters, allObstacles, self.mainChar)
                    self.exploded = True
            allMonsters.update()
            self.mainChar.update(allMonsters, allObstacles)
            if self.exploded:
                self.explosionDelay += 1
            if self.explosionDelay % 20 == 0:
                self.exploded = False

    def redrawAll(self, screen):

        # title screen
        if self.title1:
            self.screen.blit(self.titleScreen, self.titleScreenRect)
        elif self.title2:
            self.screen.blit(self.titleScreen2, self.titleScreen2Rect)
        elif self.title3:
            self.screen.blit(self.titleScreen3, self.titleScreen3Rect)

        # game screen
        elif self.gameState == "game":
            pygame.Surface.blit(self.screen, self.gameScreen, (0 - self.scrollX, 0))

            # obstacles
            for obstacle in allObstacles:
                if not obstacle.destroyed:
                    screen.blit(obstacle.image, (obstacle.rect.left - self.scrollX, obstacle.rect.top))

            # monsters
            # monsterA
            for monster in allMonsters:
                if monster.alive:
                    screen.blit(monster.image, (monster.rect.left - self.scrollX, monster.locationY))

            # sketches
            if len(self.tempPoints) >= 2:
                for i in range(len(self.tempPoints)):
                    if i == len(self.tempPoints) - 1:
                        break
                    # connecting lines together
                    pygame.draw.lines(screen, black, True, (self.tempPoints[i], self.tempPoints[i + 1]), 6)

            # sticks
            self.stick.update()

            # bombs
            if self.bomb.bombPoints != (0, 0):  # if it is actually drawn
                # make the bomb fall
                self.bomb.draw()
                if self.bomb.bombPoints[1] + self.bomb.radius <= 610:
                    self.bomb.bombPoints = (self.bomb.bombPoints[0], self.bomb.bombPoints[1] + gravity)
                else:
                    self.bomb.fallen = True
            if self.exploded:
                self.screen.blit(self.bomb.explosion, self.explosionPoint)

            # weapons
            if len(self.mainChar.weapon) == 2:
                pygame.draw.lines(screen, black, True, (self.mainChar.weapon[0], self.mainChar.weapon[1]), 6)

            # main character
            if not self.mainChar.alive:
                self.gameState = "Game Over"
            if self.mainChar.attackState:
                self.mainChar.attackAnimation()
            self.mainChar.charDisplay()

        elif self.gameState == "Game Over":
            self.screen.blit(self.gameOverScreen, self.gameOverScreenRect)


# creating and running the game
game = SketchyQuest()
game.run()



