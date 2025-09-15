import pygame
import random
import sys

# --- Costanti ---
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20
GRID_W = COLUMNS * BLOCK_SIZE  # 300
GRID_H = ROWS * BLOCK_SIZE     # 600
SIDE_PANEL_W = 140

WIDTH = GRID_W + SIDE_PANEL_W
HEIGHT = GRID_H

# Colori
BLACK  = (0, 0, 0)
GRAY   = (128, 128, 128)
DGRAY  = (60, 60, 60)
WHITE  = (255, 255, 255)
RED    = (200, 30, 30)
YELLOW = (240, 240, 0)
GHOST  = (80, 80, 80)

COLORS = [
    (0, 255, 255),   # I
    (0, 0, 255),     # J
    (255, 165, 0),   # L
    (255, 255, 0),   # O
    (0, 255, 0),     # S
    (128, 0, 128),   # T
    (255, 0, 0),     # Z
]

SHAPES = [
    [[1, 1, 1, 1]],                       # I
    [[1, 0, 0], [1, 1, 1]],               # J
    [[0, 0, 1], [1, 1, 1]],               # L
    [[1, 1], [1, 1]],                     # O
    [[0, 1, 1], [1, 1, 0]],               # S
    [[0, 1, 0], [1, 1, 1]],               # T
    [[1, 1, 0], [0, 1, 1]]                # Z
]

LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}

# --- Classe Tetromino ---
class Tetromino:
    def __init__(self, shape, color):
        self.shape = [row[:] for row in shape]
        self.color = color
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(r) for r in zip(*self.shape[::-1])]

    def positions(self):
        pos = []
        for i, row in enumerate(self.shape):
            for j, v in enumerate(row):
                if v:
                    pos.append((self.x + j, self.y + i))
        return pos

# --- Funzioni di griglia ---
def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    for i, row in enumerate(piece.shape):
        for j, val in enumerate(row):
            if val:
                positions.append((piece.x + j, piece.y + i))
    return positions

def valid_space(piece, grid):
    accepted = [[(x, y) for x in range(COLUMNS) if grid[y][x] == BLACK] for y in range(ROWS)]
    accepted = [x for row in accepted for x in row]
    formatted = convert_shape_format(piece)
    return all(pos in accepted and 0 <= pos[0] < COLUMNS and 0 <= pos[1] < ROWS for pos in formatted)

def clear_rows(grid, locked):
    cleared = 0
    for y in range(ROWS - 1, -1, -1):
        if BLACK not in grid[y]:
            cleared += 1
            for x in range(COLUMNS):
                locked.pop((x, y), None)
            for key in sorted(locked.keys(), key=lambda k: k[1])[::-1]:
                x, y1 = key
                if y1 < y:
                    locked[(x, y1 + 1)] = locked.pop((x, y1))
    return cleared

# --- Disegno griglia ---
def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    for x in range(COLUMNS):
        pygame.draw.line(surface, DGRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, GRID_H))
    for y in range(ROWS):
        pygame.draw.line(surface, DGRAY, (0, y * BLOCK_SIZE), (GRID_W, y * BLOCK_SIZE))

# --- Disegno pannello laterale ---
def draw_side_panel(surface, score, lines, level, next_piece):
    panel_x = GRID_W
    pygame.draw.rect(surface, (20, 20, 20), (panel_x, 0, SIDE_PANEL_W, HEIGHT))

    font = pygame.font.SysFont("Arial", 20, bold=True)
    small = pygame.font.SysFont("Arial", 16)

    score_lbl = font.render("Score", True, WHITE)
    val_lbl   = font.render(str(score), True, YELLOW)
    lines_lbl = font.render(f"Lines: {lines}", True, WHITE)
    level_lbl = font.render(f"Level: {level}", True, WHITE)

    surface.blit(score_lbl, (panel_x + 20, 20))
    surface.blit(val_lbl,   (panel_x + 20, 45))
    surface.blit(lines_lbl, (panel_x + 20, 80))
    surface.blit(level_lbl, (panel_x + 20, 110))

    nxt_lbl = font.render("Next:", True, WHITE)
    surface.blit(nxt_lbl, (panel_x + 20, 160))

    # preview
    for i, row in enumerate(next_piece.shape):
        for j, val in enumerate(row):
            if val:
                rect = pygame.Rect(panel_x + 40 + j*20, 190 + i*20, 20, 20)
                pygame.draw.rect(surface, next_piece.color, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)

    # comandi
    help_y = 300
    help_texts = ["← → Muovi", "↑ Ruota", "↓ Scendi", "SPACE Drop"]
    for i, t in enumerate(help_texts):
        surface.blit(small.render(t, True, GRAY), (panel_x + 10, help_y + i*22))

# --- Disegno finestra ---
def draw_window(surface, grid, score, lines, level, next_piece, game_over):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    draw_side_panel(surface, score, lines, level, next_piece)

    if game_over:
        font = pygame.font.SysFont("Arial", 36, bold=True)
        label = font.render("GAME OVER", True, RED)
        surface.blit(label, (GRID_W//2 - label.get_width()//2, HEIGHT//2 - 30))

# --- Main ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris con Pannello")
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    score = 0
    lines = 0
    level = 1

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
    next_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))

    running = True
    game_over = False

    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed and not game_over:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                for pos in convert_shape_format(current_piece):
                    locked_positions[pos] = current_piece.color
                current_piece = next_piece
                next_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
                cleared = clear_rows(grid, locked_positions)
                if cleared:
                    score += LINE_SCORES.get(cleared, 0) * level
                    lines += cleared
                    if lines % 10 == 0:
                        level += 1
                        fall_speed = max(0.1, fall_speed * 0.9)

                if not valid_space(current_piece, grid):
                    game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and not game_over:
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
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        for _ in range(3): current_piece.rotate()
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1

        if not game_over:
            for x, y in convert_shape_format(current_piece):
                if y >= 0:
                    grid[y][x] = current_piece.color

        draw_window(screen, grid, score, lines, level, next_piece, game_over)
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()