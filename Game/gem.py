import pygame
import pygame.freetype
import random
import numpy as np

# - - - - - + - - - - - #
# CONSTANTS - kinda
# - - - - - + - - - - - #
BOARD_COLUMNS = 10
BOARD_ROWS = 20
SCREEN_WIDTH = 612
SCREEN_HEIGHT = 792
ARENA_X = 360
ARENA_Y = 720
SCALE_OFFSET = 36
GRID_OFFSET = 36

# - - - - - + - - - - - #
# PRESET COLORS
# - - - - - + - - - - - #
# Colors based off RGB values
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# - - - - - + - - - - - #
# GLOBAL ARRAY
# - - - - - + - - - - - #
matrix = np.zeros([BOARD_ROWS, BOARD_COLUMNS], dtype=int)

# - - - - - + - - - - - #
# Shape Class
# * Info on all 7 shapes possible
# * Assign/Retrieve shape data
# - - - - - + - - - - - #
class Shape:
    I_SHAPE = 0
    O_SHAPE = 3

    figureT = [
        [1, 3, 5, 7], # I
        [3, 5, 7, 6], # J
        [2, 3, 5, 7], # L
        [2, 3, 4, 5], # O
        [3, 5, 4, 6], # S
        [3, 5, 4, 7], # T
        [2, 4, 5, 7] # Z
    ]

    @staticmethod
    def giveShapeID():
        return random.randint(0, 6)

    @staticmethod
    def getShapeData(x, y):
        return Shape.figureT[x][y]

# - - - - - + - - - - - #
# Point Class
# * 2D Coordinate System
# * Hold current/previous locations
# - - - - - + - - - - - #
class Point:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.px = 0
        self.py = 0
        self.hasBlock = False
        self.blockRef = None

    def set(self, x, y):
        self.px = self.x
        self.py = self.y
        self.x = x
        self.y = y

    def move(self, x, y):
        self.px = self.x
        self.py = self.y
        self.x += x
        self.y += y

    def reset(self):
        #print("OLD: " + str(self.px) + ", " + str(self.py))
        self.x = self.px
        self.y = self.py

