import pyxel
import random

GRID_SIZE = 10
CELL_SIZE = 8
BOMB_COUNT = 10

class Game:
    def __init__(self):
        pyxel.init(GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE + 20, title="Deceptive Minesweeper")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.revealed = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.flagged = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.game_over = False
        self.win = False
        self.started = False
        self.revealed_count = 0
        self.turns = 0
        self.generate_bombs()
        self.generate_trust_map()
        self.generate_fake_counts()

    def generate_bombs(self):
        self.bombs = set()
        while len(self.bombs) < BOMB_COUNT:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            self.bombs.add((x, y))

    def generate_trust_map(self):
        self.trust_map = [[random.uniform(0.2, 1.0) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def count_adjacent_bombs(self, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx = x + dx
                ny = y + dy
                if (dx != 0 or dy != 0) and 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if (nx, ny) in self.bombs:
                        count += 1
        return count

    def get_fake_count(self, true_count, trust, x, y):
        unopened_count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx = x + dx
                ny = y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and not self.revealed[ny][nx]:
                    unopened_count += 1

        if trust > 0.8:
            return true_count
        elif trust > 0.5:
            return max(0, true_count + random.choice([-1, 0, 1]))
        elif trust > 0.2:
            return max(0, true_count + random.choice([-2, -1, 0, 1, 2]))
        else:
            if true_count == 0:
                return None
            return random.randint(0, min(8, unopened_count))

    def generate_fake_counts(self):
        self.fake_counts = [[None] * GRID_SIZE for _ in range(GRID_SIZE)]
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if (x, y) in self.bombs:
                    self.fake_counts[y][x] = "X"
                else:
                    true_count = self.count_adjacent_bombs(x, y)
                    trust = self.trust_map[y][x]
                    self.fake_counts[y][x] = self.get_fake_count(true_count, trust, x, y)

    def move_bombs_near_player(self, px, py):
        move_count = random.randint(1, 2)
        new_bombs = set(self.bombs)
        candidates_from = list(self.bombs)
        nearby_cells = []

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx = px + dx
                ny = py + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if (nx, ny) not in self.bombs and not self.revealed[ny][nx] and (nx, ny) != (px, py):
                        nearby_cells.append((nx, ny))

        random.shuffle(nearby_cells)
        move_count = min(move_count, len(nearby_cells), len(candidates_from))

        for _ in range(move_count):
            from_bomb = random.choice(candidates_from)
            candidates_from.remove(from_bomb)
            to_cell = nearby_cells.pop()
            new_bombs.remove(from_bomb)
            new_bombs.add(to_cell)

        self.bombs = new_bombs

    def update_trust_map(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.revealed[y][x]:
                    change = random.uniform(-0.1, 0.1)
                    self.trust_map[y][x] = max(0.0, min(1.0, self.trust_map[y][x] + change))

    def update(self):
        if self.game_over or self.win:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()
            return

        if pyxel.btnp(pyxel.KEY_LEFT):
            self.cursor_x = max(0, self.cursor_x - 1)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.cursor_x = min(GRID_SIZE - 1, self.cursor_x + 1)
        if pyxel.btnp(pyxel.KEY_UP):
            self.cursor_y = max(0, self.cursor_y - 1)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.cursor_y = min(GRID_SIZE - 1, self.cursor_y + 1)

        # Enter でフラグ
        if pyxel.btnp(pyxel.KEY_RETURN):
            if not self.revealed[self.cursor_y][self.cursor_x]:
                self.flagged[self.cursor_y][self.cursor_x] = not self.flagged[self.cursor_y][self.cursor_x]

        # スペースで開ける（フラグがない場合）
        if pyxel.btnp(pyxel.KEY_SPACE):
            if not self.revealed[self.cursor_y][self.cursor_x] and not self.flagged[self.cursor_y][self.cursor_x]:
                self.revealed[self.cursor_y][self.cursor_x] = True
                self.started = True
                self.revealed_count += 1

                if (self.cursor_x, self.cursor_y) in self.bombs:
                    self.game_over = True
                    for y in range(GRID_SIZE):
                        for x in range(GRID_SIZE):
                            self.revealed[y][x] = True
                else:
                    self.move_bombs_near_player(self.cursor_x, self.cursor_y)
                    self.generate_fake_counts()

                self.update_trust_map()
                self.turns += 1

                total_cells = GRID_SIZE * GRID_SIZE
                if self.revealed_count == total_cells - BOMB_COUNT:
                    self.win = True
                    self.game_over = True
                    for y in range(GRID_SIZE):
                        for x in range(GRID_SIZE):
                            self.revealed[y][x] = True

    def draw(self):
        pyxel.cls(0)
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                screen_x = x * CELL_SIZE
                screen_y = y * CELL_SIZE
                trust = self.trust_map[y][x]

                if self.revealed[y][x]:
                    if trust > 0.8:
                        color = 7
                    elif trust > 0.5:
                        color = 6
                    elif trust > 0.2:
                        color = 2
                    else:
                        color = 8
                else:
                    color = 5

                pyxel.rect(screen_x, screen_y, CELL_SIZE - 1, CELL_SIZE - 1, color)

                if (x, y) == (self.cursor_x, self.cursor_y):
                    pyxel.rectb(screen_x, screen_y, CELL_SIZE - 1, CELL_SIZE - 1, 13)

                if self.revealed[y][x]:
                    val = self.fake_counts[y][x]
                    if val == "X":
                        pyxel.text(screen_x + 2, screen_y + 1, "X", 1)
                    elif val is not None and val != 0:
                        pyxel.text(screen_x + 2, screen_y + 1, str(val), 0)
                elif self.flagged[y][x]:
                    pyxel.text(screen_x + 2, screen_y + 1, "F", 8)

        pyxel.rect(0, GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE, 20, 1)
        if self.win:
            pyxel.text(2, GRID_SIZE * CELL_SIZE + 2, "YOU WIN! Press R to retry", 10)
        elif self.game_over:
            pyxel.text(2, GRID_SIZE * CELL_SIZE + 2, "GAME OVER! Press R to retry", 8)
        else:
            pyxel.text(2, GRID_SIZE * CELL_SIZE + 2, f"Revealed: {self.revealed_count} cells", 6)
            pyxel.text(2, GRID_SIZE * CELL_SIZE + 10, f"Turn: {self.turns}", 6)

        total_cells = GRID_SIZE * GRID_SIZE
        remaining_safe = total_cells - BOMB_COUNT - self.revealed_count
        pyxel.text(100, GRID_SIZE * CELL_SIZE + 2, f"Safe Left: {remaining_safe}", 11)

Game()

