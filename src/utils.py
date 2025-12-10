import string

letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']


def coord_to_idx(coord):
    coord = coord.strip().upper()

    if len(coord) < 2:
        # these are not emojis, these are symbols, don't kill me Mr. Nikolas
        raise ValueError('Wrong coord ☹') 
    
    letter = coord[0]
    num = coord[1:]
    
    if letter not in letters:
        raise ValueError('Wrong letter ☹')
    
    row = letters.index(letter)
    col = int(num) - 1
    if not (0 <= col < 10):
        raise ValueError('Wrong number ☹')
    return row, col

# (0,0) → "A1"
# (2,2) → "C3"
def idx_to_coord(row, col):
    return f"{letters[row]}{col+1}"

# check if our ships are too close
def neighbors(row, col):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr = row + dr
            cc = col + dc
            if 0 <= rr < 10 and 0 <= cc < 10:
                yield rr, cc

# this if for returnin neighbors only -- and |
# posle popadania
def orthogonal_neighbors(r, c):
    for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
        rr, cc = r+dr, c+dc
        if 0 <= rr < 10 and 0 <= cc < 10:
            yield rr, cc