# - - - - - + - - - - - #
# Tetromino Class
# * All tetrominos work from this class
# * Translate, Rotate, Bounds
# * Gravity, Creation
# - - - - - + - - - - - #
class Tetromino:
    def __init__(self):
        self.id = Shape.giveShapeID()
        self.position = [Point() for i in range(4)]
        self.color = (random.randint(0, 7)) * SCALE_OFFSET
        self.letThereBeShape()
        self.freeze = False
        self.overlapping = False
        self.outside = False

    def drawTetromino(self, tiles, screen):
        for pt in self.position:
            nx = SCALE_OFFSET * pt.x
            ny = SCALE_OFFSET * pt.y
            screen.blit(tiles, (nx, ny), (self.color, 0, 36, 36))

    def resetPosition(self):
        for i in range(4):
            self.position[i].reset()

    def letThereBeShape(self):
        for i in range(4):
            x = self.id
            y = Shape.getShapeData(x, i)
            self.position[i].x = int(y % 2) + 5
            self.position[i].y = int(y / 2) if x != Shape.I_SHAPE else int(y / 2) + 1
            self.position[i].px = self.position[i].x
            self.position[i].py = self.position[i].y

    def withinBounds(self):
        global matrix
        for pt in self.position:
            #print("Point: " + str(pt.x-1) + ", " + str(pt.y-1))
            if pt.x < 1 or pt.x > BOARD_COLUMNS or pt.y-1 >= BOARD_ROWS:
                #print("BOUNDS")
                self.outside = True
                return False
            elif matrix[pt.y-1][pt.x-1] != 0:
                #print("ALREADY THERE")
                self.overlapping = True
                return False
        return True

    def experiment(self):
        global matrix
        for pt in self.position:
            if pt.x < 1 or pt.x > BOARD_COLUMNS or pt.y-1 >= BOARD_ROWS:
                self.outside = True
                #print("BOUNDS")
            elif matrix[pt.y-1][pt.x-1] != 0:
                self.overlapping = True
                #print("ALREADY THERE")

    def gravity(self):
        reset = False
        for i in range(4):
            self.position[i].move(0, 1)

        if not self.withinBounds():
            self.freeze = True
            self.resetPosition()

    def translatePiece(self, dx):
        reset = False
        for i in range(4):
            self.position[i].move(dx, 0)

        if not self.withinBounds():
            #print("Reset")
            self.outside = False
            self.overlapping = False
            self.resetPosition()

    def rotatePiece(self):
        # O block doesn't rotate
        if self.id == Shape.O_SHAPE: return

        # Center axis is block[1]
        center = self.position[1]

        for i in range(4):
            dx = center.x - (self.position[i].y - center.y)
            dy = center.y + (self.position[i].x - center.x)
            self.position[i].set(dx, dy)

        self.experiment()

        if self.overlapping:
            #print("OVERLAP")
            self.overlapping = False
            self.resetPosition()
        elif self.outside:
            #print("OUTSIDE")
            self.outside = False
            maxDiff = 0
            vert = 0
            tooLeft = False
            tooRight = False
            tooDown = False
            self.outside = False
            array = [[self.position[i].px, self.position[i].py] for i in range(4)]
            for i in range(4):
                x, y = self.position[i].x, self.position[i].y
                #print(x)
                if x < 1: tooLeft = True
                if x > BOARD_COLUMNS: tooRight = True
                if y > BOARD_ROWS: tooDown = True
                if tooLeft and x <= maxDiff:
                    maxDiff = x
                    #print("E")
                if tooRight and x >= maxDiff:
                    maxDiff = x
                    #print("F")
                if tooDown and y >= vert:
                    vert = y

            maxDiff = -maxDiff + 1 if tooLeft else BOARD_COLUMNS - maxDiff
            if tooLeft or tooRight:
                [self.position[i].move(maxDiff, 0) for i in range(4)]
            if tooDown: [self.position[i].move(0,BOARD_ROWS-(vert+1)) for i in range(4)]
            self.experiment()
            if self.overlapping:
                for i in range(4):
                    self.position[i].px = array[i][0]
                    self.position[i].py = array[i][1]
                self.overlapping = False
                self.resetPosition()

# - - - - - + - - - - - #
# Grid Class
# * Holds current info on arena and moving tetrominos
# * Draw Grid/Shapes and Update for New Shapes
# - - - - - + - - - - - #
class Grid:
    def __init__(self, tetromino, screen, tiles):
        self.curr = tetromino
        self.next = Tetromino()
        self.window = screen
        self.texture = tiles

    def clearLines(self):
        global matrix
        k = BOARD_ROWS - 1
        for i in range(BOARD_ROWS-1, 0, -1):
            counter = 0
            for j in range(BOARD_COLUMNS):
                if matrix[i][j] != 0: counter += 1
                matrix[k][j] = matrix[i][j]
            if counter < BOARD_COLUMNS: k -= 1

    def drawBoard(self):
        self.drawPreview()
        self.clearLines()
        global matrix

        for i in range( BOARD_ROWS ):
            for j in range( BOARD_COLUMNS ):
                if matrix[i][j] != 0:
                    color = matrix[i][j] - 1
                    nx = (SCALE_OFFSET * (j+1))
                    ny = (SCALE_OFFSET * (i+1))
                    self.window.blit(self.texture, (nx, ny), (color, 0, 36, 36))

        self.drawGrid()

    def drawGrid(self):
        for i in range( BOARD_ROWS + 1 ):
            start = ( GRID_OFFSET, (i * SCALE_OFFSET) + GRID_OFFSET )
            end = ( ARENA_X + GRID_OFFSET, ( i * SCALE_OFFSET ) + GRID_OFFSET )
            pygame.draw.line(self.window, WHITE, start, end)

            for j in range( BOARD_COLUMNS + 1  ):
                start = ( (j * SCALE_OFFSET) + GRID_OFFSET, GRID_OFFSET )
                end = ( (j * SCALE_OFFSET) + GRID_OFFSET, ARENA_Y + GRID_OFFSET )
                pygame.draw.line(self.window, WHITE, start, end)

    def drawPreview(self):
        for pt in self.next.position:
            nx = (pt.x * SCALE_OFFSET) + 290
            #print("nx = " + str(nx))
            ny = (pt.y * SCALE_OFFSET) + 290
            #print("ny = " + str(ny))
            self.window.blit(self.texture, (nx, ny), (self.next.color, 0, 36, 36))

        for i in range(5):
            start = (468, (i * SCALE_OFFSET) + GRID_OFFSET + 288)
            end = (540, (i * SCALE_OFFSET) + GRID_OFFSET + 288)
            pygame.draw.line(self.window, WHITE, start, end)
            for j in range(3):
                start = ( (j * SCALE_OFFSET) + GRID_OFFSET + 432, 324 )
                end = ( (j * SCALE_OFFSET) + GRID_OFFSET + 432, 468 )
                pygame.draw.line(self.window, WHITE, start, end)

    def update(self):
        global matrix
        for pt in self.curr.position:
            #print("pt: " + str(pt.px-1) + ", " + str(pt.py-1))
            matrix[pt.py-1][pt.px-1] = self.curr.color + 1
            #print("Color = " + str(self.ref.color))
        self.curr = self.next
        self.next = Tetromino()
        return self.curr

    def gameOver(self):
        global matrix
        for pt in self.curr.position:
            if matrix[pt.y-1][pt.x-1] != 0:
                return True
        return False

    def restart(self):
        global matrix
        self.curr = self.next
        self.next = Tetromino()
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLUMNS):
                matrix[i][j] = 0
        return self.curr

