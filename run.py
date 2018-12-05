import pygame, math, random, string

from pygamegame import PygameGame
from charSprites import Field, CharSprites, RedBlob, Obstacles, BlueBlob, Dragon
from SketchedObjects import Stick, Bomb, Block

size = width, height = 1024, 768
screen = pygame.display.set_mode(size)  # my surface
allMonsters = pygame.sprite.Group()
allObstacles = pygame.sprite.Group()
blueBlobs = pygame.sprite.Group()

# for survival
monstersSpawned = pygame.sprite.Group()
obstaclesSpawned = pygame.sprite.Group()

# for stage editing
obstaclesAdded = pygame.sprite.Group()
monstersAdded = pygame.sprite.Group()

# for stage playing
allObstacles2 = pygame.sprite.Group()
allMonsters2 = pygame.sprite.Group()

black = 0, 0, 0
white = 255, 255, 255
yellow = 255, 255, 0
gravity = 8

pygame.mixer.init(48000, -16, 1, 1024)
# initializing sound, shamelessly stolen from stackoverflow

# please play with music!!


font = pygame.font.SysFont("arial", 36)
font2 = pygame.font.SysFont("arial", 72)


pygame.init()


def getDistance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5


def isCircle(tempPoints):
    # check for
    if len(tempPoints) <= 10:  # drawing circles make a lot more points
        return [False]
    count = 0
    for i in range(len(tempPoints)):
        for j in range(len(tempPoints)):
            if abs(i - j) <= 10:
                # each point compared must be at least 11 points apart
                continue
            elif abs(tempPoints[i][0] - tempPoints[j][0]) <= 40 \
                    and abs(tempPoints[i][1] - tempPoints[j][1]) <= 40:
                count += 1
            if count >= 6:
                # at least 10 such points must be close to one another
                return [True, tempPoints[i]]
    return [False]


def isCorner(tempPoints):
    # this function doesn't actually count the number of corners
    # but if numCorner is high, it is likely that the
    # shape drawn has many corners
    numCorner = 0
    for i in range(len(tempPoints)):
        for j in range(len(tempPoints)):
            if abs(i - j) >= 3 or (i - j) == 0:
                # each point compared must be at most 3 points apart
                continue
            elif abs(tempPoints[i][0] - tempPoints[j][0]) <= 5:
                # straight vertical line section of block
                try:
                    if abs(tempPoints[i][0] - tempPoints[j + 3][0]) <= 20:
                        # corner
                        numCorner += 1
                except:
                    pass
            elif abs(tempPoints[i][1] - tempPoints[j][1]) <= 5:
                try:
                    if abs(tempPoints[i][1] - tempPoints[j + 3][1]) <= 20:
                        # corner
                        numCorner += 1
                except:
                    pass
    return numCorner


def isBlock(tempPoints):
    if len(tempPoints) < 20:
        return [False]
    if isCorner(tempPoints) < 40:  # blocks have a lot of "numCorners"
        return [False]
    else:
        # tempPoints[0], (tempPoints[0] + 100, tempPoints[1] + 300)]
        return [True, tempPoints[0]]


def withinBounds(tempPoints):
    for i in range(len(tempPoints)):
        if tempPoints[i][1] > 600:
            return False
    return True


def saveStage():
    f = open("saveState.txt", "w")
    f.write("#obstacles\n")
    for obstacle in obstaclesAdded:
        f.write(str((obstacle.rect.left, obstacle.rect.top)) + "\n")
    f.write("#blueblobs\n")
    for monster in monstersAdded:
        if isinstance(monster, BlueBlob):
            f.write(str([(monster.rect.center[0], 555), monster.radius,
                         monster.bulletVelocity, "play stage"]) + "\n")
    f.write("#redblobs\n")
    for monster in monstersAdded:
        if not isinstance(monster, BlueBlob):
            f.write(str([(monster.rect.left, 499), monster.radius,
                        monster.velocityX, "play stage"]) + "\n")
    f.close()


def overwrite(filename):
    if filename == "highscore.txt":
        f = open(filename, "w")
        for i in range(4):
            f.write("0\n")
        f.close()

def convertToLst(s):
    # used to convert the strings in .txt files back to list
    lst = []
    for stuff in s.split(","):
        lst += [stuff]
    item = lst[0] + "," + lst[1]
    location = convertToTuple(item)
    radius = int(lst[2])
    velocity = int(lst[3])
    stage = lst[4][:-2]  # ignore the ] and \n
    return [location, radius, velocity, stage]


def convertToTuple(s):
    # used to convert strings in .txt files back into a tuple
    lst = []
    for stuff in s.split(","):
        lst += [stuff]
    item1 = lst[0]
    item2 = lst[1]
    newItem = ""
    for letters in item1:
        if letters in string.digits:
            newItem += letters
    item1 = newItem
    if item2[-2:-1] == ")":
        item2 = item2[:-1]
    return int(item1), int(item2[1:-1])


