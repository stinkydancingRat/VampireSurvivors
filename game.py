import pygame
import math
import random
import time

pygame.init()
pygame.font.init()


class Game:
    def __init__(self):
        self.width, self.height = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        self.running = True
        self.on_level_up_screen = False
        self.second = 0
        self.time_passed = time.time()
        self.difficulty_start_time = time.time()
        self.last_enemy_spawn = time.time()
        self.enemy_spawn_speed = 0.5

        self.font = pygame.font.Font("pixelfont.ttf", 48)
        self.level_font = pygame.font.Font("pixelfont.ttf", 24)

        self.load_sprites()

        self.xp = 0
        self.xp_orbs = []

        self.abilities = ["fireball", " "]
        self.inventory = ["sword"]
        self.current_weapon = "sword"
        self.reset_level_up_cards()

        self.card1_pos = self.width // 2 - 180
        self.card2_pos = self.width // 4 - 180
        self.card3_pos = self.width // 2 + 270

        self.player = Player(self.width // 2, self.height // 2, self.player_sprite)

        self.sword = Sword(self)
        self.fireball_system = FireballSystem(self)

        self.enemies = []
        self.spawn_first_enemies()

        self.attacking = False

        self.last_weapon_switch = 0
        self.weapon_switch_cooldown = 0.3

    def load_sprites(self):
        sword_swing_image = pygame.image.load("sprites/swordSwing.png").convert_alpha()
        self.sword_swing_sprite = pygame.transform.scale(sword_swing_image, (90, 96))

        sword_image = pygame.image.load("sprites/sword.png").convert_alpha()
        self.sword_sprite = pygame.transform.scale(sword_image, (20, 32))

        level_up_card_image = pygame.image.load("sprites/levelUpCard.png").convert_alpha()
        self.level_up_card = pygame.transform.scale(level_up_card_image, (320, 640))

        xp_orb_image = pygame.image.load("sprites/xpOrb.png").convert_alpha()
        self.xp_orb_sprite = pygame.transform.scale(xp_orb_image, (16, 16))

        player_image = pygame.image.load("sprites/player.png").convert_alpha()
        self.player_sprite = pygame.transform.scale(player_image, (32, 32))

        enemy_image = pygame.image.load("sprites/enemy.png").convert_alpha()
        self.enemy_sprite = pygame.transform.scale(enemy_image, (32, 32))

        fireball_image = pygame.image.load("sprites/fireball.png").convert_alpha()
        self.fireball_image = fireball_image
        self.fireball_icon = pygame.transform.scale(fireball_image, (160, 200))

    def reset_level_up_cards(self):
        self.card1_ability = None
        self.card2_ability = None
        self.card3_ability = None

    def spawn_enemy(self):
        side = random.choice(['bottom', 'left', 'right'])

        if side == 'bottom':
            enemy_x = random.randint(0, self.width)
            enemy_y = self.height + 50
        elif side == 'left':
            enemy_x = -50
            enemy_y = random.randint(0, self.height)
        elif side == 'right':
            enemy_x = self.width + 50
            enemy_y = random.randint(0, self.height)

        enemy_is_facing_right = enemy_x < self.player.x
        self.enemies.append([enemy_x, enemy_y, enemy_is_facing_right, 10])

    def spawn_first_enemies(self):
        initial_enemy_count = random.randint(5, 10)
        for _ in range(initial_enemy_count):
            self.spawn_enemy()

    def spawn_xp(self, enemy_x, enemy_y):
        self.xp_orbs.append([enemy_x, enemy_y])

    def draw_health_bar(self, health, x, y):
        bar_width = 60
        bar_height = 10
        fill = (health / 100) * bar_width
        outline_rect = pygame.Rect(x - 15, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x - 15, y, fill, bar_height)
        blank_rect = pygame.Rect(x - 15, y, bar_width, bar_height)
        pygame.draw.rect(self.window, (150, 0, 0), blank_rect)
        pygame.draw.rect(self.window, (255, 0, 0), fill_rect)
        pygame.draw.rect(self.window, (0, 0, 0), outline_rect, 2)

    def draw_xp_bar(self):
        bar_width = self.width
        bar_height = 50
        fill = (self.xp / 100) * bar_width
        outline_rect = pygame.Rect(0, 0, bar_width, bar_height)
        fill_rect = pygame.Rect(0, 0, fill, bar_height)
        blank_rect = pygame.Rect(0, 0, bar_width, bar_height)
        pygame.draw.rect(self.window, (0, 50, 0), blank_rect)
        pygame.draw.rect(self.window, (0, 255, 0), fill_rect)
        pygame.draw.rect(self.window, (0, 0, 0), outline_rect, 5)

    def fireball_level_up(self, card_pos):

        level_text = self.font.render(f"LVL:{self.fireball_system.level}→{self.fireball_system.level + 1}", True,
                                      (255, 255, 255))
        level_rect = level_text.get_rect(center=(card_pos - 24 + 180, self.height // 2))

        info_text1 = self.level_font.render("   Increase size and", True, (255, 255, 255))
        info_text2 = self.level_font.render("lower cooldown", True, (255, 255, 255))

        info_rect1 = info_text1.get_rect(center=(card_pos - 50 + 180, self.height // 2 + 50))
        info_rect2 = info_text2.get_rect(center=(card_pos - 50 + 180, self.height // 2 + 80))

        self.window.blit(info_text1, info_rect1)
        self.window.blit(info_text2, info_rect2)

        self.window.blit(self.fireball_icon, (card_pos - 100 + 180, self.height // 2 - 260))
        self.window.blit(level_text, level_rect)

    def check_ability(self, card_pos, ability):
        if ability == "fireball":
            self.fireball_level_up(card_pos)

    def draw_card1(self):
        if self.card1_ability is None:
            available_abilities = [a for a in self.abilities if a not in [self.card2_ability, self.card3_ability]]
            if available_abilities:
                self.card1_ability = random.choice(available_abilities)

        self.window.blit(self.level_up_card, (self.card1_pos, self.height // 2 - 320))
        if self.card1_ability:
            self.check_ability(self.card1_pos, self.card1_ability)

    def draw_card2(self):
        if self.card2_ability is None:
            available_abilities = [a for a in self.abilities if a not in [self.card1_ability, self.card3_ability]]
            if available_abilities:
                self.card2_ability = random.choice(available_abilities)

        self.window.blit(self.level_up_card, (self.card2_pos, self.height // 2 - 320))
        if self.card2_ability:
            self.check_ability(self.card2_pos, self.card2_ability)

    def draw_card3(self):
        if self.card3_ability is None:
            available_abilities = [a for a in self.abilities if a not in [self.card1_ability, self.card2_ability]]
            if available_abilities:
                self.card3_ability = random.choice(available_abilities)

        self.window.blit(self.level_up_card, (self.card3_pos, self.height // 2 - 320))
        if self.card3_ability:
            self.check_ability(self.card3_pos, self.card3_ability)

    def level_up_ability_check(self, selected_card):
        if selected_card == self.card1_pos and self.card1_ability == "fireball" or \
                selected_card == self.card2_pos and self.card2_ability == "fireball" or \
                selected_card == self.card3_pos and self.card3_ability == "fireball":
            self.fireball_system.level_up(self.inventory)

    def attack(self):
        if self.current_weapon == "fireball" and self.fireball_system.amount > 0:
            mouse_pos = pygame.mouse.get_pos()
            self.fireball_system.spawn_fireball(self.player.x, self.player.y, mouse_pos[0], mouse_pos[1])
        elif self.current_weapon == "sword" and not self.sword.swinging and self.sword.can_swing:
            self.sword.start_swing()
        self.attacking = False

    def handle_level_up_screen(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        self.draw_card1()
        self.draw_card2()
        self.draw_card3()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.card1_pos <= mouse_x <= self.card1_pos + 320 and \
                            self.height // 2 - 320 <= mouse_y <= self.height // 2 + 320:
                        self.xp = 0
                        self.level_up_ability_check(self.card1_pos)
                        time.sleep(0.5)
                        self.on_level_up_screen = False
                        self.player.health += 10

                    if self.card2_pos <= mouse_x <= self.card2_pos + 320 and \
                            self.height // 2 - 320 <= mouse_y <= self.height // 2 + 320:
                        self.xp = 0
                        self.level_up_ability_check(self.card2_pos)
                        time.sleep(0.5)
                        self.on_level_up_screen = False
                        self.player.health += 10

                    if self.card3_pos <= mouse_x <= self.card3_pos + 320 and \
                            self.height // 2 - 320 <= mouse_y <= self.height // 2 + 320:
                        self.xp = 0
                        self.level_up_ability_check(self.card3_pos)
                        time.sleep(0.5)
                        self.on_level_up_screen = False
                        self.player.health += 10

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not self.on_level_up_screen:
                if event.button == 1:
                    self.attacking = True
            if event.type == pygame.KEYDOWN:
                self.switch_weapons(event.key)

        if self.xp >= 100:
            self.on_level_up_screen = True
            self.reset_level_up_cards()

    def switch_weapons(self, key):
        current_time = time.time()
        if current_time - self.last_weapon_switch < self.weapon_switch_cooldown:
            return

        if key == pygame.K_1 and "sword" in self.inventory:
            self.current_weapon = "sword"
            self.last_weapon_switch = current_time
        elif key == pygame.K_2 and "fireball" in self.inventory:
            self.current_weapon = "fireball"
            self.last_weapon_switch = current_time

    def update_difficulty(self):
        elapsed_time = time.time() - self.difficulty_start_time

        if elapsed_time > 20:
            self.enemy_spawn_speed = 0.4
        elif elapsed_time > 50:
            self.enemy_spawn_speed = 0.3
        elif elapsed_time > 100:
            self.enemy_spawn_speed = 0.2
        elif elapsed_time > 150:
            self.enemy_spawn_speed = 0.17
        elif elapsed_time > 400:
            self.enemy_spawn_speed = 0.15
        elif elapsed_time > 600:
            self.enemy_spawn_speed = 0.1
        elif elapsed_time > 800:
            self.enemy_spawn_speed = 0.05

    def update_xp_orbs(self):
        for i in range(len(self.xp_orbs) - 1, -1, -1):
            xp_x, xp_y = self.xp_orbs[i]

            distance = math.sqrt((self.player.x - xp_x) ** 2 + (self.player.y - xp_y) ** 2)

            if distance < 120:
                if distance > 1:
                    xp_orb_dx = (self.player.x - xp_x) / distance * 3.5
                    xp_orb_dy = (self.player.y - xp_y) / distance * 3.5
                    xp_x += xp_orb_dx
                    xp_y += xp_orb_dy

            self.window.blit(self.xp_orb_sprite, (xp_x, xp_y))

            if self.player.check_collision(xp_x, xp_y, 16, 16):
                self.xp += 2.5
                self.xp_orbs.pop(i)
            else:
                self.xp_orbs[i] = [xp_x, xp_y]

    def normalize(self, enemy_x, enemy_y):
        distance = math.sqrt((self.player.x - enemy_x) ** 2 + (self.player.y - enemy_y) ** 2)
        if distance == 0:
            return 0, 0
        dx = (self.player.x - enemy_x) / distance
        dy = (self.player.y - enemy_y) / distance
        return dx, dy

    def separation(self, enemy_index):
        separation_force_x = 0
        separation_force_y = 0
        for i, (other_enemy_x, other_enemy_y, _, _) in enumerate(self.enemies):
            if i != enemy_index:
                distance = math.sqrt((self.enemies[enemy_index][0] - other_enemy_x) ** 2 +
                                     (self.enemies[enemy_index][1] - other_enemy_y) ** 2)
                if distance < 32:
                    separation_force_x += (self.enemies[enemy_index][0] - other_enemy_x) / distance
                    separation_force_y += (self.enemies[enemy_index][1] - other_enemy_y) / distance
        return separation_force_x, separation_force_y

    def draw_game(self):
        self.window.fill((85, 170, 0))

        self.draw_xp_bar()

        self.draw_health_bar(self.player.health, self.player.x, self.player.y + 40)

        self.player.draw(self.window)

        self.draw_current_weapon()

        minutes = self.second // 60
        seconds = self.second % 60
        time_text = self.font.render(f"{minutes}:{seconds:02}", True, (0, 0, 0))
        time_rect = time_text.get_rect(center=(self.width // 2, 100))
        self.window.blit(time_text, time_rect)

        self.draw_weapon_ui()

    def draw_current_weapon(self):
        if self.current_weapon == "sword":
            if self.sword.swinging:
                self.sword.draw_swing(self.window)
            else:
                self.sword.draw_idle(self.window)

    def draw_weapon_ui(self):
        weapons_text = self.level_font.render("Weapons:", True, (0, 0, 0))
        self.window.blit(weapons_text, (10, 60))

        for i, weapon in enumerate(self.inventory):
            if weapon == self.current_weapon:
                color = (255, 255, 0)
            else:
                color = (255, 255, 255)

            weapon_text = self.level_font.render(f"{i + 1}: {weapon.capitalize()}", True, color)
            self.window.blit(weapon_text, (10, 90 + i * 30))

            if weapon == "fireball" and weapon == self.current_weapon:
                ammo_text = self.level_font.render(
                    f"Ammo: {self.fireball_system.amount}/{self.fireball_system.max_amount}", True, color)
                self.window.blit(ammo_text, (200, 90 + i * 30))

    def update_game_state(self):
        if self.player.health >= 100:
            self.player.health = 100

        if time.time() - self.time_passed >= 1:
            self.second += 1
            self.time_passed = time.time()

        self.update_difficulty()

        if time.time() - self.last_enemy_spawn > self.enemy_spawn_speed:
            self.spawn_enemy()
            self.last_enemy_spawn = time.time()

        self.player.update()

        self.sword.update(self.player.x, self.player.y, self.player.is_facing_right)

        self.fireball_system.update()

        if self.attacking:
            self.attack()

    def attack(self):
        if self.current_weapon == "fireball" and self.fireball_system.amount > 0:
            mouse_pos = pygame.mouse.get_pos()
            self.fireball_system.spawn_fireball(self.player.x, self.player.y, mouse_pos[0], mouse_pos[1])
        elif self.current_weapon == "sword" and not self.sword.swinging and self.sword.can_swing:
            self.sword.start_swing()
        self.attacking = False

    def update_enemies(self):
        for i in range(len(self.enemies) - 1, -1, -1):
            enemy_x, enemy_y, enemy_is_facing_right, enemy_health = self.enemies[i]

            dx, dy = self.normalize(enemy_x, enemy_y)
            sep_force_x, sep_force_y = self.separation(i)
            dx += sep_force_x
            dy += sep_force_y

            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance != 0:
                dx /= distance
                dy /= distance

            enemy_x += dx * 1
            enemy_y += dy * 1

            self.enemies[i] = [enemy_x, enemy_y, enemy_is_facing_right, enemy_health]

            self.window.blit(pygame.transform.flip(self.enemy_sprite, True, False)
                             if not enemy_is_facing_right else self.enemy_sprite, (enemy_x, enemy_y))

            enemy_hit = False
            for j in range(len(self.fireball_system.active_fireballs) - 1, -1, -1):
                fireball = self.fireball_system.active_fireballs[j]
                if fireball.check_collision(enemy_x, enemy_y, 30, 32):
                    enemy_hit = True

                    should_destroy = fireball.hit_enemy()
                    if should_destroy:
                        self.fireball_system.active_fireballs.pop(j)
                    break

            if enemy_hit:
                self.enemies.pop(i)
                self.spawn_xp(enemy_x, enemy_y)
                continue

            if self.sword.swinging and self.sword.check_collision(enemy_x, enemy_y, 30, 32):
                self.enemies.pop(i)
                self.spawn_xp(enemy_x, enemy_y)
                continue

            if self.player.check_collision(enemy_x, enemy_y, 30, 32):
                if time.time() - self.player.last_hit_time > 1:
                    self.player.health -= 10
                    self.player.apply_knockback(enemy_x, enemy_y)
                    self.player.last_hit_time = time.time()

    def run(self):
        while self.running:
            self.fireball = pygame.transform.scale(self.fireball_image, self.fireball_system.size)

            if self.on_level_up_screen:
                self.handle_level_up_screen()
            else:
                self.handle_input()
                self.update_game_state()
                self.draw_game()
                self.update_enemies()
                self.update_xp_orbs()

                for fireball in self.fireball_system.active_fireballs:
                    fireball.draw(self.window, self.fireball)

            pygame.display.update()
            self.clock.tick(60)


class Player:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.is_facing_right = True
        self.speed = 3
        self.health = 100
        self.last_hit_time = 0
        self.knockback_velocity_x = 0
        self.knockback_velocity_y = 0

    def update(self):
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0

        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x + 2 > 0:
            move_x = -1
            self.is_facing_right = False

        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x + 30 < pygame.display.Info().current_w:
            move_x = 1
            self.is_facing_right = True

        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.y > 0:
            move_y = -1

        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.y + 32 < pygame.display.Info().current_h:
            move_y = 1

        if move_x != 0 and move_y != 0:
            move_x *= math.sqrt(0.5)
            move_y *= math.sqrt(0.5)

        self.x += move_x * self.speed
        self.y += move_y * self.speed

        self.x += self.knockback_velocity_x
        self.y += self.knockback_velocity_y

        self.knockback_velocity_x *= 0.9
        self.knockback_velocity_y *= 0.9

        if self.x < 0:
            self.x = 0
        elif self.x + 30 > pygame.display.Info().current_w:
            self.x = pygame.display.Info().current_w - 30

        if self.y < 50:
            self.y = 50
        elif self.y + 32 > pygame.display.Info().current_h:
            self.y = pygame.display.Info().current_h - 32

    def draw(self, window):
        window.blit(pygame.transform.flip(self.sprite, True, False)
                    if not self.is_facing_right else self.sprite, (self.x, self.y))

    def apply_knockback(self, enemy_x, enemy_y):
        knockback_distance = 10
        dx = self.x - enemy_x
        dy = self.y - enemy_y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance != 0:
            dx /= distance
            dy /= distance
        self.knockback_velocity_x = dx * knockback_distance
        self.knockback_velocity_y = dy * knockback_distance

    def check_collision(self, obj_x, obj_y, obj_width, obj_height):
        return (
                self.x + 30 >= obj_x and
                self.x + 2 <= obj_x + obj_width and
                self.y + 32 >= obj_y and
                self.y <= obj_y + obj_height
        )


class Sword:
    def __init__(self, game):
        self.game = game
        self.swinging = False
        self.can_swing = True
        self.swing_time = time.time()
        self.cooldown_time = time.time()
        self.swinging_time = 0.2
        self.cooldown_duration = 1.5
        self.x = 0
        self.y = 0
        self.is_facing_right = True

    def update(self, player_x, player_y, player_is_facing_right):
        self.x = player_x
        self.y = player_y
        self.is_facing_right = player_is_facing_right

        if time.time() - self.swing_time > self.swinging_time:
            self.swinging = False
            self.swing_time = time.time()

        if time.time() - self.cooldown_time > self.cooldown_duration:
            self.can_swing = True
            self.cooldown_time = time.time()

    def start_swing(self):
        self.swinging = True
        self.can_swing = False
        self.cooldown_time = time.time()

    def draw_swing(self, window):
        if self.is_facing_right:
            window.blit(self.game.sword_swing_sprite, (self.x, self.y - 32))
        else:
            window.blit(pygame.transform.flip(self.game.sword_swing_sprite, True, False), (self.x - 54, self.y - 32))

    def draw_idle(self, window):
        if self.is_facing_right:
            window.blit(self.game.sword_sprite, (self.x + 24, self.y + 5))
        else:
            window.blit(self.game.sword_sprite, (self.x - 8, self.y + 5))

    def check_collision(self, enemy_x, enemy_y, enemy_width, enemy_height):
        if not self.swinging:
            return False

        if self.is_facing_right:
            return (
                    self.x + 90 >= enemy_x and
                    self.x + 2 <= enemy_x + enemy_width and
                    self.y + 48 >= enemy_y and
                    self.y - 48 <= enemy_y + enemy_height
            )
        else:
            return (
                    self.x >= enemy_x and
                    self.x - 52 <= enemy_x + enemy_width and
                    self.y + 48 >= enemy_y and
                    self.y - 48 <= enemy_y + enemy_height
            )


class Fireball:
    def __init__(self, x, y, angle, dx, dy, size):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.angle = angle
        self.size = size
        self.enemies_hit = 0
        self.max_enemies = 10

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, window, sprite):
        rotated_fireball = pygame.transform.rotate(sprite, -self.angle - 90)
        window.blit(rotated_fireball, (self.x, self.y))

    def check_collision(self, enemy_x, enemy_y, enemy_width, enemy_height):
        return (
                self.x + self.size[0] >= enemy_x and
                self.x <= enemy_x + enemy_width and
                self.y + self.size[1] >= enemy_y and
                self.y <= enemy_y + enemy_height
        )

    def is_out_of_bounds(self, width, height):
        return (
                self.x < -200 or
                self.x > width + 200 or
                self.y < -200 or
                self.y > height + 200
        )

    def hit_enemy(self):
        self.enemies_hit += 1
        return self.enemies_hit >= self.max_enemies


class FireballSystem:
    def __init__(self, game):
        self.game = game
        self.size = (32, 40)
        self.level = 0
        self.amount = 3
        self.max_amount = 3
        self.regen_time = 12
        self.active_fireballs = []
        self.last_regen = None  # Initialize to None to indicate no regeneration in progress
        self.cooldown = 0.5
        self.last_fireball_time = 0

    def update(self):
        if self.amount < self.max_amount:
            if self.last_regen is None:
                self.last_regen = time.time()

            elif time.time() - self.last_regen > self.regen_time:
                self.amount += 1
                self.last_regen = time.time()
                if self.amount >= self.max_amount:
                    self.last_regen = None

        for i in range(len(self.active_fireballs) - 1, -1, -1):
            fireball = self.active_fireballs[i]
            fireball.update()
            if fireball.is_out_of_bounds(self.game.width, self.game.height):
                self.active_fireballs.pop(i)

    def spawn_fireball(self, player_x, player_y, mouse_x, mouse_y):
        current_time = time.time()
        if self.amount <= 0 or current_time - self.last_fireball_time < self.cooldown:
            return

        self.amount -= 1

        if self.last_regen is None and self.amount < self.max_amount:
            self.last_regen = current_time

        self.last_fireball_time = current_time

        angle = math.atan2(mouse_y - player_y, mouse_x - player_x)
        angle_degrees = math.degrees(angle)

        fireball_x = player_x + 16 - self.size[0] // 2
        fireball_y = player_y + 16 - self.size[1] // 2

        fireball_dx = math.cos(angle) * 15
        fireball_dy = math.sin(angle) * 15

        new_fireball = Fireball(fireball_x, fireball_y, angle_degrees, fireball_dx, fireball_dy, self.size)
        self.active_fireballs.append(new_fireball)

    def level_up(self, inventory):
        self.inventory = inventory
        if "fireball" not in self.inventory:
            self.inventory.append("fireball")
        self.level += 1
        if self.regen_time > 3:
            self.regen_time -= 0.5
        self.size = (self.size[0] + 8, self.size[1] + 10)
        self.cooldown = max(0.1, self.cooldown - 0.05)

if __name__ == "__main__":
    game = Game()
    game.run()