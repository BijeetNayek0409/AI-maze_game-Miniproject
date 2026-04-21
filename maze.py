import pygame
import sys
from collections import deque
import heapq

#Settings
ROWS, COLS = 25, 25
UI_BAR = 52

pygame.init()
info = pygame.display.Info()

max_w = int(info.current_w * 0.9)
max_h = int(info.current_h * 0.9) - UI_BAR

CELL   = min(max_w // COLS, max_h // ROWS)
GRID_W = CELL * COLS
GRID_H = CELL * ROWS
WIDTH  = GRID_W
HEIGHT = GRID_H + UI_BAR

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("AI Maze Solver (BFS vs A*)")

#Colors
WHITE  = (255, 255, 255)
BLACK  = (30,  30,  30)
GREEN  = (0,   200, 100)
RED    = (255, 80,  80)
BLUE   = (50,  120, 255)
YELLOW = (255, 215, 0)
CYAN   = (0,   255, 255)
GRAY   = (60,  60,  60)
DIM    = (160, 160, 160)

# state
grid    = [[0] * COLS for _ in range(ROWS)]
start   = None
end     = None
visited = set()
path    = []
mode    = "BFS"

# recalc
def recalc(w, h):
    global CELL, GRID_W, GRID_H, WIDTH, HEIGHT
    avail_w = w
    avail_h = h - UI_BAR
    CELL   = max(4, min(avail_w // COLS, avail_h // ROWS))
    GRID_W = CELL * COLS
    GRID_H = CELL * ROWS
    WIDTH  = GRID_W
    HEIGHT = GRID_H + UI_BAR

def ui_font(target_w):
    """Return the largest font size where both hint lines fit within target_w."""
    line1 = f"Mode: {mode}  |  S: Start   E: End   Click: Wall   RClick: Erase   1/2: BFS/A*"
    line2 = "SPACE: Solve   C: Clear"
    for size in range(17, 7, -1):
        f = pygame.font.SysFont("consolas", size)
        if f.size(line1)[0] <= target_w - 16 and f.size(line2)[0] <= target_w - 16:
            return f, line1, line2
    return pygame.font.SysFont("consolas", 8), line1, line2

#draw
def draw():
    screen.fill(BLACK)

    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == 1:
                color = GRAY
            elif (r, c) in path:
                color = YELLOW
            elif (r, c) in visited:
                color = BLUE
            else:
                color = WHITE
            pygame.draw.rect(screen, color,
                             (c * CELL, r * CELL, CELL - 1, CELL - 1))

    if start:
        pygame.draw.rect(screen, GREEN,
                         (start[1] * CELL, start[0] * CELL, CELL, CELL))
    if end:
        pygame.draw.rect(screen, RED,
                         (end[1] * CELL, end[0] * CELL, CELL, CELL))

    # UI bar - two lines, auto-sized
    bar_y = GRID_H
    pygame.draw.rect(screen, (20, 20, 20), (0, bar_y, WIDTH, UI_BAR))

    f, line1, line2 = ui_font(WIDTH)
    lh    = f.get_height()
    gap   = 3
    total = lh * 2 + gap
    y0    = bar_y + (UI_BAR - total) // 2

    screen.blit(f.render(line1, True, CYAN), (8, y0))
    screen.blit(f.render(line2, True, DIM),  (8, y0 + lh + gap))

    pygame.display.update()

#helpers
def cell_at(mx, my):
    r, c = my // CELL, mx // CELL
    if 0 <= r < ROWS and 0 <= c < COLS:
        return r, c
    return None

def neighbors(node):
    r, c = node
    result = []
    for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == 0:
            result.append((nr, nc))
    return result


def bfs():
    global visited, path
    queue   = deque([(start, [])])
    visited = set()
    while queue:
        node, p = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        if node == end:
            path = p + [node]
            return
        for n in neighbors(node):
            queue.append((n, p + [node]))
        draw()
        pygame.time.delay(15)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar():
    global visited, path
    pq      = [(0, start, [])]
    visited = set()
    while pq:
        cost, node, p = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        if node == end:
            path = p + [node]
            return
        for n in neighbors(node):
            heapq.heappush(pq, (len(p) + heuristic(n, end), n, p + [node]))
        draw()
        pygame.time.delay(15)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()


recalc(WIDTH, HEIGHT)

while True:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.VIDEORESIZE:
            recalc(event.w, event.h)
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            cell = cell_at(mx, my)
            if cell and cell != start and cell != end:
                grid[cell[0]][cell[1]] = 1

        if pygame.mouse.get_pressed()[2]:
            mx, my = pygame.mouse.get_pos()
            cell = cell_at(mx, my)
            if cell:
                grid[cell[0]][cell[1]] = 0

        if event.type == pygame.KEYDOWN:
            mx, my = pygame.mouse.get_pos()

            if event.key == pygame.K_s:
                cell = cell_at(mx, my)
                if cell:
                    start = cell
                    grid[cell[0]][cell[1]] = 0

            if event.key == pygame.K_e:
                cell = cell_at(mx, my)
                if cell:
                    end = cell
                    grid[cell[0]][cell[1]] = 0

            if event.key == pygame.K_c:
                grid    = [[0] * COLS for _ in range(ROWS)]
                start   = None
                end     = None
                visited = set()
                path    = []

            if event.key == pygame.K_1:
                mode = "BFS"
            if event.key == pygame.K_2:
                mode = "A*"

            if event.key == pygame.K_SPACE and start and end:
                visited = set()
                path    = []
                if mode == "BFS":
                    bfs()
                else:
                    astar()

    draw()
