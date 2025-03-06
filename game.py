import pygame
import math
import random
import time

pygame.init()
pygame.font.init()

#Original size is 16 by 20
fireballSize = (32, 40)

font = pygame.font.Font("pixelfont.ttf", 48)
levelFont = pygame.font.Font("pixelfont.ttf", 24)

WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# SPRITES
swordSwingImage = pygame.image.load("sprites/swordSwing.png")
swordSwing = pygame.transform.scale(swordSwingImage, (90, 96))

swordImage = pygame.image.load("sprites/sword.png")
sword = pygame.transform.scale(swordImage, (20, 32))

levelUpCardImage = pygame.image.load("sprites/levelUpCard.png")
levelUpCard = pygame.transform.scale(levelUpCardImage, (320, 640))

xpOrbImage = pygame.image.load("sprites/xpOrb.png")
xpOrb = pygame.transform.scale(xpOrbImage, (16, 16))

playerImage = pygame.image.load("sprites/player.png")
player = pygame.transform.scale(playerImage, (32, 32))

enemyImage = pygame.image.load("sprites/enemy.png")
enemy = pygame.transform.scale(enemyImage, (32, 32))

fireballImage = pygame.image.load("sprites/fireball.png")
fireballIcon = pygame.transform.scale(fireballImage, (160, 200))

swingingTime = 0.2
swingTime = time.time()
swinging = False
swordCooldown = time.time()
swordCooldownTime = 1.5
canSwing = True


class Sword:
    def __init__(self, plrX, plrY, is_facing_right, swinging):
        self.x = plrX
        self.y = plrY
        self.is_facing_right = is_facing_right
        self.swinging = swinging

    def swing(self):
        self.swinging = True
        if self.is_facing_right:
            window.blit(swordSwing, (self.x, self.y - 32))
        else:
            window.blit(pygame.transform.flip(swordSwing, True, False), (self.x - 54, self.y - 32))

    def idle(self):
        self.swinging = False
        if self.is_facing_right:
            window.blit(sword, (self.x + 24, self.y + 5))
        else:
            window.blit(sword, (self.x - 8, self.y + 5))


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
    for i, (other_enemyX, other_enemyY, _, _) in enumerate(enemies):
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

enemySpeed = 1
enemyHealth = 10
enemies = []

plrSpeed = 3
plrX = WIDTH // 2
plrY = HEIGHT // 2
plrIsFacingRight = True
plrHealth = 100
lastHitTime = 0


def spawn_enemy():
    side = random.choice(['bottom', 'left', 'right'])

    if side == 'bottom':
        enemyX = random.randint(0, WIDTH)
        enemyY = HEIGHT + 50
    elif side == 'left':
        enemyX = -50
        enemyY = random.randint(0, HEIGHT)
    elif side == 'right':
        enemyX = WIDTH + 50
        enemyY = random.randint(0, HEIGHT)

    enemyIsFacingRight = enemyX < plrX
    enemies.append([enemyX, enemyY, enemyIsFacingRight, enemyHealth])


def spawn_first_enemies():
    initial_enemy_count = random.randint(5, 10)
    for _ in range(initial_enemy_count):
        spawn_enemy()


xp = 0
xpOrbX = 0
xpOrbY = 0
xpOrbDX = 0
xpOrbDY = 0
xpOrbs = []


def spawn_xp(enemyX, enemY):
    global xpOrbX, xpOrbY
    xpOrbX = enemyX
    xpOrbY = enemY

    xpOrbs.append([xpOrbX, xpOrbY])


def xp_distance(xpX, xpY):
    distance = math.sqrt((plrX - xpX) ** 2 + (plrY - xpY) ** 2)
    if distance == 0:
        return 0, 0
    xpOrbDX = (plrX - xpX) / distance
    xpOrbDY = (plrY - xpY) / distance
    return xpOrbDX, xpOrbDY


lastEnemySpawn = time.time()
enemySpawnSpeed = 0.5

difficulty = time.time()

second = 0
timePassed = time.time()

running = True

spawn_first_enemies()

fireballX = 0
fireballY = 0
fireballDX = 0
fireballDY = 0
fireballExists = False
fireballAngle = 0
fireballRegenTime = 12
fireballRegen = time.time()
fireballAmount = 3
fireballMaxAmount = 3


