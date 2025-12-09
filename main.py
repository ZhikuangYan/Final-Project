import pygame
import os
from os import listdir
from os.path import isfile, join

# ============================================================
# 2D Platformer Final Project
#
# Features:
# - Levels loaded from txt files (character maps)
# - Player movement, jumping, gravity, and collisions
# - Standard platforms, breakable blocks, and goal
# - Enemies (patrol left and right, turn around when hitting walls or platform edges)
# - Coin collection system + score summary screen
# - Three-heart health + brief invincibility after collisions
# ============================================================


# --- Basic parameters ---
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREY = (180, 180, 180)
GREEN = (0, 200, 0)       # default goal color
BROWN = (160, 100, 40)    # breakable block color

WIDTH = 960               # screen width
HEIGHT = 540              # screen height

# Tile size: one char in txt map = one grid cell
TILE_W = 50
TILE_H = 50

# Total level width in world coordinates
LEVEL_WIDTH = 0

PLAYER_MAX_HEALTH = 3           # player max HP
PLAYER_INVINCIBLE_FRAMES = 60   # invincibility frames (1s)

# 关卡内的全局状态
coin_count = 0          # coins collected
TOTAL_COINS = 0         # total coins in level

enemies = []            # list of Enemy 
coins = []              # list of Coin

# Physics parameters
GRAVITY = 0.5
JUMP_SPEED = -12
PLAYER_SPEED_X = 5

# --- Pygame init ---
pygame.init()
pygame.display.set_caption("2D platformer game")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Asset root dir ---
# Expected assets folder structure:
# assets/
#   Background/Blue.png
#   Terrain/tilemaps.png
#   MainCharacters/PinkMan/*.png
#   Enemy/Slime/idle.png
#   Items/coin.png
#   UI/heart_full.png, heart_empty.png, goal.png
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


# ============================================================
# Tile / Helper: image & tile loading
# ============================================================

def load_image(rel_path, size=None):
    img = pygame.image.load(os.path.join(ASSET_DIR, rel_path)).convert_alpha()
    if size is not None:
        img = pygame.transform.scale(img, size)
    return img


# ---UI sprites ---
COIN_SIZE = 32
COIN_IMG = load_image("Items/coin.png", (COIN_SIZE, COIN_SIZE))

HEART_SIZE = 50
HEART_FULL_IMG = load_image("UI/heart_full.png", (HEART_SIZE, HEART_SIZE))
HEART_EMPTY_IMG = load_image("UI/heart_empty.png", (HEART_SIZE, HEART_SIZE))

GOAL_IMG = load_image("UI/goal.png", (TILE_W, TILE_H))  # goal tile


# --- Terrain tiles ---
TERRAIN_SHEET_PATH = os.path.join(ASSET_DIR, "Terrain", "tilemaps.png")
TERRAIN_SHEET = pygame.image.load(TERRAIN_SHEET_PATH).convert_alpha()

# Size of one tile in the original tilemap image
SRC_TILE_W = 48
SRC_TILE_H = 48


def get_tile(col, row):
    """
    Cut one tile from TERRAIN_SHEET and scale to TILE_W x TILE_H.
    """
    surface = pygame.Surface((SRC_TILE_W, SRC_TILE_H), pygame.SRCALPHA, 32)
    rect = pygame.Rect(col * SRC_TILE_W, row * SRC_TILE_H,
                       SRC_TILE_W, SRC_TILE_H)
    surface.blit(TERRAIN_SHEET, (0, 0), rect)
    return pygame.transform.scale(surface, (TILE_W, TILE_H))


def get_floor_tile():
    # grass floor
    return get_tile(col=1.37, row=0) 


def get_platform_tile():
    # floating platform
    return get_tile(col=2.366, row=0)


def get_breakable_tile():
    # breakable block
    return get_tile(col=0, row=2)


def get_goal_tile():
    # goal
    return GOAL_IMG


def flip(sprites):
    """flip sprite list horizontally"""
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    """
    Load sprite sheets from assets/dir1/dir2 and slice into frames.

    - dir1, dir2: directory names under ASSET_DIR
    - width, height: frame size in source image
    - direction: left and right
    """
    path = join(ASSET_DIR, dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)

            # scale player frames to one tile
            scaled = pygame.transform.scale(surface, (TILE_W, TILE_H))
            sprites.append(scaled)

        name = image.replace(".png", "")
        if direction:
            all_sprites[name + "_right"] = sprites
            all_sprites[name + "_left"] = flip(sprites)
        else:
            all_sprites[name] = sprites

    return all_sprites


