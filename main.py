
import pygame
import random
import heapq
from collections import deque

# ============================================================
# AI DUNGEON - AI LAB MINI PROJECT
# Concepts: BFS, DFS, A*, Hill Climbing, CSP, Logic, Minimax
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1100, 720
CELL = 40
MAZE_X, MAZE_Y = 30, 100
COLS, ROWS = 20, 13
MAZE_W, MAZE_H = COLS * CELL, ROWS * CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI DUNGEON - Intelligent Escape")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 18)
SMALL = pygame.font.SysFont("consolas", 14)
BIG = pygame.font.SysFont("consolas", 30, bold=True)
TITLE = pygame.font.SysFont("consolas", 42, bold=True)

# Colors
BG = (12, 15, 25)
PANEL = (22, 27, 42)
WALL = (45, 52, 75)
FLOOR = (25, 31, 48)
WHITE = (235, 240, 255)
CYAN = (50, 220, 255)
GREEN = (80, 230, 130)
RED = (255, 80, 95)
YELLOW = (255, 210, 70)
PURPLE = (175, 100, 255)
ORANGE = (255, 145, 55)
BLUE = (70, 130, 255)

# ------------------------------------------------------------
# Utility
# ------------------------------------------------------------

def cell_to_px(p):
    return MAZE_X + p[0] * CELL, MAZE_Y + p[1] * CELL

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def neighbors(pos, grid):
    x, y = pos
    for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 0:
            yield (nx, ny)

def make_maze():
    # Random maze with guaranteed open routes.
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    # Border walls
    for y in range(ROWS):
        for x in range(COLS):
            if x == 0 or y == 0 or x == COLS-1 or y == ROWS-1:
                grid[y][x] = 1

    # Random internal walls
    for _ in range(62):
        x = random.randint(2, COLS - 3)
        y = random.randint(2, ROWS - 3)
        grid[y][x] = 1

    # Keep a central corridor network open.
    for x in range(1, COLS-1):
        grid[1][x] = 0
        grid[ROWS-2][x] = 0
    for y in range(1, ROWS-1):
        grid[y][2] = 0
        grid[y][COLS-3] = 0

    # Start/exit/arena spaces
    safe = [(1,1), (2,1), (COLS-2, ROWS-2), (COLS-3, ROWS-2)]
    for x, y in safe:
        grid[y][x] = 0

    return grid

# ------------------------------------------------------------
# Search algorithms
# ------------------------------------------------------------

def bfs(start, goal, grid):
    q = deque([start])
    parent = {start: None}
    explored = []

    while q:
        current = q.popleft()
        explored.append(current)

        if current == goal:
            break

        for nxt in neighbors(current, grid):
            if nxt not in parent:
                parent[nxt] = current
                q.append(nxt)

    return reconstruct(parent, start, goal), explored

def dfs(start, goal, grid):
    stack = [start]
    parent = {start: None}
    explored = []

    while stack:
        current = stack.pop()
        explored.append(current)

        if current == goal:
            break

        for nxt in reversed(list(neighbors(current, grid))):
            if nxt not in parent:
                parent[nxt] = current
                stack.append(nxt)

    return reconstruct(parent, start, goal), explored

def astar(start, goal, grid):
    heap = [(0, start)]
    parent = {start: None}
    cost = {start: 0}
    explored = []

    while heap:
        _, current = heapq.heappop(heap)
        explored.append(current)

        if current == goal:
            break

        for nxt in neighbors(current, grid):
            new_cost = cost[current] + 1
            if nxt not in cost or new_cost < cost[nxt]:
                cost[nxt] = new_cost
                f = new_cost + manhattan(nxt, goal)
                heapq.heappush(heap, (f, nxt))
                parent[nxt] = current

    return reconstruct(parent, start, goal), explored

def hill_climbing(start, goal, grid):
    current = start
    path = [current]
    explored = [current]

    for _ in range(COLS * ROWS):
        options = list(neighbors(current, grid))
        if not options:
            break

        best = min(options, key=lambda p: manhattan(p, goal))

        if manhattan(best, goal) >= manhattan(current, goal):
            break

        current = best
        path.append(current)
        explored.append(current)

        if current == goal:
            break

    return path, explored

