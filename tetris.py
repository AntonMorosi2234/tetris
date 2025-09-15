import pygame
import random
import sys
import os
import time

# =========================
# Costanti e setup
# =========================
BLOCK_SIZE = 30
COLUMNS, ROWS = 10, 20
GRID_W, GRID_H = COLUMNS * BLOCK_SIZE, ROWS * BLOCK_SIZE
SIDE_PANEL_W = 240
WIDTH, HEIGHT = GRID_W + SIDE_PANEL_W, GRID_H

HIGHSCORE_FILE = "highscore.txt"

# Colori
BLACK  = (0, 0, 0)
DGRAY  = (40, 40, 40)
WHITE  = (255, 255, 255)
RED    = (200, 30, 30)
YELLOW = (240, 240, 0)
GHOSTC = (90, 90, 90)

# Colori pezzi (I,J,L,O,S,T,Z)
COLORS = {
    "I": (0, 255, 255),
    "J": (0, 0, 255),
    "L": (255, 165, 0),
    "O": (255, 255, 0),
    "S": (0, 255, 0),
    "T": (128, 0, 128),
    "Z": (255, 0, 0),
}

# Punteggi base per numero di righe
LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}

# =========================
# Rotazioni SRS (matrici)
# =========================
# Ogni pezzo ha 4 stati di rotazione (0,1,2,3). Per l'O sono identici.
PIECE_ROTATIONS = {
    "I": [
        [[1,1,1,1]],                         # 0
        [[1],[1],[1],[1]],                   # 1
        [[1,1,1,1]],                         # 2 (uguale a 0 ma gestito con rot_index)
        [[1],[1],[1],[1]],                   # 3 (uguale a 1)
    ],
    "O": [
        [[1,1],
         [1,1]],  # 0
        [[1,1],
         [1,1]],  # 1
        [[1,1],
         [1,1]],  # 2
        [[1,1],
         [1,1]],  # 3
    ],
    "J": [
        [[1,0,0],
         [1,1,1]],  # 0
        [[1,1],
         [1,0],
         [1,0]],    # 1
        [[1,1,1],
         [0,0,1]],  # 2
        [[0,1],
         [0,1],
         [1,1]],    # 3
    ],
    "L": [
        [[0,0,1],
         [1,1,1]],  # 0
        [[1,0],
         [1,0],
         [1,1]],    # 1
        [[1,1,1],
         [1,0,0]],  # 2
        [[1,1],
         [0,1],
         [0,1]],    # 3
    ],
    "S": [
        [[0,1,1],
         [1,1,0]],  # 0
        [[1,0],
         [1,1],
         [0,1]],    # 1
        [[0,1,1],
         [1,1,0]],  # 2
        [[1,0],
         [1,1],
         [0,1]],    # 3
    ],
    "T": [
        [[0,1,0],
         [1,1,1]],  # 0
        [[1,0],
         [1,1],
         [1,0]],    # 1
        [[1,1,1],
         [0,1,0]],  # 2
        [[0,1],
         [1,1],
         [0,1]],    # 3
    ],
    "Z": [
        [[1,1,0],
         [0,1,1]],  # 0
        [[0,1],
         [1,1],
         [1,0]],    # 1
        [[1,1,0],
         [0,1,1]],  # 2
        [[0,1],
         [1,1],
         [1,0]],    # 3
    ],
}

# =========================
# SRS wall kicks
# =========================
# Implementazione comune: set di offset DELTA tra stato A->B.
# Per JLSTZ:
KICKS_JLSTZ = {
    (0,1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],
    (1,0): [(0,0), (1,0),  (1,-1), (0,2),  (1,2)],
    (1,2): [(0,0), (1,0),  (1,-1), (0,2),  (1,2)],
    (2,1): [(0,0), (-1,0), (-1,1), (0,-2), (-1,-2)],
    (2,3): [(0,0), (1,0),  (1,1),  (0,-2), (1,-2)],
    (3,2): [(0,0), (-1,0), (-1,-1),(0,2),  (-1,2)],
    (3,0): [(0,0), (-1,0), (-1,-1),(0,2),  (-1,2)],
    (0,3): [(0,0), (1,0),  (1,1),  (0,-2), (1,-2)],
}

