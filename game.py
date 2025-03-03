import pygame
import math
import random
import time

pygame.init()
pygame.font.init()

font = pygame.font.Font("pixelfont.ttf", 48)
levelFont = pygame.font.Font("pixelfont.ttf", 24)

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# SPRITES

levelUpCardImage = pygame.image.load("levelUpCard.png")
levelUpCard = pygame.transform.scale(levelUpCardImage, (320, 640))

xpOrbImage = pygame.image.load("xpOrb.png")
xpOrb = pygame.transform.scale(xpOrbImage, (16, 16))

playerImage = pygame.image.load("player.png")
player = pygame.transform.scale(playerImage, (32, 32))

enemyImage = pygame.image.load("enemy.png")
enemy = pygame.transform.scale(enemyImage, (32, 32))

fireballImage = pygame.image.load("fireball.png")
fireball = pygame.transform.scale(fireballImage, (48, 60))
fireballIcon = pygame.transform.scale(fireballImage, (160, 200))

def normalize(enemyX, enemyY):
    distance = math.sqrt((plrX - enemyX) ** 2 + (plrY - enemyY) ** 2)
    if distance == 0:
        return 0, 0
    dx = (plrX - enemyX) / distance
    dy = (plrY - enemyY) / distance
    return dx, dy

def check_collision(enemy1, enemy2):
    return (
        enemy1[0] < enemy2[0] + 30 and
        enemy1[0] + 30 > enemy2[0] and
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

def knockback(enemy_index, dx, dy):
    enemies[enemy_index][0] += dx * 10
    enemies[enemy_index][1] += dy * 10

knockback_velocity_x = 0
knockback_velocity_y = 0

def player_knockback(enemyX, enemyY):
    global knockback_velocity_x, knockback_velocity_y
    knockback_distance = 10
    dx = plrX - enemyX
    dy = plrY - enemyY
    distance = math.sqrt(dx ** 2 + dy ** 2)
    if distance != 0:
        dx /= distance
        dy /= distance
    knockback_velocity_x = dx * knockback_distance
    knockback_velocity_y = dy * knockback_distance


clock = pygame.time.Clock()

enemySpeed = 1.8
enemies = []

plrSpeed = 3
plrX = WIDTH // 2
plrY = HEIGHT // 2
plrIsFacingRight = True
plrHealth = 100
lastHitTime = 0

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

def spawnInitialEnemies():
    initial_enemy_count = random.randint(5, 10)
    for _ in range(initial_enemy_count):
        spawnEnemy()

xp = 0
xpOrbX = 0
xpOrbY = 0
xpOrbDX = 0
xpOrbDY = 0
xpOrbs = []


def spawnXP(enemyX, enemY):
    global xpOrbX, xpOrbY
    xpOrbX = enemyX
    xpOrbY = enemY

    xpOrbs.append([xpOrbX, xpOrbY])

def xpDistance(xpX, xpY):
    distance = math.sqrt((plrX - xpX) ** 2 + (plrY - xpY) ** 2)
    if distance == 0:
        return 0, 0
    xpOrbDX = (plrX - xpX) / distance
    xpOrbDY = (plrY - xpY) / distance
    return xpOrbDX, xpOrbDY

lastEnemySpawn = time.time()
enemySpawnSpeed = 1

difficulty = time.time()

second = 0
timePassed = time.time()

running = True

spawnInitialEnemies()

fireballX = 0
fireballY = 0
fireballDX = 0
fireballDY = 0
fireballExists = False
fireballAngle = 0
fireballRegenTime = 12
fireballRegen = 0
fireballAmount = 3

def spawnFireball(playerX, playerY, mouseX, mouseY):
    global fireballX, fireballY, fireballDX, fireballDY, fireballExists, fireballAngle, fireballAmount

    fireballAmount -= 1

    angle = math.atan2(mouseY - playerY, mouseX - playerX)
    fireballAngle = math.degrees(angle)
    
    fireballX = playerX - 32
    fireballY = playerY - 32

    fireballDX = math.cos(angle) * 15
    fireballDY = math.sin(angle) * 15
    
    fireballExists = True

healthBarX = 0
healthBarY = 0

def draw_health_bar(health, plrX, plrY):
    bar_width = 60
    bar_height = 10
    fill = (health / 100) * bar_width
    outline_rect = pygame.Rect(plrX - 15, plrY, bar_width, bar_height)
    fill_rect = pygame.Rect(plrX - 15, plrY, fill, bar_height)
    blank_rect = pygame.Rect(plrX - 15, plrY, bar_width, bar_height)
    pygame.draw.rect(window, (150, 0, 0), blank_rect)
    pygame.draw.rect(window, (255, 0, 0), fill_rect)
    pygame.draw.rect(window, (0, 0, 0), outline_rect, 2)

def draw_xp_bar(xp):
    bar_width = WIDTH
    bar_height = 50
    fill = (xp / 100) * bar_width
    outline_rect = pygame.Rect(0, 0, bar_width, bar_height)
    fill_rect = pygame.Rect(0, 0, fill, bar_height)
    blank_rect = pygame.Rect(0, 0, bar_width, bar_height)
    pygame.draw.rect(window, (0, 50, 0), blank_rect)
    pygame.draw.rect(window, (0, 255, 0), fill_rect)
    pygame.draw.rect(window, (0, 0, 0), outline_rect, 5)

def fireballLevelUp(cardPos):
    levelText = font.render(f"LVL:{fireballLevel}→{fireballLevel + 1}", True, (255, 255, 255))
    levelRect = levelText.get_rect(center=(cardPos - 24 + 180, HEIGHT // 2))
    
    infoText1 = levelFont.render("   Increase size and", True, (255, 255, 255))
    infoText2 = levelFont.render("lower cooldown", True, (255, 255, 255))

    infoRect1 = infoText1.get_rect(center=(cardPos - 50 + 180, HEIGHT // 2 + 50))
    infoRect2 = infoText2.get_rect(center=(cardPos - 50 + 180, HEIGHT // 2 + 80))

    
    window.blit(infoText1, infoRect1)
    window.blit(infoText2, infoRect2)
    
    window.blit(fireballIcon, (cardPos - 100 + 180, HEIGHT // 2 - 260))
    window.blit(levelText, levelRect)

card1Pos, card2Pos, card3Pos = WIDTH // 2 - 180, WIDTH // 4 - 180, WIDTH // 2 + 270

cards = [card1Pos, card2Pos, card3Pos]

def card1():
    global card1Pos
    window.blit(levelUpCard, (card1Pos, HEIGHT // 2 - 320))

def card2():
    global card2Pos
    window.blit(levelUpCard, (card2Pos, HEIGHT // 2 - 320))

def card3():
    global card3Pos
    window.blit(levelUpCard, (card3Pos, HEIGHT // 2 - 320))

onLevelUpScreen = True

fireballLevel = 1

abilities = ["fireball"]

randomCard = random.choice(cards)
randomAbility = random.sample(abilities, 1)

while running:
    mouseX, mouseY = pygame.mouse.get_pos()
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    if xp >= 100:
        onLevelUpScreen = True

    if onLevelUpScreen == True:
        card1()
        card2()
        card3()
        if randomAbility[0] == "fireball":
            fireballLevelUp(randomCard)
        if pygame.mouse.get_pressed()[0]:
            if mouseX >= WIDTH // 2 - 180 and mouseX <= WIDTH // 2 + 140 and mouseY >= HEIGHT // 2 - 320 and mouseY <= HEIGHT // 2 + 320:
                xp = 0
                fireballLevel += 1
                fireballRegenTime -= 1
                onLevelUpScreen = False
            

    elif onLevelUpScreen == False:
        minutes = second // 60
        seconds = second % 60
        timeText = font.render(f"{minutes}:{seconds:02}", True, (0, 0, 0))
        timeRect = timeText.get_rect(center=(WIDTH // 2, 100))

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

        if pygame.mouse.get_pressed()[0] and not fireballExists:
            spawnFireball(plrX + 16, plrY + 16, *pygame.mouse.get_pos())

        if moveX != 0 and moveY != 0:
            moveX *= math.sqrt(0.5)
            moveY *= math.sqrt(0.5)

        plrX += moveX * plrSpeed
        plrY += moveY * plrSpeed

        window.fill((85, 170, 0))

        if time.time() - difficulty > 20:
            enemySpawnSpeed = 0.9
        elif time.time() - difficulty > 50:
            enemySpawnSpeed = 0.8
        elif time.time() - difficulty > 100:
            enemySpawnSpeed = 0.6
        elif time.time() - difficulty > 150:
            enemySpawnSpeed = 0.5
        elif time.time() - difficulty > 400:
            enemySpawnSpeed = 0.4
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

        for i in range(len(enemies) - 1, -1, -1):
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
            if fireballX + 48 >= enemyX and fireballX <= enemyX + 30 and fireballY + 60 >= enemyY and fireballY <= enemyY + 32:
                enemies.pop(i)
                spawnXP(enemyX, enemyY)
            if plrX + 30 >= enemyX and plrX + 2 <= enemyX + 30 and plrY + 32 >= enemyY and plrY <= enemyY + 32:
                if time.time() - lastHitTime > 1:
                    plrHealth -= 10
                    player_knockback(enemyX, enemyY)
                    lastHitTime = time.time()
        for i in range(len(xpOrbs) - 1, -1, -1):
            xpX, xpY = xpOrbs[i]

            distance = math.sqrt((plrX - xpX) ** 2 + (plrY - xpY) ** 2)
            
            if distance < 120:
                if distance > 1:
                    xpOrbDX = (plrX - xpX) / distance * 2
                    xpOrbDY = (plrY - xpY) / distance * 2
                    xpX += xpOrbDX
                    xpY += xpOrbDY
            
            window.blit(xpOrb, (xpX, xpY))

            if plrX + 30 >= xpX and plrX + 2 <= xpX + 16 and plrY + 32 >= xpY and plrY <= xpY + 16:
                xp += 10
                xpOrbs.pop(i)
            else:
                xpOrbs[i] = [xpX, xpY]
        plrX += knockback_velocity_x
        plrY += knockback_velocity_y

        knockback_velocity_x *= 0.9
        knockback_velocity_y *= 0.9

        if plrX < 0:
            plrX = 0
        elif plrX + 30 > WIDTH:
            plrX = WIDTH - 30

        if plrY < 50:
            plrY = 50
        elif plrY + 32 > HEIGHT:
            plrY = HEIGHT - 32

        if time.time() - lastHitTime > 1:
            lastHitTime = 0
        draw_xp_bar(xp)
        draw_health_bar(plrHealth, plrX, plrY + 40)

        if fireballAmount <= 2:
            if time.time() - fireballRegen > fireballRegenTime:
                fireballAmount += 1
                fireballRegen = time.time()

        if fireballExists:
            rotated_fireball = pygame.transform.rotate(fireball, -fireballAngle - 90)
            window.blit(rotated_fireball, (fireballX, fireballY))
            fireballX += fireballDX
            fireballY += fireballDY
            if fireballX < -80 or fireballX > WIDTH + 80 or fireballY < -80 or fireballY > HEIGHT + 80:
                fireballExists = False
        window.blit(pygame.transform.flip(player, True, False) if not plrIsFacingRight else player, (plrX, plrY))
        window.blit(timeText, timeRect)
    pygame.display.update()
    clock.tick(60)