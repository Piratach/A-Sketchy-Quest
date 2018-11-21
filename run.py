import pygame

from pygamegame import PygameGame

size = width, height = 1024, 768
screen = pygame.display.set_mode(size)  # my surface

black = 0, 0, 0
white = 255, 255, 255
gravity = 8

pygame.init()


def getDistance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5


class CharSprites:
    # class for each character's functions
    def __init__(self, fileName, location):
        self.image = pygame.image.load(fileName)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.jumpState = False
        self.velocity = 35
        self.gravity = 5
        self.equipped = False
        self.weapon = []
        self.attackState = False
        self.angle = 0  # angle for weapon attacking
        self.weaponDown = False

    def charDisplay(self):
        screen.blit(self.image, self.rect)

    def moveRight(self):
        self.rect.left += 20
        if self.equipped:
            self.weapon = [(self.weapon[0][0] + 20, self.weapon[0][1]),
                           (self.weapon[1][0] + 20, self.weapon[1][1])]

    def moveLeft(self):
        self.rect.left -= 20
        if self.equipped:
            self.weapon = [(self.weapon[0][0] - 20, self.weapon[0][1]),
                           (self.weapon[1][0] - 20, self.weapon[1][1])]

    def jump(self):
        if not self.jumpState:
            self.velocity = 35
            self.jumpState = True

    def attack(self):
        if not self.attackState:
            self.attackState = True


class SketchyQuest(PygameGame):
    def __init__(self):
        self.title = "A Sketchy Quest"
        self.screen = pygame.display.set_mode(size)  # my surface
        self.fps = 50
        self.maxDistance = 0
        self.tempPoints = []  # shows sketch
        self.linePoints = []  # actual line drawn
        self.mainChar = CharSprites("characterDude(COLOURED).png", (21, 465))
        self.stickLen = 0  # length of each stick
        self.isLine = True  # to identify if weapon sketched is a stick
        self.stickFallen = False  # if stick has reached the ground
        self.gameState = "start"

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
        self.gameScreen = pygame.image.load("testStage.png")
        self.gameScreenRect = self.gameScreen.get_rect()

    def mousePressed(self, x, y):
        # no mousePressed is needed for title screen
        if self.gameState == "game":
            self.tempPoints += [(x, y)]

    def mouseReleased(self):
        if self.gameState == "game":
            try:
                self.linePoints = [self.tempPoints[0], self.tempPoints[-1]]  # adding permanent lines
                self.stickLen = getDistance(self.linePoints[0], self.linePoints[1])
                self.tempPoints = []  # removing sketches
                self.stickFallen = False
                if self.mainChar.equipped and self.isLine:
                    self.mainChar.equipped = False
                    self.mainChar.weapon = []

            except:
                pass

    def keyPressed(self, currKey):
        # for title screen
        if self.gameState == "start":
            if self.title1:
                if currKey == "return":
                    self.gameState = "game"
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
            if currKey == "a":
                self.mainChar.moveLeft()
            elif currKey == "d":
                self.mainChar.moveRight()
            elif currKey == "space":
                self.mainChar.jump()
            elif currKey == "w":  # equip sticks
                # can only equip if near and stick has fallen
                if len(self.linePoints) == 2 and abs(self.mainChar.rect.left - self.linePoints[0][0]) <= 200 \
                        and self.stickFallen:
                    diffX = self.linePoints[1][0] - self.linePoints[0][0]
                    diffY = self.linePoints[1][1] - self.linePoints[0][1]
                    # magic numbers!!!
                    self.mainChar.weapon = [(self.mainChar.rect.left+5, self.mainChar.rect.top+100),
                                       (self.mainChar.rect.left+5 + diffX, self.mainChar.rect.top+100 + diffY)]
                    self.mainChar.equipped = True
                    self.linePoints = []

            # equipped state
            if self.mainChar.equipped:
                if not self.mainChar.attackState and currKey == "s":  # attack
                    self.mainChar.attackState = True
                    self.mainChar.angle = 0
                    self.mainChar.weaponDown = False
                    self.mainChar.attack()

    def redrawAll(self, screen):

        # title screen
        if self.gameState == "start":
                if self.title1:
                    self.screen.blit(self.titleScreen, self.titleScreenRect)
                elif self.title2:
                    self.screen.blit(self.titleScreen2, self.titleScreen2Rect)
                elif self.title3:
                    self.screen.blit(self.titleScreen3, self.titleScreen3Rect)

        # game screen
        elif self.gameState == "game":
            self.screen.blit(self.gameScreen, self.gameScreenRect)
            # sketches
            if len(self.tempPoints) >= 2:
                for i in range(len(self.tempPoints)):
                    if i == len(self.tempPoints) - 1:
                        break
                    # connecting lines together
                    pygame.draw.lines(screen, black, True, (self.tempPoints[i], self.tempPoints[i + 1]), 6)

            # sticks
            if len(self.linePoints) == 2:
                diff = abs(self.stickLen - (getDistance(self.linePoints[0], self.linePoints[1])))
                if 100 <= self.stickLen <= 250:  # only allow sticks of reasonable length
                    pygame.draw.lines(screen, black, True, (self.linePoints[0], self.linePoints[1]), 6)
                # make these sticks fall
                if self.linePoints[0][1] >= self.linePoints[1][1]:
                    if self.linePoints[0][1] <= 600:
                        self.linePoints[0] = (self.linePoints[0][0], self.linePoints[0][1] + gravity)
                    if self.linePoints[1][1] <= 600:
                        self.linePoints[1] = (self.linePoints[1][0] + diff, self.linePoints[1][1] + gravity)
                else:
                    if self.linePoints[1][1] <= 600:
                        self.linePoints[1] = (self.linePoints[1][0], self.linePoints[1][1] + gravity)
                    if self.linePoints[0][1] <= 600:
                        self.linePoints[0] = (self.linePoints[0][0] - diff, self.linePoints[0][1] + gravity)
                # making sure the point on the left is index 0
                if self.linePoints[1][0] < self.linePoints[0][0]:
                    self.linePoints = [self.linePoints[1], self.linePoints[0]]
                # checking if it has reached the ground
                if self.linePoints[0][1] >= 580:
                    self.stickFallen = True

            # weapons
            if len(self.mainChar.weapon) == 2:
                pygame.draw.lines(screen, black, True, (self.mainChar.weapon[0], self.mainChar.weapon[1]), 6)

            # main character
            self.mainChar.charDisplay()


# creating and running the game
game = SketchyQuest()
game.run()



