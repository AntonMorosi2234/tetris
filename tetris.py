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

# Colori pezzi
COLORS = {
    "I": (0, 255, 255),
    "J": (0, 0, 255),
    "L": (255, 165, 0),
    "O": (255, 255, 0),
    "S": (0, 255, 0),
    "T": (128, 0, 128),
    "Z": (255, 0, 0),
}

# Punteggi righe
LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}

# =========================
# Rotazioni SRS (matrici)
# =========================
PIECE_ROTATIONS = {
    "I": [
        [[1,1,1,1]],
        [[1],[1],[1],[1]],
        [[1,1,1,1]],
        [[1],[1],[1],[1]],
    ],
    "O": [[[1,1],[1,1]]]*4,
    "J": [
        [[1,0,0],[1,1,1]],
        [[1,1],[1,0],[1,0]],
        [[1,1,1],[0,0,1]],
        [[0,1],[0,1],[1,1]],
    ],
    "L": [
        [[0,0,1],[1,1,1]],
        [[1,0],[1,0],[1,1]],
        [[1,1,1],[1,0,0]],
        [[1,1],[0,1],[0,1]],
    ],
    "S": [
        [[0,1,1],[1,1,0]],
        [[1,0],[1,1],[0,1]],
        [[0,1,1],[1,1,0]],
        [[1,0],[1,1],[0,1]],
    ],
    "T": [
        [[0,1,0],[1,1,1]],
        [[1,0],[1,1],[1,0]],
        [[1,1,1],[0,1,0]],
        [[0,1],[1,1],[0,1]],
    ],
    "Z": [
        [[1,1,0],[0,1,1]],
        [[0,1],[1,1],[1,0]],
        [[1,1,0],[0,1,1]],
        [[0,1],[1,1],[1,0]],
    ],
}

# =========================
# Wall-kicks SRS
# =========================
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

def kick_table(ptype, fr, to):
    if ptype == "I": return KICKS_I.get((fr,to), [(0,0)])
    if ptype == "O": return [(0,0)]
    return KICKS_JLSTZ.get((fr,to), [(0,0)])

# =========================
# Classi
# =========================
class Tetromino:
    def __init__(self, t):
        self.type = t
        self.rot = 0
        self.color = COLORS[t]
        # spawn centrato rispetto alla larghezza della forma nello stato 0
        spawn_w = len(PIECE_ROTATIONS[t][0][0])
        self.x = COLUMNS // 2 - spawn_w // 2
        self.y = 0

    @property
    def shape(self):
        return PIECE_ROTATIONS[self.type][self.rot]

    def cells(self):
        return [(self.x+j, self.y+i)
                for i,row in enumerate(self.shape)
                for j,v in enumerate(row) if v]

    def try_rotate(self, dir_sign, grid):
        """Rotazione SRS con wall-kick. dir_sign: +1=CW, -1=CCW."""
        fr = self.rot
        to = (self.rot + (1 if dir_sign > 0 else -1)) % 4
        shape_to = PIECE_ROTATIONS[self.type][to]

        def can_place(nx, ny):
            for i, row in enumerate(shape_to):
                for j, v in enumerate(row):
                    if not v: continue
                    x, y = nx + j, ny + i
                    if x < 0 or x >= COLUMNS or y >= ROWS: return False
                    if y >= 0 and grid[y][x] != BLACK: return False
            return True

        for dx, dy in kick_table(self.type, fr, to):
            nx, ny = self.x + dx, self.y + dy
            if can_place(nx, ny):
                self.rot = to
                self.x, self.y = nx, ny
                return True
        return False

class BagRandomizer:
    def __init__(self):
        self.bag = []
        self.refill()
    def refill(self):
        b = list("IJLOSTZ")
        random.shuffle(b)
        self.bag += b
    def get_piece(self):
        if not self.bag: self.refill()
        return Tetromino(self.bag.pop(0))

# =========================
# Utility griglia / punteggio
# =========================
def create_grid(locked):
    g = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for (x, y), c in locked.items():
        if 0 <= x < COLUMNS and 0 <= y < ROWS:
            g[y][x] = c
    return g

def valid_space(p, g):
    for x, y in p.cells():
        if x < 0 or x >= COLUMNS or y >= ROWS: return False
        if y >= 0 and g[y][x] != BLACK: return False
    return True

def clear_rows(g, locked):
    return [y for y in range(ROWS) if BLACK not in g[y]]

def load_highscore():
    try:
        with open(HIGHSCORE_FILE) as f: return int(f.read().strip())
    except:
        return 0

def save_highscore(s):
    try:
        with open(HIGHSCORE_FILE, "w") as f: f.write(str(s))
    except:
        pass

# =========================
# Disegno
# =========================
def draw_block(surf, x, y, color, ghost=False):
    r = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surf, GHOSTC if ghost else color, r)
    if not ghost:
        pygame.draw.rect(surf, BLACK, r, 2)