# Per I:
KICKS_I = {
    (0,1): [(0,0), (-2,0), (1,0),  (-2,-1), (1,2)],
    (1,0): [(0,0), (2,0),  (-1,0), (2,1),   (-1,-2)],
    (1,2): [(0,0), (-1,0), (2,0),  (-1,2),  (2,-1)],
    (2,1): [(0,0), (1,0),  (-2,0), (1,-2),  (-2,1)],
    (2,3): [(0,0), (2,0),  (-1,0), (2,1),   (-1,-2)],
    (3,2): [(0,0), (-2,0), (1,0),  (-2,-1), (1,2)],
    (3,0): [(0,0), (1,0),  (-2,0), (1,-2),  (-2,1)],
    (0,3): [(0,0), (-1,0), (2,0),  (-1,2),  (2,-1)],
}

def kick_table(piece_type, from_rot, to_rot):
    if piece_type == "I":
        return KICKS_I.get((from_rot, to_rot), [(0,0)])
    elif piece_type == "O":
        return [(0,0)]  # O non ha kick significativi
    else:
        return KICKS_JLSTZ.get((from_rot, to_rot), [(0,0)])

# =========================
# Classi pezzi e randomizer
# =========================
class Tetromino:
    def __init__(self, ptype: str):
        self.type = ptype              # "I","J","L","O","S","T","Z"
        self.rot = 0                   # indice rotazione (0..3)
        self.color = COLORS[ptype]
        shape = PIECE_ROTATIONS[self.type][self.rot]
        self.w = len(shape[0])
        # spawn centrato
        self.x = COLUMNS // 2 - self.w // 2
        self.y = 0

    @property
    def shape(self):
        return PIECE_ROTATIONS[self.type][self.rot]

    def cells(self):
        """Coordinate occupate dal pezzo nello stato attuale."""
        out = []
        for i, row in enumerate(self.shape):
            for j, v in enumerate(row):
                if v:
                    out.append((self.x + j, self.y + i))
        return out

    def try_rotate(self, dir_sign, grid):
        """
        dir_sign = +1 (CW) o -1 (CCW).
        Applica SRS con wall-kick; ritorna True se ruota con successo.
        """
        old_rot = self.rot
        new_rot = (self.rot + (1 if dir_sign > 0 else -1)) % 4

        # prova rotazione senza kick
        def can_place_at(nx, ny, rot):
            shape = PIECE_ROTATIONS[self.type][rot]
            for i, row in enumerate(shape):
                for j, v in enumerate(row):
                    if not v:
                        continue
                    x, y = nx + j, ny + i
                    if x < 0 or x >= COLUMNS or y >= ROWS:
                        return False
                    if y >= 0 and grid[y][x] != BLACK:
                        return False
            return True

        # kick list per SRS
        kicks = kick_table(self.type, old_rot, new_rot)
        for dx, dy in kicks:
            nx = self.x + dx
            ny = self.y + dy
            if can_place_at(nx, ny, new_rot):
                # applica
                self.rot = new_rot
                self.x, self.y = nx, ny
                return True
        return False

class BagRandomizer:
    def __init__(self):
        self.bag = []
        self.refill()

    def refill(self):
        pieces = ["I","J","L","O","S","T","Z"]
        random.shuffle(pieces)
        self.bag.extend(pieces)

    def get_piece(self):
        if not self.bag:
            self.refill()
        return Tetromino(self.bag.pop(0))

# =========================
# Utility griglia e punteggio
# =========================
def create_grid(locked_positions):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS and 0 <= x < COLUMNS:
            grid[y][x] = color
    return grid

def valid_space(piece: Tetromino, grid):
    for x, y in piece.cells():
        if x < 0 or x >= COLUMNS or y >= ROWS:
            return False
        if y >= 0 and grid[y][x] != BLACK:
            return False
    return True

def convert_shape_format(piece: Tetromino):
    return piece.cells()

def clear_rows(grid, locked):
    to_clear = [y for y in range(ROWS) if BLACK not in grid[y]]
    return to_clear

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except:
        pass

# =========================
# Disegno
# =========================
def draw_block(surface, x, y, color, ghost=False):
    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    if ghost:
        pygame.draw.rect(surface, GHOSTC, rect)
    else:
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            if grid[y][x] != BLACK:
                draw_block(surface, x, y, grid[y][x])
    # griglia
    for x in range(COLUMNS + 1):
        pygame.draw.line(surface, DGRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, GRID_H))
    for y in range(ROWS + 1):
        pygame.draw.line(surface, DGRAY, (0, y * BLOCK_SIZE), (GRID_W, y * BLOCK_SIZE))

