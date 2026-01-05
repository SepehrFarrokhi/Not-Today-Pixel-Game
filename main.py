import pygame
import math
import sys
import random

# --- CONFIGURATION & CONSTANTS ---
WIDTH, HEIGHT = 800, 600
WHITE, BLACK, RED, YELLOW, GREEN = (255, 255, 255), (20, 20, 20), (200, 50, 50), (255, 255, 0), (50, 200, 50)
GRAY, PURPLE, CYAN, ORANGE = (50, 50, 50), (150, 0, 150), (0, 255, 255), (255, 165, 0)

GAME_MENU, GAME_LOADING, GAME_PLAYING, GAME_PAUSED, GAME_SHOP, GAME_WIN = range(6)

# --- INITIALIZATION ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NOT TODAY!")
clock = pygame.time.Clock()
font_big = pygame.font.SysFont(None, 80)
font_mid = pygame.font.SysFont(None, 50)
font_small = pygame.font.SysFont(None, 28)

# --- GAME STATE ---
game = {
    "state": GAME_MENU,
    "score": 0,
    "phase": 1,
    "max_phases": 10,
    "shake_timer": 0,
    "shake_intensity": 5,
    "loading_timer": 0,
    "loading_duration": 7000,
    "phase_card_timer": 0,
    "phase_card_duration": 2000
}

