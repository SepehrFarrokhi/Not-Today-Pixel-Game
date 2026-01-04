import pygame
import math
import sys

# ---------- SETUP ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Shooter")
clock = pygame.time.Clock()

# ---------- COLORS ----------
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (200, 50, 50)

# ---------- PLAYER ----------
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_speed = 5
player_radius = 15

# ---------- BULLETS ----------
bullets = []
bullet_speed = 10
bullet_radius = 4

# ---------- MAIN LOOP ----------
running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    # ---------- EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            direction = pygame.Vector2(mouse_pos) - player_pos
            if direction.length() != 0:
                direction = direction.normalize()
                bullets.append({
                    "pos": player_pos.copy(),
                    "dir": direction
                })

    # ---------- INPUT ----------
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= player_speed
    if keys[pygame.K_s]:
        player_pos.y += player_speed
    if keys[pygame.K_a]:
        player_pos.x -= player_speed
    if keys[pygame.K_d]:
        player_pos.x += player_speed

    # ---------- UPDATE BULLETS ----------
    for bullet in bullets:
        bullet["pos"] += bullet["dir"] * bullet_speed

    bullets = [
        b for b in bullets
        if 0 < b["pos"].x < WIDTH and 0 < b["pos"].y < HEIGHT
    ]

    # ---------- DRAW ----------
    pygame.draw.circle(screen, WHITE, player_pos, player_radius)

    for bullet in bullets:
        pygame.draw.circle(screen, RED, bullet["pos"], bullet_radius)

    pygame.display.flip()

pygame.quit()
sys.exit()
