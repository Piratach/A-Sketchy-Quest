import pygame, math

from pygamegam import PygameGame
from charSprites import CharSprites, RedBlob, Obstacles, BlueBlob, Dragon
from SketchedObjects import Stick, Bomb, Block

size = width, height = 1024, 768
screen = pygame.display.set_mode(size)  # my surface
allMonsters = pygame.sprite.Group()
allObstacles = pygame.sprite.Group()
blueBlobs = pygame.sprite.Group()

black = 0, 0, 0
white = 255, 255, 255
gravity = 8

pygame.mixer.init(48000, -16, 1, 1024)  # initializing sound, shamelessly stolen from stackoverflow

# please play with music!!

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
            if abs(i - j) <= 10:  # each point compared must be at least 11 points apart
                continue
            elif abs(tempPoints[i][0] - tempPoints[j][0]) <= 40 and abs(tempPoints[i][1] - tempPoints[j][1]) <= 40:
                count += 1
            if count >= 6:  # at least 10 such points must be close to one another
                return [True, tempPoints[i]]
    return [False]

def isCorner(tempPoints):
    # this function doesn't actually count the number of corners
    # but if numCorner is high, it is likely that the
    # shape drawn has many corners
    numCorner = 0
    for i in range(len(tempPoints)):
        for j in range(len(tempPoints)):
            if abs(i - j) >= 3 or (i - j) == 0:  # each point compared must be at most 3 points apart
                continue
            elif abs(tempPoints[i][0] - tempPoints[j][0]) <= 5:  # straight vertical line section of block
                try:
                    if abs(tempPoints[i][0] - tempPoints[j + 3][0]) <= 20: # corner
                        numCorner += 1
                except:
                    pass
            elif abs(tempPoints[i][1] - tempPoints[j][1]) <= 5:
                try:
                    if abs(tempPoints[i][1] - tempPoints[j + 3][1]) <= 20:  # corner
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
        self.ground = 465  # we will work on ground/platforming
        self.mainChar = CharSprites("characterDude(COLOURED).png", (21, self.ground))
        self.health3 = pygame.image.load("health3.png")
        self.health3rect = self.health3.get_rect()
        self.health3rect.right, self.health3rect.top = self.screenWidth, 0
        self.health2 = pygame.image.load("health2.png")
        self.health2rect = self.health3.get_rect()
        self.health2rect.right, self.health2rect.top = self.screenWidth, 0
        self.health1 = pygame.image.load("health1.png")
        self.health1rect = self.health1.get_rect()
        self.health1rect.right, self.health1rect.top = self.screenWidth, 0

        # monsterA - can only move around
        # stage 1
        self.redblob1 = RedBlob("monster1?.png", (2000, 499), 600, -5, "stage1")
        self.redblob2 = RedBlob("monster1?.png", (4000, 499), 600, 5, "stage1")
        self.redblob3 = RedBlob("monster1?.png", (6000, 499), 600, 10, "stage1")
        self.redblob4 = RedBlob("monster1?.png", (9000, 499), 600, 10, "stage1")

        # stage 2
        self.redblob5 = RedBlob("monster1?.png", (2000, 499), 600, -10, "stage2")
        self.redblob6 = RedBlob("monster1?.png", (4000, 499), 600, 10, "stage2")
        allMonsters.add(self.redblob1, self.redblob2, self.redblob3, self.redblob4,
                        self.redblob5, self.redblob6)

        # monsterB - can attack with projectiles
        self.blueRight = pygame.image.load("monster2a.png")
        # stage 1
        self.blueblob1 = BlueBlob("monster2.png", (5000, 499), 1500, 25, "stage1")
        self.blueblob2 = BlueBlob("monster2.png", (8000, 499), 2000, 30, "stage1")
        self.blueblob3 = BlueBlob("monster2.png", (9500, 499), 1500, 30, "stage1")

        # stage 2
        self.blueblob4 = BlueBlob("monster2.png", (5000, 499), 1500, 30, "stage2")
        self.blueblob5 = BlueBlob("monster2.png", (7000, 499), 1500, 35, "stage2")
        blueBlobs.add(self.blueblob1, self.blueblob2, self.blueblob3,
                      self.blueblob4, self.blueblob5)
        allMonsters.add(self.blueblob1, self.blueblob2, self.blueblob3,
                        self.blueblob4, self.blueblob5)

        # boss - can breathe fire
        self.boss = Dragon("dragon.png", (550, 0))

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
        self.title3 = False
        self.titleScreen = pygame.image.load("aSketchyQuestTitleScreen.png")
        self.titleScreenRect = self.titleScreen.get_rect()
        self.titleScreen2 = pygame.image.load("aSketchyQuestTitleScreen2.png")
        self.titleScreen2Rect = self.titleScreen.get_rect()
        self.titleScreen3 = pygame.image.load("aSketchyQuestTitleScreen3.png")
        self.titleScreen3Rect = self.titleScreen.get_rect()

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

        # game over state
        self.gameOverScreen = pygame.image.load("Game Over!!.png")
        self.gameOverScreenRect = self.gameOverScreen.get_rect()

    def mousePressed(self, x, y):
        # no mousePressed is needed for title screen
        if self.gameState == "stage1" or self.gameState == "stage2" or self.gameState == "boss1":
            self.tempPoints += [(x, y)]

    def mouseReleased(self):
        if self.gameState == "stage1" or self.gameState == "stage2" or self.gameState == "boss1":
            print("Length: ", len(self.tempPoints))
            print("Corners: ", isCorner(self.tempPoints))
            if withinBounds(self.tempPoints):
                try:
                    # blocks
                    if isBlock(self.tempPoints)[0]:
                        points = isBlock(self.tempPoints)[1]
                        self.block = Block(points, (points[0] + self.scrollX, points[1]))
                        if self.block.rect.top + self.block.height >= 610:
                            self.block = Block((-1, -1), (-1, -1))
                            self.tempPoints = []
                        else:
                            self.block.colour = self.colour
                            self.block.timer = 150
                            self.block.destroyed = False
                            self.tempPoints = []

                    # bombs
                    elif isCircle(self.tempPoints)[0]:  # isCircle returns a list of truth value and a point
                        centreX = isCircle(self.tempPoints)[1][0]
                        centreY = isCircle(self.tempPoints)[1][1]
                        bombPoints = (centreX, centreY)
                        radius = 40
                        explosionRadius = 200
                        self.tempPoints = []
                        self.bomb = Bomb((centreX - radius, centreY - radius), bombPoints,
                                         (bombPoints[0] + self.scrollX, bombPoints[1]),
                                         radius, explosionRadius)
                        self.bomb.colour = self.colour
                        self.bomb.fallen = False
                        self.bomb.fuse = 0

                    # sticks
                    else:
                        self.stickPoints = [self.tempPoints[0], self.tempPoints[-1]]  # adding a permanent stick
                        self.stickLen = getDistance(self.stickPoints[0], self.stickPoints[1])
                        self.tempPoints = []  # removing sketches
                        self.stickFallen = False
                        self.stick = Stick(self.stickPoints, self.stickLen, self.stickFallen)
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
            elif self.title2:
                if currKey == "w" or currKey == "up":
                    self.title2 = False
                    self.title1 = True
                elif currKey == "s" or currKey == "down":
                    self.title2 = False
                    self.title3 = True
            else:
                if currKey == "w" or currKey == "up":
                    self.title3 = False
                    self.title2 = True

        # for the game screen
        elif self.gameState == "stage1" or self.gameState == "stage2" or self.gameState == "boss1":
            #  move left and right has been implemented in the run function
            if currKey == "d":
                self.mainChar.weapon = self.mainChar.weaponRight
            elif currKey == "a":
                self.mainChar.weapon = self.mainChar.weaponLeft
            elif currKey == "space" or currKey == "left shift":
                self.mainChar.jump()
            elif currKey == "w":  # equip sticks
                # can only equip if near and stick has fallen
                if len(self.stick.stickPoints) == 2 and \
                        abs(self.mainChar.tempRect - self.stick.stickPoints[0][0]) <= 200 and self.stick.fallen:
                    self.mainChar.equip(self.stick)
                    self.stick = Stick([], 0, False)
            elif currKey == "q":
                # cheat code
                self.mainChar.health = 300

            # equipped state
            if self.mainChar.equipped:
                if not self.mainChar.attackState and currKey == "s":  # attack
                    self.mainChar.attackState = True
                    self.mainChar.angle = 0
                    self.mainChar.weaponDown = False
                    self.mainChar.attack(allMonsters, self.boss)

    def timerFired(self, dt):
        if self.gameState == "stage1" or self.gameState == "stage2" or self.gameState == "boss1":
            self.timerCalls += 1
            # bombs
            if self.bomb.fallen:
                self.bomb.fuse += 1  # start counting after bomb has fallen
                if self.bomb.fuse % 50 == 0:
                    self.explosionPoint = (self.bomb.bombPoints[0] - 200,
                                           self.bomb.bombPoints[1] - 200)
                    self.bomb.explode(allMonsters, allObstacles, self.mainChar)
                    self.exploded = True
            for monster in allMonsters:
                if monster.stage == self.gameState:
                    monster.update()
            for dudes in blueBlobs:
                if dudes.alive:
                    dudes.fire(self.mainChar)  # sends out the projectiles
            self.mainChar.update(allMonsters, self.boss.fire, self.boss, allObstacles, self.block, self.gameState)
            if self.exploded:
                self.explosionDelay += 1
            if self.explosionDelay % 20 == 0:
                self.exploded = False
                self.explosionDelay = 0
            self.block.time()
        if self.gameState == "boss1":
            self.boss.fly()
            self.boss.attack()
            if self.boss.attacking:
                self.boss.fire.update(self.block, self.mainChar)
        if self.credits:
            self.mainChar.creditsDelay -= 1

    def redrawAll(self, screen):

        # title screen
        if self.title1:
            self.screen.blit(self.titleScreen, self.titleScreenRect)
        elif self.title2:
            self.screen.blit(self.titleScreen2, self.titleScreen2Rect)
        elif self.title3:
            self.screen.blit(self.titleScreen3, self.titleScreen3Rect)

        # music
        if self.gameState == "start":
            if self.music == 0:
                pygame.mixer.music.load("titleTheme.wav")  # from wii sports resort
                pygame.mixer.music.play(-1)
                self.music = 1

        # game screen
        elif self.gameState == "stage1" or self.gameState == "stage2" or self.gameState == "boss1":

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
                pygame.mixer.music.load("Boss Theme.wav")  # from final fantasy VII
                pygame.mixer.music.play(-1)
                self.music = 4

            if self.gameState == "stage1":
                pygame.Surface.blit(self.screen, self.gameScreen, (0 - self.scrollX, 0))
            elif self.gameState == "stage2":
                pygame.Surface.blit(self.screen, self.stage2Screen, (0 - self.scrollX, 0))
            elif self.gameState == "boss1":
                pygame.Surface.blit(self.screen, self.bossScreen, self.bossScreenRect)

            # obstacles
            for obstacle in allObstacles:
                if not obstacle.destroyed:
                    screen.blit(obstacle.image, (obstacle.rect.left - self.scrollX, obstacle.rect.top))

            # monsters
            # monsterA
            for monster in allMonsters:
                if monster.stage == self.gameState:
                    if monster.alive and not isinstance(monster, BlueBlob):
                        monster.checkCollision(self.block)
                        screen.blit(monster.image, (monster.rect.left - self.scrollX, monster.locationY))
                    elif monster.alive and isinstance(monster, BlueBlob):
                        if monster.right and not monster.left:
                            screen.blit(self.blueRight, (monster.rect.left - self.scrollX, monster.locationY))
                        else:
                            screen.blit(monster.image, (monster.rect.left - self.scrollX, monster.locationY))
                    if isinstance(monster, BlueBlob) and len(monster.bullets) >= 1:
                        for bullet in monster.bullets:
                            bullet.gameState = self.gameState
                            bullet.update()
                            screen.blit(bullet.image,
                                        (bullet.rect.left - self.scrollX, bullet.rect.top))
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
                elif not self.boss.alive:
                    self.music = 6
                    self.credits = True

            # sketches
            if len(self.tempPoints) >= 2:
                for i in range(len(self.tempPoints)):
                    if i == len(self.tempPoints) - 1:
                        break
                    # connecting lines together
                    pygame.draw.lines(screen, self.colour, True, (self.tempPoints[i], self.tempPoints[i + 1]), 6)

            # sticks
            self.stick.update()

            # bombs
            if self.bomb.bombPoints != (0, 0):  # if it is actually drawn
                self.bomb.draw()
                # make the bomb fall
                if self.bomb.bombPoints[1] + self.bomb.radius <= 610:
                    self.bomb.bombPoints = (self.bomb.bombPoints[0], self.bomb.bombPoints[1] + gravity)
                else:
                    self.bomb.fallen = True
            if self.exploded:
                self.screen.blit(self.bomb.explosion, self.explosionPoint)

            # blocks
            if self.block.location != (-1, -1) and not self.block.destroyed:
                self.block.draw()
                self.block.checkCollision(self.gameState, allMonsters)
                # make the block fall
                if not self.block.fallen and self.block.tempRect.top + 300 <= 610:
                    self.block.tempRect.top += gravity
                else:
                    self.block.fallen = True

            # weapons
            if len(self.mainChar.weapon) == 2:
                pygame.draw.lines(screen, self.colour, True, (self.mainChar.weapon[0], self.mainChar.weapon[1]), 6)

            # main character
            if self.mainChar.health == 3:
                screen.blit(self.health3, self.health3rect)
            elif self.mainChar.health == 2:
                screen.blit(self.health2, self.health2rect)
            elif self.mainChar.health == 1:
                screen.blit(self.health1, self.health1rect)
            if not self.mainChar.alive:
                print(self.mainChar.health)
                self.gameState = "Game Over"
            if self.mainChar.attackState:
                self.mainChar.attackAnimation()
            if self.mainChar.rect.left >= self.gameScreenLen:
                if self.gameState == "stage1":
                    self.gameState = "stage2"
                elif self.gameState == "stage2":
                    self.gameState = "boss1"
            self.mainChar.charDisplay()

            # credits
            if self.credits:
                if self.mainChar.creditsDelay != 20 and self.mainChar.creditsDelay > 0:
                    pygame.mixer.music.load("credits.wav")
                    pygame.mixer.music.play(1)
                elif self.mainChar.creditsDelay == 20:
                    self.mainChar.rect.top = self.ground
                    self.mainChar.weapon = []
                    self.mainChar.tempWeapon = []
                    self.mainChar.weaponLeft = []
                    self.mainChar.weaponRight = []
                    self.mainChar.equipped = False
                elif self.mainChar.creditsDelay <= 0:
                    self.mainChar.rect.top -= 1
                    if self.mainChar.rect.top + self.mainChar.height <= -483: # correct timing!!
                        self.gameState = "credits"
                    if self.music == 6:
                        pygame.mixer.music.load("credits.wav")  # from final fantasy III
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


# creating and running the game
game = SketchyQuest()
game.run()



