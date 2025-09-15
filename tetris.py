import pygame
import random
import sys
import os
import time

# --- Costanti ---
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20
GRID_W = COLUMNS * BLOCK_SIZE
GRID_H = ROWS * BLOCK_SIZE
SIDE_PANEL_W = 220

WIDTH = GRID_W + SIDE_PANEL_W
HEIGHT = GRID_H

# File high score
HIGHSCORE_FILE = "highscore.txt"

# Colori
BLACK  = (0, 0, 0)
DGRAY  = (40, 40, 40)
WHITE  = (255, 255, 255)
RED    = (200, 30, 30)
YELLOW = (240, 240, 0)
GHOST  = (90, 90, 90)

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
    [[1, 1, 1, 1]],                       
    [[1, 0, 0], [1, 1, 1]],               
    [[0, 0, 1], [1, 1, 1]],               
    [[1, 1], [1, 1]],                     
    [[0, 1, 1], [1, 1, 0]],               
    [[0, 1, 0], [1, 1, 1]],               
    [[1, 1, 0], [0, 1, 1]]                
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

# --- Funzioni griglia ---
def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if 0 <= y < ROWS:
            grid[y][x] = color
    return grid

def convert_shape_format(piece):
    return [(piece.x + j, piece.y + i) for i, row in enumerate(piece.shape) for j, v in enumerate(row) if v]

def valid_space(piece, grid):
    accepted = {(x, y) for y in range(ROWS) for x in range(COLUMNS) if grid[y][x] == BLACK}
    return all((x, y) in accepted and 0 <= x < COLUMNS and 0 <= y < ROWS for x, y in convert_shape_format(piece))

def clear_rows(grid, locked):
    cleared_rows = []
    for y in range(ROWS):
        if BLACK not in grid[y]:
            cleared_rows.append(y)
    return cleared_rows

# --- High score ---
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

# --- Grafica ---
def draw_block(surface, x, y, color, ghost=False):
    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    if ghost:
        pygame.draw.rect(surface, GHOST, rect)
    else:
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            if grid[y][x] != BLACK:
                draw_block(surface, x, y, grid[y][x])
    for x in range(COLUMNS + 1):
        pygame.draw.line(surface, DGRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, GRID_H))
    for y in range(ROWS + 1):
        pygame.draw.line(surface, DGRAY, (0, y * BLOCK_SIZE), (GRID_W, y * BLOCK_SIZE))

def draw_mini_piece(surface, piece, x, y):
    for i, row in enumerate(piece.shape):
        for j, v in enumerate(row):
            if v:
                rect = pygame.Rect(x + j * 20, y + i * 20, 20, 20)
                pygame.draw.rect(surface, piece.color, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)

def draw_side_panel(surface, score, highscore, lines, level, next_piece, hold_piece, music_on, mode, time_left):
    panel_x = GRID_W
    pygame.draw.rect(surface, (25, 25, 25), (panel_x, 0, SIDE_PANEL_W, HEIGHT))

    font = pygame.font.SysFont("Arial", 20, bold=True)
    value = pygame.font.SysFont("Arial", 18)

    surface.blit(font.render("Mode", True, WHITE), (panel_x + 20, 20))
    surface.blit(value.render(mode, True, YELLOW), (panel_x + 20, 45))

    surface.blit(font.render("Score", True, WHITE), (panel_x + 20, 80))
    surface.blit(value.render(str(score), True, YELLOW), (panel_x + 20, 105))

    surface.blit(font.render("High Score", True, WHITE), (panel_x + 20, 140))
    surface.blit(value.render(str(highscore), True, YELLOW), (panel_x + 20, 165))

    surface.blit(font.render("Lines", True, WHITE), (panel_x + 20, 200))
    surface.blit(value.render(str(lines), True, YELLOW), (panel_x + 20, 225))

    surface.blit(font.render("Level", True, WHITE), (panel_x + 20, 260))
    surface.blit(value.render(str(level), True, YELLOW), (panel_x + 20, 285))

    if mode == "Time Attack":
        surface.blit(font.render("Time Left", True, WHITE), (panel_x + 20, 320))
        surface.blit(value.render(f"{time_left}s", True, YELLOW), (panel_x + 20, 345))

    surface.blit(font.render("Next:", True, WHITE), (panel_x + 20, 380))
    draw_mini_piece(surface, next_piece, panel_x + 40, 410)

    surface.blit(font.render("Hold:", True, WHITE), (panel_x + 20, 480))
    if hold_piece:
        draw_mini_piece(surface, hold_piece, panel_x + 40, 510)

    status = "ON" if music_on else "OFF"
    surface.blit(font.render(f"Music: {status}", True, WHITE), (panel_x + 20, 580))