def load_slime_sprites():
    """
    Here the frames are not evenly spaced. We manually specify
    the (start_col, end_col) of each frame and crop them.

    return dict: {"idle_right": [...], "idle_left": [...]}
    """
    sheet_path = os.path.join(ASSET_DIR, "Enemy", "Slime", "idle.png")
    sheet = pygame.image.load(sheet_path).convert_alpha()
    h = sheet.get_height()

    # For each slime frame: (x_start, x_end)
    frame_cols = [
        (1, 15),      # frame 1
        (66, 78),     # frame 2
        (130, 142),   # frame 3
        (194, 206),   # frame 4
    ]

    sprites_right = []

    for x1, x2 in frame_cols:
        frame_w = x2 - x1 + 1
        surface = pygame.Surface((frame_w, h), pygame.SRCALPHA, 32)
        rect = pygame.Rect(x1, 0, frame_w, h)
        surface.blit(sheet, (0, 0), rect)

        # enemies also one tile big
        scaled = pygame.transform.scale(surface, (TILE_W, TILE_H))
        sprites_right.append(scaled)

    sprites_left = flip(sprites_right)

    return {
        "idle_right": sprites_right,
        "idle_left": sprites_left,
    }


# enemy sprite dict
ENEMY_SPRITES = load_slime_sprites()
ENEMY_BASE = "idle"


