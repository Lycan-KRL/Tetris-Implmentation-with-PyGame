import pygame
import random
import math
import numpy as np
from enum import Enum, unique

# - - - - - + - - - - - #
# CONSTANTS - kinda
# - - - - - + - - - - - #
BOARD_COLUMNS = 10
BOARD_ROWS = 20
TEXTURE_WIDTH = 288
TEXTURE_HEIGHT = 36
SCREEN_WIDTH = 684
SCREEN_HEIGHT = 900
ARENA_WIDTH = 360
ARENA_HEIGHT = 720

# - - - - - + - - - - - #
# PRESET COLORS
# - - - - - + - - - - - #
# Colors based off RGB values
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Enumerate all 7 shape tetrominos
# Each tetromino is made of 4 blocks
@unique
class Shape(Enum):
    I = 0
    J = 1
    L = 2
    O = 3
    S = 4
    T = 5
    Z = 6

    # So uh, this became an enum too 
    # So shit
    figureT = [
        [1, 3, 5, 7], # I
        [3, 5, 7, 6], # J
        [2, 3, 5, 7], # L
        [2, 3, 4, 5], # O
        [3, 5, 4, 6], # S
        [3, 5, 4, 7], # T
        [2, 4, 5, 7] # Z
    ]

    def giveShapeID():
        return random.randint(0, 6)
    
    def getShapeData(x, y):
        return Shape.figureT.value[x][y], Shape.figureT.value[x][y]

class Tetromino:

    class Point:
        def __init__(self, x=0, y=0):
            self.currX = x
            self.currY = y
            self.prevX = x
            self.prevY = y

    def __init__(self):
        self.id = Shape.giveShapeID()
        self.position = [Tetromino.Point() for i in range(4)]
        self.color = random.randint(0, 7)
        self.block = 36 * self.color
        self.createShape()
        self.freeze = False

    def createShape(self):
        for i in range(4):
            x, y = Shape.getShapeData(self.id, i)
            self.position[i].currX = int(x % 2)
            self.position[i].currY = int(y / 2)
            self.position[i].prevX = self.position[i].currX
            self.position[i].prevY = self.position[i].currY
        
    def rotatePiece(self):
        if self.id == Shape.O.value: return

        centerPt = self.position[1]

        for i in range(4):
            dy = self.position[i].currX - centerPt.currX
            dx = self.position[i].currY - centerPt.currY
            self.position[i].currX = centerPt.currX - dx
            self.position[i].currY = centerPt.currY + dy

        if not self.withinBounds():
            for i in range(4):
                self.position[i].currX = self.position[i].prevX
                self.position[i].currY = self.position[i].prevY


    def withinBounds(self):
        for point in self.position:
            if point.currX < 0 or point.currX * 36 >= SCREEN_WIDTH or point.currY >= SCREEN_HEIGHT:
                return False
            elif point.currY * 36 > ARENA_HEIGHT:
                self.freeze = True
                return False
        return True

    def translatePiece(self, dx):
        reset = False

        for i in range( len(self.position) ):
            self.position[i].prevX = self.position[i].currX
            self.position[i].prevY = self.position[i].currY

            self.position[i].currX += dx

        if not self.withinBounds():
            for i in range(4):
                self.position[i].currX = self.position[i].prevX
                self.position[i].currY = self.position[i].prevY

    def drop(self):
        for i in range(4):
            self.position[i].currY += 1


class Board:
    def __init__(self):
        self.matrix = np.zeros([BOARD_ROWS, BOARD_COLUMNS], dtype=bool)

    def drawGrid(self, screen):
        for i in range(BOARD_ROWS + 1):
            start = ( 36, (i * 36) + 36 )
            end = ( ARENA_WIDTH + 36, (i * 36) + 36 )
            pygame.draw.line(screen, WHITE, start, end)
            for j in range(BOARD_COLUMNS + 1):
                start = ( (j * 36) + 36, 36 )
                end = ( (j * 36) + 36, ARENA_HEIGHT + 36 )
                pygame.draw.line(screen, WHITE, start, end)
                

    def drawBoard(self, tiles, screen, s):
        self.drawGrid(screen)

        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLUMNS):
                if self.matrix[j][i]:
                    

        for i in range(4):
            x = sample.position[i].currX
            y = sample.position[i].currY
            left = sample.block
            screen.blit(tiles, (36*x, 36*y), (left, 0, 36,36))

    def update(self, tetromino):
        for point in tetromino.position:
            x = point.currX
            y = point.currY

            if y >= 20: y = 19
            if x >= 10: x = 9

            self.matrix[y][x] = True

class PyLoop:
    def frameLoop(self):

        # Game's EXIT flag while running
        exitGame = False
        pause = False
        tiles = pygame.image.load("tiles.png")
        tiles = pygame.transform.scale(tiles, (TEXTURE_WIDTH, TEXTURE_HEIGHT))

        # Pygame screen reference and dimensions
        # 'width' and 'height' are individually available for access
        dimensions = width, height = SCREEN_WIDTH, SCREEN_HEIGHT
        screen = pygame.display.set_mode(dimensions)

        # Keep track of the elapsed time per frame
        clock = pygame.time.Clock()
        delay = 0
        limit = 400

        # The game runs while the flag remains False
        while not exitGame:

            # Each tetromino may move if the player decides to
            # Available: Left, Right, and Down
            dx = 0

            # Up rotates the object
            rotate = False
            delay += clock.get_time()

            # - - - Events - - - #
            for e in pygame.event.get():
                # Click the 'X' to close the game
                if e.type == pygame.QUIT: 
                    exitGame = True

                # Triggered while a key is down
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:
                        dx = -1
                    elif e.key == pygame.K_RIGHT:
                        dx = 1
                    elif e.key == pygame.K_UP:
                        rotate = True
                    elif e.key == pygame.K_DOWN:
                        limit = 100
                    elif e.key == pygame.K_p:
                        pause = not pause
                    elif e.key == pygame.K_q:
                        exitGame = True

                if e.type == pygame.KEYUP:
                    if e.key == pygame.K_DOWN:
                        limit = 300

            # - - - The Game can Pause - - - #
            if pause: 
                delay = 0
                continue

            # - - - Tetromino Mechanics - - - #
            if dx != 0: sample.translatePiece(dx)
            if rotate: sample.rotatePiece()

            if delay >= limit:
                delay = 0
                sample.drop()

                if not sample.withinBounds():
                    gameBoard.update(sample)
                    print("Generate New Shape")
                    

            # - - - Graphics - - - #
            screen.fill(BLACK)
            gameBoard.drawBoard(tiles, screen, sample)
            pygame.display.flip()

            # Lock at 60fps
            clock.tick(60)

# - - - - - + - - - - - #
# USABLE OBJECTS
# - - - - - + - - - - - #
gameFunction = PyLoop()
gameBoard = Board()
sample = Tetromino()