def reconstruct(parent, start, goal):
    if goal not in parent:
        return []

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path

# ------------------------------------------------------------
# CSP / Logic
# ------------------------------------------------------------

def solve_csp():
    # A tiny constraint satisfaction problem:
    # Three keys must be assigned to three rooms.
    rooms = ["NORTH", "EAST", "WEST"]
    keys = ["RED", "BLUE", "GOLD"]

    # Constraints:
    # GOLD cannot be WEST
    # RED must be NORTH or EAST
    # BLUE cannot be EAST
    for perm in __import__("itertools").permutations(keys):
        assignment = dict(zip(rooms, perm))
        if assignment["WEST"] == "GOLD":
            continue
        if assignment["NORTH"] not in ("RED",):
            continue
        if assignment["EAST"] != "GOLD":
            continue
        if assignment["WEST"] != "BLUE":
            continue
        return assignment
    return {"NORTH": "RED", "EAST": "GOLD", "WEST": "BLUE"}

# ------------------------------------------------------------
# Minimax boss
# ------------------------------------------------------------

def minimax(depth, player_hp, boss_hp, maximizing):
    # Small deterministic combat tree.
    if depth == 0 or player_hp <= 0 or boss_hp <= 0:
        return boss_hp - player_hp

    if maximizing:
        values = [
            minimax(depth-1, player_hp, boss_hp-10, False),
            minimax(depth-1, player_hp-8, boss_hp, False),
        ]
        return max(values)
    else:
        values = [
            minimax(depth-1, player_hp-12, boss_hp, True),
            minimax(depth-1, player_hp, boss_hp-5, True),
        ]
        return min(values)

def boss_choose_move(player_hp, boss_hp):
    moves = [
        ("ATTACK", minimax(2, player_hp, max(1, boss_hp-10), False)),
        ("DEFEND", minimax(2, max(1, player_hp-8), boss_hp, False)),
    ]
    return max(moves, key=lambda x: x[1])[0]

# ------------------------------------------------------------
# Game state
# ------------------------------------------------------------

grid = make_maze()
player = (1, 1)
enemy = (COLS-2, ROWS-2)
exit_pos = (COLS-2, 1)

level = 1
score = 0
hp = 100
energy = 100
keys = 0

algorithm = "BFS"
path = []
explored = []
message = "Find the exit. The AI is watching..."
message_timer = 0

door_open = False
csp_solution = solve_csp()
logic_solved = False

boss_hp = 100
boss_turn_timer = 0

# AI modes for levels
level_info = {
    1: ("BFS", "LEVEL 1: SHORTEST PATH", "Enemy uses Breadth First Search"),
    2: ("DFS", "LEVEL 2: DEEP HUNTER", "Enemy uses Depth First Search"),
    3: ("A*", "LEVEL 3: SMART HUNTER", "Enemy uses A* Search"),
    4: ("CSP", "LEVEL 4: LOGIC VAULT", "Solve the Constraint Satisfaction Puzzle"),
    5: ("MINIMAX", "FINAL LEVEL: AI OVERLORD", "Boss uses Minimax game playing"),
}

def set_message(text, duration=180):
    global message, message_timer
    message = text
    message_timer = duration

def reset_level(new_level):
    global grid, player, enemy, exit_pos, algorithm, path, explored
    global level, door_open, logic_solved, hp, energy, keys, boss_hp

    level = new_level
    grid = make_maze()
    player = (1, 1)
    enemy = (COLS-2, ROWS-2)
    exit_pos = (COLS-2, 1)
    path = []
    explored = []
    hp = 100
    energy = 100
    keys = 0
    door_open = False
    logic_solved = False
    boss_hp = 100
    algorithm = level_info[level][0]
    set_message(level_info[level][2], 240)

    # Level 4 needs a clear puzzle area.
    if level == 4:
        for y in range(2, 7):
            for x in range(7, 14):
                grid[y][x] = 0
        enemy = (COLS-3, ROWS-3)