def get_background(name):
    """
    load and tile background image.
    retrun：[(x, y), ...], image
    """
    image = pygame.image.load(join(ASSET_DIR, "Background", name)).convert()
    _, _, w, h = image.get_rect()
    tiles = []
    for i in range(WIDTH // w + 2):
        for j in range(HEIGHT // h + 2):
            tiles.append((i * w, j * h))
    return tiles, image


# ============================================================
# Platform, Goal, Enemy, Coin classes
# ============================================================

class Platform:
    """
    Simple platform: a rect plus optional tile image.
    """

    def __init__(self, x, y, w, h, color=GREY, image=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.image = image

    def draw(self, surface, offset_x):
        """draw platform with camera offset"""
        draw_rect = self.rect.move(-offset_x, 0)
        if self.image:
            surface.blit(self.image, draw_rect)
        else:
            pygame.draw.rect(surface, self.color, draw_rect)


class BreakableBlock(Platform):
    """
    Breakable block: destroyed when hit from below by player.
    """

    def __init__(self, x, y, w, h, color=BROWN, image=None):
        if image is None:
            image = get_breakable_tile()
        super().__init__(x, y, w, h, color, image)


class Goal:
    """
    Goal: touching it completes the level.
    """

    def __init__(self, x, y, w, h, color=GREEN, image=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.image = image

    def draw(self, surface, offset_x):
        draw_rect = self.rect.move(-offset_x, 0)
        if self.image:
            img = pygame.transform.scale(
                self.image, (self.rect.width, self.rect.height)
            )
            surface.blit(img, draw_rect)
        else:
            pygame.draw.rect(surface, self.color, draw_rect)


class Enemy:
    """
    Simple enemy:
    - Affected by gravity, walks on platforms
    - Keeps moving horizontally
    - Turns around when hitting wall or platform edge
    """

    def __init__(self, x, y, w, h, speed=2):
        # physics rect
        self.rect = pygame.Rect(x, y, w, h)

        self.vx = -speed        # start moving left
        self.vy = 0
        self.speed = speed

        self.on_ground = False
        self.direction = "left"

        # animation
        self.animation_count = 0
        self.ANIMATION_DELAY = 5
        self.sprite = ENEMY_SPRITES["idle_left"][0]

    def apply_gravity(self):
        """apply gravity."""
        self.vy += GRAVITY
        if self.vy > 20:
            self.vy = 20

    def move_and_collide(self, platforms):
        """
        Enemy movement & collisions:
        - Vertical step then horizontal step
        """
        # vertical
        self.on_ground = False
        self.rect.y += self.vy

        for plat in platforms:
            if not self.rect.colliderect(plat.rect):
                continue

            if self.vy > 0:  # landing
                self.rect.bottom = plat.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:  
                self.rect.top = plat.rect.bottom
                self.vy = 0

        # Horizontal
        self.rect.x += self.vx
        hit_wall = False

        for plat in platforms:
            if not self.rect.colliderect(plat.rect):
                continue
            hit_wall = True
            if self.vx > 0:
                self.rect.right = plat.rect.left
            elif self.vx < 0:
                self.rect.left = plat.rect.right

        # Edge detection 
        if self.on_ground:
            # small probe in front of enemy
            if self.vx > 0:
                front_x = self.rect.right + 1
            else:
                front_x = self.rect.left - 1

            foot_y = self.rect.bottom + 1
            check_rect = pygame.Rect(front_x, foot_y, 2, 2)

            supported = False
            for plat in platforms:
                if check_rect.colliderect(plat.rect):
                    supported = True
                    break

            if not supported:
                hit_wall = True  # treat as wall

        # Turn around 
        if hit_wall:
            self.vx *= -1
            self.direction = "right" if self.vx > 0 else "left"

    def update_sprite(self):
        """update enemy sprite frame"""
        sheet_name = f"{ENEMY_BASE}_{self.direction}"  # "idle_left/right"
        sprites = ENEMY_SPRITES[sheet_name]
        index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[index]
        self.animation_count += 1

    def update(self, platforms):
        """update enemy each frame"""
        self.apply_gravity()
        self.move_and_collide(platforms)
        self.update_sprite()

    def draw(self, surface, offset_x):
        """draw enemy"""
        draw_x = self.rect.x - offset_x
        draw_y = self.rect.y + self.rect.height - self.sprite.get_height()
        surface.blit(self.sprite, (draw_x, draw_y))


class Coin:
    """
    Coin: disappears when collected by player
    """

    def __init__(self, x, y, image=None):
        self.image = image if image is not None else COIN_IMG
        w, h = self.image.get_width(), self.image.get_height()
        # rect centered at (x, y)
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)

    def draw(self, surface, offset_x):
        draw_rect = self.rect.move(-offset_x, 0)
        surface.blit(self.image, draw_rect)


# ============================================================
# Player class
# ============================================================

class Player(pygame.sprite.Sprite):
    """
    Player Character:
    - A / D for horizontal movement
    - Space to jump (only on the ground)
    - Affected by gravity and platform collisions
    - Can break bricks by hitting from below
    """

    def __init__(self, x, y, width, height):
        super().__init__()

        # physics rect
        self.rect = pygame.Rect(x, y, width, height)

        # animation & facing
        self.direction = "right"
        self.animation_count = 0
        self.ANIMATION_DELAY = 5

        # Load animation sequences
        self.SPRITES = load_sprite_sheets(
            "MainCharacters", "PinkMan", 32, 32, True
        )
        self.sprite = self.SPRITES["idle_right"][0]

        # Velocity
        self.vx = 0
        self.vy = 0

        self.on_ground = False

        self.health = PLAYER_MAX_HEALTH
        self.invincible_timer = 0

    def handle_input(self):
        """handle keyboard input"""
        keys = pygame.key.get_pressed()
        self.vx = 0

        if keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED_X
            self.direction = "left"
        if keys[pygame.K_d]:
            self.vx = PLAYER_SPEED_X
            self.direction = "right"

        # Can only jump when on the ground
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_SPEED
            self.on_ground = False

    def apply_gravity(self):
        """apply gravity to player"""
        self.vy += GRAVITY
        if self.vy > 20:
            self.vy = 20

    def move_and_collide(self, platforms):
        """
        Player collision handling (axis-separated):
        1. Move along the y first to handle vertical collisions (landing / hitting the ceiling / smashing blocks).
        2. Then move along the x to handle horizontal collisions (hitting walls).
        """

        # Vertical 
        self.on_ground = False
        self.rect.y += self.vy

        for plat in platforms[:]:
            if not self.rect.colliderect(plat.rect):
                continue

            if self.vy > 0:
                # landing on platform
                self.rect.bottom = plat.rect.top
                self.vy = 0
                self.on_ground = True

            elif self.vy < 0:
                # hit ceiling
                if isinstance(plat, BreakableBlock):
                    # destroy breakable block
                    platforms.remove(plat)
                    self.vy = 0
                else:
                    self.rect.top = plat.rect.bottom
                    self.vy = 0

        # Horizontal 
        self.rect.x += self.vx

        for plat in platforms:
            if not self.rect.colliderect(plat.rect):
                continue

            if self.vx > 0:
                self.rect.right = plat.rect.left
            elif self.vx < 0:
                self.rect.left = plat.rect.right

    def handle_horizontal_bounds(self):
        """keep player within level bounds"""
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH

    def update(self, platform_list):
        """main update per frame"""
        # decrease invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        self.handle_input()
        self.apply_gravity()
        self.move_and_collide(platform_list)
        self.handle_horizontal_bounds()
        self.update_sprite()

    def update_sprite(self):
        """pick animation based on velocity & state"""
        if not self.on_ground and self.vy < 0:
            sheet = "jump"
        elif not self.on_ground and self.vy > 0:
            sheet = "fall"
        elif self.vx != 0:
            sheet = "run"
        else:
            sheet = "idle"

        sheet_name = f"{sheet}_{self.direction}"
        sprites = self.SPRITES.get(sheet_name, self.SPRITES["idle_right"])
        index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[index]
        self.animation_count += 1

    def draw(self, surface, offset_x):
        """draw player"""
        draw_pos = (self.rect.x - offset_x, self.rect.y)
        surface.blit(self.sprite, draw_pos)


# ============================================================
# Scene & level loading
# ============================================================

platforms = []
goal = None


def load_level_from_txt(filename):
    """
    Read the level map from a txt file.  
    Each line represents a row of the map, with the characters meaning:  
    . Empty space  
    # Ground  
    P Floating platform  
    B Breakable brick  
    G Goal  
    E Enemy  
    C Coin
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, filename)

    with open(full_path, "r") as f:
        level_map = [line.rstrip("\n") for line in f]

    return level_map


def build_level_from_map(level_map):
    """
    Build platforms, enemies, coins, goal from char map
    """
    global platforms, goal, LEVEL_WIDTH
    global enemies, coins, coin_count, TOTAL_COINS

    rows = len(level_map)
    cols = len(level_map[0]) if rows > 0 else 0
    LEVEL_WIDTH = cols * TILE_W

    platforms = []
    enemies = []
    coins = []
    goal = None

    coin_count = 0
    TOTAL_COINS = 0

    for row_idx, row in enumerate(level_map):
        for col_idx, ch in enumerate(row):
            if ch == ".":
                continue

            x = col_idx * TILE_W
            # first line -> top of screen
            y = HEIGHT - (rows - row_idx) * TILE_H

            if ch == "#":
                floor_img = get_floor_tile()
                platforms.append(Platform(x, y, TILE_W, TILE_H, GREY, floor_img))

            elif ch == "P":
                plat_img = get_platform_tile()
                platforms.append(Platform(x, y, TILE_W, TILE_H, GREY, plat_img))

            elif ch == "B":
                platforms.append(BreakableBlock(x, y, TILE_W, TILE_H))

            elif ch == "G":
                goal_img = get_goal_tile()
                goal = Goal(x, y, TILE_W, TILE_H, image=goal_img)

            elif ch == "E":
                enemies.append(Enemy(x, y, TILE_W, TILE_H))

            elif ch == "C":
                coins.append(Coin(x + TILE_W // 2, y + TILE_H // 2))

    # count coins after loops
    TOTAL_COINS = len(coins)


LEVEL_MAP = load_level_from_txt("level1.txt")
build_level_from_map(LEVEL_MAP)
bg_tiles, bg_image = get_background("Blue.png")

player = Player(100, 150, TILE_W, TILE_H)

game_state = "PLAYING"  

# camera offset (horizontal only)
camera_offset_x = 0
SCROLL_AREA = 200  

font = pygame.font.SysFont(None, 36)


# ============================================================
# Camera & rendering
# ============================================================

def update_camera(player_rect, offset_x):
    """
    Keep player inside a scroll area; move camera when needed.
    """
    player_screen_x = player_rect.centerx - offset_x

    # scroll right
    if player_screen_x > WIDTH - SCROLL_AREA:
        offset_x += player_screen_x - (WIDTH - SCROLL_AREA)

    # scroll left
    if player_screen_x < SCROLL_AREA:
        offset_x -= SCROLL_AREA - player_screen_x

    # clamp offset
    offset_x = max(0, min(offset_x, LEVEL_WIDTH - WIDTH))

    return offset_x


def draw_scene():
    """draw the whole scene"""
    screen.fill(WHITE)

    # background
    for pos in bg_tiles:
        screen.blit(bg_image, pos)

    # platforms
    for plat in platforms:
        plat.draw(screen, camera_offset_x)

    # enemies
    for e in enemies:
        e.draw(screen, camera_offset_x)

    # coins
    for c in coins:
        c.draw(screen, camera_offset_x)

    # goal
    goal.draw(screen, camera_offset_x)

    # player
    player.draw(screen, camera_offset_x)

    # --- hearts ---
    for i in range(PLAYER_MAX_HEALTH):
        x = 10 + i * (HEART_SIZE + 5)
        y = 10
        if i < player.health:
            screen.blit(HEART_FULL_IMG, (x, y))
        else:
            screen.blit(HEART_EMPTY_IMG, (x, y))

    # coin counter in HUD
    coin_text = font.render(f"Coins: {coin_count}/{TOTAL_COINS}", True, (0, 0, 0))
    screen.blit(coin_text, (10, 50))

    # --- status screens ---
    if game_state == "START_MENU":
        title = font.render("2D Platformer", True, (0, 0, 0))
        tip = font.render("Press ENTER to start", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 3 + 50))

    elif game_state == "GAME_OVER":
        over = font.render("Game Over!", True, (200, 0, 0))
        tip = font.render("Press R to restart", True, (0, 0, 0))
        screen.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 3))
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT // 3 + 50))

    elif game_state == "LEVEL_COMPLETE":
        # Rating: 1~3 stars based on coin ratio
        if TOTAL_COINS == 0:
            stars = 3
        else:
            ratio = coin_count / TOTAL_COINS
            if ratio > 0.66:
                stars = 3
            elif ratio > 0.33:
                stars = 2
            else:
                stars = 1

        msg = font.render("Level Complete!", True, (0, 0, 0))
        rating = font.render(f"Rating: {stars}/3", True, (255, 165, 0))
        tip = font.render("Press R to restart, ESC to quit", True, (0, 0, 0))

        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 3))
        screen.blit(rating, (WIDTH // 2 - rating.get_width() // 2,
                             HEIGHT // 3 + 40))
        screen.blit(tip, (WIDTH // 2 - tip.get_width() // 2,
                          HEIGHT // 3 + 80))

    pygame.display.update()


# ============================================================
# Main game loop
# ============================================================

running = True
while running:
    clock.tick(FPS)

    # event handling 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # state machine
    if game_state == "START_MENU":
        # start menu
        if keys[pygame.K_RETURN]:
            game_state = "PLAYING"

    elif game_state == "GAME_OVER":
        # restart on R
        if keys[pygame.K_r]:
            build_level_from_map(LEVEL_MAP)
            player = Player(100, 150, TILE_W, TILE_H)
            camera_offset_x = 0
            game_state = "PLAYING"

    elif game_state == "LEVEL_COMPLETE":
        # restart on R
        if keys[pygame.K_r]:
            build_level_from_map(LEVEL_MAP)
            player = Player(100, 150, TILE_W, TILE_H)
            camera_offset_x = 0
            game_state = "PLAYING"

    # main gameplay 
    if game_state == "PLAYING":
        # update player
        player.update(platforms)

        # update enemies
        for e in enemies:
            e.update(platforms)

        # coin collection
        for c in coins[:]:
            if player.rect.colliderect(c.rect):
                coins.remove(c)
                coin_count += 1

        # damage from enemy
        for e in enemies:
            if player.rect.colliderect(e.rect) and player.invincible_timer == 0:
                player.health -= 1
                player.invincible_timer = PLAYER_INVINCIBLE_FRAMES
                if player.health <= 0:
                    game_state = "GAME_OVER"
                    break
        
        if player.rect.top > HEIGHT + 200:  
            game_state = "GAME_OVER"


        # update camera
        camera_offset_x = update_camera(player.rect, camera_offset_x)

        # check goal
        if player.rect.colliderect(goal.rect):
            game_state = "LEVEL_COMPLETE"

    # render one frame
    draw_scene()

pygame.quit()