def draw_window(surface, grid, score, highscore, lines, level, next_piece, hold_piece, ghost_pos, game_over, flash_rows, music_on, mode, time_left):
    surface.fill((10, 10, 30))
    for x, y in ghost_pos:
        if y >= 0:
            draw_block(surface, x, y, GHOST, ghost=True)
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

# --- Menu iniziale ---
def game_menu(screen):
    font = pygame.font.SysFont("Arial", 40, bold=True)
    small = pygame.font.SysFont("Arial", 28)

    while True:
        screen.fill((0, 0, 30))
        title = font.render("TETRIS", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

        opt1 = small.render("1 - Marathon", True, WHITE)
        opt2 = small.render("2 - Time Attack", True, WHITE)
        screen.blit(opt1, (WIDTH//2 - opt1.get_width()//2, 280))
        screen.blit(opt2, (WIDTH//2 - opt2.get_width()//2, 320))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "Marathon"
                elif event.key == pygame.K_2:
                    return "Time Attack"

# --- Main ---
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris con Modalità")
    clock = pygame.time.Clock()

    mode = game_menu(screen)
    music_on = False

    fall_time = 0
    fall_speed = 0.5
    score = 0
    lines = 0
    level = 1

    highscore = load_highscore()

    if mode == "Time Attack":
        total_time = 180  # 3 minuti
        start_time = time.time()

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
    next_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
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

        # Calcola tempo rimasto
        time_left = 0
        if mode == "Time Attack" and not game_over:
            elapsed = int(time.time() - start_time)
            time_left = max(0, total_time - elapsed)
            if time_left == 0:
                game_over = True

        if not game_over and flash_timer == 0:
            if fall_time / 1000 >= fall_speed:
                fall_time = 0
                current_piece.y += 1
                if not valid_space(current_piece, grid):
                    current_piece.y -= 1
                    for pos in convert_shape_format(current_piece):
                        locked_positions[pos] = current_piece.color
                    flash_rows = clear_rows(grid, locked_positions)
                    if flash_rows:
                        flash_timer = 400
                    else:
                        current_piece = next_piece
                        next_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
                        can_hold = True
                        if not valid_space(current_piece, grid):
                            game_over = True

        # Eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if not game_over:
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
                        while valid_space(current_piece, grid):
                            current_piece.y += 1
                        current_piece.y -= 1
                    elif event.key == pygame.K_c and can_hold:
                        if hold_piece is None:
                            hold_piece = current_piece
                            current_piece = next_piece
                            next_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
                        else:
                            hold_piece, current_piece = current_piece, hold_piece
                        current_piece.x = COLUMNS // 2 - len(current_piece.shape[0]) // 2
                        current_piece.y = 0
                        can_hold = False
                if event.key == pygame.K_m:
                    if music_on:
                        pygame.mixer.music.pause()
                        music_on = False
                    else:
                        pygame.mixer.music.unpause()
                        music_on = True

        # ghost piece
        ghost = Tetromino(current_piece.shape, current_piece.color)
        ghost.x, ghost.y = current_piece.x, current_piece.y
        while valid_space(ghost, grid):
            ghost.y += 1
        ghost.y -= 1
        ghost_pos = convert_shape_format(ghost)

        if not game_over and flash_timer == 0:
            for x, y in convert_shape_format(current_piece):
                if y >= 0:
                    grid[y][x] = current_piece.color

        if flash_timer > 0:
            flash_timer -= dt
            if flash_timer <= 0:
                for y in flash_rows:
                    for x in range(COLUMNS):
                        locked_positions.pop((x, y), None)
                for y in sorted(flash_rows):
                    for (lx, ly) in sorted(list(locked_positions), key=lambda k: k[1])[::-1]:
                        if ly < y:
                            locked_positions[(lx, ly + 1)] = locked_positions.pop((lx, ly))
                score += LINE_SCORES.get(len(flash_rows), 0) * level
                lines += len(flash_rows)
                if score > highscore:
                    highscore = score
                if lines % 10 == 0:
                    level += 1
                    fall_speed = max(0.1, fall_speed * 0.9)
                flash_rows = []
                current_piece = next_piece
                next_piece = Tetromino(random.choice(SHAPES), random.choice(COLORS))
                can_hold = True
                if not valid_space(current_piece, grid):
                    game_over = True

        draw_window(screen, grid, score, highscore, lines, level, next_piece, hold_piece, ghost_pos, game_over, flash_rows, music_on, mode, time_left)
        pygame.display.update()

    if score > highscore:
        save_highscore(score)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()