player = {
    "pos": pygame.Vector2(WIDTH // 2, HEIGHT // 2),
    "speed": 5,
    "max_speed": 12,
    "radius": 15,
    "health": 100,
    "max_health": 100,
    "last_hit": 0,
    "hit_flash": 0,
    "weapon": "pistol",
    "triple_unlocked": False,
    "missile_unlocked": False,
    "vampire_unlocked": False,
    "nova_unlocked": False,
    "last_shot": 0,
    "last_missile": 0,
    "last_nova": 0
}

boss = {
    "active": False,
    "intro": False,
    "pos": pygame.Vector2(WIDTH // 2, -40),
    "health": 200,
    "max_health": 200,
    "speed": 1.5,
    "radius": 40,
    "state_timer": 0,
    "hit_flash": 0,
    "bombs": [],
    "strikes": []
}

# Entities
enemies = []
bullets = []
missiles = []
particles = []
enemy_hit_flash = {}

# Constants for tuning
COOLDOWNS = {"pistol": 300, "shotgun": 600, "triple": 400, "missile": 2000, "nova": 5000, "damage": 500}
bullet_speed, bullet_radius, enemy_radius, enemy_speed = 10, 4, 12, 2

# --- SOUNDS ---
try:
    snd_shoot = pygame.mixer.Sound("sounds/shoot.wav")
    snd_hit = pygame.mixer.Sound("sounds/hit.wav")
    snd_death = pygame.mixer.Sound("sounds/death.wav")
    snd_boss = pygame.mixer.Sound("sounds/boss.wav")
    pygame.mixer.music.load("sounds/music.mp3")
    pygame.mixer.music.play(-1)
except:
    snd_shoot = snd_hit = snd_death = snd_boss = None

# --- HELPER FUNCTIONS ---
def reset_game():
    game["score"], game["phase"], game["state"] = 0, 1, GAME_MENU
    player["health"] = player["max_health"]
    player["pos"] = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    boss["active"] = False
    enemies.clear(); bullets.clear(); missiles.clear(); particles.clear()
    boss["bombs"].clear(); boss["strikes"].clear()

def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top": pos = pygame.Vector2(random.randint(0, WIDTH), -enemy_radius)
    elif side == "bottom": pos = pygame.Vector2(random.randint(0, WIDTH), HEIGHT + enemy_radius)
    elif side == "left": pos = pygame.Vector2(-enemy_radius, random.randint(0, HEIGHT))
    else: pos = pygame.Vector2(WIDTH + enemy_radius, random.randint(0, HEIGHT))
    enemies.append(pos)

def create_particles(pos, color, count=5, speed=3):
    for _ in range(count):
        particles.append({
            "pos": pygame.Vector2(pos), 
            "vel": pygame.Vector2(random.uniform(-speed, speed), random.uniform(-speed, speed)), 
            "life": 300, "col": color
        })

# --- MAIN LOOP ---
running, last_spawn_time = True, 0

while running:
    dt = clock.tick(60)
    now = pygame.time.get_ticks()
    screen.fill(BLACK)
    
    # Screen Shake
    offset = pygame.Vector2(0, 0)
    if game["shake_timer"] > 0:
        game["shake_timer"] -= dt
        offset = pygame.Vector2(random.randint(-game["shake_intensity"], game["shake_intensity"]), 
                                random.randint(-game["shake_intensity"], game["shake_intensity"]))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.KEYDOWN:
            if game["state"] == GAME_MENU and event.key == pygame.K_SPACE:
                game["state"], game["loading_timer"] = GAME_LOADING, now
            elif game["state"] == GAME_PLAYING and event.key == pygame.K_p:
                game["state"] = GAME_PAUSED
            elif game["state"] == GAME_PAUSED and event.key == pygame.K_p:
                game["state"] = GAME_PLAYING
            
            # Shop logic
            if game["state"] == GAME_SHOP:
                if event.key == pygame.K_h and game["score"] >= 20:
                    game["score"] -= 20; player["health"] = player["max_health"]
                if event.key == pygame.K_s and game["score"] >= 30 and player["speed"] < player["max_speed"]:
                    game["score"] -= 30; player["speed"] += 1
                if event.key == pygame.K_l and game["score"] >= 60:
                    game["score"] -= 60; player["max_health"] += 25; player["health"] = player["max_health"]
                if event.key == pygame.K_t and game["score"] >= 50 and not player["triple_unlocked"]:
                    game["score"] -= 50; player["triple_unlocked"] = True
                if event.key == pygame.K_m and game["score"] >= 100 and not player["missile_unlocked"]:
                    game["score"] -= 100; player["missile_unlocked"] = True
                if event.key == pygame.K_v and game["score"] >= 80 and not player["vampire_unlocked"]:
                    game["score"] -= 80; player["vampire_unlocked"] = True
                if event.key == pygame.K_n and game["score"] >= 110 and not player["nova_unlocked"]:
                    game["score"] -= 110; player["nova_unlocked"] = True
                if event.key == pygame.K_SPACE:
                    game["state"], game["phase_card_timer"] = GAME_PLAYING, now

            # Weapon Swapping
            if event.key == pygame.K_1: player["weapon"] = "pistol"
            if event.key == pygame.K_2: player["weapon"] = "shotgun"
            if event.key == pygame.K_3 and player["triple_unlocked"]: player["weapon"] = "triple"
            
            # Nova Ability
            if game["state"] == GAME_PLAYING and event.key == pygame.K_SPACE and player["nova_unlocked"]:
                if now - player["last_nova"] > COOLDOWNS["nova"]:
                    for i in range(0, 360, 20):
                        bullets.append({"pos": player["pos"].copy(), "dir": pygame.Vector2(1, 0).rotate(i), "color": CYAN})
                    player["last_nova"], game["shake_timer"] = now, 300

        if event.type == pygame.MOUSEBUTTONDOWN and game["state"] == GAME_PLAYING:
            cd = COOLDOWNS[player["weapon"]]
            if now - player["last_shot"] > cd:
                if snd_shoot: snd_shoot.play()
                direction = (pygame.Vector2(pygame.mouse.get_pos()) - player["pos"]).normalize()
                if player["weapon"] == "pistol":
                    bullets.append({"pos": player["pos"].copy(), "dir": direction, "color": RED})
                elif player["weapon"] == "shotgun":
                    for a in [-15, 0, 15]: bullets.append({"pos": player["pos"].copy(), "dir": direction.rotate(a), "color": RED})
                elif player["weapon"] == "triple":
                    for a in [-5, 0, 5]: bullets.append({"pos": player["pos"].copy(), "dir": direction.rotate(a), "color": CYAN})
                player["last_shot"] = now

    # --- STATE LOGIC ---
    if game["state"] == GAME_MENU:
        screen.blit(font_big.render("NOT TODAY!", True, RED), (WIDTH//2 - 180, HEIGHT//2 - 50))
        screen.blit(font_small.render("Press SPACE to Start", True, WHITE), (WIDTH//2 - 105, HEIGHT//2 + 50))

    elif game["state"] == GAME_LOADING:
        progress = min((now - game["loading_timer"]) / game["loading_duration"], 1)
        screen.blit(pygame.font.SysFont(None, 35).render("Actually Better Than Google Dino!!", True, WHITE), (WIDTH//2 - 200, HEIGHT//2 - 50))
        pygame.draw.rect(screen, GRAY, (WIDTH//4, HEIGHT//2, WIDTH//2, 20))
        pygame.draw.rect(screen, GREEN, (WIDTH//4, HEIGHT//2, (WIDTH//2) * progress, 20))
        if progress >= 1: game["state"], game["phase_card_timer"] = GAME_PLAYING, now

    elif game["state"] == GAME_SHOP:
        screen.blit(font_mid.render("UPGRADE SHOP", True, YELLOW), (WIDTH//2 - 140, 30))
        screen.blit(font_small.render(f"Score: {game['score']}", True, GREEN), (WIDTH//2 - 40, 80))
        items = [
            ("[H] Heal - 20 pts", WHITE),
            ("[S] Speed Up - 30 pts (Max 12)", WHITE if player["speed"] < player["max_speed"] else GRAY),
            ("[L] Max Health Up - 60 pts", WHITE),
            ("[T] Triple Shot - 50 pts", WHITE if not player["triple_unlocked"] else GRAY),
            ("[M] Missile Support - 100 pts", WHITE if not player["missile_unlocked"] else GRAY),
            ("[V] Vampire Leech - 80 pts", WHITE if not player["vampire_unlocked"] else GRAY),
            ("[N] Nova Blast - 110 pts", WHITE if not player["nova_unlocked"] else GRAY),
            ("Press [SPACE] for Next Phase", RED)
        ]
        for i, (txt, col) in enumerate(items): screen.blit(font_small.render(txt, True, col), (WIDTH//2 - 180, 130 + i*40))

    elif game["state"] == GAME_PLAYING:
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player["pos"].y -= player["speed"]
        if keys[pygame.K_s]: player["pos"].y += player["speed"]
        if keys[pygame.K_a]: player["pos"].x -= player["speed"]
        if keys[pygame.K_d]: player["pos"].x += player["speed"]

        # Missile Support
        if player["missile_unlocked"] and now - player["last_missile"] > COOLDOWNS["missile"]:
            targets = enemies + ([boss["pos"]] if boss["active"] else [])
            if targets:
                target = min(targets, key=lambda e: player["pos"].distance_to(e))
                missiles.append({"pos": player["pos"].copy(), "dir": (target - player["pos"]).normalize()})
                player["last_missile"] = now

        # Projectile Updates
        for b in bullets: b["pos"] += b["dir"] * bullet_speed
        bullets = [b for b in bullets if 0 < b["pos"].x < WIDTH and 0 < b["pos"].y < HEIGHT]
        for m in missiles: m["pos"] += m["dir"] * (bullet_speed * 0.7)
        missiles = [m for m in missiles if 0 < m["pos"].x < WIDTH and 0 < m["pos"].y < HEIGHT]

        # Spawning Logic
        if game["score"] >= (game["phase"] * 20) and not boss["active"]:
            boss["active"], boss["intro"], boss["pos"] = True, True, pygame.Vector2(WIDTH // 2, -boss["radius"])
            if snd_boss: snd_boss.play()

        if boss["active"] and boss["intro"]:
            boss["pos"].y += 1
            if boss["pos"].y >= 100: boss["intro"] = False

        spawn_delay = max(200, 1000 - (game["phase"] - 1) * 85)
        if not boss["active"] and now - last_spawn_time > spawn_delay:
            spawn_enemy(); last_spawn_time = now

        # Movement Logic
        for en in enemies: en += (player["pos"] - en).normalize() * (enemy_speed + (game["phase"] - 1) * 0.4)
        if boss["active"] and not boss["intro"]:
            boss["state_timer"] += 1
            if game["phase"] >= 2 and boss["state_timer"] % 120 == 0: boss["bombs"].append({"pos": boss["pos"].copy(), "time": now})
            if game["phase"] >= 5 and boss["state_timer"] % 300 == 0:
                for _ in range(3): enemies.append(boss["pos"] + pygame.Vector2(random.randint(-50,50), random.randint(-50,50)))
            if game["phase"] >= 8 and boss["state_timer"] % 180 == 0: boss["strikes"].append({"pos": player["pos"].copy(), "timer": 60})
            
            if 4 <= game["phase"] <= 6 and boss["state_timer"] % 120 == 0: boss["pos"] += (player["pos"] - boss["pos"]).normalize() * 100
            elif 7 <= game["phase"] <= 9 and boss["state_timer"] % 180 == 0: boss["pos"] = player["pos"] + pygame.Vector2(random.randint(-100,100), random.randint(-100,100))
            elif game["phase"] == 10 and boss["state_timer"] % 60 == 0: enemies.append(boss["pos"] + pygame.Vector2(50,0))
            boss["pos"] += (player["pos"] - boss["pos"]).normalize() * boss["speed"]

        # Collision: Damage to Player
        if boss["active"] and not boss["intro"] and player["pos"].distance_to(boss["pos"]) < player["radius"] + boss["radius"]:
            if now - player["last_hit"] > COOLDOWNS["damage"]:
                if snd_hit: snd_hit.play()
                player["health"] -= 25; player["hit_flash"] = player["last_hit"] = now; game["shake_timer"] = 300

        for bmb in boss["bombs"][:]:
            if player["pos"].distance_to(bmb["pos"]) < player["radius"] + 15:
                if now - player["last_hit"] > COOLDOWNS["damage"]:
                    player["health"] -= 15; player["hit_flash"] = player["last_hit"] = now; game["shake_timer"] = 200; boss["bombs"].remove(bmb)
            elif now - bmb["time"] > 5000: boss["bombs"].remove(bmb)

        for stk in boss["strikes"][:]:
            stk["timer"] -= 1
            if stk["timer"] <= 0:
                if player["pos"].distance_to(stk["pos"]) < 60 and now - player["last_hit"] > COOLDOWNS["damage"]:
                    player["health"] -= 30; player["hit_flash"] = player["last_hit"] = now; game["shake_timer"] = 400
                create_particles(stk["pos"], RED, 10, 5); boss["strikes"].remove(stk)

        for en in enemies:
            if player["pos"].distance_to(en) < player["radius"] + enemy_radius:
                if now - player["last_hit"] > COOLDOWNS["damage"]:
                    if snd_hit: snd_hit.play()
                    player["health"] -= 10; player["hit_flash"] = player["last_hit"] = now; game["shake_timer"] = 200

        # Collision: Projectiles
        for b in bullets[:]:
            for en in enemies[:]:
                if b["pos"].distance_to(en) < enemy_radius + bullet_radius:
                    if b in bullets: bullets.remove(b)
                    enemies.remove(en); game["score"] += 1
                    if player["vampire_unlocked"] and random.random() < 0.15: player["health"] = min(player["max_health"], player["health"] + 2)
                    enemy_hit_flash[id(en)] = now; create_particles(en, RED)
                    break
            if boss["active"] and b["pos"].distance_to(boss["pos"]) < boss["radius"] + bullet_radius:
                if b in bullets: bullets.remove(b)
                boss["health"] -= 10; boss["hit_flash"], game["shake_timer"] = now, 200

        for m in missiles[:]:
            hit = False
            for en in enemies[:]:
                if m["pos"].distance_to(en) < enemy_radius + 10:
                    enemies.remove(en); game["score"] += 1; hit = True
                    if player["vampire_unlocked"] and random.random() < 0.15: player["health"] = min(player["max_health"], player["health"] + 8)
            if boss["active"] and m["pos"].distance_to(boss["pos"]) < boss["radius"] + 10:
                boss["health"] -= 30; hit = True
            if hit:
                if m in missiles: missiles.remove(m)
                create_particles(m["pos"], ORANGE, 15, 5)

        # Death / Boss Win
        if player["health"] <= 0:
            if snd_death: snd_death.play()
            reset_game()
        if boss["active"] and boss["health"] <= 0:
            boss["active"] = False
            boss["health"] = boss["max_health"] + (game["phase"] * 70)
            game["score"] += 50; game["phase"] += 1
            game["state"] = GAME_WIN if game["phase"] > game["max_phases"] else GAME_SHOP
            enemies.clear(); bullets.clear(); missiles.clear(); boss["bombs"].clear(); boss["strikes"].clear()

        # Update Particles
        for p in particles[:]:
            p["pos"] += p["vel"]; p["life"] -= dt
            if p["life"] <= 0: particles.remove(p)

        # Draw Entities
        for bmb in boss["bombs"]: pygame.draw.circle(screen, YELLOW, bmb["pos"] + offset, 10, 2)
        for stk in boss["strikes"]: pygame.draw.circle(screen, (100,0,0) if stk["timer"] > 10 else RED, stk["pos"] + offset, 50, 1)
        for en in enemies:
            col = WHITE if id(en) in enemy_hit_flash and now - enemy_hit_flash[id(en)] < 100 else RED
            pygame.draw.circle(screen, col, en + offset, enemy_radius)
        
        p_col = WHITE if now - player["hit_flash"] > 100 else YELLOW
        pygame.draw.circle(screen, p_col, player["pos"] + offset, player["radius"])
        for b in bullets: pygame.draw.circle(screen, b["color"], b["pos"] + offset, bullet_radius)
        for m in missiles: pygame.draw.circle(screen, ORANGE, m["pos"] + offset, 6)
        for p in particles: pygame.draw.circle(screen, p["col"], p["pos"] + offset, 3)

        # UI
        screen.blit(pygame.font.SysFont(None, 30).render(f"Score: {game['score']} Phase: {game['phase']}/{game['max_phases']}", True, WHITE), (10, 10))
        pygame.draw.rect(screen, RED, (10, 40, 220, 20))
        pygame.draw.rect(screen, WHITE, (10, 40, 220 * (player["health"] / player["max_health"]), 20))
        if boss["active"]:
            bc = PURPLE if now - boss["hit_flash"] > 100 else WHITE
            pygame.draw.circle(screen, bc, boss["pos"] + offset, boss["radius"])
            cur_boss_max = boss["max_health"] + (game["phase"]-1)*70
            pygame.draw.rect(screen, RED, (WIDTH // 2 - 150, 10, 300, 25))
            pygame.draw.rect(screen, PURPLE, (WIDTH // 2 - 150, 10, 300 * (boss["health"] / cur_boss_max), 25))
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 150, 10, 300, 25), 2)
        if now - game["phase_card_timer"] < game["phase_card_duration"]:
            screen.blit(font_big.render(f"PHASE {game['phase']}", True, YELLOW), (WIDTH//2 - 120, HEIGHT//2 - 100))

    elif game["state"] == GAME_PAUSED: screen.blit(font_mid.render("PAUSED", True, WHITE), (WIDTH//2 - 100, HEIGHT//2))
    elif game["state"] == GAME_WIN: screen.blit(font_mid.render("YOU WIN!", True, GREEN), (WIDTH//2 - 120, HEIGHT//2))

    pygame.display.flip()

pygame.quit()
sys.exit()