def draw_mini_piece(surface, piece: Tetromino, x, y, scale=20):
    shp = piece.shape
    for i, row in enumerate(shp):
        for j, v in enumerate(row):
            if v:
                rect = pygame.Rect(x + j * scale, y + i * scale, scale, scale)
                pygame.draw.rect(surface, piece.color, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)

def draw_side_panel(surface, score, highscore, lines, level, next_piece, hold_piece, music_on, mode, time_left):
    panel_x = GRID_W
    pygame.draw.rect(surface, (25, 25, 25), (panel_x, 0, SIDE_PANEL_W, HEIGHT))

    font = pygame.font.SysFont("Arial", 20, bold=True)
    value = pygame.font.SysFont("Arial", 18)

    surface.blit(font.render("Mode", True, WHITE), (panel_x + 20, 16))
    surface.blit(value.render(mode, True, YELLOW), (panel_x + 20, 40))

    surface.blit(font.render("Score", True, WHITE), (panel_x + 20, 70))
    surface.blit(value.render(str(score), True, YELLOW), (panel_x + 20, 94))

    surface.blit(font.render("High Score", True, WHITE), (panel_x + 20, 124))
    surface.blit(value.render(str(highscore), True, YELLOW), (panel_x + 20, 148))

    surface.blit(font.render("Lines", True, WHITE), (panel_x + 20, 178))
    surface.blit(value.render(str(lines), True, YELLOW), (panel_x + 20, 202))

    surface.blit(font.render("Level", True, WHITE), (panel_x + 20, 232))
    surface.blit(value.render(str(level), True, YELLOW), (panel_x + 20, 256))

    if mode == "Time Attack":
        surface.blit(font.render("Time Left", True, WHITE), (panel_x + 20, 286))
        surface.blit(value.render(f"{time_left}s", True, YELLOW), (panel_x + 20, 310))

    surface.blit(font.render("Next:", True, WHITE), (panel_x + 20, 344))
    draw_mini_piece(surface, next_piece, panel_x + 40, 372)

    surface.blit(font.render("Hold:", True, WHITE), (panel_x + 130, 344))
    if hold_piece:
        draw_mini_piece(surface, hold_piece, panel_x + 130, 372)

    status = "ON" if music_on else "OFF"
    surface.blit(font.render(f"Music: {status}", True, WHITE), (panel_x + 20, 540))

