import pygame
import os

FPS = 60
white = (255,255,255)
BLUE = (0,0,255)
GREY = (180, 180, 180)
GREEN = (0, 200, 0)     # goal color
BROWN = (160, 100, 40)   # breakable block color

# Screen size
WIDTH = 960
HEIGHT = 540

# Tile size (one char in txt = one tile)
TILE_W = 50
TILE_H = 50

LEVEL_WIDTH = 0  # Total level width

GRAVITY = 0.5
JUMP_SPEED = -12
PLAYER_SPEED_X = 5

pygame.init()
pygame.display.set_caption("2D platform game")
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

class Platform:
    """
    Simple platform class: wraps a rect and draw method for future extension
    """
    def __init__(self, x, y, w, h, color=GREY):
        # Note: rect.x here is in *world coordinates*, can be > WIDTH
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, surface, offset_x):
        """
        Draw platform using camera offset
        """
        draw_rect = self.rect.move(-offset_x, 0)
        pygame.draw.rect(surface, self.color, draw_rect)

class BreakableBlock(Platform):
    """
    Breakable block that can be destroyed when hit from below
    """
    def __init__(self, x, y, w, h, color=BROWN):
        super().__init__(x, y, w, h, color)

class Goal:
    """
    Goal class: when the player touches it, game is complete
    """
    def __init__(self, x, y, w, h, color=GREEN):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, surface, offset_x):
        draw_rect = self.rect.move(-offset_x, 0)
        pygame.draw.rect(surface, self.color, draw_rect)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Player rect in world coordinates
        self.rect = pygame.Rect(x, y, width, height)

        # Horizontal & vertical velocity
        self.vx = 0
        self.vy = 0

        self.on_ground = False

    def handle_input(self):
        """
        keyboard input: A/D move, SPACE jump
        """
        keys = pygame.key.get_pressed()
        self.vx = 0

        if keys[pygame.K_a]:
            self.vx = -PLAYER_SPEED_X
        if keys[pygame.K_d]:
            self.vx = PLAYER_SPEED_X

        # Only allow jumping when on the ground
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_SPEED
            self.on_ground = False

    def apply_gravity(self):
        """
        Apply gravity
        """
        self.vy += GRAVITY
        if self.vy > 20:
            self.vy = 20

    def move_and_collide(self, platforms):
        """
        Core: axis-separated collision
        1. Move in y and resolve vertical collisions (ground / head / break block)
        2. Move in x and resolve horizontal collisions (walls)
        """
        
        self.on_ground = False
        self.rect.y += self.vy

        for plat in platforms[:]:
            if not self.rect.colliderect(plat.rect):
                continue
                
            # Falling down: land on top (both normal and breakable act as ground)
            if self.vy > 0:
                self.rect.bottom = plat.rect.top
                self.vy = 0
                self.on_ground = True

            # Moving up: hit platform bottom or break block
            elif self.vy < 0:
                # If it's a breakable block: remove it
                if isinstance(plat, BreakableBlock):
                    platforms.remove(plat)
                    self.vy = 0
                else:
                    # Normal platform: block the head
                    self.rect.top = plat.rect.bottom
                    self.vy = 0

        self.rect.x += self.vx

        for plat in platforms:
            if not self.rect.colliderect(plat.rect):
                continue

            if self.vx > 0:
                # Moving right, hit left side
                self.rect.right = plat.rect.left
            elif self.vx < 0:
                # Moving left, hit right side
                self.rect.left = plat.rect.right

    def handle_horizontal_bounds(self):
        """
        Keep player inside level bounds (0 ~ LEVEL_WIDTH)
        """
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH

    def update(self, platform_list):
        """
        Update player each frame
        """
        self.handle_input()
        self.apply_gravity()
        self.move_and_collide(platform_list)
        self.handle_horizontal_bounds()

    def draw(self, surface, offset_x):
        """
        Draw player using camera offset
        """
        draw_rect = self.rect.move(-offset_x, 0)
        pygame.draw.rect(surface, BLUE, draw_rect)

# Scene setup
platforms = []
goal = None

def load_level_from_txt(filename):
    # Find main.py
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, filename)

    with open(full_path, "r") as f:
        level_map = [line.rstrip("\n") for line in f]

    return level_map

def build_level_from_map(level_map):
    global platforms, goal, LEVEL_WIDTH

    rows = len(level_map)
    cols = len(level_map[0])
    LEVEL_WIDTH = cols * TILE_W

    platforms = []
    goal = None

    for row_idx, row in enumerate(level_map):
        for col_idx, ch in enumerate(row):
            if ch == ".":
                continue

            x = col_idx * TILE_W
            y = HEIGHT - (rows - row_idx) * TILE_H 

            if ch == "#":
                platforms.append(Platform(x, y, TILE_W, TILE_H))

            elif ch == "B":
                platforms.append(BreakableBlock(x, y, TILE_W, TILE_H))

            elif ch == "G":
                goal_w, goal_h = TILE_W // 2, TILE_H // 2
                goal_x = x + (TILE_W - goal_w) // 2
                goal_y = y + (TILE_H - goal_h) // 2
                goal = Goal(goal_x, goal_y, goal_w, goal_h)

# Build level first
LEVEL_MAP = load_level_from_txt("level1.txt")
build_level_from_map(LEVEL_MAP)

# Then create player and other states
player = Player(100, 150, 50, 70)

game_state = "PLAYING"

camera_offset_x = 0

SCROLL_AREA = 200

font = pygame.font.SysFont(None, 36)


def update_camera(player_rect, offset_x):
    """
    Update camera offset based on player position so that the player
    stays roughly within a scroll area of the screen.
    """

    # Player's on-screen position = world position - offset_x
    player_screen_x = player_rect.centerx - offset_x

    # Scroll right if player near right edge and not at end of level
    if player_screen_x > WIDTH - SCROLL_AREA:
        offset_x += player_screen_x - (WIDTH - SCROLL_AREA)

    # Scroll left if player near left edge and offset_x > 0
    if player_screen_x < SCROLL_AREA:
        offset_x -= SCROLL_AREA - player_screen_x

    # Clamp offset between [0, LEVEL_WIDTH - WIDTH]
    offset_x = max(0, min(offset_x, LEVEL_WIDTH - WIDTH))

    return offset_x


def draw_scene():
    """
    Draw the whole scene:
    """
    screen.fill(white)

    # Draw platforms
    for plat in platforms:
        plat.draw(screen, camera_offset_x)

    # Draw goal
    goal.draw(screen, camera_offset_x)

    # Draw player
    player.draw(screen, camera_offset_x)

    if game_state == "LEVEL_COMPLETE":
        text = font.render("Level Complete! Press ESC to quit.",
                           True, (0, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))

    pygame.display.update()


# Main game loop

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    if game_state == "PLAYING":
        player.update(platforms)

        camera_offset_x = update_camera(player.rect, camera_offset_x)

        if player.rect.colliderect(goal.rect):
            game_state = "LEVEL_COMPLETE"

    draw_scene()

pygame.quit()