def draw_grid(surf, g):
    for y in range(ROWS):
        for x in range(COLUMNS):
            if g[y][x] != BLACK:
                draw_block(surf, x, y, g[y][x])
    # griglia
    for x in range(COLUMNS+1):
        pygame.draw.line(surf, DGRAY, (x*BLOCK_SIZE, 0), (x*BLOCK_SIZE, GRID_H))
    for y in range(ROWS+1):
        pygame.draw.line(surf, DGRAY, (0, y*BLOCK_SIZE), (GRID_W, y*BLOCK_SIZE))

def draw_mini_piece(surf, piece, x, y, scale=20):
    shp = piece.shape
    for i, row in enumerate(shp):
        for j, v in enumerate(row):
            if v:
                r = pygame.Rect(x + j*scale, y + i*scale, scale, scale)
                pygame.draw.rect(surf, piece.color, r)
                pygame.draw.rect(surf, BLACK, r, 1)

def draw_side_panel(surf, score, hs, lines, level, nextp, holdp, music_on, mode, time_left):
    px = GRID_W
    pygame.draw.rect(surf, (25,25,25), (px, 0, SIDE_PANEL_W, HEIGHT))
    f = pygame.font.SysFont("Arial", 20, True)
    v = pygame.font.SysFont("Arial", 18)

    surf.blit(f.render("Mode", True, WHITE), (px+20, 16))
    surf.blit(v.render(mode, True, YELLOW), (px+20, 40))

    surf.blit(f.render("Score", True, WHITE), (px+20, 70))
    surf.blit(v.render(str(score), True, YELLOW), (px+20, 94))

    surf.blit(f.render("High Score", True, WHITE), (px+20, 124))
    surf.blit(v.render(str(hs), True, YELLOW), (px+20, 148))

    surf.blit(f.render("Lines", True, WHITE), (px+20, 178))
    surf.blit(v.render(str(lines), True, YELLOW), (px+20, 202))

    surf.blit(f.render("Level", True, WHITE), (px+20, 232))
    surf.blit(v.render(str(level), True, YELLOW), (px+20, 256))

    if mode == "Time Attack":
        surf.blit(f.render("Time", True, WHITE), (px+20, 286))
        surf.blit(v.render(f"{time_left}s", True, YELLOW), (px+20, 310))

    surf.blit(f.render("Next", True, WHITE), (px+20, 344))
    draw_mini_piece(surf, nextp, px+40, 372)

    surf.blit(f.render("Hold", True, WHITE), (px+130, 344))
    if holdp:
        draw_mini_piece(surf, holdp, px+130, 372)

    surf.blit(f.render(f"Music: {'ON' if music_on else 'OFF'}", True, WHITE), (px+20, 540))

