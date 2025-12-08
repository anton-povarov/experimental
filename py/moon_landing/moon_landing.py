import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.SysFont(None, 20)

lander_height = 20
lander_width = 30

lander_x = 300
lander_y = 100
vy = 0
vx = 0
gravity = 0.1
thrust = 0.3
thrust_horizontal = 0.5

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    key = pygame.key.get_pressed()
    if key[pygame.K_UP]:
        vy -= thrust

    if key[pygame.K_DOWN]:
        vy += thrust

    if key[pygame.K_LEFT]:
        vx -= thrust_horizontal

    if key[pygame.K_RIGHT]:
        vx += thrust_horizontal

    # fall until hitting the ground
    collision_down = (lander_y + lander_height / 2) >= screen.get_height()
    if collision_down:
        if vy > 0:
            vy = 0
    else:
        vy += gravity

    lander_x += vx
    lander_y += vy
    lander_x = max(0 + lander_width / 2, lander_x)
    lander_x = min(screen.get_width() - lander_width / 2, lander_x)
    lander_y = min(screen.get_height() - lander_height / 2, lander_y)

    # Draw
    screen.fill((10, 10, 10))
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        (lander_x - lander_width / 2, lander_y - lander_height / 2, lander_width, lander_height),
    )
    info = f"velocity: ({vx:.2f}, {vy:.2f}), pos: {lander_x:.3f}, {lander_y:.3f}"
    text_surface = font.render(info, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))
    pygame.display.flip()
    clock.tick(30)