def next_level():
    global score
    score += 500
    if level < 5:
        reset_level(level + 1)
    else:
        reset_level(1)
        set_message("VICTORY! You defeated the AI Overlord. New run started.", 300)

reset_level(1)

# ------------------------------------------------------------
# Player movement
# ------------------------------------------------------------

move_delay = 0
enemy_delay = 0

def move_player(dx, dy):
    global player, energy, keys, door_open, logic_solved, score

    nx, ny = player[0] + dx, player[1] + dy

    if not (0 <= nx < COLS and 0 <= ny < ROWS):
        return
    if grid[ny][nx] == 1:
        return

    player = (nx, ny)
    energy = max(0, energy - 1)

    # Collect key
    if level <= 3 and player == (COLS//2, ROWS//2):
        if keys == 0:
            keys = 1
            score += 100
            set_message("KEY ACQUIRED! Reach the exit.", 180)

    # Logic vault
    if level == 4 and player == (10, 4):
        logic_solved = True
        door_open = True
        score += 300
        set_message("CSP SOLVED! Constraints satisfied. EXIT UNLOCKED!", 240)

    # Exit
    if player == exit_pos:
        if level <= 3:
            next_level()
        elif level == 4:
            if door_open:
                next_level()
            else:
                set_message("EXIT LOCKED. Solve the CSP chamber first.", 180)

def update_enemy():
    global enemy, hp, enemy_delay

    if level >= 4:
        return

    if enemy_delay > 0:
        enemy_delay -= 1
        return

    if algorithm == "BFS":
        path, _ = bfs(enemy, player, grid)
    elif algorithm == "DFS":
        path, _ = dfs(enemy, player, grid)
    elif algorithm == "A*":
        path, _ = astar(enemy, player, grid)
    else:
        path, _ = hill_climbing(enemy, player, grid)

    if len(path) > 1:
        enemy = path[1]

    if enemy == player:
        hp -= 8
        set_message("THE AI HIT YOU! Keep moving!", 60)

    enemy_delay = 14

def calculate_ai():
    global path, explored
    if level == 1:
        path, explored = bfs(enemy, exit_pos, grid)
    elif level == 2:
        path, explored = dfs(enemy, exit_pos, grid)
    elif level == 3:
        path, explored = astar(enemy, exit_pos, grid)
    elif level == 4:
        path, explored = hill_climbing(player, exit_pos, grid)
    else:
        path, explored = astar(player, exit_pos, grid)

# ------------------------------------------------------------
# Rendering
# ------------------------------------------------------------

def draw_text(text, x, y, font=FONT, color=WHITE):
    screen.blit(font.render(str(text), True, color), (x, y))

def draw_bar(x, y, w, h, value, maximum, color):
    pygame.draw.rect(screen, (40, 45, 60), (x, y, w, h), border_radius=5)
    fill = int(w * max(0, min(value, maximum)) / maximum)
    pygame.draw.rect(screen, color, (x, y, fill, h), border_radius=5)

def draw_maze():
    # Search visualization
    for p in explored:
        x, y = cell_to_px(p)
        pygame.draw.rect(screen, (35, 55, 75), (x+4, y+4, CELL-8, CELL-8), border_radius=4)

    # A* / BFS path
    for p in path:
        x, y = cell_to_px(p)
        pygame.draw.rect(screen, (55, 90, 120), (x+9, y+9, CELL-18, CELL-18), border_radius=4)

    for y in range(ROWS):
        for x in range(COLS):
            px, py = cell_to_px((x, y))
            if grid[y][x] == 1:
                pygame.draw.rect(screen, WALL, (px, py, CELL, CELL), border_radius=4)
            else:
                pygame.draw.rect(screen, FLOOR, (px, py, CELL, CELL), border_radius=2)

    # Exit
    ex, ey = cell_to_px(exit_pos)
    exit_color = GREEN if door_open or level <= 3 else RED
    pygame.draw.rect(screen, exit_color, (ex+7, ey+7, CELL-14, CELL-14), border_radius=7)
    draw_text("X", ex+13, ey+7, FONT, BG)

    # Special center key
    if level <= 3 and keys == 0:
        kp = (COLS//2, ROWS//2)
        kx, ky = cell_to_px(kp)
        pygame.draw.circle(screen, YELLOW, (kx+20, ky+20), 10)
        pygame.draw.circle(screen, BG, (kx+20, ky+20), 5)

    # Player
    px, py = cell_to_px(player)
    pygame.draw.circle(screen, CYAN, (px+20, py+20), 14)
    pygame.draw.circle(screen, WHITE, (px+15, py+16), 3)
    pygame.draw.circle(screen, WHITE, (px+25, py+16), 3)

    # Enemy
    if level <= 3:
        ex, ey = cell_to_px(enemy)
        pygame.draw.rect(screen, RED, (ex+7, ey+7, CELL-14, CELL-14), border_radius=9)
        draw_text("AI", ex+8, ey+10, SMALL, WHITE)

def draw_header():
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 80))
    draw_text("AI DUNGEON", 25, 18, TITLE, CYAN)

    name = level_info[level][1]
    draw_text(name, 350, 18, BIG, WHITE)

    draw_text(f"SCORE {score}", 850, 18, FONT, YELLOW)
    draw_text(f"LEVEL {level}/5", 850, 45, FONT, GREEN)

