import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))

# SPRITES

playerImage = pygame.image.load("player.png")
player = pygame.transform.scale(playerImage, (32, 32))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    window.fill((255, 255, 255))
    window.blit(player, (WIDTH // 2, HEIGHT // 2))
    pygame.display.update()
    clock.tick(60)