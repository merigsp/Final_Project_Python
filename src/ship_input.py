# Allows the user to manually enter ship positions.
# Input format: For each ship, enter a list of coordinates separated by spaces or commas.
# For example, for size 3: A1 A2 A3
# You can also enter `random` to generate a random placement.

import csv
from src.utils import coord_to_idx, idx_to_coord, neighbors

def input_ships():
    ship_sizes = [4,3,3,2,2,2,1,1,1,1]
    occupied = set()   # busy blocks
    all_ships = []     # list of all ships (format [(size, [coords])])
    
    for size in ship_sizes:
        while True:
            inp = input(f"Enter positions for ship of size {size} (e.g. A1 A2 ...): ")
            coords = inp.strip().split()  # split by spaces 

            # check the size
            if len(coords) != size:
                print("Wrong number of coordinates ☝")
                continue

            # convert coord to idx
            try:
                idx_coords = [coord_to_idx(c) for c in coords]
            except ValueError as e:
                print("Bad coordinate:", e)
                continue

            # checking if the ship is straight
            rows = [r for r, c in idx_coords]
            cols = [c for r, c in idx_coords]

            if len(set(rows)) != 1 and len(set(cols)) != 1:
                print("Ship must be straight")
                continue

            # check consecutive positions
            if len(set(rows)) == 1:  # horizontal
                if sorted(cols) != list(range(min(cols), max(cols)+1)):
                    print("Coordinates not consecutive")
                    continue
            else:  # vertical
                if sorted(rows) != list(range(min(rows), max(rows)+1)):
                    print("Coordinates not consecutive")
                    continue

            # checking overlaps and touches
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

            # save the valid ship
            for r,c in idx_coords:
                occupied.add((r,c))
            all_ships.append((size, idx_coords))
            break

    # save in CSV
    with open("data/player_ships.csv","w",newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["size","coords"])
        for size, coords in all_ships:
            coords_str = ";".join([f"{r},{c}" for r,c in coords])
            writer.writerow([size, coords_str])

    print("All ships saved to data/player_ships.csv")

    player_board = [['~' for _ in range(10)] for _ in range(10)]
    for size, coords in all_ships:
        for r, c in coords:
            player_board[r][c] = 'S'  # ставим корабль
    return all_ships, player_board  # возвращаем доску сразу
            

if __name__ == "__main__":
    input_ships()

