import pygame
import math
import sys
import random

score = 0

'''setup my pygame'''
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NOT TODAY!")
clock = pygame.time.Clock()

''' colors of my game'''
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (200, 50, 50)
YELLOW = (255, 255, 0)
GREEN = (50, 200, 50)
GRAY = (50, 50, 50)
PURPLE = (150, 0, 150)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

'''game states & phases'''
GAME_MENU = 0
GAME_LOADING = 1
GAME_PLAYING = 2
GAME_PAUSED = 3
GAME_SHOP = 4
GAME_WIN = 5
state = GAME_MENU
current_phase = 1
max_phases = 10

'''loading variables'''
loading_timer = 0
loading_duration = 7000 

'''phase title card'''
phase_card_timer = 0
phase_card_duration = 2000 

'''player'''
player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
player_speed = 5
player_max_speed = 12 # set max speed
player_radius = 15

'''player health'''
player_health = 100
max_health = 100
damage_cooldown = 500
last_hit_time = 0
player_hit_flash = 0 

'''weapons & abilities'''
weapon_type = "pistol" 
triple_shot_unlocked = False
missile_support_unlocked = False
vampire_unlocked = False # vampire ability
nova_unlocked = False # nova ability
last_nova_time = 0 # nova cooldown
nova_cooldown = 5000
last_shot_time = 0
shot_cooldown = 300
last_missile_time = 0
missile_cooldown = 2000 # Fires every 2 seconds

'''enemies'''
enemies = []
enemy_radius = 12
enemy_speed = 2
spawn_delay = 1000
last_spawn_time = 0