def draw_window(surf, g, score, hs, lines, level, nextp, holdp, ghost_pos, game_over, flash_rows, music_on, mode, time_left):
    surf.fill((10,10,30))
    # ghost
    for x, y in ghost_pos:
        if y >= 0:
            draw_block(surf, x, y, GHOSTC, True)
    # griglia/pezzi (flash bianco sulle righe da cancellare)
    for y in range(ROWS):
        for x in range(COLUMNS):
            if g[y][x] != BLACK:
                color = WHITE if y in flash_rows else g[y][x]
                draw_block(surf, x, y, color)
    draw_grid(surf, g)
    draw_side_panel(surf, score, hs, lines, level, nextp, holdp, music_on, mode, time_left)

    if game_over:
        f = pygame.font.SysFont("Arial", 48, True)
        lbl = f.render("GAME OVER", True, RED)
        surf.blit(lbl, (GRID_W//2 - lbl.get_width()//2, HEIGHT//2 - 30))

# =========================
# Menu
# =========================
def game_menu(screen):
    f = pygame.font.SysFont("Arial", 40, True)
    small = pygame.font.SysFont("Arial", 28)
    while True:
        screen.fill((0,0,30))
        t = f.render("TETRIS", True, YELLOW)
        screen.blit(t, (WIDTH//2 - t.get_width()//2, 150))

        o1 = small.render("1 - Marathon", True, WHITE)
        o2 = small.render("2 - Time Attack (3 min)", True, WHITE)
        hint = small.render("← → ↓ Muovi • ↑:CW  Z:CCW  X:180 • SPACE:Drop • C:Hold • M:Musica", True, (180,180,180))

        screen.blit(o1, (WIDTH//2 - o1.get_width()//2, 280))
        screen.blit(o2, (WIDTH//2 - o2.get_width()//2, 320))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 380))

        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return "Marathon"
                if e.key == pygame.K_2: return "Time Attack"

# =========================
# Main
# =========================
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris — Completo")
    clock = pygame.time.Clock()

    # (opzionale) Musica: metti un .ogg e scommenta
    music_on = False
    # try:
    #     pygame.mixer.music.load("music/tetris_theme.ogg")
    #     pygame.mixer.music.play(-1)
    #     music_on = True
    # except: pass

    mode = game_menu(screen)

    fall_time = 0
    fall_speed = 0.5
    score = 0
    lines = 0
    level = 1
    hs = load_highscore()

    if mode == "Time Attack":
        total_time = 180
        start_time = time.time()

    locked = {}
    grid = create_grid(locked)

    bag = BagRandomizer()
    cur = bag.get_piece()
    nxt = bag.get_piece()
    hold = None
    can_hold = True

    game_over = False
    flash_timer = 0
    flash_rows = []

    running = True
    while running:
        grid = create_grid(locked)
        fall_time += clock.get_rawtime()
        dt = clock.tick()

        # timer Time Attack
        time_left = 0
        if mode == "Time Attack" and not game_over:
            elapsed = int(time.time() - start_time)
            time_left = max(0, total_time - elapsed)
            if time_left == 0:
                game_over = True

        # caduta automatica
        if not game_over and flash_timer == 0 and fall_time/1000 >= fall_speed:
            fall_time = 0
            cur.y += 1
            if not valid_space(cur, grid):
                cur.y -= 1
                # lock
                for pos in cur.cells():
                    locked[pos] = cur.color
                # check righe
                flash_rows = clear_rows(grid, locked)
                if flash_rows:
                    flash_timer = 350
                else:
                    # nuovo pezzo
                    cur = nxt
                    nxt = bag.get_piece()
                    can_hold = True
                    if not valid_space(cur, grid):
                        game_over = True

        # eventi
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                # musica
                if e.key == pygame.K_m:
                    if music_on:
                        pygame.mixer.music.pause(); music_on = False
                    else:
                        pygame.mixer.music.unpause(); music_on = True

                if game_over or flash_timer > 0:
                    continue

                if e.key == pygame.K_LEFT:
                    cur.x -= 1
                    if not valid_space(cur, grid): cur.x += 1

                elif e.key == pygame.K_RIGHT:
                    cur.x += 1
                    if not valid_space(cur, grid): cur.x -= 1

                elif e.key == pygame.K_DOWN:  # SOFT DROP (+1 per cella valida)
                    cur.y += 1
                    if valid_space(cur, grid):
                        score += 1
                    else:
                        cur.y -= 1

                elif e.key == pygame.K_UP:     # CW
                    cur.try_rotate(+1, grid)

                elif e.key == pygame.K_z:      # CCW
                    cur.try_rotate(-1, grid)

                elif e.key == pygame.K_x:      # 180°
                    cur.try_rotate(+1, grid); cur.try_rotate(+1, grid)

                elif e.key == pygame.K_SPACE:  # HARD DROP (+2 per cella)
                    dist = 0
                    while valid_space(cur, grid):
                        cur.y += 1
                        dist += 1
                    cur.y -= 1
                    dist -= 1  # ultima mossa invalida
                    if dist > 0:
                        score += dist * 2

                elif e.key == pygame.K_c and can_hold:
                    if hold is None:
                        hold = cur
                        cur = nxt
                        nxt = bag.get_piece()
                    else:
                        hold, cur = cur, hold
                    # reset posizione del pezzo preso/ritornato da hold
                    spawn_w = len(cur.shape[0])
                    cur.x = COLUMNS // 2 - spawn_w // 2
                    cur.y = 0
                    cur.rot = cur.rot % 4
                    can_hold = False

        # ghost piece (copia del pezzo corrente)
        ghost = Tetromino(cur.type)
        ghost.rot = cur.rot
        ghost.x, ghost.y = cur.x, cur.y
        while valid_space(ghost, grid):
            ghost.y += 1
        ghost.y -= 1
        ghost_pos = ghost.cells()

        # disegna pezzo corrente (se non in fase di flash)
        if not game_over and flash_timer == 0:
            for x, y in cur.cells():
                if y >= 0:
                    grid[y][x] = cur.color

        # animazione & clear righe
        if flash_timer > 0:
            flash_timer -= dt
            if flash_timer <= 0:
                # elimina righe
                for y in flash_rows:
                    for x in range(COLUMNS):
                        locked.pop((x, y), None)
                # fai cadere ciò che sta sopra
                for y in sorted(flash_rows):
                    for (lx, ly) in sorted(list(locked), key=lambda k: k[1])[::-1]:
                        if ly < y:
                            locked[(lx, ly + 1)] = locked.pop((lx, ly))

                # punteggio base per righe
                cleared = len(flash_rows)
                score += LINE_SCORES.get(cleared, 0) * level
                lines += cleared
                if score > hs:
                    hs = score

                # level up
                if lines % 10 == 0:
                    level += 1
                    fall_speed = max(0.08, fall_speed * 0.9)

                # nuovo pezzo
                flash_rows = []
                cur = nxt
                nxt = bag.get_piece()
                can_hold = True
                if not valid_space(cur, grid):
                    game_over = True

        # draw frame
        draw_window(screen, grid, score, hs, lines, level, nxt, hold, ghost_pos,
                    game_over, flash_rows, music_on, mode,
                    (time_left if mode == "Time Attack" else 0))
        pygame.display.update()

    # salva high score
    if score > hs:
        save_highscore(score)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()