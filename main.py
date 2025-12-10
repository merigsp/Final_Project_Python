
from src.bot_generation import generate_bot_ships
from src.gameplay import main as gameplay_main
from src import ship_input, bot_generation, gameplay
import os

def main():
    print('★=== Battleship (terminal) ===★')

    print('\n♖ Player ships input ♖')
    print("Place your ships:")
    print("1 ship with size 4")
    print("2 ships with size 3")
    print("3 ships with size 2")
    print("4 ships with size 1")
    print("Ships cannot be connected!")
    ship_input.input_ships()
    
    print('\n♖ Bot ships generation ♖')
    bot_generation.generate_bot_ships()
    
    print('\n☼ Game staredt ☼')
    gameplay.main()

if __name__ == '__main__':
    main()


