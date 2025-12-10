import csv
import random
from src.utils import coord_to_idx, idx_to_coord, neighbors, orthogonal_neighbors
from src.bot_generation import generate_bot_ships

# ~ — water, S — ship, X — hit, o — miss

# init the board
player_board = [['~' for _ in range(10)] for _ in range(10)]
bot_board = [['~' for _ in range(10)] for _ in range(10)]
player_view = [['~' for _ in range(10)] for _ in range(10)]  

# save CSV
with open("data/game_state.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["turn", "player_move", "player_result", "bot_move", "bot_result"])

def check_hit(board, r, c):
    if board[r][c] == 'S':
        board[r][c] = 'X'
        return True
    elif board[r][c] == '~':
        board[r][c] = 'o'
    return False

def mark_destroyed(board, ship_coords):
    for r, c in ship_coords:
        for nr, nc in neighbors(r, c):
            if board[nr][nc] == '~':
                board[nr][nc] = 'o'

def print_board(board, show_ships=True):
    print("  " + " ".join([str(i+1) for i in range(10)]))
    for r in range(10):
        row_str = ""
        for c in range(10):
            cell = board[r][c]
            if cell == 'S' and show_ships:
                cell = '■'
            elif cell == 'S' and not show_ships:
                cell = '~'
            row_str += cell + " "
        print(chr(65+r) + " " + row_str)
    print("\n")

def load_player_ships():
    global player_board
    try:
        with open("data/player_ships.csv") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for size, coords_str in reader:
                coords = coords_str.split(";")
                for c in coords:
                    r, col = map(int, c.split(","))
                    player_board[r][col] = 'S'
    except FileNotFoundError:
        print("Player ships CSV not found! Exiting.")
        exit()

# game loop
def main():
    turn = 1
    load_player_ships()         
    
    bot_ships = generate_bot_ships()  
    
    for size, coords in bot_ships:
        for r, c in coords:
            bot_board[r][c] = 'S'
    
    bot_targets = [(r,c) for r in range(10) for c in range(10)]
    random.shuffle(bot_targets)
    bot_hit_stack = []  

    while True:
        print("Your board:")
        print_board(player_board)
        print("Enemy board:")
        print_board(player_view, show_ships=False)

        # player's turn
        while True:
            move = input("Enter your shot (e.g. B5): ")
            try:
                r, c = coord_to_idx(move)
            except ValueError:
                print("Bad coordinate! Try again.")
                continue
            if player_view[r][c] in ('X','o'):
                print("Already shot here!")
                continue
            hit = check_hit(bot_board, r, c)
            player_view[r][c] = 'X' if hit else 'o'
            print("Hit!" if hit else "Miss!")
            break

        # win check 
        if all(cell != 'S' for row in bot_board for cell in row):
            print("You win!")
            break

        # bot's turn
        if bot_hit_stack:
            r, c = bot_hit_stack.pop()
        else:
            r, c = bot_targets.pop()
        hit = check_hit(player_board, r, c)
        print(f"Bot shoots at {idx_to_coord(r,c)}: {'Hit' if hit else 'Miss'}")
        if hit:
            # add neighbors blocks for next bot shots
            for nr, nc in orthogonal_neighbors(r,c):
                if player_board[nr][nc] == '~':
                    bot_hit_stack.append((nr,nc))

        # bot's win check
        if all(cell != 'S' for row in player_board for cell in row):
            print("Bot wins!")
            break

        # update CSV
        with open("data/game_state.csv","a",newline='') as f:
            writer = csv.writer(f)
            writer.writerow([turn, move, "Hit" if player_view[r][c]=='X' else "Miss",
                             idx_to_coord(r,c), "Hit" if hit else "Miss"])

        turn += 1

if __name__ == "__main__":
    main()