def draw_side_panel():
    x = 850
    y = 100

    pygame.draw.rect(screen, PANEL, (x, y, 230, 560), border_radius=12)

    draw_text("AI CONTROL", x+18, y+18, BIG, CYAN)

    draw_text(f"ALGORITHM: {algorithm}", x+18, y+65, FONT, YELLOW)

    if algorithm == "BFS":
        desc = "Breadth First\nShortest path"
    elif algorithm == "DFS":
        desc = "Depth First\nDeep exploration"
    elif algorithm == "A*":
        desc = "A* Search\nf(n)=g(n)+h(n)"
    elif algorithm == "CSP":
        desc = "Constraint\nSatisfaction"
    else:
        desc = "MINIMAX\nGame playing"

    yy = y + 100
    for line in desc.split("\n"):
        draw_text(line, x+18, yy, SMALL, WHITE)
        yy += 22

    pygame.draw.line(screen, WALL, (x+15, yy+12), (x+215, yy+12), 2)

    draw_text("PLAYER", x+18, yy+30, FONT, CYAN)
    draw_text(f"HP: {hp}", x+18, yy+58, SMALL)
    draw_bar(x+18, yy+80, 190, 12, hp, 100, RED)

    draw_text(f"ENERGY: {energy}", x+18, yy+105, SMALL)
    draw_bar(x+18, yy+127, 190, 12, energy, 100, CYAN)

    draw_text(f"KEYS: {keys}", x+18, yy+155, SMALL, YELLOW)

    pygame.draw.line(screen, WALL, (x+15, yy+188), (x+215, yy+188), 2)

    draw_text("CONTROLS", x+18, yy+205, FONT, GREEN)
    controls = [
        "Arrow / WASD = Move",
        "SPACE = Show AI path",
        "R = Restart level",
        "1-5 = Jump level",
        "ESC = Quit",
    ]
    cy = yy + 238
    for line in controls:
        draw_text(line, x+18, cy, SMALL)
        cy += 25

def draw_logic_panel():
    if level != 4:
        return

    x, y = 55, 610
    pygame.draw.rect(screen, PANEL, (x, y, 760, 75), border_radius=10)

    draw_text("CSP / LOGIC VAULT", x+15, y+8, FONT, PURPLE)
    draw_text("NORTH = RED KEY   |   EAST = GOLD KEY   |   WEST = BLUE KEY",
              x+15, y+32, SMALL, WHITE)

    if logic_solved:
        draw_text("✓ Constraints satisfied — EXIT UNLOCKED", x+15, y+53, SMALL, GREEN)
    else:
        draw_text("Reach the center chamber to validate the constraints.",
                  x+15, y+53, SMALL, YELLOW)