'''BOSS FIGHT'''
boss_active = False
boss_radius = 40
boss_health = 200
boss_max_health = 200
boss_speed = 1.5
boss_pos = pygame.Vector2(WIDTH // 2, -boss_radius)
boss_intro = False
boss_hit_flash = 0 
boss_state_timer = 0 # For unique abilities

# NEW BOSS ABILITY LISTS
boss_bombs = [] # Electric Bombs
boss_strikes = [] # Orbital Strikes

'''projectiles'''
bullets = []
missiles = []
bullet_speed = 10
bullet_raduis = 4

'''visuals'''
enemy_hit_flash = {}
particles = []
shake_timer = 0
shake_intensity = 5

'''sounds'''
try:
    snd_shoot = pygame.mixer.Sound("sounds/shoot.wav")
    snd_hit = pygame.mixer.Sound("sounds/hit.wav")
    snd_death = pygame.mixer.Sound("sounds/death.wav")
    snd_boss = pygame.mixer.Sound("sounds/boss.wav")
    pygame.mixer.music.load("sounds/music.wav")
    pygame.mixer.music.play(-1)
except:
    snd_shoot = snd_hit = snd_death = snd_boss = None

'''main loop'''
running = True
while running:
    clock.tick(60)
    current_time = pygame.time.get_ticks()
    screen.fill(BLACK)

    offset = pygame.Vector2(0, 0)
    if shake_timer > 0:
        shake_timer -= clock.get_time()
        offset.x = random.randint(-shake_intensity, shake_intensity)
        offset.y = random.randint(-shake_intensity, shake_intensity)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if state == GAME_MENU and event.key == pygame.K_SPACE:
                state = GAME_LOADING
                loading_timer = current_time
            if state == GAME_PLAYING and event.key == pygame.K_p:
                state = GAME_PAUSED
            elif state == GAME_PAUSED and event.key == pygame.K_p:
                state = GAME_PLAYING
            
            '''check shop inputs'''
            if state == GAME_SHOP:
                if event.key == pygame.K_h and score >= 20:
                    score -= 20
                    player_health = max_health
                if event.key == pygame.K_s and score >= 30 and player_speed < player_max_speed:
                    score -= 30
                    player_speed += 1
                if event.key == pygame.K_l and score >= 60:
                    score -= 60
                    max_health += 25
                    player_health = max_health
                if event.key == pygame.K_t and score >= 50 and not triple_shot_unlocked:
                    score -= 50
                    triple_shot_unlocked = True
                if event.key == pygame.K_m and score >= 100 and not missile_support_unlocked:
                    score -= 100
                    missile_support_unlocked = True
                if event.key == pygame.K_v and score >= 80 and not vampire_unlocked:
                    score -= 80
                    vampire_unlocked = True
                if event.key == pygame.K_n and score >= 110 and not nova_unlocked:
                    score -= 110
                    nova_unlocked = True
                if event.key == pygame.K_SPACE:
                    state = GAME_PLAYING
                    phase_card_timer = current_time 

            if event.key == pygame.K_1: weapon_type = "pistol"
            if event.key == pygame.K_2: weapon_type = "shotgun"
            if event.key == pygame.K_3 and triple_shot_unlocked: weapon_type = "triple"
            
            '''trigger nova ability'''
            if state == GAME_PLAYING and event.key == pygame.K_SPACE and nova_unlocked:
                if current_time - last_nova_time > nova_cooldown:
                    for i in range(0, 360, 20):
                        n_dir = pygame.Vector2(1, 0).rotate(i)
                        bullets.append({"pos": player_pos.copy(), "dir": n_dir, "color": CYAN})
                    last_nova_time = current_time
                    shake_timer = 300

        if event.type == pygame.MOUSEBUTTONDOWN and state == GAME_PLAYING:
            if current_time - last_shot_time > shot_cooldown:
                if snd_shoot: snd_shoot.play()
                mouse_pos = pygame.mouse.get_pos()
                direction = (pygame.Vector2(mouse_pos) - player_pos).normalize()
                
                if weapon_type == "pistol":
                    bullets.append({"pos": player_pos.copy(), "dir": direction, "color": RED})
                    shot_cooldown = 300
                elif weapon_type == "shotgun":
                    for angle in [-15, 0, 15]:
                        bullets.append({"pos": player_pos.copy(), "dir": direction.rotate(angle), "color": RED})
                    shot_cooldown = 600
                elif weapon_type == "triple":
                    for angle in [-5, 0, 5]:
                        bullets.append({"pos": player_pos.copy(), "dir": direction.rotate(angle), "color": CYAN})
                    shot_cooldown = 400
                last_shot_time = current_time

    if state == GAME_MENU:
        f_big, f_small = pygame.font.SysFont(None, 80), pygame.font.SysFont(None, 40)
        screen.blit(f_big.render("NOT TODAY!", True, RED), (WIDTH//2 - 180, HEIGHT//2 - 50))
        screen.blit(f_small.render("Press SPACE to Start", True, WHITE), (WIDTH//2 - 140, HEIGHT//2 + 50))

    elif state == GAME_LOADING:
        elapsed = current_time - loading_timer
        progress = min(elapsed / loading_duration, 1)
        screen.blit(pygame.font.SysFont(None, 35).render("Actually Better Than Google Dino!!", True, WHITE), (WIDTH//2 - 200, HEIGHT//2 - 50))
        pygame.draw.rect(screen, GRAY, (WIDTH//4, HEIGHT//2, WIDTH//2, 20))
        pygame.draw.rect(screen, GREEN, (WIDTH//4, HEIGHT//2, (WIDTH//2) * progress, 20))
        if progress >= 1: state = GAME_PLAYING; phase_card_timer = current_time

    elif state == GAME_SHOP:
        '''draw shop menu'''
        f_b, f_m = pygame.font.SysFont(None, 50), pygame.font.SysFont(None, 28)
        screen.blit(f_b.render("UPGRADE SHOP", True, YELLOW), (WIDTH//2 - 140, 30))
        screen.blit(f_m.render(f"Score: {score}", True, GREEN), (WIDTH//2 - 40, 80))
        items = [
            ("[H] Heal - 20 pts", WHITE),
            ("[S] Speed Up - 30 pts (Max 12)", WHITE if player_speed < player_max_speed else GRAY),
            ("[L] Max Health Up - 60 pts", WHITE),
            ("[T] Triple Shot - 50 pts", WHITE if not triple_shot_unlocked else GRAY),
            ("[M] Missile Support - 100 pts", WHITE if not missile_support_unlocked else GRAY),
            ("[V] Vampire Leech - 80 pts", WHITE if not vampire_unlocked else GRAY),
            ("[N] Nova Blast - 110 pts", WHITE if not nova_unlocked else GRAY),
            ("Press [SPACE] for Next Phase", RED)
        ]
        for i, (text, col) in enumerate(items):
            screen.blit(f_m.render(text, True, col), (WIDTH//2 - 180, 130 + i*40))

    elif state == GAME_PLAYING:
        '''player movement'''
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos.y -= player_speed
        if keys[pygame.K_s]: player_pos.y += player_speed
        if keys[pygame.K_a]: player_pos.x -= player_speed
        if keys[pygame.K_d]: player_pos.x += player_speed

        '''Missile Support Ability'''
        if missile_support_unlocked and current_time - last_missile_time > missile_cooldown:
            target_list = enemies + ([boss_pos] if boss_active else [])
            if target_list:
                closest = min(target_list, key=lambda e: player_pos.distance_to(e))
                m_dir = (closest - player_pos).normalize()
                missiles.append({"pos": player_pos.copy(), "dir": m_dir})
                last_missile_time = current_time

        '''update projectiles'''
        for b in bullets: b["pos"] += b["dir"] * bullet_speed
        bullets = [b for b in bullets if 0 < b["pos"].x < WIDTH and 0 < b["pos"].y < HEIGHT]
        
        for m in missiles: m["pos"] += m["dir"] * (bullet_speed * 0.7)
        missiles = [m for m in missiles if 0 < m["pos"].x < WIDTH and 0 < m["pos"].y < HEIGHT]

        '''Boss and Enemy Spawning'''
        if score >= (current_phase * 20) and not boss_active:
            boss_active, boss_intro, boss_pos = True, True, pygame.Vector2(WIDTH // 2, -boss_radius)
            if snd_boss: snd_boss.play()

        if boss_active and boss_intro:
            boss_pos.y += 1
            if boss_pos.y >= 100: boss_intro = False

        c_delay = max(200, spawn_delay - (current_phase - 1) * 85)
        if not boss_active and current_time - last_spawn_time > c_delay:
            last_spawn_time = current_time
            side = random.choice(["top", "botton", "left", "right"])
            if side == "top": x, y = random.randint(0, WIDTH), -enemy_radius
            elif side == "botton": x, y = random.randint(0, WIDTH), HEIGHT + enemy_radius
            elif side == "left": x, y = -enemy_radius, random.randint(0, HEIGHT)
            else: x, y = WIDTH + enemy_radius, random.randint(0, HEIGHT)
            enemies.append(pygame.Vector2(x, y))

        '''Movements'''
        for en in enemies:
            en += (player_pos - en).normalize() * (enemy_speed + (current_phase - 1) * 0.4)

        if boss_active and not boss_intro:
            boss_state_timer += 1
            
            # --- NEW BOSS ABILITIES ---
            
            # 1. Electric Bombs (Phase 2+)
            if current_phase >= 2 and boss_state_timer % 120 == 0:
                boss_bombs.append({"pos": boss_pos.copy(), "time": current_time})
            
            # 2. Spawn Soldiers (Phase 5+)
            if current_phase >= 5 and boss_state_timer % 300 == 0:
                for _ in range(3):
                    soldier = boss_pos + pygame.Vector2(random.randint(-50,50), random.randint(-50,50))
                    enemies.append(soldier)
            
            # 3. Orbital Strike (Phase 8+)
            if current_phase >= 8 and boss_state_timer % 180 == 0:
                boss_strikes.append({"pos": player_pos.copy(), "timer": 60}) # 60 frames warning

            # Logic for Existing Dash/TP
            if 4 <= current_phase <= 6 and boss_state_timer % 120 == 0:
                boss_pos += (player_pos - boss_pos).normalize() * 100
            elif 7 <= current_phase <= 9 and boss_state_timer % 180 == 0:
                boss_pos = player_pos + pygame.Vector2(random.randint(-100,100), random.randint(-100,100))
            elif current_phase == 10 and boss_state_timer % 60 == 0:
                enemies.append(boss_pos + pygame.Vector2(50,0))
            
            boss_pos += (player_pos - boss_pos).normalize() * boss_speed

        '''Collision Logic'''
        # Fix: Boss Damage to Player
        if boss_active and not boss_intro:
            if player_pos.distance_to(boss_pos) < player_radius + boss_radius:
                if current_time - last_hit_time > damage_cooldown:
                    if snd_hit: snd_hit.play()
                    player_health -= 25
                    player_hit_flash, last_hit_time, shake_timer = current_time, current_time, 300

        # Bomb/Strike Damage
        for bomb in boss_bombs[:]:
            if player_pos.distance_to(bomb["pos"]) < player_radius + 15:
                if current_time - last_hit_time > damage_cooldown:
                    player_health -= 15
                    player_hit_flash, last_hit_time, shake_timer = current_time, current_time, 200
                    boss_bombs.remove(bomb)
            elif current_time - bomb["time"] > 5000: boss_bombs.remove(bomb)

        for strike in boss_strikes[:]:
            strike["timer"] -= 1
            if strike["timer"] <= 0:
                if player_pos.distance_to(strike["pos"]) < 60:
                     if current_time - last_hit_time > damage_cooldown:
                        player_health -= 30
                        player_hit_flash, last_hit_time, shake_timer = current_time, current_time, 400
                # Animation
                for _ in range(10): particles.append({"pos": strike["pos"].copy(), "vel": pygame.Vector2(random.uniform(-5,5), random.uniform(-5,5)), "life": 400, "col": RED})
                boss_strikes.remove(strike)

        for en in enemies:
            if player_pos.distance_to(en) < player_radius + enemy_radius:
                if current_time - last_hit_time > damage_cooldown:
                    if snd_hit: snd_hit.play()
                    player_health -= 10
                    player_hit_flash, last_hit_time, shake_timer = current_time, current_time, 200

        # Bullets hitting things
        for b in bullets[:]:
            for en in enemies[:]:
                if b["pos"].distance_to(en) < enemy_radius + bullet_raduis:
                    if b in bullets: bullets.remove(b)
                    enemies.remove(en); score += 1
                    
                    '''trigger vampire heal'''
                    if vampire_unlocked and random.random() < 0.15:
                        player_health = min(max_health, player_health + 2)
                        
                    enemy_hit_flash[id(en)] = current_time
                    for _ in range(5): particles.append({"pos": en.copy(), "vel": pygame.Vector2(random.uniform(-3,3), random.uniform(-3,3)), "life": 300, "col": RED})
                    break
            if boss_active and b["pos"].distance_to(boss_pos) < boss_radius + bullet_raduis:
                if b in bullets: bullets.remove(b)
                boss_health -= 10; boss_hit_flash, shake_timer = current_time, 200

        # Missiles hitting things (Explosive)
        for m in missiles[:]:
            targets_hit = False
            for en in enemies[:]:
                if m["pos"].distance_to(en) < enemy_radius + 10:
                    enemies.remove(en); score += 1; targets_hit = True
                    '''trigger vampire heal'''
                    if vampire_unlocked and random.random() < 0.15:
                        player_health = min(max_health, player_health + 8)
            if boss_active and m["pos"].distance_to(boss_pos) < boss_radius + 10:
                boss_health -= 30; targets_hit = True
            
            if targets_hit:
                if m in missiles: missiles.remove(m)
                for _ in range(15): particles.append({"pos": m["pos"].copy(), "vel": pygame.Vector2(random.uniform(-5,5), random.uniform(-5,5)), "life": 500, "col": ORANGE})

        if player_health <= 0:
            if snd_death: snd_death.play()
            enemies.clear(); bullets.clear(); missiles.clear(); particles.clear()
            boss_bombs.clear(); boss_strikes.clear()
            player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
            player_health, score, current_phase, boss_active, state = max_health, 0, 1, False, GAME_MENU

        if boss_active and boss_health <= 0:
            boss_active = False
            boss_health = boss_max_health + (current_phase * 70)
            score, current_phase, state = score + 50, current_phase + 1, GAME_WIN if current_phase > max_phases else GAME_SHOP
            enemies.clear(); bullets.clear(); missiles.clear(); boss_bombs.clear(); boss_strikes.clear()

        for p in particles[:]:
            p["pos"] += p["vel"]; p["life"] -= clock.get_time()
            if p["life"] <= 0: particles.remove(p)

        '''Drawing'''
        # Draw Bombs
        for bomb in boss_bombs: pygame.draw.circle(screen, YELLOW, bomb["pos"] + offset, 10, 2)
        # Draw Strikes
        for strike in boss_strikes: 
            color = (100, 0, 0) if strike["timer"] > 10 else RED
            pygame.draw.circle(screen, color, strike["pos"] + offset, 50, 1)

        for en in enemies:
            col = RED
            if id(en) in enemy_hit_flash and current_time - enemy_hit_flash[id(en)] < 100: col = WHITE
            pygame.draw.circle(screen, col, en + offset, enemy_radius)

        p_col = WHITE if current_time - player_hit_flash > 100 else YELLOW
        pygame.draw.circle(screen, p_col, player_pos + offset, player_radius)
        
        for b in bullets: pygame.draw.circle(screen, b["color"], b["pos"] + offset, bullet_raduis)
        for m in missiles: pygame.draw.circle(screen, ORANGE, m["pos"] + offset, 6)
        for p in particles: pygame.draw.circle(screen, p["col"], p["pos"] + offset, 3)

        f = pygame.font.SysFont(None, 30)
        screen.blit(f.render(f"Score: {score}  Phase: {current_phase}/{max_phases}", True, WHITE), (10, 10))
        pygame.draw.rect(screen, RED, (10, 40, 220, 20))
        pygame.draw.rect(screen, WHITE, (10, 40, 220 * (player_health / max_health), 20))

        if boss_active:
            bc = PURPLE if current_time - boss_hit_flash > 100 else WHITE
            pygame.draw.circle(screen, bc, boss_pos + offset, boss_radius)
            pygame.draw.rect(screen, RED, (WIDTH // 2 - 150, 10, 300, 25))
            pygame.draw.rect(screen, PURPLE, (WIDTH // 2 - 150, 10, 300 * (boss_health / (boss_max_health + (current_phase-1)*70)), 25))
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 150, 10, 300, 25), 2)

        if current_time - phase_card_timer < phase_card_duration:
            screen.blit(pygame.font.SysFont(None, 80).render(f"PHASE {current_phase}", True, YELLOW), (WIDTH//2 - 120, HEIGHT//2 - 100))

    elif state == GAME_PAUSED:
        screen.blit(pygame.font.SysFont(None, 70).render("PAUSED", True, WHITE), (WIDTH//2 - 100, HEIGHT//2))

    elif state == GAME_WIN:
        screen.blit(pygame.font.SysFont(None, 70).render("YOU WIN!", True, GREEN), (WIDTH//2 - 120, HEIGHT//2))

    pygame.display.flip()

pygame.quit()
sys.exit()