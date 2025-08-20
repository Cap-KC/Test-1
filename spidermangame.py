import pygame, random, math

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spider-Man Swing Game")

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
GRAY = (50, 50, 50)

# Load images
spiderman_img = pygame.image.load("spiderman.png").convert_alpha()
spiderman_img = pygame.transform.scale(spiderman_img, (40, 40))

coin_img = pygame.image.load("coin.png").convert_alpha()
coin_img = pygame.transform.scale(coin_img, (20, 20))

bg_img = pygame.image.load("background.png").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

# Clock
clock = pygame.time.Clock()

# Player
player_pos = [100, 300]
player_vel = [0, 0]
gravity = 0.5
move_speed = 3
friction = 0.9
on_ground = False

# Rope
rope_active = False
rope_anchor = None

# Buildings + Coins
buildings = []
coins = []
camera_x = 0
level = 1
coins_collected = 0

font = pygame.font.SysFont(None, 36)

def generate_buildings():
    global buildings
    buildings = []
    x = 0
    for _ in range(10):
        w = random.randint(80, 120)
        h = random.randint(150, 400)
        y = HEIGHT - h
        buildings.append(pygame.Rect(x, y, w, h))
        x += w + random.randint(50, 100)

def generate_coins():
    global coins
    coins = []
    for b in buildings:
        cx = b.centerx
        cy = b.top - 40
        coins.append(pygame.Rect(cx, cy, 20, 20))

generate_buildings()
generate_coins()

# Game Over screen
def game_over_screen():
    screen.fill((0, 0, 0))
    font_big = pygame.font.SysFont(None, 72)
    text = font_big.render("GAME OVER", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
    screen.blit(text, text_rect)
    info_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    info_rect = info_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
    screen.blit(info_text, info_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    return False

# Main loop
running = True
while running:
    clock.tick(60)
    screen.blit(bg_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            rope_active = True
            rope_anchor = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONUP:
            rope_active = False
            rope_anchor = None

    keys = pygame.key.get_pressed()

    # Movement only when on ground
    if on_ground:
        if keys[pygame.K_a]:
            player_vel[0] -= move_speed
        if keys[pygame.K_d]:
            player_vel[0] += move_speed

    # Gravity
    player_vel[1] += gravity

    # Rope physics
    if rope_active and rope_anchor:
        dx = rope_anchor[0] - player_pos[0]
        dy = rope_anchor[1] - player_pos[1]
        dist = math.hypot(dx, dy)
        if dist > 5:
            player_vel[0] += dx / dist * 0.3
            player_vel[1] += dy / dist * 0.3

    # Apply movement
    player_pos[0] += player_vel[0]
    player_pos[1] += player_vel[1]
    player_vel[0] *= friction

    player_rect = spiderman_img.get_rect(center=player_pos)

    # Collision with buildings
    on_ground = False
    for b in buildings:
        if player_rect.colliderect(b):
            player_pos[1] = b.top - 20
            player_vel[1] = 0
            on_ground = True
            break

    # Collect coins
    for c in coins[:]:
        if player_rect.colliderect(c):
            coins.remove(c)
            coins_collected += 1

    # Draw rope
    if rope_active and rope_anchor:
        pygame.draw.line(screen, WHITE, player_pos, rope_anchor, 2)

    # Draw buildings
    for b in buildings:
        pygame.draw.rect(screen, GRAY, b.move(-camera_x, 0))

    # Draw coins
    for c in coins:
        screen.blit(coin_img, c.move(-camera_x, 0))

    # Draw player
    screen.blit(spiderman_img, player_rect.move(-camera_x, 0))

    # Update camera
    if player_pos[0] - camera_x > WIDTH // 2:
        camera_x = player_pos[0] - WIDTH // 2

    # Next level
    if player_pos[0] - camera_x > buildings[-1].x:
        level += 1
        generate_buildings()
        generate_coins()
        camera_x = 0
        player_pos = [100, 300]

    # Game Over if falls
    if player_pos[1] > HEIGHT:
        restart = game_over_screen()
        if restart:
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
        continue

    # Score
    score_text = font.render(f"Coins: {coins_collected}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()
