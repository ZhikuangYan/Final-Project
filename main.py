import pygame

FPS = 60
white = (255,255,255)
BLUE = (0,0,255)
GREY = (180, 180, 180)
WIDTH = 960
HEIGHT = 540

GRAVITY = 0.5
JUMP_SPEED = -12
PLAYER_SPEED_X = 5

pygame.init()
pygame.display.set_caption("2D platform game")
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

platforms = []

# Ground platform
ground_rect = pygame.Rect(0, HEIGHT - 40, WIDTH, 40)
platforms.append(ground_rect)

# Float platform
mid_platform = pygame.Rect(300, 350, 300, 30)
platforms.append(mid_platform)

class Player(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.speed_x = PLAYER_SPEED_X
        self.v_y = 0
        self.on_ground = False
    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Move left and right
        if keys[pygame.K_a]:
            self.rect.x -= self.speed_x
        if keys[pygame.K_d]:
            self.rect.x += self.speed_x

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.v_y = JUMP_SPEED
            self.on_ground = False

    def apply_gravity(self):
        # Add gravity
        self.v_y += GRAVITY
        if self.v_y > 20:   
            self.v_y = 20

        self.rect.y += self.v_y

    def check_collisions(self, platform_list):
        self.on_ground = False

        for plat in platform_list:
            if self.rect.colliderect(plat):
                if self.v_y > 0 and self.rect.bottom > plat.top:
                    self.rect.bottom = plat.top
                    self.v_y = 0
                    self.on_ground = True

    def update(self, platform_list):
        self.handle_input()
        self.apply_gravity()
        self.check_collisions(platform_list)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def draw(self,screen):
        pygame.draw.rect(screen,BLUE,self.rect)

running =True
player = Player(100,150,50,70)

while running:
    clock.tick(FPS)

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False
            break

    player.update(platforms)  
    screen.fill(white)

    # Draw platform
    for plat in platforms:
        pygame.draw.rect(screen, GREY, plat)

    player.draw(screen)
    pygame.display.update()

pygame.quit()
