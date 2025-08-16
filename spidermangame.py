import pygame
import math
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spider-Man Swing")

font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# Load graphics
background = pygame.image.load("city_background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

spiderman_img = pygame.image.load("spiderman.png").convert_alpha()
spiderman_img = pygame.transform.scale(spiderman_img, (50, 50))

# Game variables
gravity = 0.5
move_speed = 0.5
friction = 0.98

# Player variables
player_pos = [200, 300]
player_vel = [0, 0]

# Rope variables
rope_anchor = None
rope_length = 0
rope_active = False

# Buildings list
buildings = []

# Coins list: list of pygame.Rect for coin hitboxes and positions
coins = []

# Level variables
level = 1
level_width = 3000  # distance in pixels
camera_x = 0

def generate_buildings():
    """Create a list of random buildings for the current level."""
    global buildings
    buildings = []
    x = 0
    while x < level_width:
        w = random.randint(100, 200)  # width
        h = random.randint(50, 200)   # height
        y = HEIGHT - h
        buildings.append(pygame.Rect(x, y, w, h))
        x += w + random.randint(50, 150)

def generate_coins():
    """Place coins randomly on top of some buildings."""
    global coins
    coins = []
    for b in buildings:
        if random.random() < 0.4:  # 40% chance to have a coin on this building
            coin_x = random.randint(b.x + 10, b.x + b.width - 20)
            coin_y = b.y - 20
            coins.append(pygame.Rect(coin_x, coin_y, 15, 15))

def draw_buildings():
    """Draw all buildings shifted by camera position."""
    for b in buildings:
        pygame.draw.rect(screen, (60, 60, 60), (b.x - camera_x, b.y, b.width, b.height))

def draw_coins():
    """Draw all coins shifted by camera position."""
    for c in coins:
        pygame.draw.circle(screen, (255, 223, 0), (c.x + 7 - camera_x, c.y + 7), 7)

def draw_rope():
    """Draw rope from player to anchor."""
    if rope_active and rope_anchor:
        pygame.draw.line(screen, (255, 255, 255), (player_pos[0] - camera_x, player_pos[1]), 
                         (rope_anchor[0] - camera_x, rope_anchor[1]), 2)

def draw_coin_count(count):
    text = font.render(f"Coins: {count}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def game_over_screen():
    screen.fill((0, 0, 0))
    font_big = pygame.font.SysFont(None, 72)
    text = font_big.render("GAME OVER", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
    screen.blit(text, text_rect)
    info_text = font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
    info_rect = info_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
    screen.blit(info_text, info_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                return False  # quit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    return True  # restart game
                if event.key == pygame.K_q:
                    waiting = False
                    return False  # quit game

# Initial setup
generate_buildings()
generate_coins()

coins_collected = 0

running = True
while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Shoot web
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            rope_anchor = (pygame.mouse.get_pos()[0] + camera_x, pygame.mouse.get_pos()[1])
            dx = rope_anchor[0] - player_pos[0]
            dy = rope_anchor[1] - player_pos[1]
            rope_length = math.sqrt(dx**2 + dy**2)
            rope_active = True

        # Release web
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            rope_active = False
            rope_anchor = None

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and not keys[pygame.K_d]:
        player_vel[0] -= move_speed
    elif keys[pygame.K_d] and not keys[pygame.K_a]:
        player_vel[0] += move_speed
    if keys[pygame.K_q]:  # Quit option
        running = False

    # Apply gravity
    player_vel[1] += gravity

    # Rope physics
    if rope_active and rope_anchor:
        dx = rope_anchor[0] - player_pos[0]
        dy = rope_anchor[1] - player_pos[1]
        dist = math.sqrt(dx**2 + dy**2)

        if dist != 0:
            diff = (dist - rope_length) / dist
            player_pos[0] += dx * diff
            player_pos[1] += dy * diff

            # Swing force
            angle = math.atan2(dy, dx)
            player_vel[0] += math.cos(angle + math.pi / 2) * 0.1
            player_vel[1] += math.sin(angle + math.pi / 2) * 0.1

    # Update position
    player_pos[0] += player_vel[0]
    player_pos[1] += player_vel[1]

    # Clamp player position so he can't go past level width (right edge)
    if player_pos[0] > level_width - 15:
        player_pos[0] = level_width - 15
        player_vel[0] = 0

    # Check for falling off screen (game over)
    if player_pos[1] > HEIGHT:
        restart = game_over_screen()
        if restart:
            # Reset game state
            player_pos = [100, 300]
            player_vel = [0, 0]
            coins_collected = 0
            level = 1
            camera_x = 0
            generate_buildings()
            generate_coins()
            rope_active = False
            rope_anchor = None
        else:
            running = False
        continue  # Skip rest of loop this frame

    # Collision with buildings
    player_rect = pygame.Rect(player_pos[0] - 15, player_pos[1] - 15, 30, 30)
    for b in buildings:
        if player_rect.colliderect(b):
            player_pos[1] = b.top - 15
            player_vel[1] = 0

    # Collect coins
    for coin in coins[:]:
        if player_rect.colliderect(coin):
            coins.remove(coin)
            coins_collected += 1

    # Friction only on horizontal velocity
    player_vel[0] *= friction

    # Camera follows player
    camera_x = max(0, player_pos[0] - WIDTH // 2)

    # Draw everything
    draw_buildings()
    draw_coins()
    draw_rope()
    screen.blit(spiderman_img, (player_pos[0] - 25 - camera_x, player_pos[1] - 25))
    draw_coin_count(coins_collected)

    # Level progression after collecting all coins or crossing level edge
    if len(coins) == 0 or player_pos[0] >= level_width - 15:
        level += 1
        player_pos = [100, 300]
        camera_x = 0
        coins_collected = 0
        generate_buildings()
        generate_coins()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
