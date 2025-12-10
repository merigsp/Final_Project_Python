import csv
import random
from src.utils import neighbors

def generate_bot_ships():
    ship_sizes = [4,3,3,2,2,2,1,1,1,1]
    occupied = set()  # busy blocks
    all_ships = []
    
    for size in ship_sizes:
        while True:
            orientation = random.choice(['H','V'])  # for eack ship we randomly take Horiz or vert
            
            if orientation == 'H':
                r = random.randint(0, 9)
                c = random.randint(0, 10 - size)
                idx_coords = [(r, c + i) for i in range(size)]
            else:  # if V
                r = random.randint(0, 10 - size)
                c = random.randint(0, 9)
                idx_coords = [(r + i, c) for i in range(size)]

            # checking overlaps and touches
            conflict = False
            for r_cell, c_cell in idx_coords:
                if (r_cell, c_cell) in occupied:
                    conflict = True
                    break
                for nr, nc in neighbors(r_cell, c_cell):
                    if (nr, nc) in occupied:
                        conflict = True
                        break
            if conflict:
                continue  # try another position

            # save the ship
            for r_cell, c_cell in idx_coords:
                occupied.add((r_cell, c_cell))
            all_ships.append((size, idx_coords))
            break  # go to the next ship

    # savew in CSV
    with open("data/bot_ships.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["size", "coords"])
        for size, coords in all_ships:
            coords_str = ";".join([f"{r},{c}" for r, c in coords])
            writer.writerow([size, coords_str])

    print("Bot ships saved to data/bot_ships.csv")
    return all_ships

if __name__ == "__main__":
    generate_bot_ships()