def draw_boss():
    if level != 5:
        return

    # Overlay boss arena
    pygame.draw.rect(screen, (18, 15, 30), (850, 100, 230, 560), border_radius=12)
    draw_text("AI OVERLORD", 865, 120, BIG, RED)

    pygame.draw.circle(screen, PURPLE, (965, 240), 70)
    pygame.draw.circle(screen, BG, (940, 225), 10)
    pygame.draw.circle(screen, BG, (990, 225), 10)

    draw_text("BOSS HP", 875, 335, FONT)
    draw_bar(875, 365, 180, 18, boss_hp, 100, PURPLE)

    draw_text("MINIMAX DECISION", 875, 410, SMALL, YELLOW)
    move = boss_choose_move(hp, boss_hp)
    draw_text(f"AI MOVE: {move}", 875, 435, FONT, RED)

    draw_text("A = ATTACK", 875, 485, SMALL)
    draw_text("D = DEFEND", 875, 510, SMALL)
    draw_text("H = HEAL", 875, 535, SMALL)
    draw_text("SPACE = AI ANALYSIS", 875, 560, SMALL, CYAN)

    draw_bar(875, 595, 180, 12, hp, 100, RED)

def draw_message():
    if message_timer > 0:
        pygame.draw.rect(screen, (20, 25, 40), (30, 55, 790, 36), border_radius=8)
        draw_text(message, 45, 64, SMALL, YELLOW)

# ------------------------------------------------------------
# Boss combat
# ------------------------------------------------------------

def player_boss_action(action):
    global boss_hp, hp, energy, score

    if action == "attack":
        damage = random.randint(10, 18)
        boss_hp -= damage
        energy = max(0, energy - 8)
        set_message(f"You attacked the AI for {damage} damage!", 90)

    elif action == "defend":
        energy = min(100, energy + 10)
        set_message("Defensive stance: energy restored.", 90)

    elif action == "heal":
        hp = min(100, hp + 15)
        energy = max(0, energy - 15)
        set_message("You restored 15 HP.", 90)

    if boss_hp <= 0:
        score += 2000
        set_message("AI OVERLORD DEFEATED! YOU WIN!", 400)
        return

    ai_move = boss_choose_move(hp, boss_hp)

    if ai_move == "ATTACK":
        damage = random.randint(8, 15)
        hp -= damage
        set_message(f"MINIMAX chose ATTACK. You lost {damage} HP.", 120)
    else:
        boss_hp = min(100, boss_hp + 6)
        set_message("MINIMAX chose DEFEND. Boss recovered 6 HP.", 120)

    if hp <= 0:
        set_message("GAME OVER! Press R to restart.", 300)

# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------

running = True
show_path = False

while running:
    dt = clock.tick(60)

    if message_timer > 0:
        message_timer -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_r:
                reset_level(level)

            elif event.key == pygame.K_SPACE:
                calculate_ai()
                show_path = True
                set_message(
                    f"{algorithm} analyzed {len(explored)} states and found "
                    f"a path of {len(path)} nodes.", 180
                )

            elif pygame.K_1 <= event.key <= pygame.K_5:
                reset_level(event.key - pygame.K_0)

            elif level == 5 and boss_hp > 0 and hp > 0:
                if event.key == pygame.K_a:
                    player_boss_action("attack")
                elif event.key == pygame.K_d:
                    player_boss_action("defend")
                elif event.key == pygame.K_h:
                    player_boss_action("heal")

    keys_pressed = pygame.key.get_pressed()

    # Movement
    if level != 5 and hp > 0:
        if move_delay > 0:
            move_delay -= 1
        else:
            dx = dy = 0
            if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
                dx = -1
            elif keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                dx = 1
            elif keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
                dy = -1
            elif keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
                dy = 1

            if dx or dy:
                move_player(dx, dy)
                move_delay = 7

        update_enemy()

    # Drawing
    screen.fill(BG)
    draw_header()
    draw_maze()

    if level == 5:
        draw_boss()

    draw_side_panel()
    draw_logic_panel()
    draw_message()

    # Footer
    draw_text(
        "AI LAB: Search Strategies • CSP • Logical Reasoning • Minimax",
        30, 690, SMALL, (150, 160, 185)
    )

    pygame.display.flip()

pygame.quit()
