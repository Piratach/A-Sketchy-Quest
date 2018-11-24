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
    print("counts: ", count)
    return [False]


def withinBounds(tempPoints):
    for i in range(len(tempPoints)):
        if tempPoints[i][1] > 600:
            return False
    return True


# from https://www.pygame.org/docs/ref/sprite.html
class CharSprites(pygame.sprite.Sprite):
    # class for each character's functions
    def __init__(self, fileName, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(fileName)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.imageSurface = pygame.Surface([self.rect.left, self.rect.top])
        self.jumpState = False
        self.velocity = 35
        self.gravity = 5
        self.equipped = False
        self.weapon = []
        self.tempWeapon = []
        self.attackState = False
        self.angle = 0  # angle for weapon attacking
        self.weaponDown = False

    def charDisplay(self):
        screen.blit(self.image, self.rect)

    def moveRight(self):
        self.rect.left += 7
        if self.equipped:
            self.weapon = [(self.weapon[0][0] + 7, self.weapon[0][1]),
                           (self.weapon[1][0] + 7, self.weapon[1][1])]

    def moveLeft(self):
        self.rect.left -= 7
        if self.equipped:
            self.weapon = [(self.weapon[0][0] - 7, self.weapon[0][1]),
                           (self.weapon[1][0] - 7, self.weapon[1][1])]

    def jump(self):
        if not self.jumpState:
            self.velocity = 35
            self.jumpState = True

    def attack(self):
        if not self.attackState:
            self.attackState = True


class SketchedObjects(pygame.sprite.Sprite):
    # class for things like bombs and blocks
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)
        self.location = location
        self.image = pygame.Surface(location)
        self.image.fill(black)
        self.rect = self.image.get_rect()
        self.fallen = False  # if object has reached the ground


class Stick(SketchedObjects):
    def __init__(self, stickPoints, stickLen):
        SketchedObjects.__init__(self)
        self.stickPoints = stickPoints
        self.stickLen = stickLen  # length of each stick


class Bomb(SketchedObjects):
    def __init__(self, location, bombPoints, radius):
        SketchedObjects.__init__(self, location)
        self.bombPoints = bombPoints
        self.radius = radius
        self.fuse = 0

    def draw(self):
        pygame.draw.circle(screen, black, self.bombPoints, self.radius, 6)

    def explode(self):
        pass


class SketchyQuest(PygameGame):
    def __init__(self):
        self.title = "A Sketchy Quest"
        self.screen = pygame.display.set_mode(size)  # my surface
        self.fps = 50
        self.timerCalls = 0
        self.maxDistance = 0
        self.tempPoints = []  # shows sketch
        self.mainChar = CharSprites("characterDude(COLOURED).png", (21, 465))

        # sticks
        self.stickFallen = False  # if stick has reached the ground
        self.stickPoints = []  # actual stick drawn
        self.stickLen = 0  # length of each stick

        # bombs
        self.bomb = Bomb((0, 0), (0, 0), 1)  # initializing

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
        self.gameScreen = pygame.image.load("nextTestStage copy.png")
        self.gameScreenRect = screen.get_rect()

    def mousePressed(self, x, y):
        # no mousePressed is needed for title screen
        if self.gameState == "game":
            self.tempPoints += [(x, y)]

    def mouseReleased(self):
        if self.gameState == "game":
            print(self.tempPoints)
            print(len(self.tempPoints))
            if withinBounds(self.tempPoints):
                try:
                    # bombs
                    if isCircle(self.tempPoints)[0]:  # isCircle returns a list of truth value and a point
                        centreX = isCircle(self.tempPoints)[1][0]
                        centreY = isCircle(self.tempPoints)[1][1]
                        bombPoints = (centreX, centreY)
                        radius = 40
                        self.tempPoints = []
                        self.bomb = Bomb((centreX - radius, centreY - radius), bombPoints, radius)
                        self.bomb.fallen = False
                        self.bomb.fuse = 0
                    # sticks
                    else:
                        self.stickPoints = [self.tempPoints[0], self.tempPoints[-1]]  # adding a permanent stick
                        self.stickLen = getDistance(self.stickPoints[0], self.stickPoints[1])
                        self.tempPoints = []  # removing sketches
                        self.stickFallen = False
                        if self.mainChar.equipped and self.isLine:
                            self.mainChar.equipped = False
                            self.mainChar.weapon = []

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
            if currKey == "space":
                self.mainChar.jump()
            elif currKey == "w":  # equip sticks
                # can only equip if near and stick has fallen
                if len(self.stickPoints) == 2 and abs(self.mainChar.rect.left - self.stickPoints[0][0]) <= 200 \
                        and self.stickFallen:
                    diffX = self.stickPoints[1][0] - self.stickPoints[0][0]
                    diffY = self.stickPoints[1][1] - self.stickPoints[0][1]
                    self.mainChar.weapon = [(self.mainChar.rect.left+5,
                                             self.mainChar.rect.top+100),
                                            (self.mainChar.rect.left+5 + diffX,
                                             self.mainChar.rect.top+100 + diffY)]
                    self.mainChar.equipped = True
                    self.stickPoints = []

            # equipped state
            if self.mainChar.equipped:
                if not self.mainChar.attackState and currKey == "s":  # attack
                    self.mainChar.attackState = True
                    self.mainChar.angle = 0
                    self.mainChar.weaponDown = False
                    self.mainChar.attack()

    def timerFired(self, dt):
        self.timerCalls += 1
        if self.bomb.fallen:
            self.bomb.fuse += 1  # start counting after bomb has fallen
            if self.bomb.fuse % 100 == 0:
                self.bomb.bombPoints = (0, 0)
                self.bomb.fuse = 0
                self.bomb.Fallen = False

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
                    self.stickFallen = True

            # bombs
            if self.bomb.bombPoints != (0, 0):  # if it is actually drawn
                # make the bomb fall
                self.bomb.draw()
                if self.bomb.bombPoints[1] + self.bomb.radius <= 610:
                    self.bomb.bombPoints = (self.bomb.bombPoints[0], self.bomb.bombPoints[1] + gravity)
                else:
                    self.bomb.fallen = True
            # weapons
            if len(self.mainChar.weapon) == 2:
                pygame.draw.lines(screen, black, True, (self.mainChar.weapon[0], self.mainChar.weapon[1]), 6)

            # main character
            self.mainChar.charDisplay()


# creating and running the game
game = SketchyQuest()
game.run()



