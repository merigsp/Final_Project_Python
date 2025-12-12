import csv
import random
from src.utils import coord_to_idx, idx_to_coord, neighbors, orthogonal_neighbors
from src.bot_generation import generate_bot_ships


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

# Loads ships into the player board and returns ship list.
def load_player_ships(player_board):
    ships = []
    try:
        with open("data/player_ships.csv") as f:
            reader = csv.reader(f)
            next(reader)
            for size, coords_str in reader:
                coords = []
                for c in coords_str.split(";"):
                    r, col = map(int, c.split(","))
                    coords.append((r, col))
                    player_board[r][col] = 'S'
                ships.append((int(size), coords))
    except FileNotFoundError:
        print("Player ships CSV not found! Exiting.")
        exit()
    return ships


def place_bot_ships(bot_board, ships):
    for size, coords in ships:
        for r, c in coords:
            bot_board[r][c] = 'S'
    return ships


def check_and_mark_destroyed(board, ship_list):
    for size, coords in ship_list:
        if all(board[r][c] == 'X' for r, c in coords):
            mark_destroyed(board, coords)
# main game loop
def main():

    # initialize all boards 
    player_board = [['~' for _ in range(10)] for _ in range(10)]
    bot_board = [['~' for _ in range(10)] for _ in range(10)]
    player_view = [['~' for _ in range(10)] for _ in range(10)]

    # init CSV
    with open("data/game_state.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["turn", "player_move", "player_result", "bot_move", "bot_result"])

    # load ships
    player_ship_list = load_player_ships(player_board)
    bot_ship_list = place_bot_ships(bot_board, generate_bot_ships())

    # bot logic
    bot_targets = [(r, c) for r in range(10) for c in range(10)]
    random.shuffle(bot_targets)
    bot_hit_stack = []

    turn = 1

    while True:

        print("Your board:")
        print_board(player_board)

        print("Enemy board:")
        print_board(player_view, show_ships=False)

        # my turn
        while True:
            move = input("Enter your shot (e.g. B5): ")
            try:
                r, c = coord_to_idx(move)
            except ValueError:
                print("Bad coordinate! Try again.")
                continue

            if player_view[r][c] in ('X', 'o'):
                print("Already shot here!")
                continue

            hit = check_hit(bot_board, r, c)
            player_view[r][c] = 'X' if hit else 'o'
            print("Hit!" if hit else "Miss!")
            break

        # mark destroyed ships for bot
        check_and_mark_destroyed(bot_board, bot_ship_list)

        # win check
        if all(cell != 'S' for row in bot_board for cell in row):
            print("You win!")
            break

        #his turn   
        if bot_hit_stack:
            r, c = bot_hit_stack.pop()
        else:
            r, c = bot_targets.pop()

        hit = check_hit(player_board, r, c)
        print(f"Bot shoots at {idx_to_coord(r,c)}: {'Hit' if hit else 'Miss'}")

        if hit:
            for nr, nc in orthogonal_neighbors(r, c):
                if player_board[nr][nc] == '~':
                    bot_hit_stack.append((nr, nc))

        # mark destroyed ships for player
        check_and_mark_destroyed(player_board, player_ship_list)

        # bot win check
        if all(cell != 'S' for row in player_board for cell in row):
            print("Bot wins!")
            break

        # save turn to CSV
        with open("data/game_state.csv", "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                turn,
                move,
                "Hit" if player_view[r][c] == 'X' else "Miss",
                idx_to_coord(r, c),
                "Hit" if hit else "Miss"
            ])

        turn += 1


if __name__ == "__main__":
    main()

