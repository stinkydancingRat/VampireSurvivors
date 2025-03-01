import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))

# SPRITES

playerImage = pygame.image.load("player.png")
player = pygame.transform.scale(playerImage, (32, 32))
clock = pygame.time.Clock()

plrSpeed = 3
plrX = WIDTH // 2
plrY = HEIGHT // 2
plrIsFacingRight = True

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        plrX -= plrSpeed
        plrIsFacingRight = False
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        plrX += plrSpeed
        plrIsFacingRight = True
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        plrY -= plrSpeed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        plrY += plrSpeed

    window.fill((255, 255, 255))
    window.blit(pygame.transform.flip(player, True, False) if not plrIsFacingRight else player, (plrX, plrY))
    pygame.display.update()
    clock.tick(60)