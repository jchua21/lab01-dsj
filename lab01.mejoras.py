import pygame
import math
import random
from pygame import mixer

# Initialize the pygame
pygame.init()
# create the screen
screen = pygame.display.set_mode((800, 600))

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)

# Background
background = pygame.Surface((800, 600))
background.fill((0, 0, 50))  # Dark blue background

# Title and icon
pygame.display.set_caption("Space Invaders Enhanced")

# Player
playerImg = pygame.Surface((64, 64))
playerImg.fill(GREEN)
pygame.draw.polygon(playerImg, WHITE, [(32, 10), (10, 54), (54, 54)])

playerX = 370
playerY = 480
playerX_change = 0
player_speed = 3

# Enemy types
ENEMY_TYPES = {
    'basic': {'color': RED, 'points': 10, 'speed': 1.2, 'health': 1},
    'fast': {'color': YELLOW, 'points': 20, 'speed': 2.0, 'health': 1},
    'tank': {'color': PURPLE, 'points': 50, 'speed': 0.8, 'health': 3},
    'boss': {'color': (255, 100, 0), 'points': 100, 'speed': 1.0, 'health': 5}
}

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
enemy_type = []
enemy_health = []
num_of_enemies = 8

enemyYMov = 25

# Power-ups
powerups = []
POWERUP_TYPES = {
    'double_shot': {'color': BLUE, 'duration': 400},  # Más duración
    'rapid_fire': {'color': GREEN, 'duration': 400},
    'shield': {'color': YELLOW, 'duration': 500}
}

# Player power-up states
double_shot_active = False
double_shot_timer = 0
rapid_fire_active = False
rapid_fire_timer = 0
shield_active = False
shield_timer = 0
player_lives = 3


def create_enemy_wave(level):
    global enemyImg, enemyX, enemyY, enemyX_change, enemyY_change, enemy_type, enemy_health

    enemyImg.clear()
    enemyX.clear()
    enemyY.clear()
    enemyX_change.clear()
    enemyY_change.clear()
    enemy_type.clear()
    enemy_health.clear()

    # More enemies and different types as level increases
    base_enemies = 6 + (level * 2)
    if base_enemies > 15:
        base_enemies = 15

    for i in range(base_enemies):
        # Create enemy sprite based on type
        enemy_img = pygame.Surface((48, 48))

        # Determine enemy type based on level and randomness
        rand = random.random()
        if level == 1:
            if rand < 0.8:
                e_type = 'basic'
            else:
                e_type = 'fast'
        elif level <= 3:
            if rand < 0.5:
                e_type = 'basic'
            elif rand < 0.8:
                e_type = 'fast'
            else:
                e_type = 'tank'
        else:
            if rand < 0.3:
                e_type = 'basic'
            elif rand < 0.6:
                e_type = 'fast'
            elif rand < 0.9:
                e_type = 'tank'
            else:
                e_type = 'boss'

        enemy_img.fill(ENEMY_TYPES[e_type]['color'])
        pygame.draw.rect(enemy_img, WHITE, (4, 4, 40, 40), 2)

        enemyImg.append(enemy_img)
        enemyX.append(random.randint(0, 752))
        enemyY.append(random.randint(50, 150))
        enemyX_change.append(ENEMY_TYPES[e_type]['speed'])
        enemyY_change.append(enemyYMov)
        enemy_type.append(e_type)
        enemy_health.append(ENEMY_TYPES[e_type]['health'])


# Initialize first wave
current_level = 1
create_enemy_wave(current_level)

# Bullet
bullets = []

# Score and game state
score_value = 0
font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 64)
textX = 10
textY = 10
game_state = "playing"  # "playing", "game_over", "victory", "level_complete"
enemies_killed_this_level = 0


def create_powerup(x, y):
    powerup_type = random.choice(list(POWERUP_TYPES.keys()))
    powerup = {
        'x': x,
        'y': y,
        'type': powerup_type,
        'timer': 0
    }
    powerups.append(powerup)


def show_score(x, y):
    score = font.render(f"Score: {score_value}", True, WHITE)
    screen.blit(score, (x, y))

    lives = font.render(f"Lives: {player_lives}", True, WHITE)
    screen.blit(lives, (x, y + 30))

    level = font.render(f"Level: {current_level}", True, WHITE)
    screen.blit(level, (x, y + 60))


