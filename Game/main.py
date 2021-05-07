from gem import PyLoop
import sys

if __name__ == "__main__":
    print("Game Start")
    game = PyLoop()
    game.frameLoop()
    print("Game End")
    sys.exit()
