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
WIDTH_SINGLE, HEIGHT = GRID_W + SIDE_PANEL_W, GRID_H

HIGHSCORE_FILE = "highscore.txt"

# Colori
BLACK  = (0, 0, 0)
DGRAY  = (40, 40, 40)
WHITE  = (255, 255, 255)
RED    = (200, 30, 30)
YELLOW = (240, 240, 0)
GHOSTC = (90, 90, 90)
GARBAGE = (100, 100, 100)

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
# Utility griglia / file
# =========================
def create_grid(locked):
    """Crea una griglia 10x20 a partire dai blocchi bloccati"""
    g = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for (x, y), c in locked.items():
        if 0 <= x < COLUMNS and 0 <= y < ROWS:
            g[y][x] = c
    return g

def valid_space(p, g):
    """Controlla se un tetramino p è in una posizione valida sulla griglia g"""
    for x, y in p.cells():
        if x < 0 or x >= COLUMNS or y >= ROWS:
            return False
        if y >= 0 and g[y][x] != BLACK:
            return False
    return True

def load_highscore():
    """Carica l’highscore da file"""
    try:
        with open(HIGHSCORE_FILE) as f:
            return int(f.read().strip())
    except:
        return 0

def save_highscore(s):
    """Salva l’highscore su file"""
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(s))
    except:
        pass

# =========================
# Garbage & gestione righe (per il versus)
# =========================
def clear_rows_and_compact(locked):
    """Ritorna quante righe sono state pulite ed esegue la compattazione"""
    full = [y for y in range(ROWS) if all((x,y) in locked for x in range(COLUMNS))]
    for y in full:
        for x in range(COLUMNS):
            locked.pop((x,y), None)
        # sposta giù tutto ciò che sta sopra
        for (lx, ly) in sorted(list(locked), key=lambda k: k[1])[::-1]:
            if ly < y:
                locked[(lx, ly+1)] = locked.pop((lx, ly))
    return len(full)

def add_garbage(locked, lines):
    """Aggiunge righe di spazzatura al campo (versus)"""
    for _ in range(lines):
        # spingi su tutto
        for (lx, ly) in sorted(list(locked), key=lambda k: k[1]):
            if ly > 0:
                locked[(lx, ly-1)] = locked.pop((lx, ly))
        # crea nuova riga in basso con un buco
        hole = random.randint(0, COLUMNS-1)
        for x in range(COLUMNS):
            if x != hole:
                locked[(x, ROWS-1)] = GARBAGE
# =========================
# Disegno (single player)
# =========================
def draw_block(surf, x, y, color, ghost=False):
    r = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surf, GHOSTC if ghost else color, r)
    if not ghost:
        pygame.draw.rect(surf, BLACK, r, 2)

def draw_grid_lines(surf):
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

def draw_side_panel(surf, score, hs, lines, level, nextp, holdp,
                    music_on, mode, time_left):
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