def show_powerup_status():
    y_offset = 100
    if double_shot_active:
        text = font.render("Double Shot!", True, BLUE)
        screen.blit(text, (10, y_offset))
        y_offset += 25
    if rapid_fire_active:
        text = font.render("Rapid Fire!", True, GREEN)
        screen.blit(text, (10, y_offset))
        y_offset += 25
    if shield_active:
        text = font.render("Shield Active!", True, YELLOW)
        screen.blit(text, (10, y_offset))


def game_over_text():
    over_text = big_font.render("GAME OVER", True, RED)
    screen.blit(over_text, (200, 250))
    restart_text = font.render("Press R to restart", True, WHITE)
    screen.blit(restart_text, (280, 320))


def victory_text():
    victory_text = big_font.render("YOU WIN!", True, GREEN)
    screen.blit(victory_text, (220, 250))
    restart_text = font.render("Press R to play again", True, WHITE)
    screen.blit(restart_text, (270, 320))


def level_complete_text():
    complete_text = big_font.render("LEVEL COMPLETE!", True, YELLOW)
    screen.blit(complete_text, (150, 250))
    next_text = font.render("Press SPACE for next level", True, WHITE)
    screen.blit(next_text, (240, 320))


def player(x, y):
    screen.blit(playerImg, (x, y))
    # Draw shield if active
    if shield_active:
        pygame.draw.circle(screen, YELLOW, (int(x + 32), int(y + 32)), 40, 3)


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))
    # Draw health indicator for tanks and bosses
    if enemy_type[i] in ['tank', 'boss']:
        health_width = int((enemy_health[i] / ENEMY_TYPES[enemy_type[i]]['health']) * 40)
        pygame.draw.rect(screen, RED, (x + 4, y - 10, 40, 4))
        pygame.draw.rect(screen, GREEN, (x + 4, y - 10, health_width, 4))


def fire_bullet(x, y):
    bullet = {
        'x': x + 32,
        'y': y,
        'speed': 6  # Balas más rápidas
    }
    bullets.append(bullet)

    if double_shot_active:
        bullet_left = {
            'x': x + 16,
            'y': y,
            'speed': 6
        }
        bullet_right = {
            'x': x + 48,
            'y': y,
            'speed': 6
        }
        bullets.append(bullet_left)
        bullets.append(bullet_right)


def isCollision(x1, y1, x2, y2, threshold=40):
    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance < threshold


def reset_game():
    global playerX, playerY, playerX_change, score_value, current_level
    global game_state, enemies_killed_this_level, player_lives
    global double_shot_active, rapid_fire_active, shield_active
    global double_shot_timer, rapid_fire_timer, shield_timer

    playerX = 370
    playerY = 480
    playerX_change = 0
    score_value = 0
    current_level = 1
    game_state = "playing"
    enemies_killed_this_level = 0
    player_lives = 3

    # Reset power-ups
    double_shot_active = False
    rapid_fire_active = False
    shield_active = False
    double_shot_timer = 0
    rapid_fire_timer = 0
    shield_timer = 0

    bullets.clear()
    powerups.clear()
    create_enemy_wave(current_level)


# Game Loop
running = True
clock = pygame.time.Clock()
last_shot_time = 0

