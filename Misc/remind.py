import pygame as py
import sys

def main():
    # You need to initialize the library
    py.init()

    # Define screen size. This makes a tuple
    size = width, height = 1000, 800
    # Bouncing ball animation. x-velocity = y-velocity = 2
    speed = [2, 2]
    # Colors go by RGB, so black is 0,0,0
    black = 0, 0, 0

    # Return a pointer to the display screen
    screen = py.display.set_mode(size)

    # Retrieve image from files
    ball = py.image.load("ball.png")
    ball = py.transform.scale(ball, (int(1233/4), int(1216/4)))
    # Internally, I need to know its "physical" borders
    ballRect = ball.get_rect()

    cock = py.time.Clock()
    timestep = 0

    # Intentional infinite loop for calculations
    while 1:
        # The timestep is reliant upon a specified framerate
        cock.tick()
        timestep += cock.get_time()

        # Event handler for key/button presses
        for event in py.event.get():
            # If the event = QUIT (a constant), exit the game
            if event.type == py.QUIT: sys.exit()

        if timestep >= 1/100:
            timestep = 0
            ballRect = ballRect.move(speed)

        if ballRect.left < 0 or ballRect.right > width:
            speed[0] = -speed[0]
        if ballRect.top < 0 or ballRect.bottom > height:
            speed[1] = -speed[1]

        screen.fill(black) 
        screen.blit(ball, ballRect)
        py.display.flip()


if __name__ == "__main__": main()