def draw_window(surface, grid, score, highscore, lines, level, next_piece, hold_piece, ghost_pos, game_over, flash_rows, music_on, mode, time_left):
    surface.fill((10, 10, 30))
    # ghost
    for x, y in ghost_pos:
        if y >= 0:
            draw_block(surface, x, y, GHOSTC, ghost=True)

    # griglia con eventuale flash bianco sulle righe da cancellare
    for y in range(ROWS):
        for x in range(COLUMNS):
            if grid[y][x] != BLACK:
                color = WHITE if y in flash_rows else grid[y][x]
                draw_block(surface, x, y, color)

    draw_grid(surface, grid)
    draw_side_panel(surface, score, highscore, lines, level, next_piece, hold_piece, music_on, mode, time_left)

    if game_over:
        font = pygame.font.SysFont("Arial", 48, bold=True)
        label = font.render("GAME OVER", True, RED)
        surface.blit(label, (GRID_W//2 - label.get_width()//2, HEIGHT//2 - 30))

# =========================
# Menu
# =========================
def game_menu(screen):
    font = pygame.font.SysFont("Arial", 40, bold=True)
    small = pygame.font.SysFont("Arial", 28)

    while True:
        screen.fill((0, 0, 30))
        title = font.render("TETRIS", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        opt1 = small.render("1 - Marathon", True, WHITE)
        opt2 = small.render("2 - Time Attack (3 min)", True, WHITE)
        hint = small.render("Tasti: ← → ↓ Ruota:↑  Drop:SPACE  Hold:C  Musica:M", True, (180,180,180))

        screen.blit(opt1, (WIDTH//2 - opt1.get_width()//2, 280))
        screen.blit(opt2, (WIDTH//2 - opt2.get_width()//2, 320))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 380))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: return "Marathon"
                if event.key == pygame.K_2: return "Time Attack"

# =========================
# Main Loop
# =========================
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris — SRS + Wall-Kick")
    clock = pygame.time.Clock()

    # (opzionale) carica musica:
    music_on = False
    # try:
    #     pygame.mixer.music.load("music/tetris_theme.ogg")
    #     pygame.mixer.music.play(-1)
    #     music_on = True
    # except:
    #     music_on = False

    mode = game_menu(screen)

    fall_time = 0
    fall_speed = 0.5
    score = 0
    lines = 0
    level = 1
    highscore = load_highscore()

    # Time Attack
    if mode == "Time Attack":
        total_time = 180
        start_time = time.time()

    locked_positions = {}
    grid = create_grid(locked_positions)

    bag = BagRandomizer()
    current_piece = bag.get_piece()
    next_piece = bag.get_piece()
    hold_piece = None
    can_hold = True

    game_over = False
    flash_timer = 0
    flash_rows = []

    running = True
    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        dt = clock.tick()

        # Timer per Time Attack
        time_left = 0
        if mode == "Time Attack" and not game_over:
            elapsed = int(time.time() - start_time)
            time_left = max(0, total_time - elapsed)
            if time_left == 0:
                game_over = True

        # Caduta automatica
        if not game_over and flash_timer == 0:
            if fall_time / 1000 >= fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not valid_space(current_piece, grid):
                    current_piece.y -= 1
                    # blocca il pezzo
                    for pos in convert_shape_format(current_piece):
                        locked_positions[pos] = current_piece.color
                    # check righe
                    flash_rows = clear_rows(grid, locked_positions)
                    if flash_rows:
                        flash_timer = 350
                    else:
                        # nuovo pezzo
                        current_piece = next_piece
                        next_piece = bag.get_piece()
                        can_hold = True
                        if not valid_space(current_piece, grid):
                            game_over = True

        # Eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # musica
                if event.key == pygame.K_m:
                    if music_on:
                        pygame.mixer.music.pause(); music_on = False
                    else:
                        pygame.mixer.music.unpause(); music_on = True

                if game_over or flash_timer > 0:
                    continue

                # movimento
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                # rotazione SRS
                elif event.key == pygame.K_UP:
                    current_piece.try_rotate(+1, grid)  # CW
                # hard drop
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                # hold
                elif event.key == pygame.K_c and can_hold:
                    if hold_piece is None:
                        hold_piece = current_piece
                        current_piece = next_piece
                        next_piece = bag.get_piece()
                    else:
                        hold_piece, current_piece = current_piece, hold_piece
                    # reset posizione del pezzo preso dallo hold
                    shape = current_piece.shape
                    spawn_w = len(shape[0])
                    current_piece.x = COLUMNS // 2 - spawn_w // 2
                    current_piece.y = 0
                    current_piece.rot = current_piece.rot % 4
                    can_hold = False

        # Ghost piece
        ghost = Tetromino(current_piece.type)
        ghost.rot = current_piece.rot
        ghost.x, ghost.y = current_piece.x, current_piece.y
        while valid_space(ghost, grid):
            ghost.y += 1
        ghost.y -= 1
        ghost_pos = ghost.cells()

        # Disegna il pezzo corrente
        if not game_over and flash_timer == 0:
            for x, y in current_piece.cells():
                if y >= 0:
                    grid[y][x] = current_piece.color

        # Lampeggio e clear righe
        if flash_timer > 0:
            flash_timer -= dt
            if flash_timer <= 0:
                # rimuovi righe
                for y in flash_rows:
                    for x in range(COLUMNS):
                        locked_positions.pop((x, y), None)
                # fai cadere i blocchi
                for y in sorted(flash_rows):
                    for (lx, ly) in sorted(list(locked_positions), key=lambda k: k[1])[::-1]:
                        if ly < y:
                            locked_positions[(lx, ly + 1)] = locked_positions.pop((lx, ly))

                # punteggio
                cleared = len(flash_rows)
                score += LINE_SCORES.get(cleared, 0) * level
                lines += cleared
                if score > highscore:
                    highscore = score
                if lines % 10 == 0:
                    level += 1
                    fall_speed = max(0.08, fall_speed * 0.9)

                flash_rows = []
                current_piece = next_piece
                next_piece = bag.get_piece()
                can_hold = True
                if not valid_space(current_piece, grid):
                    game_over = True

        # Disegna frame
        draw_window(
            screen, grid, score, highscore, lines, level,
            next_piece, hold_piece, ghost_pos, game_over, flash_rows,
            music_on, mode, (time_left if mode == "Time Attack" else 0)
        )
        pygame.display.update()

    # salva highscore
    if score > highscore:
        save_highscore(score)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()