def draw_window_single(surf, grid, score, hs, lines, level, nextp, holdp,
                       ghost_pos, game_over, flash_rows,
                       music_on, mode, time_left):
    surf.fill((10,10,30))
    # ghost
    for x, y in ghost_pos:
        if y >= 0:
            draw_block(surf, x, y, GHOSTC, True)
    # celle
    for y in range(ROWS):
        for x in range(COLUMNS):
            if grid[y][x] != BLACK:
                color = WHITE if y in flash_rows else grid[y][x]
                draw_block(surf, x, y, color)

    draw_grid_lines(surf)
    draw_side_panel(surf, score, hs, lines, level, nextp, holdp,
                    music_on, mode, time_left)

    if game_over:
        f = pygame.font.SysFont("Arial", 48, True)
        lbl = f.render("GAME OVER", True, RED)
        surf.blit(lbl, (GRID_W//2 - lbl.get_width()//2, HEIGHT//2 - 30))

# =========================
# Disegno (versus)
# =========================
def draw_block_offset(surf, x, y, color, ox):
    r = pygame.Rect(ox + x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(surf, color, r)
    pygame.draw.rect(surf, BLACK, r, 2)

def draw_board_vs(surf, grid, ox, title, nextp, holdp, ghost_pos=None):
    # titolo
    ftitle = pygame.font.SysFont("Arial", 20, True)
    lbl = ftitle.render(title, True, WHITE)
    surf.blit(lbl, (ox + GRID_W//2 - lbl.get_width()//2, 8))

    # ghost
    if ghost_pos:
        for x,y in ghost_pos:
            if y >= 0:
                draw_block_offset(surf, x, y, GHOSTC, ox)

    # celle
    for y in range(ROWS):
        for x in range(COLUMNS):
            if grid[y][x] != BLACK:
                draw_block_offset(surf, x, y, grid[y][x], ox)

    # griglia
    for x in range(COLUMNS+1):
        pygame.draw.line(surf, DGRAY,
                         (ox+x*BLOCK_SIZE, 0),
                         (ox+x*BLOCK_SIZE, GRID_H))
    for y in range(ROWS+1):
        pygame.draw.line(surf, DGRAY,
                         (ox, y*BLOCK_SIZE),
                         (ox+GRID_W, y*BLOCK_SIZE))

    # next / hold
    f = pygame.font.SysFont("Arial", 16, True)
    surf.blit(f.render("Next", True, WHITE), (ox + 8, GRID_H - 94))
    draw_mini_piece(surf, nextp, ox + 8, GRID_H - 72, scale=18)
    surf.blit(f.render("Hold", True, WHITE), (ox + GRID_W - 90, GRID_H - 94))
    if holdp:
        draw_mini_piece(surf, holdp, ox + GRID_W - 90, GRID_H - 72, scale=18)
# =========================
# Controller support
# =========================
DEADZONE = 0.35
REPEAT_DELAY = 150  # ms tra movimenti orizzontali ripetuti da stick

def init_controllers():
    pygame.joystick.init()
    ctrls = []
    for i in range(pygame.joystick.get_count()):
        j = pygame.joystick.Joystick(i)
        j.init()
        ctrls.append(j)
    return ctrls

def axis_once(timer_dict, key, now, delay=REPEAT_DELAY):
    """Ritorna True se è passato abbastanza tempo per consentire il repeat di un asse."""
    t = timer_dict.get(key, 0)
    if now - t >= delay:
        timer_dict[key] = now
        return True
    return False

def read_controller_actions(joy, repeat_timers):
    """Ritorna una lista di azioni astratte dal controller."""
    if joy is None:
        return []
    actions = []
    now = pygame.time.get_ticks()

    # Assi (0: orizz, 1: vert)
    try:
        ax0 = joy.get_axis(0)
        ax1 = joy.get_axis(1)
    except Exception:
        ax0, ax1 = 0.0, 0.0

    if ax0 < -DEADZONE and axis_once(repeat_timers, "left", now):
        actions.append("left")
    if ax0 > DEADZONE and axis_once(repeat_timers, "right", now):
        actions.append("right")
    if ax1 > DEADZONE:
        actions.append("down")

    # Bottoni (layout standard Xbox/PS)
    try:
        if joy.get_button(0): actions.append("rotate_cw")     # A / X
        if joy.get_button(1): actions.append("rotate_ccw")    # B / O
        if joy.get_button(2): actions.append("rotate_180")    # X / Square
        if joy.get_button(3): actions.append("hold")          # Y / Triangle
        if joy.get_button(5): actions.append("hard_drop")     # RB
    except Exception:
        pass

    return actions
# =========================
# Menu e Istruzioni
# =========================
def show_instructions(screen):
    W, H = screen.get_size()
    font_title = pygame.font.SysFont("Arial", 36, True)
    font = pygame.font.SysFont("Arial", 22)
    screen.fill((0, 0, 30))

    title = font_title.render("Istruzioni", True, YELLOW)
    screen.blit(title, (W // 2 - title.get_width() // 2, 40))

    p1 = [
        "Giocatore 1 (Freccette + RCtrl/RShift) o Controller 1:",
        "← → : Muovi | ↓ : Soft Drop (+1/cella)",
        "↑ : CW | Z : CCW | X : 180° | RShift : Hard Drop | RCtrl : Hold",
        "Controller: Stick SX (muovi), A: CW, B: CCW, X: 180°, Y: Hold, RB: Drop",
    ]
    p2 = [
        "Giocatore 2 (WASD + Q/E/C/Space) o Controller 2:",
        "A D : Muovi | S : Soft Drop (+1/cella)",
        "W : CW | Q : CCW | E : 180° | Space : Hard Drop | C : Hold",
        "Controller: Stick SX, A: CW, B: CCW, X: 180°, Y: Hold, RB: Drop",
    ]
    misc = [
        "Generali: M = Musica ON/OFF | P = Pausa",
        "Single: Marathon / Time Attack (3 min) + Difficoltà",
        "Versus: Garbage attack (2→1, 3→2, 4→3)",
    ]

    y = 110
    for line in p1:
        screen.blit(font.render(line, True, WHITE), (60, y)); y += 28
    y += 10
    for line in p2:
        screen.blit(font.render(line, True, WHITE), (60, y)); y += 28
    y += 10
    for line in misc:
        screen.blit(font.render(line, True, WHITE), (60, y)); y += 28

    msg = font.render("Premi un tasto qualsiasi per tornare al menu", True, RED)
    screen.blit(msg, (W // 2 - msg.get_width() // 2, H - 50))
    pygame.display.update()

    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                waiting = False


def main_menu(screen):
    W, H = WIDTH_SINGLE, HEIGHT
    font_title = pygame.font.SysFont("Arial", 40, True)
    font = pygame.font.SysFont("Arial", 28)

    while True:
        screen.fill((0, 0, 30))
        title = font_title.render("TETRIS", True, YELLOW)
        screen.blit(title, (W // 2 - title.get_width() // 2, 140))

        opt1 = font.render("1 - Single Player", True, WHITE)
        opt2 = font.render("2 - Versus Locale", True, WHITE)
        optH = font.render("H - Istruzioni", True, WHITE)
        optQ = font.render("Q - Esci", True, WHITE)

        screen.blit(opt1, (W // 2 - opt1.get_width() // 2, 240))
        screen.blit(opt2, (W // 2 - opt2.get_width() // 2, 280))
        screen.blit(optH, (W // 2 - optH.get_width() // 2, 320))
        screen.blit(optQ, (W // 2 - optQ.get_width() // 2, 360))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return "single"
                if e.key == pygame.K_2: return "versus"
                if e.key == pygame.K_h: show_instructions(screen)
                if e.key == pygame.K_q: pygame.quit(); sys.exit()


def single_mode_menu(screen):
    W, H = WIDTH_SINGLE, HEIGHT
    f = pygame.font.SysFont("Arial", 36, True)
    s = pygame.font.SysFont("Arial", 26)
    while True:
        screen.fill((0, 0, 30))
        t = f.render("Single Player", True, YELLOW)
        screen.blit(t, (W // 2 - t.get_width() // 2, 100))

        o1 = s.render("1 - Marathon", True, WHITE)
        o2 = s.render("2 - Time Attack (3 min)", True, WHITE)
        esc = s.render("Esc - Indietro", True, WHITE)

        screen.blit(o1, (W // 2 - o1.get_width() // 2, 180))
        screen.blit(o2, (W // 2 - o2.get_width() // 2, 220))
        screen.blit(esc, (W // 2 - esc.get_width() // 2, 280))

        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return "Marathon"
                if e.key == pygame.K_2: return "Time Attack"
                if e.key == pygame.K_ESCAPE: return None


def difficulty_menu(screen):
    W, H = WIDTH_SINGLE, HEIGHT
    f = pygame.font.SysFont("Arial", 36, True)
    s = pygame.font.SysFont("Arial", 26)
    while True:
        screen.fill((0, 0, 30))
        t = f.render("Seleziona Difficoltà", True, YELLOW)
        screen.blit(t, (W // 2 - t.get_width() // 2, 100))

        d1 = s.render("1 - Facile (lento)", True, WHITE)
        d2 = s.render("2 - Normale", True, WHITE)
        d3 = s.render("3 - Difficile (veloce)", True, WHITE)
        esc = s.render("Esc - Indietro", True, WHITE)

        screen.blit(d1, (W // 2 - d1.get_width() // 2, 180))
        screen.blit(d2, (W // 2 - d2.get_width() // 2, 220))
        screen.blit(d3, (W // 2 - d3.get_width() // 2, 260))
        screen.blit(esc, (W // 2 - esc.get_width() // 2, 320))

        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return "Easy"
                if e.key == pygame.K_2: return "Normal"
                if e.key == pygame.K_3: return "Hard"
                if e.key == pygame.K_ESCAPE: return None
# =========================
# Modalità Single Player
# =========================
def run_single(mode, difficulty):
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH_SINGLE, HEIGHT))
    pygame.display.set_caption(f"Tetris — Single Player ({mode}, {difficulty})")
    clock = pygame.time.Clock()

    # Musica opzionale
    music_on = False

    # Controller
    controllers = init_controllers()
    joy1 = controllers[0] if len(controllers) >= 1 else None
    repeat_timers_p1 = {}

    fall_time = 0
    score = 0
    lines = 0
    level = 1
    hs = load_highscore()
    paused = False

    # Velocità iniziale in base alla difficoltà
    if difficulty == "Easy":
        fall_speed = 0.8
    elif difficulty == "Hard":
        fall_speed = 0.3
    else:
        fall_speed = 0.5

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
        dt = clock.tick(60)
        if paused:
            # Draw pause overlay
            grid = create_grid(locked)
            ghost = Tetromino(cur.type); ghost.rot = cur.rot; ghost.x, ghost.y = cur.x, cur.y
            while valid_space(ghost, grid): ghost.y += 1
            ghost.y -= 1
            ghost_pos = ghost.cells()
            draw_window_single(screen, grid, score, hs, lines, level, nxt, hold, ghost_pos,
                               game_over, flash_rows, music_on, mode,
                               (max(0, total_time - int(time.time() - start_time)) if mode=="Time Attack" else 0))
            font = pygame.font.SysFont("Arial", 48, True)
            lbl = font.render("PAUSED", True, YELLOW)
            screen.blit(lbl, (GRID_W//2 - lbl.get_width()//2, HEIGHT//2-30))
            pygame.display.update()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: running = False
                if e.type == pygame.KEYDOWN and e.key == pygame.K_p: paused = False
            continue

        grid = create_grid(locked)
        fall_time += dt

        # timer Time Attack
        time_left = 0
        if mode == "Time Attack" and not game_over:
            elapsed = int(time.time() - start_time)
            time_left = max(0, total_time - elapsed)
            if time_left == 0:
                game_over = True

        # === INPUT: Tastiera
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p: paused = not paused
                if e.key == pygame.K_m:
                    if music_on: pygame.mixer.music.pause(); music_on = False
                    else: pygame.mixer.music.unpause(); music_on = True
                if game_over or flash_timer > 0: continue

                if e.key == pygame.K_LEFT:
                    cur.x -= 1
                    if not valid_space(cur, grid): cur.x += 1
                elif e.key == pygame.K_RIGHT:
                    cur.x += 1
                    if not valid_space(cur, grid): cur.x -= 1
                elif e.key == pygame.K_DOWN:  # soft drop (+1)
                    cur.y += 1
                    if valid_space(cur, grid): score += 1
                    else: cur.y -= 1
                elif e.key == pygame.K_UP:     # CW
                    cur.try_rotate(+1, grid)
                elif e.key == pygame.K_z:      # CCW
                    cur.try_rotate(-1, grid)
                elif e.key == pygame.K_x:      # 180°
                    cur.try_rotate(+1, grid); cur.try_rotate(+1, grid)
                elif e.key == pygame.K_SPACE:  # hard drop (+2/cella)
                    dist = 0
                    while valid_space(cur, grid):
                        cur.y += 1; dist += 1
                    cur.y -= 1; dist -= 1
                    if dist > 0: score += dist * 2
                elif e.key == pygame.K_c and can_hold:
                    if hold is None:
                        hold = cur
                        cur = nxt
                        nxt = bag.get_piece()
                    else:
                        hold, cur = cur, hold
                    spawn_w = len(cur.shape[0])
                    cur.x = COLUMNS // 2 - spawn_w // 2
                    cur.y = 0
                    cur.rot %= 4
                    can_hold = False

        # === INPUT: Controller P1
        if not (game_over or flash_timer > 0):
            actions = read_controller_actions(joy1, repeat_timers_p1)
            for act in actions:
                if act == "left":
                    cur.x -= 1
                    if not valid_space(cur, grid): cur.x += 1
                elif act == "right":
                    cur.x += 1
                    if not valid_space(cur, grid): cur.x -= 1
                elif act == "down":
                    cur.y += 1
                    if valid_space(cur, grid): score += 1
                    else: cur.y -= 1
                elif act == "rotate_cw":
                    cur.try_rotate(+1, grid)
                elif act == "rotate_ccw":
                    cur.try_rotate(-1, grid)
                elif act == "rotate_180":
                    cur.try_rotate(+1, grid); cur.try_rotate(+1, grid)
                elif act == "hard_drop":
                    dist = 0
                    while valid_space(cur, grid):
                        cur.y += 1; dist += 1
                    cur.y -= 1; dist -= 1
                    if dist > 0: score += dist * 2
                elif act == "hold" and can_hold:
                    if hold is None:
                        hold = cur
                        cur = nxt
                        nxt = bag.get_piece()
                    else:
                        hold, cur = cur, hold
                    spawn_w = len(cur.shape[0])
                    cur.x = COLUMNS // 2 - spawn_w // 2
                    cur.y = 0
                    cur.rot %= 4
                    can_hold = False

        # caduta automatica
        if not game_over and flash_timer == 0 and fall_time >= fall_speed*1000:
            fall_time = 0
            cur.y += 1
            if not valid_space(cur, grid):
                cur.y -= 1
                # lock
                for pos in cur.cells():
                    locked[pos] = cur.color
                # check righe
                to_clear = [y for y in range(ROWS) if all((x,y) in locked for x in range(COLUMNS))]
                if to_clear:
                    flash_rows = to_clear[:]
                    flash_timer = 350
                else:
                    cur = nxt; nxt = bag.get_piece(); can_hold = True
                    if not valid_space(cur, grid): game_over = True

        # ghost
        ghost = Tetromino(cur.type); ghost.rot=cur.rot; ghost.x, ghost.y=cur.x,cur.y
        while valid_space(ghost, grid): ghost.y += 1
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

                # punteggi e livello
                cleared = len(flash_rows)
                score += LINE_SCORES.get(cleared, 0) * level
                lines += cleared
                if score > hs: hs = score
                if lines % 10 == 0:
                    level += 1
                    fall_speed = max(0.08, fall_speed * 0.9)

                flash_rows = []
                cur = nxt; nxt = bag.get_piece(); can_hold = True
                if not valid_space(cur, grid): game_over = True

        draw_window_single(screen, grid, score, hs, lines, level, nxt, hold, ghost_pos,
                           game_over, flash_rows, music_on, mode, (time_left if mode=="Time Attack" else 0))
        pygame.display.update()

    if score > hs: save_highscore(score)
    pygame.quit()
    sys.exit()
# =========================
# Modalità Versus con Garbage e Difficoltà
# =========================
def clear_rows_and_compact(locked):
    """Ritorna quante righe sono state pulite ed esegue la compattazione (senza animazione)."""
    full = [y for y in range(ROWS) if all((x,y) in locked for x in range(COLUMNS))]
    for y in full:
        for x in range(COLUMNS):
            locked.pop((x,y), None)
        # sposta giù tutto ciò che sta sopra
        for (lx, ly) in sorted(list(locked), key=lambda k: k[1])[::-1]:
            if ly < y:
                locked[(lx, ly+1)] = locked.pop((lx, ly))
    return len(full)

def add_garbage(locked, lines):
    """Aggiunge 'lines' righe spazzatura dal basso con un buco casuale e spinge su il campo."""
    for _ in range(lines):
        # spingi su tutto
        for (lx, ly) in sorted(list(locked), key=lambda k: k[1]):
            if ly > 0:
                locked[(lx, ly-1)] = locked.pop((lx, ly))
        # crea nuova riga in basso
        hole = random.randint(0, COLUMNS-1)
        for x in range(COLUMNS):
            if x != hole:
                locked[(x, ROWS-1)] = GARBAGE

# =========================
# Modalità Versus con Garbage e Difficoltà
# =========================
def run_versus(difficulty):
    margin = 40
    WIDTH_VS = GRID_W*2 + margin
    screen = pygame.display.set_mode((WIDTH_VS, HEIGHT))
    pygame.display.set_caption(f"Tetris — Versus Locale ({difficulty})")
    clock = pygame.time.Clock()

    # Controller
    controllers = init_controllers()
    joy1 = controllers[0] if len(controllers) >= 1 else None
    joy2 = controllers[1] if len(controllers) >= 2 else None
    rpt1, rpt2 = {}, {}

    # P1
    locked1, bag1 = {}, BagRandomizer()
    cur1, nxt1 = bag1.get_piece(), bag1.get_piece()
    hold1, can_hold1 = None, True
    # P2
    locked2, bag2 = {}, BagRandomizer()
    cur2, nxt2 = bag2.get_piece(), bag2.get_piece()
    hold2, can_hold2 = None, True

    fall_t1 = fall_t2 = 0

    # Velocità iniziale in base alla difficoltà
    if difficulty == "Easy":
        fall_speed = 0.8
    elif difficulty == "Hard":
        fall_speed = 0.3
    else:
        fall_speed = 0.5

    over1 = over2 = False
    paused = False

    while True:
        dt = clock.tick(60)
        if paused:
            # Disegna schermata pausa
            grid1 = create_grid(locked1)
            grid2 = create_grid(locked2)

            # ghost p1
            g1 = Tetromino(cur1.type)
            g1.rot = cur1.rot
            g1.x, g1.y = cur1.x, cur1.y
            while valid_space(g1, grid1): g1.y += 1
            g1.y -= 1
            ghost1 = g1.cells()

            # ghost p2
            g2 = Tetromino(cur2.type)
            g2.rot = cur2.rot
            g2.x, g2.y = cur2.x, cur2.y
            while valid_space(g2, grid2): g2.y += 1
            g2.y -= 1
            ghost2 = g2.cells()

            screen.fill((10,10,30))
            draw_board_vs(screen, grid1, 10, "P1", nxt1, hold1, ghost1)
            draw_board_vs(screen, grid2, GRID_W + margin, "P2", nxt2, hold2, ghost2)

            font = pygame.font.SysFont("Arial",48,True)
            lbl = font.render("PAUSED", True, YELLOW)
            screen.blit(lbl, (WIDTH_VS//2 - lbl.get_width()//2, HEIGHT//2 - 30))
            pygame.display.update()

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                    paused = False
            continue

        fall_t1 += dt
        fall_t2 += dt
        grid1 = create_grid(locked1)
        grid2 = create_grid(locked2)

        # === INPUT tastiera
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    paused = not paused

                # --- Player 1 (freccette + Z/X/RShift/RCtrl)
                if not over1:
                    if e.key == pygame.K_LEFT:
                        cur1.x -= 1
                        if not valid_space(cur1, grid1): cur1.x += 1
                    elif e.key == pygame.K_RIGHT:
                        cur1.x += 1
                        if not valid_space(cur1, grid1): cur1.x -= 1
                    elif e.key == pygame.K_DOWN:
                        cur1.y += 1
                        if not valid_space(cur1, grid1): cur1.y -= 1
                    elif e.key == pygame.K_UP:
                        cur1.try_rotate(+1, grid1)
                    elif e.key == pygame.K_z:
                        cur1.try_rotate(-1, grid1)
                    elif e.key == pygame.K_x:
                        cur1.try_rotate(+1, grid1); cur1.try_rotate(+1, grid1)
                    elif e.key == pygame.K_RSHIFT:  # hard drop
                        while valid_space(cur1, grid1): cur1.y += 1
                        cur1.y -= 1
                    elif e.key == pygame.K_RCTRL and can_hold1:
                        if hold1 is None:
                            hold1 = cur1; cur1 = nxt1; nxt1 = bag1.get_piece()
                        else:
                            hold1, cur1 = cur1, hold1
                        sw = len(cur1.shape[0])
                        cur1.x = COLUMNS//2 - sw//2; cur1.y = 0; cur1.rot %= 4
                        can_hold1 = False

                # --- Player 2 (WASD + Q/E/C/Space)
                if not over2:
                    if e.key == pygame.K_a:
                        cur2.x -= 1
                        if not valid_space(cur2, grid2): cur2.x += 1
                    elif e.key == pygame.K_d:
                        cur2.x += 1
                        if not valid_space(cur2, grid2): cur2.x -= 1
                    elif e.key == pygame.K_s:
                        cur2.y += 1
                        if not valid_space(cur2, grid2): cur2.y -= 1
                    elif e.key == pygame.K_w:
                        cur2.try_rotate(+1, grid2)
                    elif e.key == pygame.K_q:
                        cur2.try_rotate(-1, grid2)
                    elif e.key == pygame.K_e:
                        cur2.try_rotate(+1, grid2); cur2.try_rotate(+1, grid2)
                    elif e.key == pygame.K_SPACE:  # hard drop
                        while valid_space(cur2, grid2): cur2.y += 1
                        cur2.y -= 1
                    elif e.key == pygame.K_c and can_hold2:
                        if hold2 is None:
                            hold2 = cur2; cur2 = nxt2; nxt2 = bag2.get_piece()
                        else:
                            hold2, cur2 = cur2, hold2
                        sw = len(cur2.shape[0])
                        cur2.x = COLUMNS//2 - sw//2; cur2.y = 0; cur2.rot %= 4
                        can_hold2 = False

        # === INPUT controller P1
        if not over1:
            for act in read_controller_actions(joy1, rpt1):
                if act == "left":
                    cur1.x -= 1
                    if not valid_space(cur1, grid1): cur1.x += 1
                elif act == "right":
                    cur1.x += 1
                    if not valid_space(cur1, grid1): cur1.x -= 1
                elif act == "down":
                    cur1.y += 1
                    if not valid_space(cur1, grid1): cur1.y -= 1
                elif act == "rotate_cw":
                    cur1.try_rotate(+1, grid1)
                elif act == "rotate_ccw":
                    cur1.try_rotate(-1, grid1)
                elif act == "rotate_180":
                    cur1.try_rotate(+1, grid1); cur1.try_rotate(+1, grid1)
                elif act == "hard_drop":
                    while valid_space(cur1, grid1): cur1.y += 1
                    cur1.y -= 1
                elif act == "hold" and can_hold1:
                    if hold1 is None:
                        hold1 = cur1; cur1 = nxt1; nxt1 = bag1.get_piece()
                    else:
                        hold1, cur1 = cur1, hold1
                    sw = len(cur1.shape[0])
                    cur1.x = COLUMNS//2 - sw//2; cur1.y = 0; cur1.rot %= 4
                    can_hold1 = False

        # === INPUT controller P2
        if not over2:
            for act in read_controller_actions(joy2, rpt2):
                if act == "left":
                    cur2.x -= 1
                    if not valid_space(cur2, grid2): cur2.x += 1
                elif act == "right":
                    cur2.x += 1
                    if not valid_space(cur2, grid2): cur2.x -= 1
                elif act == "down":
                    cur2.y += 1
                    if not valid_space(cur2, grid2): cur2.y -= 1
                elif act == "rotate_cw":
                    cur2.try_rotate(+1, grid2)
                elif act == "rotate_ccw":
                    cur2.try_rotate(-1, grid2)
                elif act == "rotate_180":
                    cur2.try_rotate(+1, grid2); cur2.try_rotate(+1, grid2)
                elif act == "hard_drop":
                    while valid_space(cur2, grid2): cur2.y += 1
                    cur2.y -= 1
                elif act == "hold" and can_hold2:
                    if hold2 is None:
                        hold2 = cur2; cur2 = nxt2; nxt2 = bag2.get_piece()
                    else:
                        hold2, cur2 = cur2, hold2
                    sw = len(cur2.shape[0])
                    cur2.x = COLUMNS//2 - sw//2; cur2.y = 0; cur2.rot %= 4
                    can_hold2 = False


        # Caduta automatica P1
        if not over1 and fall_t1 >= fall_speed*1000:
            fall_t1 = 0
            cur1.y += 1
            if not valid_space(cur1, grid1):
                cur1.y -= 1
                for pos in cur1.cells(): locked1[pos] = cur1.color
                cleared = clear_rows_and_compact(locked1)
                if cleared >= 2: add_garbage(locked2, cleared-1)
                cur1 = nxt1; nxt1 = bag1.get_piece(); can_hold1 = True
                if not valid_space(cur1, create_grid(locked1)): over1 = True

        # Caduta automatica P2
        if not over2 and fall_t2 >= fall_speed*1000:
            fall_t2 = 0
            cur2.y += 1
            if not valid_space(cur2, grid2):
                cur2.y -= 1
                for pos in cur2.cells(): locked2[pos] = cur2.color
                cleared = clear_rows_and_compact(locked2)
                if cleared >= 2: add_garbage(locked1, cleared-1)
                cur2 = nxt2; nxt2 = bag2.get_piece(); can_hold2 = True
                if not valid_space(cur2, create_grid(locked2)): over2 = True

        # 👇 FIX: aggiungi i pezzi correnti ai campi
        for x, y in cur1.cells():
            if y >= 0:
                grid1[y][x] = cur1.color
        for x, y in cur2.cells():
            if y >= 0:
                grid2[y][x] = cur2.color

        # Disegno
        screen.fill((10,10,30))
        draw_board_vs(screen, grid1, 10, "P1", nxt1, hold1)
        draw_board_vs(screen, grid2, GRID_W + margin, "P2", nxt2, hold2)
        pygame.display.update()

        # Fine partita
        if over1 and not over2:
            end_msg(screen, "Giocatore 2 vince!")
            return
        if over2 and not over1:
            end_msg(screen, "Giocatore 1 vince!")
            return
        if over1 and over2:
            end_msg(screen, "Pareggio!")
            return

# =========================
# End Message
# =========================
def end_msg(screen, text):
    W,H = screen.get_size()
    font = pygame.font.SysFont("Arial", 42, True)
    lbl = font.render(text, True, YELLOW)
    screen.blit(lbl, (W//2 - lbl.get_width()//2, H//2 - 20))
    pygame.display.update()
    pygame.time.wait(2500)

# =========================
# Main
# =========================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_SINGLE, HEIGHT))
    pygame.display.set_caption("Tetris — Completo (Controller + Difficoltà)")

    while True:
        choice = main_menu(screen)
        if choice == "single":
            mode = single_mode_menu(screen)
            if mode:
                diff = difficulty_menu(screen)
                if diff:
                    run_single(mode, diff)
        elif choice == "versus":
            diff = difficulty_menu(screen)
            if diff:
                run_versus(diff)

if __name__ == "__main__":
    main()
