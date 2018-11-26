import pygame
import math

'''
pygamegame.py
created by Lukas Peraza
 for 15-112 F15 Pygame Optional Lecture, 11/11/15
'''

size = width, height = 1024, 768

black = 0, 0, 0
white = 255, 255, 255
gravity = 8

class CharSprites:

    def __init__(self, fileName, location):
        pass

    def charDisplay(self):
        pass

    def moveRight(self):
        pass

    def moveLeft(self):
        pass

    def jump(self):
        pass


class PygameGame(object):

    def init(self):
        pass

    def mousePressed(self, x, y):
        pass

    def mouseReleased(self):
        pass

    def mouseMotion(self, x, y):
        pass

    def mouseDrag(self, x, y):
        pass

    def keyPressed(self, currKey):
        pass

    def keyReleased(self, keyCode, modifier):
        pass

    def timerFired(self, dt):
        pass

    def redrawAll(self, screen):
        pass

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=600, height=400, fps=50, title="112 Pygame Game"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        pygame.init()

    def run(self):
        clock = pygame.time.Clock()
        # set the title of the window
        pygame.display.set_caption(self.title)
        # stores all the keys currently being held down
        self._keys = dict()
        # call game-specific initialization
        self.init()
        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)

            # jump!
            if self.mainChar.jumpState:  # while jumping
                if self.mainChar.tempWeapon == []:
                    self.mainChar.tempWeapon = self.mainChar.weapon
                self.mainChar.rect.top -= self.mainChar.velocity
                if self.mainChar.equipped:
                    self.mainChar.weapon = [(self.mainChar.weapon[0][0],
                                             self.mainChar.weapon[0][1] - self.mainChar.velocity),
                                            (self.mainChar.weapon[1][0],
                                             self.mainChar.weapon[1][1] - self.mainChar.velocity)]
                    self.mainChar.weaponRight = [(self.mainChar.weaponRight[0][0],
                                                  self.mainChar.weaponRight[0][1] - self.mainChar.velocity),
                                                 (self.mainChar.weaponRight[1][0],
                                                  self.mainChar.weaponRight[1][1] - self.mainChar.velocity)]
                    self.mainChar.weaponLeft = [(self.mainChar.weaponLeft[0][0],
                                                 self.mainChar.weaponLeft[0][1] - self.mainChar.velocity),
                                                (self.mainChar.weaponLeft[1][0],
                                                 self.mainChar.weaponLeft[1][1] - self.mainChar.velocity)]
                self.mainChar.velocity -= self.mainChar.gravity
                if self.mainChar.rect.top >= 465:
                    self.mainChar.rect.top = 465  # in case character goes above 465
                    if self.mainChar.equipped:
                        if self.mainChar.right:
                            self.mainChar.weapon = [(self.mainChar.weapon[0][0],
                                                     self.mainChar.tempWeapon[0][1]),
                                                    (self.mainChar.weapon[0][0] + self.stickLen,
                                                     self.mainChar.weapon[0][1])]
                        elif self.mainChar.left:
                            self.mainChar.weapon = [(self.mainChar.weapon[0][0],
                                                     self.mainChar.tempWeapon[0][1]),
                                                    (self.mainChar.weapon[0][0] - self.stickLen,
                                                     self.mainChar.weapon[0][1])]
                    self.mainChar.tempWeapon = []
                    self.mainChar.jumpState = False

            # hold key to move continuously
            # https://stackoverflow.com/questions/9961563/how-can-i-make-a-sprite-move-when-key-is-held-down
            if self.gameState == "game":
                currKeys = pygame.key.get_pressed()
                if currKeys[pygame.K_d]:
                    self.mainChar.moveRight()
                    #  add stuff for when he's halfway over only
                    if not self.mainChar.blocked:
                        if self.scrollX == 0:
                            if self.mainChar.tempRect + self.mainChar.width / 2 + self.scrollSpeed >= width / 2:
                                self.scrollSpeed = 15
                            else:
                                self.scrollSpeed = 0
                        elif self.scrollX >= self.gameScreenLen - self.screenWidth:
                            self.scrollX = self.gameScreenLen - self.screenWidth
                            self.scrollSpeed = 0
                        self.scrollX += self.scrollSpeed
                        # check if there's a stick
                        if len(self.stick.stickPoints) == 2:
                            self.stick.stickPoints = [(self.stick.stickPoints[0][0] - self.scrollSpeed,
                                                       self.stick.stickPoints[0][1]),
                                                      (self.stick.stickPoints[1][0] - self.scrollSpeed,
                                                       self.stick.stickPoints[1][1])]
                        # check if there's a bomb
                        if self.bomb.bombPoints != (0, 0):
                            self.bomb.bombPoints = (self.bomb.bombPoints[0] - self.scrollSpeed,
                                                    self.bomb.bombPoints[1])
                        if self.exploded:
                            self.explosionPoint = (self.explosionPoint[0] - self.scrollSpeed, self.explosionPoint[1])

                elif currKeys[pygame.K_a]:
                    #  when it's at the end, nothing happens
                    if self.scrollX == 0:
                        self.scrollSpeed = 0
                    elif self.scrollX < 0:
                        self.scrollX = 0
                        self.scrollSpeed = 0
                    elif self.scrollX >= self.gameScreenLen - self.screenWidth:
                        if self.mainChar.tempRect + self.mainChar.width / 2 + self.scrollSpeed <= 517.5:
                            self.scrollX = self.gameScreenLen - self.screenWidth
                            self.scrollSpeed = 15
                        else:
                            self.scrollX = self.gameScreenLen - self.screenWidth
                            self.scrollSpeed = 0
                    else:
                        if self.mainChar.tempRect + self.mainChar.width / 2 + self.scrollSpeed > width / 2:
                            self.scrollSpeed = 15
                    self.scrollX -= self.scrollSpeed
                    self.mainChar.moveLeft()
                    # check if there's a stick
                    if len(self.stick.stickPoints) == 2:
                        self.stick.stickPoints = [(self.stick.stickPoints[0][0] + self.scrollSpeed,
                                             self.stick.stickPoints[0][1]),
                                            (self.stick.stickPoints[1][0] + self.scrollSpeed,
                                             self.stick.stickPoints[1][1])]
                    # check if there's a bomb
                    if self.bomb.bombPoints != (0, 0):
                        self.bomb.bombPoints = (self.bomb.bombPoints[0] + self.scrollSpeed,
                                                self.bomb.bombPoints[1])

            for event in pygame.event.get():
                if pygame.mouse.get_pressed()[0] == 1:
                    # changed so that it keeps recording
                    # the various points drawn
                    pos = pygame.mouse.get_pos()
                    self.mousePressed(pos[0], pos[1])
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouseReleased()
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*event.pos)
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDrag(*event.pos)
                elif event.type == pygame.KEYDOWN:
                    currKey = pygame.key.name(event.key)
                    self.keyPressed(currKey)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    self.keyReleased(event.key, event.mod)
                elif event.type == pygame.QUIT:
                    playing = False
            self.redrawAll(self.screen)
            pygame.display.update()

        pygame.quit()


def main():
    game = PygameGame()
    game.run()


if __name__ == '__main__':
    main()