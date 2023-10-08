import sys
import argparse
from game import Game


def parse_arguments():
    parser = argparse.ArgumentParser(description="Shut the box game solver")
    
    # Specify the player (one or two)
    parser.add_argument('--one', action='store_true', help='Solve for player one')
    parser.add_argument('--two', action='store_true', help='Solve for player two')
    
    # Specify whether to calculate expected wins or optimal move
    parser.add_argument('--expect', action='store_true', help='Calculate expected wins')
    parser.add_argument('--move', action='store_true', help='Calculate optimal move')
    
    # Specify the position (a string of unique, increasing digits in the range 1-9)
    parser.add_argument('position', type=str, help='Current position as a string of digits (e.g., "123456789")')
    
    # Optional argument for player 1's score
    parser.add_argument('prev_score', type=int, nargs='?', help='Player 1\'s score (only for Player 2)')
    
    # Optional argument for the sum of the roll (used for move calculation)
    parser.add_argument('roll_sum', type=int, nargs='?', help='Sum of the roll (only for move)')
    
    return parser.parse_args()

def main():
    args = parse_arguments()    
    
    # Create an instance of the game and run it.
    my_game = Game(args)
    my_game.run()
    
    

if __name__ == "__main__":        
    main()