import csv
from src.utils import coord_to_idx, neighbors

player_board = [['~' for _ in range(10)] for _ in range(10)]

def print_board(board):
    print("  " + " ".join(str(i+1) for i in range(10)))
    for r in range(10):
        row = ""
        for c in range(10):
            cell = board[r][c]
            if cell == 'S':
                cell = '■'
            row += cell + " "
        print(chr(65+r) + " " + row)
    print()

def input_ships():
    ship_sizes = [4,3,3,2,2,2,1,1,1,1]
    occupied = set()
    all_ships = []
    
    print("\nCurrent board (empty):")
    print_board(player_board)

    for size in ship_sizes:
        while True:
            inp = input(f"Enter positions for ship of size {size} (e.g. A1 A2 ...): ")
            coords = inp.strip().split()

            if len(coords) != size:
                print("Wrong number of coordinates ☝")
                continue

            try:
                idx_coords = [coord_to_idx(c) for c in coords]
            except ValueError as e:
                print("Bad coordinate:", e)
                continue

            rows = [r for r,c in idx_coords]
            cols = [c for r,c in idx_coords]

            # straight check
            if len(set(rows)) != 1 and len(set(cols)) != 1:
                print("Ship must be straight")
                continue

            # consecutive check
            if len(set(rows)) == 1:
                if sorted(cols) != list(range(min(cols), max(cols)+1)):
                    print("Coordinates not consecutive")
                    continue
            else:
                if sorted(rows) != list(range(min(rows), max(rows)+1)):
                    print("Coordinates not consecutive")
                    continue

            # no touching / overlapping
            conflict = False
            for r,c in idx_coords:
                if (r,c) in occupied:
                    conflict = True
                    break
                for nr,nc in neighbors(r,c):
                    if (nr,nc) in occupied:
                        conflict = True
                        break

            if conflict:
                print("Ship overlaps or touches another ship")
                continue

            # add ship
            for r,c in idx_coords:
                occupied.add((r,c))
                player_board[r][c] = 'S'
            all_ships.append((size, idx_coords))

            print("\nUpdated board:")
            print_board(player_board)

            break

    # save CSV
    with open("data/player_ships.csv","w",newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["size","coords"])
        for size, coords in all_ships:
            coords_str = ";".join(f"{r},{c}" for r,c in coords)
            writer.writerow([size, coords_str])

    print("All ships saved to data/player_ships.csv")
    return all_ships

if __name__ == "__main__":
    input_ships()

