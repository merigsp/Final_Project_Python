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

def mark_destroyed_on_bot_board(bot_board, player_view, ship_coords):
    for r, c in ship_coords:
        for nr, nc in neighbors(r, c):
            if 0 <= nr < 10 and 0 <= nc < 10:
                if bot_board[nr][nc] == '~':
                    bot_board[nr][nc] = 'o'
                    player_view[nr][nc] = 'o'

def check_and_mark_destroyed_bot(bot_board, player_view, bot_ship_list):
    for size, coords in bot_ship_list:
        if all(bot_board[r][c] == 'X' for r, c in coords):
            mark_destroyed_on_bot_board(bot_board, player_view, coords)

def mark_destroyed_on_player_board(player_board, ship_coords):
    for r, c in ship_coords:
        for nr, nc in neighbors(r, c):
            if 0 <= nr < 10 and 0 <= nc < 10:
                if player_board[nr][nc] == '~':
                    player_board[nr][nc] = 'o'

def check_and_mark_destroyed_player(player_board, player_ship_list):
    for size, coords in player_ship_list:
        if all(player_board[r][c] == 'X' for r, c in coords):
            mark_destroyed_on_player_board(player_board, coords)

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

def load_player_ships(player_board):
    ships = []
    try:
        with open("data/player_ships.csv") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
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

def get_valid_neighbors(r, c, board):
    neighbors_list = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 10 and 0 <= nc < 10:
            if board[nr][nc] in ('~', 'S'):
                neighbors_list.append((nr, nc))
    return neighbors_list

def main():
    # Initialize all boards 
    player_board = [['~' for _ in range(10)] for _ in range(10)]
    bot_board = [['~' for _ in range(10)] for _ in range(10)]
    player_view = [['~' for _ in range(10)] for _ in range(10)]

    # Initialize CSV
    with open("data/game_state.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["turn", "player_move", "player_result", "bot_move", "bot_result"])

    # Load ships
    player_ship_list = load_player_ships(player_board)
    bot_ship_list = place_bot_ships(bot_board, generate_bot_ships())

    # Bot logic
    bot_targets = [(r, c) for r in range(10) for c in range(10)]
    random.shuffle(bot_targets)
    
    bot_hit_stack = []  # Stack for smart shooting
    bot_last_hit = None  # Bot's last successful hit
    bot_direction = None  # Direction to continue shooting

    turn = 1

    while True:
        print("Your board:")
        print_board(player_board)

        print("Enemy board:")
        print_board(player_view, show_ships=False)

        # Player's turn
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
            
            # Check if player destroyed a ship and mark around it
            if hit:
                check_and_mark_destroyed_bot(bot_board, player_view, bot_ship_list)
            break

        # Win check for player
        if all(cell != 'S' for row in bot_board for cell in row):
            print("You win!")
            break

        # Bot's turn
        hit = False
        target = None
        
        if bot_last_hit:
            # Bot has an unfinished target (hit but not sunk)
            if bot_direction:
                # Continue shooting in the same direction
                r, c = bot_last_hit
                dr, dc = bot_direction
                nr, nc = r + dr, c + dc
                
                # Check boundaries and if not shot here before
                if 0 <= nr < 10 and 0 <= nc < 10 and player_board[nr][nc] in ('~', 'S'):
                    target = (nr, nc)
                else:
                    # Change direction or find new targets
                    bot_direction = None
                    # Get all valid neighbors of the last hit
                    valid_neighbors = get_valid_neighbors(bot_last_hit[0], bot_last_hit[1], player_board)
                    if valid_neighbors:
                        target = valid_neighbors[0]
                    else:
                        while bot_targets:
                            t = bot_targets.pop()
                            tr, tc = t
                            if player_board[tr][tc] in ('~', 'S'):
                                target = t
                                break
            else:
                # Find direction for shooting
                valid_neighbors = get_valid_neighbors(bot_last_hit[0], bot_last_hit[1], player_board)
                if valid_neighbors:
                    target = valid_neighbors[0]
                    # Remember direction for next shot
                    dr = target[0] - bot_last_hit[0]
                    dc = target[1] - bot_last_hit[1]
                    bot_direction = (dr, dc)
                else:
                    while bot_targets:
                        t = bot_targets.pop()
                        tr, tc = t
                        if player_board[tr][tc] in ('~', 'S'):
                            target = t
                            break
        else:
            # Random shooting
            while bot_targets:
                t = bot_targets.pop()
                tr, tc = t
                if player_board[tr][tc] in ('~', 'S'):
                    target = t
                    break
        
        if target is None:
            # No more targets, game should have ended
            break
            
        r, c = target
        hit = check_hit(player_board, r, c)
        print(f"Bot shoots at {idx_to_coord(r,c)}: {'Hit' if hit else 'Miss'}")
        
        if hit:
            bot_last_hit = (r, c)
            # Check if bot destroyed a ship and mark around it
            check_and_mark_destroyed_player(player_board, player_ship_list)
            
            # Check if this ship still has undamaged cells
            # If ship is destroyed, reset bot state
            ship_destroyed = False
            for size, coords in player_ship_list:
                if (r, c) in coords:
                    if all(player_board[x][y] == 'X' for x, y in coords):
                        ship_destroyed = True
                    break
            
            if ship_destroyed:
                bot_last_hit = None
                bot_direction = None
                bot_hit_stack = []
        else:
            if bot_direction:
                # Change to opposite direction
                bot_direction = (-bot_direction[0], -bot_direction[1])
                # Move 2 cells from original to skip already hit cell
                br, bc = bot_last_hit
                dr, dc = bot_direction
                nr, nc = br + dr * 2, bc + dc * 2
                if 0 <= nr < 10 and 0 <= nc < 10 and player_board[nr][nc] in ('~', 'S'):
                    bot_targets.append((nr, nc))

        # Bot win check
        if all(cell != 'S' for row in player_board for cell in row):
            print("Bot wins!")
            break

        # Save turn to CSV
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