# - - - - - + - - - - - #
# PyLoop Class
# * Loop that handles each frame
# - - - - - + - - - - - #
class PyLoop:
    def __init__(self):
        # Game flags
        pygame.init()
        pygame.font.init()
        # Create window and title the game
        dimensions = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(dimensions)
        pygame.display.set_caption("TETRIS")
        # Retrieve blocks and background for the game
        self.bg = pygame.image.load("Images/tetrisbackground.png")
        self.bg = pygame.transform.scale(self.bg, (900, 900))
        self.bg.set_alpha(90)
        self.tiles = pygame.image.load("Images/tiles.png")
        self.tiles = pygame.transform.scale(self.tiles, (288, 36))
        # Text nonsense
        font = pygame.font.Font("Quantico/Quantico-Regular.ttf", 50)
        self.nextSurf = font.render("Next", True, WHITE)
        self.endSurf = font.render("Oh No", True, WHITE)

    def frameLoop(self):
        # These handle block and board drawing/calculating respectively
        tetromino = Tetromino()
        grid = Grid(tetromino, self.screen, self.tiles)

        exitGame = False
        endGame = False
        pause = False

        # Keep track of the elapsed time per frame
        clock = pygame.time.Clock()
        timer = 0
        limit = 800

        while not exitGame:

            # Each tetromino moves: Left, Right, and Down
            # Up rotates the object
            dx = 0
            rotate = False

            # Accumulate time from previous tick
            timer += clock.get_time()

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
                    elif e.key == pygame.K_SPACE:
                        endGame = False
                        tetromino = grid.restart()
                        timer = 0

                if e.type == pygame.KEYUP:
                    if e.key == pygame.K_DOWN:
                        limit = 800

            # - - - The Game can Pause - - - #
            if pause:
                timer = 0
                continue
            elif endGame:
                self.screen.blit(self.endSurf, (435, 580))
                pygame.display.flip()
                continue

            # - - - Tetromino Mechanics - - - #
            if dx != 0: tetromino.translatePiece(dx) # tetromino.translatePiece()
            if rotate: tetromino.rotatePiece() # tetromino.rotatePiece()

            if timer >= limit:
                timer = 0
                tetromino.gravity()

                if tetromino.freeze or not tetromino.withinBounds():
                    #print("Limit Reached")
                    tetromino = grid.update()
                    if grid.gameOver():
                        print("SAD FACE")
                        endGame = True

            # - - - Graphics - - - #
            self.screen.fill(BLACK)
            # - - -
            self.screen.blit(self.bg, (0,0))
            self.screen.blit(self.nextSurf, (450, 250))
            tetromino.drawTetromino(self.tiles, self.screen)
            grid.drawBoard()
            # - - -
            pygame.display.flip()
            # Up to 60fps allowed
            clock.tick(60)