class SketchyQuest(PygameGame):
    def __init__(self):
        # screen
        self.title = "A Sketchy Quest"
        self.screen = pygame.display.set_mode(size)  # my surface
        self.screenWidth, self.screenHeight = 1024, 768
        self.fps = 50
        self.timerCalls = 0
        self.maxDistance = 0
        self.music = 0

        # stage
        self.colour = black
        self.tempPoints = []  # shows sketch
        self.scrollX = 0
        self.scrollSpeed = 0
        self.rubble = Obstacles("rubble.png", (11000, 210))
        allObstacles.add(self.rubble)

        # main character
        self.ground = 465
        self.mainChar = CharSprites("characterDude(COLOURED).png",
                                    (21, self.ground))

        # monsterA - can only move around
        # stage 1
        self.redblob1 = RedBlob("monster1?.png",
                                (2000, 499), 600, -5, "stage1")
        self.redblob2 = RedBlob("monster1?.png",
                                (4000, 499), 600, 5, "stage1")
        self.redblob3 = RedBlob("monster1?.png",
                                (6000, 499), 600, 10, "stage1")
        self.redblob4 = RedBlob("monster1?.png",
                                (9000, 499), 600, 10, "stage1")

        # stage 2
        self.redblob5 = RedBlob("monster1?.png",
                                (2000, 499), 600, -10, "stage2")
        self.redblob6 = RedBlob("monster1?.png",
                                (4000, 499), 600, 10, "stage2")
        allMonsters.add(self.redblob1, self.redblob2,
                        self.redblob3, self.redblob4,
                        self.redblob5, self.redblob6)

        # monsterB - can attack with projectiles
        self.blueRight = pygame.image.load("monster2a.png")
        # stage 1
        self.blueblob1 = BlueBlob("monster2.png",
                                  (5000, 499), 1500, 25, "stage1")
        self.blueblob2 = BlueBlob("monster2.png",
                                  (8000, 499), 2000, 30, "stage1")
        self.blueblob3 = BlueBlob("monster2.png",
                                  (9500, 499), 1500, 30, "stage1")

        # stage 2
        self.blueblob4 = BlueBlob("monster2.png",
                                  (5000, 499), 1500, 30, "stage2")
        self.blueblob5 = BlueBlob("monster2.png",
                                  (7000, 499), 1500, 35, "stage2")
        blueBlobs.add(self.blueblob1, self.blueblob2, self.blueblob3,
                      self.blueblob4, self.blueblob5)
        allMonsters.add(self.blueblob1, self.blueblob2, self.blueblob3,
                        self.blueblob4, self.blueblob5)

        # boss - can breathe fire
        self.boss = Dragon("dragon.png", (550, 0), "boss1")
        # image from mega man

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

        # blocks
        self.block = Block((-1, -1), (-1, -1))

        # states
        self.gameState = "start"  # starts at the title state

        # title states
        self.title1 = True
        self.title2 = False
        self.title21 = False  # for the second screen after
        self.title22 = False
        self.title23 = False # back button
        self.title3 = False
        self.title31 = False
        self.title32 = False
        self.title33 = False # back button
        self.titleScreen = pygame.image.load("aSketchyQuestTitleScreen.png")
        self.titleScreenRect = self.titleScreen.get_rect()
        self.titleScreen2 = pygame.image.load("aSketchyQuestTitleScreen2.png")
        self.titleScreen2Rect = self.titleScreen.get_rect()
        self.titleScreen21 = pygame.image.load("aSketchyQuestTitleScreen21.png")
        self.titleScreen21Rect = self.titleScreen.get_rect()
        self.titleScreen22 = pygame.image.load("aSketchyQuestTitleScreen22.png")
        self.titleScreen22Rect = self.titleScreen.get_rect()
        self.titleScreen23 = pygame.image.load("aSketchyQuestTitleScreen23.png")
        self.titleScreen23Rect = self.titleScreen.get_rect()
        self.titleScreen3 = pygame.image.load("aSketchyQuestTitleScreen3.png")
        self.titleScreen3Rect = self.titleScreen.get_rect()
        self.titleScreen31 = pygame.image.load("aSketchyQuestTitleScreen31.png")
        self.titleScreen31Rect = self.titleScreen.get_rect()
        self.titleScreen32 = pygame.image.load("aSketchyQuestTitleScreen32.png")
        self.titleScreen32Rect = self.titleScreen.get_rect()
        self.titleScreen33 = pygame.image.load("aSketchyQuestTitleScreen33.png")
        self.titleScreen33Rect = self.titleScreen.get_rect()

        # game states
        self.gameScreen = pygame.image.load("stage1.png")
        self.gameScreenRect = self.gameScreen.get_rect()
        self.gameScreenLen = 12026
        self.stage2Screen = pygame.image.load("stage2.png")
        self.stage2ScreenRect = self.gameScreenRect
        self.bossScreen = pygame.image.load("BossStage.png")
        self.bossScreenRect = self.bossScreen.get_rect()

        # credits
        self.credits = False
        self.creditsScreen = pygame.image.load("credits.png")
        self.creditsScreenRect = self.creditsScreen.get_rect()

        # survival
        self.survivalScreen = pygame.image.load("survival.png")
        self.survivalScreenRect = self.survivalScreen.get_rect()
        self.dragon = Dragon("dragon.png", (2000, 0), "survival")
        self.monstersKilled = 0
        self.overlapCount = 0
        self.redKills = 0
        self.blueKills = 0
        self.dragonKills = 0
        self.healRadius = 8000
        self.healZone = Field(8000, (self.gameScreenLen/2, 465))

        # stage builder
        self.stageBuildScreen = pygame.image.load("stage builder.png")
        self.stageBuildScreenRect = self.stageBuildScreen.get_rect()
        self.monster1 = pygame.image.load("monster1?.png")
        self.monster1pos = (20, 10)
        self.monster1Held = False
        self.monster2 = pygame.image.load("monster2.png")
        self.monster2pos = (160, 10)
        self.monster2Held = False
        self.penDown = False

        # game over state
        self.gameOverScreen = pygame.image.load("Game Over!!.png")
        self.gameOverScreenRect = self.gameOverScreen.get_rect()

    def mousePressed(self, x, y):
        # no mousePressed is needed for title screen
        if self.gameState != "start" and self.gameState != "high scores" and \
                self.gameState != "edit stage":
            self.tempPoints += [(x, y)]
            if self.gameState == "play stage":
                # exit!
                if 9 <= x < 109 and 700 <= y < 750:
                    allObstacles2.empty()
                    allMonsters2.empty()
                    self.title31 = True
                    self.gameState = "start"
                    self.music = 1
                    self.mainChar.rect.left = 21
                    self.mainChar.tempRect = 21
                    self.scrollX = 0
                    self.mainChar.health = 3
                    self.tempPoints = []
                    self.mainChar.equipped = False
                    self.mainChar.weapon = []
                    self.mainChar.weaponRight = []
                    self.mainChar.weaponLeft = []
                    self.bomb = Bomb((0, 0), (0, 0), (0, 0), 1, 1)
                    self.exploded = False
                    self.explosionDelay = 0
                    self.block = Block((-1, -1), (-1, -1))

        elif self.gameState == "high scores":
            if 890 <= x < 1005 and 695 <= y < 755:
                overwrite("highscore.txt")
            else:
                self.title22 = True
                self.gameState = "start"
        # stage editor
        elif self.gameState == "edit stage":
            # print("Pen Down: ", self.penDown)
            # print("Monster 2 Held: ", self.monster2Held)
            # print("Monster 1 Held: ", self.monster1Held)
            # red blob
            if not self.monster2Held and 4 <= x < 131 and 2 <= y < 131:
                self.monster1pos = (x, y)
                self.monster1Held = True
            # blue blob
            elif not self.monster1Held and 145 <= x < 276 and 2 <= y < 131:
                self.monster2pos = (x, y)
                self.monster2Held = True
            # save!
            elif not self.penDown and not self.monster2Held and \
                    not self.monster1Held and 557 <= x < 773 and 11 <= y < 121:
                saveStage()
            # clear!
            elif not self.penDown and not self.monster2Held and \
                    not self.monster1Held and 779 <= x < 995 and 11 <= y < 121:
                obstaclesAdded.empty()
                monstersAdded.empty()
            # exit!
            elif not self.monster2Held and \
                    not self.monster1Held and 9 <= x < 109 and 700 <= y < 750:
                obstaclesAdded.empty()
                monstersAdded.empty()
                self.title32 = True
                self.gameState = "start"
                self.music = 1
                self.mainChar.rect.left = 21
                self.scrollX = 0
            else:
                if not self.monster1Held and not self.monster2Held:
                    self.tempPoints += [(x, y)]
                    self.penDown = True
            if self.monster1Held:
                self.monster1pos = (x - 45, y - 45)
            elif self.monster2Held:
                self.monster2pos = (x - 45, y - 45)

    def mouseReleased(self):
        if self.gameState == "stage1" or \
                self.gameState == "stage2" or self.gameState == "boss1" \
                or self.gameState == "survival" or \
                self.gameState == "play stage":
            # print("Length: ", len(self.tempPoints)) for debugging
            # print("Corners: ", isCorner(self.tempPoints))
            if withinBounds(self.tempPoints):
                try:
                    # blocks
                    if isBlock(self.tempPoints)[0]:
                        points = isBlock(self.tempPoints)[1]
                        self.block = Block(points,
                                           (points[0] + self.scrollX,
                                            points[1]))
                        if self.block.rect.top + self.block.height >= 610:
                            self.block = Block((-1, -1), (-1, -1))
                            self.tempPoints = []
                        else:
                            self.block.colour = self.colour
                            self.block.timer = 150
                            self.block.destroyed = False
                            self.tempPoints = []

                    # bombs
                    elif isCircle(self.tempPoints)[0]:
                        # isCircle returns a list of truth value and a point
                        centreX = isCircle(self.tempPoints)[1][0]
                        centreY = isCircle(self.tempPoints)[1][1]
                        bombPoints = (centreX, centreY)
                        radius = 40
                        explosionRadius = 200
                        self.tempPoints = []
                        self.bomb = Bomb((centreX - radius, centreY - radius),
                                         bombPoints,
                                         (bombPoints[0] + self.scrollX,
                                          bombPoints[1]),
                                         radius, explosionRadius)
                        self.bomb.colour = self.colour
                        self.bomb.fallen = False
                        self.bomb.fuse = 0

                    # sticks
                    else:
                        # adding a permanent stick
                        self.stickPoints = [self.tempPoints[0],
                                            self.tempPoints[-1]]
                        self.stickLen = getDistance(self.stickPoints[0],
                                                    self.stickPoints[1])
                        self.tempPoints = []  # removing sketches
                        self.stickFallen = False
                        self.stick = Stick(self.stickPoints,
                                           self.stickLen, self.stickFallen)
                        self.stick.colour = self.colour

                        if self.mainChar.equipped:
                            self.mainChar.equipped = False
                            self.mainChar.weapon = []
                            self.mainChar.weaponLeft = []
                            self.mainChar.weaponRight = []

                except:
                    pass
            else:
                self.tempPoints = []

        elif self.gameState == "edit stage":
            self.penDown = False
            if not self.monster1Held and not self.monster2Held and \
                    len(self.tempPoints) >= 40 \
                    and self.tempPoints[0][1] <= 250:
                rubble = Obstacles("rubble.png",
                                   (self.tempPoints[0][0]
                                    - 300 + self.scrollX,  # to offset rect.left
                                    self.tempPoints[0][1])
                                   )
                obstaclesAdded.add(rubble)
                self.tempPoints = []
            else:
                self.tempPoints = []
            if self.monster1Held:
                self.monster1Held = False
                if 4 <= self.monster1pos[0] < 131 and \
                   2 <= self.monster1pos[1] < 131:
                    self.monster1pos = (20, 10)
                else:
                    radius = random.randint(200,
                                            int(self.gameScreenLen / 3))
                    velocity = random.randint(-10, 10)
                    try:
                        monster1 = RedBlob("monster1?.png", (self.monster1pos[0]
                                                             + self.scrollX,
                                                             self.monster1pos[1]
                                                             + 10),
                                           radius, velocity, "edit stage")
                        monstersAdded.add(monster1)
                        self.monster1pos = (20, 10)
                    except:
                        pass
            elif self.monster2Held:
                self.monster2Held = False
                if 145 <= self.monster2pos[0] < 276 \
                   and 2 <= self.monster2pos[1] < 131:
                    self.monster2pos = (160, 10)
                else:
                    radius = random.randint(200,
                                            int(self.gameScreenLen / 4))
                    try:
                        monster2 = BlueBlob("monster2.png", (self.monster2pos[0]
                                                             + 45
                                                             + self.scrollX,
                                                             self.monster2pos[1]
                                                             + 10),
                                            radius, 20, "edit stage")
                        monstersAdded.add(monster2)
                    except:
                        pass
                    self.monster2pos = (160, 10)

    def keyPressed(self, currKey):
        # for title screen
        if self.gameState == "start":
            if self.title1:
                if currKey == "return":
                    self.gameState = "stage1"
                    self.title1 = False
                    self.title2 = False
                    self.title3 = False
                elif currKey == "s" or currKey == "down":
                    self.title1 = False
                    self.title2 = True
                    self.title3 = False
                elif currKey == "w" or currKey == "up":
                    self.title1 = False
                    self.title2 = False
                    self.title3 = True
            elif self.title2:
                if currKey == "return":
                    self.title1 = False
                    self.title2 = False
                    self.title21 = True
                    self.title3 = False
                elif currKey == "w" or currKey == "up":
                    self.title2 = False
                    self.title1 = True
                elif currKey == "s" or currKey == "down":
                    self.title2 = False
                    self.title3 = True
            elif self.title21:
                if currKey == "return":
                    self.gameState = "survival"
                    self.mainChar.health = 10  # you get 10 health for survival
                    self.title21 = False
                    self.title22 = False
                    self.title23 = False
                elif currKey == "s" or currKey == "down":
                    self.title21 = False
                    self.title22 = True
                    self.title23 = False
            elif self.title22:
                if currKey == "return":
                    self.gameState = "high scores"
                    self.title22 = False
                    self.title21 = False
                    self.title23 = False
                elif currKey == "w" or currKey == "up":
                    self.title22 = False
                    self.title21 = True
                    self.title23 = False
                elif currKey == "s" or currKey == "down":
                    self.title21 = False
                    self.title22 = False
                    self.title23 = True
            elif self.title23:
                if currKey == "return":
                    self.title21 = False
                    self.title22 = False
                    self.title23 = False
                    self.title2 = True
                elif currKey == "w" or currKey == "up":
                    self.title21 = False
                    self.title22 = True
                    self.title23 = False
            elif self.title3:
                if currKey == "return":
                    self.title3 = False
                    self.title31 = True
                    self.title32 = False
                    self.title33 = False
                elif currKey == "w" or currKey == "up":
                    self.title3 = False
                    self.title2 = True
                    self.title1 = False
                elif currKey == "s" or currKey == "down":
                    self.title1 = True
                    self.title2 = False
                    self.title3 = False
            elif self.title31:
                if currKey == "return":
                    self.gameState = "play stage"
                    self.mainChar.stage = "play stage"
                    self.title31 = False
                elif currKey == "s" or currKey == "down":
                    self.title31 = False
                    self.title32 = True
                    self.title33 = False
            elif self.title32:
                if currKey == "return":
                    self.gameState = "edit stage"
                    self.title32 = False
                elif currKey == "w" or currKey == "up":
                    self.title31 = True
                    self.title32 = False
                    self.title33 = False
                elif currKey == "s" or currKey == "down":
                    self.title31 = False
                    self.title32 = False
                    self.title33 = True
            elif self.title33:
                if currKey == "return":
                    self.title33 = False
                    self.title3 = True
                elif currKey == "w" or currKey == "up":
                    self.title31 = False
                    self.title32 = True
                    self.title33 = False
        elif self.gameState == "high scores":
            if currKey == "return":
                self.gameState = "start"
                self.title22 = True

        # for the game screen
        elif self.gameState != "title" and self.gameState != "high scores" \
                and self.gameState != "edit stage":
            #  move left and right has been implemented in the run function
            if currKey == "d":
                self.mainChar.weapon = self.mainChar.weaponRight
            elif currKey == "a":
                self.mainChar.weapon = self.mainChar.weaponLeft
            elif currKey == "space" or currKey == "left shift":
                self.mainChar.jump()
            elif not self.mainChar.jumpState and currKey == "w":  # equip sticks
                # can only equip if near and stick has fallen
                if len(self.stick.stickPoints) == 2 and \
                    abs(self.mainChar.tempRect - self.stick.stickPoints[0][0])\
                        <= 200 and self.stick.fallen:
                    self.mainChar.equip(self.stick)
                    self.stick = Stick([], 0, False)
            elif currKey == "q":
                # cheat code
                self.mainChar.health = 300
                print(self.boss.health)
                print(self.mainChar.rect.left)

            # equipped state
            if self.mainChar.equipped:
                if not self.mainChar.attackState and currKey == "s":  # attack
                    self.mainChar.attackState = True
                    self.mainChar.angle = 0
                    self.mainChar.weaponDown = False
                    if self.gameState != "survival" and \
                            self.gameState != "play stage":
                        self.mainChar.attack(allMonsters, self.boss)
                    elif self.gameState == "play stage":
                        self.mainChar.attack(allMonsters2, self.boss)
                    else:
                        self.mainChar.attack(monstersSpawned, self.dragon)
                        if self.dragon.health == 0:
                            self.mainChar.health += 5
                            self.monstersKilled += 1
                            self.dragonKills += 1
                            if self.dragonKills <= 4:
                                self.healRadius -= 2000
                                self.healZone = Field(self.healRadius,
                                                      (self.gameScreenLen / 2,
                                                       465))
                            else:
                                self.healRadius = 0
                                self.healZone = Field(0, (0, 0))
                            self.dragon.health = 5
                            self.dragon.alive = False

    def timerFired(self, dt):
        if self.gameState == "stage1" or \
                self.gameState == "stage2" or self.gameState == "boss1" or \
                self.gameState == "survival" or self.gameState == "play stage":
            self.timerCalls += 1
            # bombs
            if self.bomb.fallen:
                self.bomb.fuse += 1  # start counting after bomb has fallen
                if self.bomb.fuse % 50 == 0:
                    self.explosionPoint = (self.bomb.bombPoints[0] - 200,
                                           self.bomb.bombPoints[1] - 200)
                    if self.gameState == "survival":
                        self.bomb.explode(monstersSpawned,
                                          obstaclesSpawned,
                                          self.mainChar, self.dragon)
                        self.exploded = True
                    elif self.gameState == "play stage":
                        self.bomb.explode(allMonsters2,
                                          allObstacles2,
                                          self.mainChar, self.boss)
                        self.exploded = True
                    else:
                        self.bomb.explode(allMonsters,
                                          allObstacles,
                                          self.mainChar, self.boss)
                    self.exploded = True
            if self.gameState == "stage1" or \
               self.gameState == "stage2" or self.gameState == "boss1":
                for monster in allMonsters:
                    if monster.stage == self.gameState:
                        monster.update()
                for dudes in blueBlobs:
                    if dudes.alive:
                        dudes.fire(self.mainChar)  # sends out the projectiles
            if self.gameState != "survival" and self.gameState != "play stage":
                self.mainChar.update(allMonsters, self.boss.fire,
                                     self.boss, allObstacles,
                                     self.block, self.gameState)
            if self.exploded:
                self.explosionDelay += 1
            if self.explosionDelay % 20 == 0:
                self.exploded = False
                self.explosionDelay = 0
            self.block.time()
            if self.gameState == "boss1":
                self.boss.fly()
                self.boss.attack(0)
                if self.boss.attacking:
                    self.boss.fire.update(self.block,
                                          self.mainChar, self.gameState)
            if self.credits:
                self.mainChar.creditsDelay -= 1

            # survival mode
            if self.gameState == "survival":
                self.mainChar.update(monstersSpawned, self.dragon.fire,
                                     self.dragon, obstaclesSpawned,
                                     self.block, self.gameState)

                # updating monsters
                for monster in monstersSpawned:
                    if monster.alive:
                        monster.update()
                        if isinstance(monster, BlueBlob):
                            monster.fire(self.mainChar)

                # spawns red blobs
                if not self.dragon.alive and self.timerCalls % 150 == 0:
                    location = random.randint(200, self.gameScreenLen - 200)
                    if abs(location - self.mainChar.rect.left) <= 200:
                        if location + 1000 >= self.gameScreenLen:
                            location = \
                                random.randint(0, self.mainChar.rect.left - 200)
                        else:
                            location = \
                                random.randint(self.mainChar.rect.left + 200,
                                               self.gameScreenLen - 200)
                    radius = random.randint(200,
                                            int(self.gameScreenLen / 3))
                    tempV = 5 + int(0.4 * self.monstersKilled)
                    if tempV >= self.mainChar.velocityX:
                        tempV = self.mainChar.velocityX - 1
                    velocity = random.choice([str(-tempV), str(tempV)])
                    monster = RedBlob("monster1?.png", (location, 499), radius,
                                      int(velocity), "survival")
                    monstersSpawned.add(monster)

                # spawns blue blobs
                if not self.dragon.alive and \
                        self.timerCalls % 200 == 0 and \
                        self.monstersKilled >= 10:
                    location = random.randint(200, self.gameScreenLen - 200)
                    if abs(location - self.mainChar.rect.left) <= 200:
                        if location + 1000 >= self.gameScreenLen:
                            location = \
                                random.randint(0, self.mainChar.rect.left - 200)
                        else:
                            location = \
                                random.randint(self.mainChar.rect.left + 200,
                                               self.gameScreenLen - 200)
                    radius = 1500 + int(10 * self.monstersKilled)
                    velocity = 20 + int(0.4 * self.monstersKilled)
                    monster2 = BlueBlob("monster2.png", (location, 499), radius,
                                        int(velocity), "survival")
                    monstersSpawned.add(monster2)

                # spawn dragon boss!
                if self.monstersKilled >= 20 and self.monstersKilled % 10 == 0 \
                        and not self.dragon.alive:
                    monstersSpawned.empty()
                    self.dragon.alive = True
                    location = self.mainChar.rect.left + 400
                    if location >= self.gameScreenLen:
                        location = self.mainChar.rect.left - 400
                        self.dragon = Dragon("dragon.png", (location, 0),
                                             self.gameState)
                    else:
                        self.dragon = Dragon("dragon right.png", (location, 0),
                                             self.gameState)

                if self.dragon.alive:
                    self.dragon.fly()
                    self.dragon.attack(self.scrollX)
                    if self.dragon.attacking:
                        self.dragon.fire.update(self.block,
                                                self.mainChar,
                                                self.gameState)

                if self.timerCalls % 700 == 0 and \
                        pygame.sprite.collide_rect(self.healZone,
                                                   self.mainChar):
                    if self.mainChar.health < 10:
                        self.mainChar.health += 1

            # play stage
            elif self.gameState == "play stage":
                self.mainChar.update(allMonsters2, self.dragon.fire,
                                     self.dragon, allObstacles2,
                                     self.block, self.gameState)

                # updating monsters
                for monster in allMonsters2:
                    if monster.alive and monster.rect.top == 499:
                        monster.update()
                        if isinstance(monster, BlueBlob):
                            monster.tempCenterY = 499
                            monster.fire(self.mainChar)

    def redrawAll(self, screen):

        # title screen
        if self.title1:
            self.screen.blit(self.titleScreen, self.titleScreenRect)
        elif self.title2:
            self.screen.blit(self.titleScreen2, self.titleScreen2Rect)
        elif self.title21:
            self.screen.blit(self.titleScreen21, self.titleScreen21Rect)
        elif self.title22:
            self.screen.blit(self.titleScreen22, self.titleScreen22Rect)
        elif self.title23:
            self.screen.blit(self.titleScreen23, self.titleScreen23Rect)
        elif self.title3:
            self.screen.blit(self.titleScreen3, self.titleScreen3Rect)
        elif self.title31:
            self.screen.blit(self.titleScreen31, self.titleScreen31Rect)
        elif self.title32:
            self.screen.blit(self.titleScreen32, self.titleScreen32Rect)
        elif self.title33:
            self.screen.blit(self.titleScreen33, self.titleScreen33Rect)

        # music
        if self.gameState == "start":
            if self.music == 0:
                pygame.mixer.music.load("titleTheme.wav")
                # from wii sports resort
                pygame.mixer.music.play(-1)
                self.music = 1

        # game screen
        elif self.gameState == "stage1" or \
                self.gameState == "stage2" or self.gameState == "boss1":

            # music
            if self.gameState == "stage1" and self.music == 1:
                self.mainChar.stage = "stage1"
                pygame.mixer.music.load("kirby.wav")  # from kirby
                pygame.mixer.music.play(-1)
                self.music = 2

            # music + init again
            if self.gameState == "stage2" and self.music == 2:
                # main character
                self.mainChar.stage = "stage2"
                self.mainChar.rect.left = 100
                self.mainChar.tempRect = 100
                self.mainChar.equipped = False
                self.mainChar.weapon = []
                self.mainChar.weaponRight = []
                self.mainChar.weaponLeft = []
                self.bomb = Bomb((0, 0), (0, 0), (0, 0), 1, 1)
                self.exploded = False
                self.explosionDelay = 0
                self.block = Block((-1, -1), (-1, -1))

                # monsters
                for monster in allMonsters:
                    if isinstance(monster, BlueBlob):
                        monster.bullets.empty()

                # other stuff
                self.colour = white
                self.scrollX = 0
                pygame.mixer.music.load("stage2.wav")  # from final fantasy VI
                pygame.mixer.music.play(-1)
                self.music = 3

            if self.gameState == "boss1" and self.music == 3:
                self.mainChar.stage = "boss1"
                self.mainChar.rect.left = 100
                self.mainChar.tempRect = 100
                self.mainChar.equipped = False
                self.mainChar.weapon = []
                self.mainChar.weaponRight = []
                self.mainChar.weaponLeft = []
                self.bomb = Bomb((0, 0), (0, 0), (0, 0), 1, 1)
                self.exploded = False
                self.explosionDelay = 0
                self.block = Block((-1, -1), (-1, -1))

                self.colour = black
                self.scrollX = 0
                pygame.mixer.music.load("Boss Theme.wav")
                # from final fantasy VII
                pygame.mixer.music.play(-1)
                self.music = 4

            if self.gameState == "stage1":
                pygame.Surface.blit(self.screen,
                                    self.gameScreen, (0 - self.scrollX, 0))
            elif self.gameState == "stage2":
                pygame.Surface.blit(self.screen,
                                    self.stage2Screen, (0 - self.scrollX, 0))
            elif self.gameState == "boss1":
                pygame.Surface.blit(self.screen,
                                    self.bossScreen, self.bossScreenRect)

            # obstacles
            for obstacle in allObstacles:
                if not obstacle.destroyed:
                    screen.blit(obstacle.image,
                                (obstacle.rect.left - self.scrollX,
                                 obstacle.rect.top))

            # monsters
            # monsterA
            for monster in allMonsters:
                if monster.stage == self.gameState:
                    if monster.alive and not isinstance(monster, BlueBlob):
                        monster.checkCollision(self.block)
                        screen.blit(monster.image,
                                    (monster.rect.left - self.scrollX,
                                     monster.locationY))
                    elif monster.alive and isinstance(monster, BlueBlob):
                        if monster.right and not monster.left:
                            screen.blit(self.blueRight,
                                        (monster.rect.left - self.scrollX,
                                         monster.locationY))
                        else:
                            screen.blit(monster.image,
                                        (monster.rect.left - self.scrollX,
                                         monster.locationY))
                    if isinstance(monster, BlueBlob) and \
                            len(monster.bullets) >= 1:
                        for bullet in monster.bullets:
                            bullet.gameState = self.gameState
                            bullet.update()
                            screen.blit(bullet.image,
                                        (bullet.rect.left - self.scrollX,
                                         bullet.rect.top))
                            try:
                                if bullet.outOfBounds:
                                    monster.bullets.remove(bullet)
                            except:
                                pass

            # for final boss only
            if not self.credits and self.gameState == "boss1":
                self.boss.update()
                if self.boss.alive and not self.boss.attacking:
                    screen.blit(self.boss.image, self.boss.rect)
                elif self.boss.alive and self.boss.attacking:
                    self.boss.fire.draw()
                    screen.blit(self.boss.attackStance, self.boss.rect)
                elif not self.boss.alive and self.music == 4:
                    self.music = 6
                    pygame.mixer.music.load("victory!.wav")
                    # from Dragon Quest VIII
                    pygame.mixer.music.play(1)
                    self.credits = True

            # sketches
            if len(self.tempPoints) >= 2:
                for i in range(len(self.tempPoints)):
                    if i == len(self.tempPoints) - 1:
                        break
                    # connecting lines together
                    pygame.draw.lines(screen, self.colour, True,
                                      (self.tempPoints[i],
                                       self.tempPoints[i + 1]), 6)

            # sticks
            self.stick.update()

            # bombs
            if self.bomb.bombPoints != (0, 0):  # if it is actually drawn
                self.bomb.draw()
                # make the bomb fall
                if self.bomb.bombPoints[1] + self.bomb.radius <= 610:
                    self.bomb.bombPoints = (self.bomb.bombPoints[0],
                                            self.bomb.bombPoints[1] + gravity)
                else:
                    self.bomb.fallen = True
            if self.exploded:
                self.screen.blit(self.bomb.explosion, self.explosionPoint)

            # blocks
            if self.block.location != (-1, -1) and not self.block.destroyed:
                self.block.draw()
                self.block.checkCollision(self.gameState, allMonsters)
                # make the block fall
                if not self.block.fallen and \
                        self.block.tempRect.top + 300 <= 610:
                    self.block.tempRect.top += gravity
                else:
                    self.block.fallen = True

            # weapons
            if len(self.mainChar.weapon) == 2:
                pygame.draw.lines(screen, self.colour, True,
                                  (self.mainChar.weapon[0],
                                   self.mainChar.weapon[1]), 6)

            # main character
            health = "Health: " + str(self.mainChar.health)
            displayHealth = font.render(health, False, (0, 0, 0))
            self.screen.blit(displayHealth, (self.screenWidth - 170, 0))
            if not self.mainChar.alive:
                self.gameState = "Game Over"
            if self.mainChar.attackState:
                self.mainChar.attackAnimation()
            # changing stages
            if self.mainChar.rect.left >= self.gameScreenLen:
                if self.gameState == "stage1":
                    self.gameState = "stage2"
                elif self.gameState == "stage2":
                    self.gameState = "boss1"
            self.mainChar.charDisplay()

            # credits
            if self.credits:
                if self.mainChar.creditsDelay == 20:
                    self.mainChar.rect.top = self.ground
                    self.mainChar.weapon = []
                    self.mainChar.tempWeapon = []
                    self.mainChar.weaponLeft = []
                    self.mainChar.weaponRight = []
                    self.mainChar.equipped = False
                elif self.mainChar.creditsDelay <= 0:
                    self.mainChar.rect.top -= 1
                    if self.mainChar.rect.top + self.mainChar.height <= -480:
                        # -480 for correct timing!!
                        self.gameState = "credits"
                    if self.music == 6:
                        pygame.mixer.music.load("credits.wav")
                        # from final fantasy III
                        pygame.mixer.music.play(1)
                        self.music = 7

        elif self.gameState == "credits":
            self.screen.blit(self.creditsScreen, self.creditsScreenRect)

        elif self.gameState == "Game Over":
            if self.music <= 4:
                pygame.mixer.music.load("Game Over.wav")  # from mario
                pygame.mixer.music.play(0)
                self.music = 5
            self.screen.blit(self.gameOverScreen, self.gameOverScreenRect)

        # survival mode
        elif self.gameState == "survival":
            pygame.Surface.blit(self.screen,
                                self.survivalScreen, (0 - self.scrollX, 0))

            if self.healRadius != 0:
                pygame.draw.line(self.screen, black,
                                 (self.healZone.rect.center[0] -
                                  self.healRadius/2 - self.scrollX, 465),
                                 (self.healZone.rect.center[0] -
                                  self.healRadius/2 - self.scrollX, 700), 10)

                pygame.draw.line(self.screen, black,
                                 (self.healZone.rect.center[0] +
                                  self.healRadius/2 - self.scrollX, 465),
                                 (self.healZone.rect.center[0] +
                                  self.healRadius/2 - self.scrollX, 700), 10)

            if self.music == 1:
                # pygame.mixer.music.load("kirby.wav")  # from kirby
                # pygame.mixer.music.play(-1)
                self.mainChar.stage = "survival"
                self.dragon.alive = False  # no dragon yet
                self.music = 2

            # kill count
            killCount = "Monsters Slain: " + str(self.monstersKilled)
            displayKill = font.render(killCount, False, (0, 0, 0))
            self.screen.blit(displayKill, (0, 0))

            # monsters
            for monster in monstersSpawned:
                if monster.alive:
                    screen.blit(monster.image,
                                (monster.rect.left - self.scrollX,
                                 monster.locationY))
                    if not isinstance(monster, BlueBlob):
                        monster.checkCollision(self.block)
                    else:
                        if len(monster.bullets) >= 1:
                            for bullet in monster.bullets:
                                bullet.gameState = self.gameState
                                bullet.update()
                                screen.blit(bullet.image,
                                            (bullet.rect.left - self.scrollX,
                                             bullet.rect.top))
                                try:
                                    if bullet.outOfBounds:
                                        monster.bullets.remove(bullet)
                                except:
                                    pass
                else:
                    try:
                        self.monstersKilled += 1
                        if isinstance(monster, BlueBlob):
                            self.blueKills += 1
                        elif isinstance(monster, RedBlob):
                            self.redKills += 1
                        else:
                            self.dragonKills += 1
                        monstersSpawned.remove(monster)
                    except:
                        pass
            if self.dragon.alive:
                if self.dragon.rect.left + 50 < self.mainChar.rect.left:
                    self.dragon.right = True
                else:
                    self.dragon.right = False
                self.dragon.update()
                if self.dragon.alive and not self.dragon.attacking:
                    if not self.dragon.right:
                        screen.blit(self.dragon.imageLeft,
                                    (self.dragon.rect.left - self.scrollX,
                                     self.dragon.rect.top))
                    else:
                        screen.blit(self.dragon.imageRight,
                                    (self.dragon.rect.left - self.scrollX,
                                     self.dragon.rect.top))
                elif self.dragon.alive and self.dragon.attacking:
                    self.dragon.fire.draw()
                    if not self.dragon.right:
                        screen.blit(self.dragon.attackStance,
                                    (self.dragon.rect[0] - self.scrollX,
                                     self.dragon.rect[1]))
                    else:
                        screen.blit(self.dragon.attackStanceR,
                                    (self.dragon.rect[0] - self.scrollX,
                                     self.dragon.rect[1]))

            # sketches
            if len(self.tempPoints) >= 2:
                for i in range(len(self.tempPoints)):
                    if i == len(self.tempPoints) - 1:
                        break
                    # connecting lines together
                    pygame.draw.lines(screen, black, True,
                                      (self.tempPoints[i],
                                       self.tempPoints[i + 1]), 6)

            # sticks
            self.stick.update()

            # bombs
            if self.bomb.bombPoints != (0, 0):  # if it is actually drawn
                self.bomb.draw()
                # make the bomb fall
                if self.bomb.bombPoints[1] + self.bomb.radius <= 610:
                    self.bomb.bombPoints = (self.bomb.bombPoints[0],
                                       self.bomb.bombPoints[1] + gravity)
                else:
                    self.bomb.fallen = True
            if self.exploded:
                screen.blit(self.bomb.explosion, self.explosionPoint)

            # blocks
            if self.block.location != (-1, -1) and not self.block.destroyed:
                self.block.draw()
                self.block.checkCollision(self.gameState, monstersSpawned)
                # make the block fall
                if not self.block.fallen and \
                        self.block.tempRect.top + 300 <= 610:
                    self.block.tempRect.top += gravity
                else:
                    self.block.fallen = True

            # weapons
            if len(self.mainChar.weapon) == 2:
                pygame.draw.lines(screen, black, True,
                                  (self.mainChar.weapon[0],
                                   self.mainChar.weapon[1]), 6)

            # main character
            health = "Health: " + str(self.mainChar.health)
            displayHealth = font.render(health, False, (0, 0, 0))
            self.screen.blit(displayHealth, (self.screenWidth - 170, 0))
            if not self.mainChar.alive:
                self.gameState = "dead"
            if self.mainChar.attackState:
                self.mainChar.attackAnimation()
            self.mainChar.charDisplay()

        elif self.gameState == "dead":
            screen.fill(black)
            totalKills = "Total Kills: " + str(self.monstersKilled)
            displayTotalKills = font2.render(totalKills, False, white)
            screen.blit(displayTotalKills, (20, 20))
            redKills = "Red Blob Kills: " + str(self.redKills)
            displayRedKills = font2.render(redKills, False, white)
            screen.blit(displayRedKills, (20, 120))
            blueKills = "Blue Blob Kills: " + str(self.blueKills)
            displayBlueKills = font2.render(blueKills, False, white)
            screen.blit(displayBlueKills, (20, 220))
            dragonKills = "Dragon Kills: " + str(self.dragonKills)
            displayDragonKills = font2.render(dragonKills, False, (255, 255, 0))
            screen.blit(displayDragonKills, (20, 320))
            thanks = font2.render("Thanks for playing!", False, white)
            screen.blit(thanks, (20, 420))
            allScores = [self.monstersKilled, self.redKills,
                         self.blueKills, self.dragonKills]
            f = open("highscore.txt", "r")
            highScores = f.readlines()
            f.close()
            f = open("highscore.txt", "w")
            count = 0
            for line in highScores:
                if allScores[count] >= int(line[:-1]):
                    f.write(str(allScores[count]) + "\n")
                else:
                    f.write(line)
                count += 1
            f.close()

        elif self.gameState == "high scores":
            f = open("highscore.txt", "r")
            highScores = f.readlines()
            allScores = []
            for line in highScores:
                allScores += [line[:-1]]
            screen.fill(white)
            # title
            title = font2.render("High Scores!", False, black)
            screen.blit(title, (320, 20))

            totalKills = "Total Kills: " + str(allScores[0])
            displayTotalKills = font2.render(totalKills, False, black)
            screen.blit(displayTotalKills, (20, 160))

            redKills = "Red Blob Kills: " + str(allScores[1])
            displayRedKills = font2.render(redKills, False, black)
            screen.blit(displayRedKills, (20, 260))

            blueKills = "Blue Blob Kills: " + str(allScores[2])
            displayBlueKills = font2.render(blueKills, False, black)
            screen.blit(displayBlueKills, (20, 360))

            dragonKills = "Dragon Kills: " + str(allScores[3])
            displayDragonKills = font2.render(dragonKills, False, black)
            screen.blit(displayDragonKills, (20, 460))

            f.close()

            # reset button
            pygame.draw.rect(screen, black, (895, 700, 105, 50), 5)
            reset = font.render("Reset", False, black)
            self.screen.blit(reset, (900, 703))

        elif self.gameState == "edit stage":
            pygame.Surface.blit(self.screen,
                                self.stageBuildScreen, (0 - self.scrollX, 0))

            if self.music == 1:
                lstCount = 0
                f = open("saveState.txt", "r")
                for line in f:
                    if line.startswith("#"):
                        lstCount += 1
                    else:
                        if lstCount == 1:
                            obstaclesAdded.add(Obstacles("rubble.png",
                                                         convertToTuple(line)))
                        elif lstCount == 2:
                            items = convertToLst(line)
                            monstersAdded.add(BlueBlob("monster2.png",
                                                      items[0], items[1],
                                                      items[2], items[3]))
                        elif lstCount == 3:
                            items = convertToLst(line)
                            monstersAdded.add(RedBlob("monster1?.png",
                                                       items[0], items[1],
                                                       items[2], items[3]))
                self.music = 0

            # sketches
            if len(self.tempPoints) >= 2:
                for i in range(len(self.tempPoints)):
                    if i == len(self.tempPoints) - 1:
                        break
                    # connecting lines together
                    pygame.draw.lines(screen, black, True,
                                      (self.tempPoints[i],
                                       self.tempPoints[i + 1]), 6)

            # rubbles
            for obstacle in obstaclesAdded:
                if not obstacle.destroyed:
                    screen.blit(obstacle.image,
                                (obstacle.rect.left - self.scrollX,
                                 obstacle.rect.top))
                if obstacle.rect.top <= 210:
                    obstacle.rect.top += gravity
                else:
                    obstacle.rect.top = 215

            # monsters
            for monster in monstersAdded:
                self.screen.blit(monster.image,
                            (monster.rect.left - self.scrollX,
                             monster.rect.top))
                if monster.rect.top < 499:
                    monster.rect.top += gravity
                else:
                    monster.rect.top = 499

            self.screen.blit(self.monster1, self.monster1pos)
            pygame.draw.rect(screen, black, (9, 7, 126, 126), 5)  # for red
            self.screen.blit(self.monster2, self.monster2pos)
            pygame.draw.rect(screen, black, (150, 7, 126, 126), 5)  # for blue
            # save button
            save = font2.render("Save", False, black)
            self.screen.blit(save, (583, 20))
            pygame.draw.rect(screen, black, (565, 16, 200, 100), 8)
            # clear button
            clear = font2.render("Clear", False, black)
            self.screen.blit(clear, (800, 20))
            pygame.draw.rect(screen, black, (787, 16, 200, 100), 8)
            # exit button
            pygame.draw.rect(screen, black, (9, 700, 100, 50), 8)
            self.screen.fill(white, (9, 700, 100, 50))
            exitGame = font.render("Exit", False, black)
            self.screen.blit(exitGame, (27, 703))

        elif self.gameState == "play stage":
            pygame.Surface.blit(self.screen,
                                self.stageBuildScreen, (0 - self.scrollX, 0))

            if self.music == 1:
                lstCount = 0
                f = open("saveState.txt", "r")
                for line in f:
                    if line.startswith("#"):
                        lstCount += 1
                    else:
                        if lstCount == 1:
                            allObstacles2.add(Obstacles("rubble.png",
                                                        convertToTuple(line)))
                        elif lstCount == 2:
                            items = convertToLst(line)
                            allMonsters2.add(BlueBlob("monster2.png",
                                                      items[0], items[1],
                                                      items[2], "play stage"))
                        elif lstCount == 3:
                            items = convertToLst(line)
                            allMonsters2.add(RedBlob("monster1?.png",
                                                     items[0], items[1],
                                                     items[2], "play stage"))
                self.music = 0

            # rubbles
            for obstacle in allObstacles2:
                if not obstacle.destroyed:
                    screen.blit(obstacle.image,
                                (obstacle.rect.left - self.scrollX,
                                 obstacle.rect.top))
                    if obstacle.rect.top <= 210:
                        obstacle.rect.top += gravity
                    else:
                        obstacle.rect.top = 215

            # monsters
            for monster in allMonsters2:
                if monster.alive:
                    self.screen.blit(monster.image,
                                     (monster.rect.left - self.scrollX,
                                      monster.rect.top))
                    if monster.alive and not isinstance(monster, BlueBlob):
                        monster.checkCollision(self.block, allObstacles2)
                        screen.blit(monster.image,
                                    (monster.rect.left - self.scrollX,
                                     monster.rect.top))
                    elif monster.alive and isinstance(monster, BlueBlob):
                        if monster.right and not monster.left:
                            screen.blit(self.blueRight,
                                        (monster.rect.left - self.scrollX,
                                         monster.rect.top))
                        else:
                            screen.blit(monster.image,
                                        (monster.rect.left - self.scrollX,
                                         monster.rect.top))
                    if isinstance(monster, BlueBlob) and \
                            len(monster.bullets) >= 1:
                        for bullet in monster.bullets:
                            bullet.gameState = self.gameState
                            bullet.update()
                            screen.blit(bullet.image,
                                        (bullet.rect.left - self.scrollX,
                                         bullet.rect.top))
                            try:
                                if bullet.outOfBounds:
                                    monster.bullets.remove(bullet)
                            except:
                                pass
                else:
                    try:
                        allMonsters2.remove(monster)
                    except:
                        pass

            # sticks
            self.stick.update()

            # bombs
            if self.bomb.bombPoints != (
            0, 0):  # if it is actually drawn
                self.bomb.draw()
                # make the bomb fall
                if self.bomb.bombPoints[1] + self.bomb.radius <= 610:
                    self.bomb.bombPoints = (self.bomb.bombPoints[0],
                                            self.bomb.bombPoints[
                                                1] + gravity)
                else:
                    self.bomb.fallen = True
            if self.exploded:
                screen.blit(self.bomb.explosion, self.explosionPoint)

            # blocks
            if self.block.location != (
            -1, -1) and not self.block.destroyed:
                self.block.draw()
                self.block.checkCollision(self.gameState,
                                          monstersSpawned)
                # make the block fall
                if not self.block.fallen and \
                        self.block.tempRect.top + 300 <= 610:
                    self.block.tempRect.top += gravity
                else:
                    self.block.fallen = True

            # weapons
            if len(self.mainChar.weapon) == 2:
                pygame.draw.lines(screen, black, True,
                                  (self.mainChar.weapon[0],
                                   self.mainChar.weapon[1]), 6)

            # main character
            health = "Health: " + str(self.mainChar.health)
            displayHealth = font.render(health, False, (0, 0, 0))
            self.screen.blit(displayHealth, (self.screenWidth - 170, 0))
            if not self.mainChar.alive:
                self.gameState = "Game Over"
            if self.mainChar.attackState:
                self.mainChar.attackAnimation()
            self.mainChar.charDisplay()

            # sketches
            if len(self.tempPoints) >= 2:
                for i in range(len(self.tempPoints)):
                    if i == len(self.tempPoints) - 1:
                        break
                    # connecting lines together
                    pygame.draw.lines(screen, black, True,
                                      (self.tempPoints[i],
                                       self.tempPoints[i + 1]), 6)

            # monsters left
            monstersLeft = "Monsters Left: " + str(len(allMonsters2))
            displayMonstersLeft = font.render(monstersLeft, False, (0, 0, 0))
            self.screen.blit(displayMonstersLeft, (10, 0))

            # exit button
            pygame.draw.rect(screen, black, (9, 700, 100, 50), 8)
            self.screen.fill(white, (9, 700, 100, 50))
            exitGame = font.render("Exit", False, black)
            self.screen.blit(exitGame, (27, 703))


# creating and running the game
game = SketchyQuest()
game.run()