while running:
    current_time = pygame.time.get_ticks()
    dt = clock.tick(60)

    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if event.key == pygame.K_LEFT:
                    playerX_change = -player_speed
                if event.key == pygame.K_RIGHT:
                    playerX_change = player_speed
                if event.key == pygame.K_SPACE:
                    # Rapid fire or normal fire rate
                    fire_rate = 80 if rapid_fire_active else 150  # Disparo más rápido
                    if current_time - last_shot_time > fire_rate:
                        fire_bullet(playerX, playerY)
                        last_shot_time = current_time

            elif game_state in ["game_over", "victory"]:
                if event.key == pygame.K_r:
                    reset_game()

            elif game_state == "level_complete":
                if event.key == pygame.K_SPACE:
                    current_level += 1
                    enemies_killed_this_level = 0
                    create_enemy_wave(current_level)
                    game_state = "playing"

                    # Small reward for completing level
                    score_value += current_level * 100

        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                playerX_change = 0

    if game_state == "playing":
        # Update power-up timers
        if double_shot_active:
            double_shot_timer -= 1
            if double_shot_timer <= 0:
                double_shot_active = False

        if rapid_fire_active:
            rapid_fire_timer -= 1
            if rapid_fire_timer <= 0:
                rapid_fire_active = False

        if shield_active:
            shield_timer -= 1
            if shield_timer <= 0:
                shield_active = False

        # Player movement
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        # Enemy movement
        for i in range(len(enemyX)):
            if i >= len(enemyX):  # Safety check
                break

            # Game Over condition
            if enemyY[i] > 440:
                if not shield_active:
                    player_lives -= 1
                    if player_lives <= 0:
                        game_state = "game_over"
                        break
                    else:
                        # Reset enemy position
                        enemyY[i] = random.randint(50, 150)
                        enemyX[i] = random.randint(0, 752)

            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = abs(enemyX_change[i])
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 752:
                enemyX_change[i] = -abs(enemyX_change[i])
                enemyY[i] += enemyY_change[i]

        # Bullet movement and collision
        for bullet in bullets[:]:
            bullet['y'] -= bullet['speed']
            if bullet['y'] < 0:
                bullets.remove(bullet)
                continue

            # Check collision with enemies
            for i in range(len(enemyX) - 1, -1, -1):
                if isCollision(enemyX[i] + 24, enemyY[i] + 24, bullet['x'], bullet['y']):
                    bullets.remove(bullet)

                    # Damage enemy
                    enemy_health[i] -= 1

                    if enemy_health[i] <= 0:
                        # Enemy destroyed
                        score_value += ENEMY_TYPES[enemy_type[i]]['points']
                        enemies_killed_this_level += 1

                        # Chance to drop power-up
                        if random.random() < 0.25:  # 25% más probabilidad
                            create_powerup(enemyX[i], enemyY[i])

                        # Remove enemy
                        enemyImg.pop(i)
                        enemyX.pop(i)
                        enemyY.pop(i)
                        enemyX_change.pop(i)
                        enemyY_change.pop(i)
                        enemy_type.pop(i)
                        enemy_health.pop(i)

                    break

        # Power-up movement and collection
        for powerup in powerups[:]:
            powerup['y'] += 2  # Power-ups caen más rápido
            if powerup['y'] > 600:
                powerups.remove(powerup)
                continue

            # Check collection
            if isCollision(playerX + 32, playerY + 32, powerup['x'], powerup['y'], 50):
                powerups.remove(powerup)

                # Activate power-up
                if powerup['type'] == 'double_shot':
                    double_shot_active = True
                    double_shot_timer = POWERUP_TYPES['double_shot']['duration']
                elif powerup['type'] == 'rapid_fire':
                    rapid_fire_active = True
                    rapid_fire_timer = POWERUP_TYPES['rapid_fire']['duration']
                elif powerup['type'] == 'shield':
                    shield_active = True
                    shield_timer = POWERUP_TYPES['shield']['duration']

        # Check victory conditions
        if len(enemyX) == 0:  # All enemies defeated
            if current_level >= 5:  # Win after 5 levels
                game_state = "victory"
            else:
                game_state = "level_complete"

    # Drawing
    if game_state == "playing" or game_state == "level_complete":
        # Draw enemies
        for i in range(len(enemyX)):
            enemy(enemyX[i], enemyY[i], i)

        # Draw bullets
        for bullet in bullets:
            pygame.draw.circle(screen, WHITE, (int(bullet['x']), int(bullet['y'])), 3)

        # Draw power-ups
        for powerup in powerups:
            color = POWERUP_TYPES[powerup['type']]['color']
            pygame.draw.circle(screen, color, (int(powerup['x']), int(powerup['y'])), 15)
            pygame.draw.circle(screen, WHITE, (int(powerup['x']), int(powerup['y'])), 15, 2)

        player(playerX, playerY)
        show_score(textX, textY)
        show_powerup_status()

        if game_state == "level_complete":
            level_complete_text()

    elif game_state == "game_over":
        game_over_text()

    elif game_state == "victory":
        victory_text()

    pygame.display.update()

pygame.quit()