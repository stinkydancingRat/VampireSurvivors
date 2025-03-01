import pygame
import math
import random
import time

pygame.init()
pygame.font.init()

font = pygame.font.Font("pixelfont.ttf", 36)

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# SPRITES

playerImage = pygame.image.load("player.png")
player = pygame.transform.scale(playerImage, (32, 32))

enemyImage = pygame.image.load("enemy.png")
enemy = pygame.transform.scale(enemyImage, (32, 32))

fireballImage = pygame.image.load("fireball.png")
fireball = pygame.transform.scale(fireballImage, (32, 32))




def normalize(enemyX, enemyY):
    distance = math.sqrt((plrX - enemyX) ** 2 + (plrY - enemyY) ** 2)
    if distance == 0:
        return 0, 0
    dx = (plrX - enemyX) / distance
    dy = (plrY - enemyY) / distance
    return dx, dy

def check_collision(enemy1, enemy2):
    return (
        enemy1[0] < enemy2[0] + 32 and
        enemy1[0] + 32 > enemy2[0] and
        enemy1[1] < enemy2[1] + 32 and
        enemy1[1] + 32 > enemy2[1]
    )

def separation(enemy_index):
    separation_force_x = 0
    separation_force_y = 0
    for i, (other_enemyX, other_enemyY, _) in enumerate(enemies):
        if i != enemy_index:
            distance = math.sqrt((enemies[enemy_index][0] - other_enemyX) ** 2 + (enemies[enemy_index][1] - other_enemyY) ** 2)
            if distance < 32:
                separation_force_x += (enemies[enemy_index][0] - other_enemyX) / distance
                separation_force_y += (enemies[enemy_index][1] - other_enemyY) / distance
    return separation_force_x, separation_force_y


clock = pygame.time.Clock()

enemySpeed = 1.8
enemies = []

plrSpeed = 3
plrX = WIDTH // 2
plrY = HEIGHT // 2
plrIsFacingRight = True

def spawnEnemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        enemyX = random.randint(0, WIDTH)
        enemyY = -50
    elif side == 'bottom':
        enemyX = random.randint(0, WIDTH)
        enemyY = HEIGHT + 50
    elif side == 'left':
        enemyX = -50
        enemyY = random.randint(0, HEIGHT)
    elif side == 'right':
        enemyX = WIDTH + 50
        enemyY = random.randint(0, HEIGHT)

    enemyIsFacingRight = enemyX < plrX
    enemies.append([enemyX, enemyY, enemyIsFacingRight])

lastEnemySpawn = time.time()
enemySpawnSpeed = 5

difficulty = time.time()

second = 0
timePassed = time.time()

running = True

while running:
    timeText = font.render(f"{second}", True, (0, 0, 0))
    timeRect = timeText.get_rect(center=(WIDTH //2, 50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    moveX, moveY = 0, 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        if not plrX + 2 <= 0:
            moveX = -1
        plrIsFacingRight = False

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        if not plrX + 30 >= WIDTH:
            moveX = 1
        plrIsFacingRight = True

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        if not plrY <= 0:
            moveY = -1

    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        if not plrY + 32 >= HEIGHT:
            moveY = 1

    if moveX != 0 and moveY != 0:
        moveX *= math.sqrt(0.5)
        moveY *= math.sqrt(0.5)

    plrX += moveX * plrSpeed
    plrY += moveY * plrSpeed

    window.fill((85, 170, 0))
    if time.time() - difficulty > 20:
        enemySpawnSpeed = 2
    elif time.time() - difficulty > 50:
        enemySpawnSpeed = 1.5
    elif time.time() - difficulty > 100:
        enemySpawnSpeed = 1.25
    elif time.time() - difficulty > 150:
        enemySpawnSpeed = 1
    elif time.time() - difficulty > 400:
        enemySpawnSpeed = 0.5
    elif time.time() - difficulty > 600:
        enemySpawnSpeed = 0.25
    elif time.time() - difficulty > 800:
        enemySpawnSpeed = 0.1

    if time.time() - lastEnemySpawn > enemySpawnSpeed:
        spawnEnemy()
        lastEnemySpawn = time.time()

    if time.time() - timePassed >= 1:
        second += 1
        timePassed = time.time()

    for i in range(len(enemies)):
        enemyX, enemyY, enemyIsFacingRight = enemies[i]
        dx, dy = normalize(enemyX, enemyY)

        sep_force_x, sep_force_y = separation(i)
        dx += sep_force_x
        dy += sep_force_y

        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance != 0:
            dx /= distance
            dy /= distance

        enemyX += dx * enemySpeed
        enemyY += dy * enemySpeed
        
        enemies[i] = [enemyX, enemyY, enemyIsFacingRight]
        window.blit(pygame.transform.flip(enemy, True, False) if not enemyIsFacingRight else enemy, (enemyX, enemyY))

        if plrX + 2 >= enemyX and plrX - 2 <= enemyX + 30 and plrY + 32 >= enemyY and plrY <= enemyY + 32:
            print("Diddy")

    window.blit(pygame.transform.flip(player, True, False) if not plrIsFacingRight else player, (plrX, plrY))
    window.blit(timeText, timeRect)
    pygame.display.update()
    clock.tick(60)