def spawn_fireball(playerX, playerY, mouseX, mouseY):
    global fireballX, fireballY, fireballDX, fireballDY, fireballExists, fireballAngle, fireballAmount

    fireballAmount -= 1

    angle = math.atan2(mouseY - playerY, mouseX - playerX)
    fireballAngle = math.degrees(angle)

    fireballX = playerX - fireballSize[0]
    fireballY = playerY - fireballSize[1]

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


fireballLevel = 0

abilities = ["fireball", " "]
card1_ability = None
card2_ability = None
card3_ability = None

card1_pos, card2_pos, card3_pos = WIDTH // 2 - 180, WIDTH // 4 - 180, WIDTH // 2 + 270
inventory = ["sword"]
currentWeapon = "sword"


def fireball_level_up(card_pos: int) -> None:
    if "fireball" not in inventory:
        inventory.append("fireball")
    levelText = font.render(f"LVL:{fireballLevel}→{fireballLevel + 1}", True, (255, 255, 255))
    levelRect = levelText.get_rect(center=(card_pos - 24 + 180, HEIGHT // 2))

    infoText1 = levelFont.render("   Increase size and", True, (255, 255, 255))
    infoText2 = levelFont.render("lower cooldown", True, (255, 255, 255))

    infoRect1 = infoText1.get_rect(center=(card_pos - 50 + 180, HEIGHT // 2 + 50))
    infoRect2 = infoText2.get_rect(center=(card_pos - 50 + 180, HEIGHT // 2 + 80))

    window.blit(infoText1, infoRect1)
    window.blit(infoText2, infoRect2)

    window.blit(fireballIcon, (card_pos - 100 + 180, HEIGHT // 2 - 260))
    window.blit(levelText, levelRect)


def check_ability(card_pos: int, ability: str):
    if ability == "fireball":
        fireball_level_up(card_pos)


def card1():
    global card1_ability
    if card1_ability is None:
        available_abilities = [a for a in abilities if a not in [card2_ability, card3_ability]]
        if available_abilities:
            card1_ability = random.choice(available_abilities)

    window.blit(levelUpCard, (card1_pos, HEIGHT // 2 - 320))
    if card1_ability:
        check_ability(card1_pos, card1_ability)


def card2():
    global card2_ability
    if card2_ability is None:
        available_abilities = [a for a in abilities if a not in [card1_ability, card3_ability]]
        if available_abilities:
            card2_ability = random.choice(available_abilities)

    window.blit(levelUpCard, (card2_pos, HEIGHT // 2 - 320))
    if card2_ability:
        check_ability(card2_pos, card2_ability)


def card3():
    global card3_ability
    if card3_ability is None:
        available_abilities = [a for a in abilities if a not in [card1_ability, card2_ability]]
        if available_abilities:
            card3_ability = random.choice(available_abilities)

    window.blit(levelUpCard, (card3_pos, HEIGHT // 2 - 320))
    if card3_ability:
        check_ability(card3_pos, card3_ability)


def reset_level_up_abilities():
    global card1_ability, card2_ability, card3_ability
    card1_ability = None
    card2_ability = None
    card3_ability = None


def level_up_ability_check(selected_card):
    global fireballLevel, fireballRegenTime, fireballSize, xp
    if selected_card == card1_pos and card1_ability == "fireball" or selected_card == card2_pos and card2_ability == "fireball" or selected_card == card3_pos and card3_ability == "fireball":
        fireballLevel += 1
        fireballRegenTime -= 1
        fireballSize = (fireballSize[0] + 8, fireballSize[1] + 10)


attacking = False


def attack() -> None:
    global attacking, swinging, fireballAmount, currentWeapon, canSwing
    if fireballAmount > 0 and currentWeapon == "fireball":
        spawn_fireball(plrX, plrY, *pygame.mouse.get_pos())
    if currentWeapon == "sword" and not swinging and canSwing:
        swinging = True
        canSwing = False
    attacking = False


on_level_up_screen: bool = False

while running:
    fireball = pygame.transform.scale(fireballImage, fireballSize)
    mouseX, mouseY = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not on_level_up_screen:
            if event.button == 1:
                attacking = True

    if xp >= 100:
        randomAbility = random.sample(abilities, 1)
        on_level_up_screen = True

    if on_level_up_screen:
        card1()
        card2()
        card3()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if mouseX >= card1_pos and mouseX <= card1_pos + 320 and mouseY >= HEIGHT // 2 - 320 and mouseY <= HEIGHT // 2 + 320:
                        xp = 0
                        level_up_ability_check(card1_pos)
                        time.sleep(0.5)
                        on_level_up_screen = False
                        plrHealth += 10

                    if mouseX >= card2_pos and mouseX <= card2_pos + 320 and mouseY >= HEIGHT // 2 - 320 and mouseY <= HEIGHT // 2 + 320:
                        xp = 0
                        level_up_ability_check(card2_pos)
                        time.sleep(0.5)
                        on_level_up_screen = False
                        plrHealth += 10

                    if mouseX >= card3_pos and mouseX <= card3_pos + 320 and mouseY >= HEIGHT // 2 - 320 and mouseY <= HEIGHT // 2 + 320:
                        xp = 0
                        level_up_ability_check(card3_pos)
                        time.sleep(0.5)
                        on_level_up_screen = False
                        plrHealth += 10

    elif on_level_up_screen == False:
        if plrHealth >= 100:
            plrHealth = 100
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

        if keys[pygame.K_1]:
            currentWeapon = "sword"

        if keys[pygame.K_2] and len(inventory) >= 2:
            currentWeapon = inventory[1]

        if moveX != 0 and moveY != 0:
            moveX *= math.sqrt(0.5)
            moveY *= math.sqrt(0.5)

        plrX += moveX * plrSpeed
        plrY += moveY * plrSpeed

        window.fill((85, 170, 0))

        if time.time() - difficulty > 20:
            enemySpawnSpeed = 0.4
        elif time.time() - difficulty > 50:
            enemySpawnSpeed = 0.3
        elif time.time() - difficulty > 100:
            enemySpawnSpeed = 0.2
        elif time.time() - difficulty > 150:
            enemySpawnSpeed = 0.17
        elif time.time() - difficulty > 400:
            enemySpawnSpeed = 0.15
        elif time.time() - difficulty > 600:
            enemySpawnSpeed = 0.1
        elif time.time() - difficulty > 800:
            enemySpawnSpeed = 0.05

        if time.time() - lastEnemySpawn > enemySpawnSpeed:
            spawn_enemy()
            lastEnemySpawn = time.time()

        if time.time() - timePassed >= 1:
            second += 1
            timePassed = time.time()

        for i in range(len(enemies) - 1, -1, -1):
            enemyX, enemyY, enemyIsFacingRight, enemyHealth = enemies[i]
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

            enemies[i] = [enemyX, enemyY, enemyIsFacingRight, enemyHealth]
            window.blit(pygame.transform.flip(enemy, True, False) if not enemyIsFacingRight else enemy,
                        (enemyX, enemyY))
            if fireballX + fireballSize[0] >= enemyX and fireballX <= enemyX + 30 and fireballY + fireballSize[
                1] >= enemyY and fireballY <= enemyY + 32:
                enemies.pop(i)
                spawn_xp(enemyX, enemyY)
            if swinging and ((
                                     plrIsFacingRight and plrX + 90 >= enemyX and plrX + 2 <= enemyX + 30 and plrY + 48 >= enemyY and plrY - 48 <= enemyY + 32) or (
                                     plrX >= enemyX and plrX - 52 <= enemyX + 30 and plrY + 48 >= enemyY and plrY - 48 <= enemyY + 32)):
                enemies.pop(i)
                spawn_xp(enemyX, enemyY)
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
                    xpOrbDX = (plrX - xpX) / distance * 3.5
                    xpOrbDY = (plrY - xpY) / distance * 3.5
                    xpX += xpOrbDX
                    xpY += xpOrbDY

            window.blit(xpOrb, (xpX, xpY))

            if plrX + 30 >= xpX and plrX + 2 <= xpX + 16 and plrY + 32 >= xpY and plrY <= xpY + 16:
                xp += 3
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
            if time.time() - fireballRegenTime > fireballRegen:
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

        if time.time() - swingTime > swingingTime:
            swinging = False
            swingTime = time.time()
        if currentWeapon == "sword":
            Sword(plrX, plrY, plrIsFacingRight, swinging).idle()
        if time.time() - swordCooldown > swordCooldownTime:
            canSwing = True
            swordCooldown = time.time()

        if attacking:
            attack()

        if swinging:
            Sword(plrX, plrY, plrIsFacingRight, swinging).swing()

        window.blit(timeText, timeRect)
    pygame.display.update()
    clock.tick(60)
