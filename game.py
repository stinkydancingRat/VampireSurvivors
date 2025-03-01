import pygame
import math
import random
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))

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

# SPRITES

playerImage = pygame.image.load("player.png")
player = pygame.transform.scale(playerImage, (32, 32))

enemyImage = pygame.image.load("enemy.png")
enemy = pygame.transform.scale(enemyImage, (32, 32))

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
        enemyY = -100
    elif side == 'bottom':
        enemyX = random.randint(0, WIDTH)
        enemyY = HEIGHT + 100
    elif side == 'left':
        enemyX = -100
        enemyY = random.randint(0, HEIGHT)
    elif side == 'right':
        enemyX = WIDTH + 100
        enemyY = random.randint(0, HEIGHT)

    enemyIsFacingRight = enemyX < plrX
    enemies.append([enemyX, enemyY, enemyIsFacingRight])

lastEnemySpawn = time.time()
enemySpawnSpeed = 5

difficulty = time.time()

running = True

while running:
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
    

    for i in range(len(enemies)):
        enemyX, enemyY, enemyIsFacingRight = enemies[i]
        dx, dy = normalize(enemyX, enemyY)
        
        # Move enemy
        new_enemyX = enemyX + dx * enemySpeed
        new_enemyY = enemyY + dy * enemySpeed
        
        # Check for collisions with other enemies
        collision = False
        for j in range(len(enemies)):
            if i != j and check_collision([new_enemyX, new_enemyY, enemyIsFacingRight], enemies[j]):
                collision = True
                break
        
        if not collision:
            enemyX = new_enemyX
            enemyY = new_enemyY
        
        enemies[i] = [enemyX, enemyY, enemyIsFacingRight]
        window.blit(pygame.transform.flip(enemy, True, False) if not enemyIsFacingRight else enemy, (enemyX, enemyY))
        
        # Check for collision with player
        if plrX + 2 >= enemyX and plrX - 2 <= enemyX + 30 and plrY + 32 >= enemyY and plrY <= enemyY + 32:
            print("Diddy")

    window.blit(pygame.transform.flip(player, True, False) if not plrIsFacingRight else player, (plrX, plrY))
    pygame.display.update()
    clock.tick(60)