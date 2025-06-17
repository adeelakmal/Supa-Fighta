import pygame
import config

class Player:
    def __init__(self, x, y, net):
        self.rect = pygame.Rect(x, y, config.PLAYER_SIZE, config.PLAYER_SIZE)
        self.color = config.PLAYER_COLOR
        self.speed = 5
        self.net = net
    def handle_keys(self):
        keys = pygame.key.get_pressed()

        moved = False
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            moved = True
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            moved = True
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
            moved = True
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
            moved = True

        # if moved:
        #     self.rect.move_ip(dx, dy)    # local prediction
        #     # tell the server; keep the payload tiny
        #     self.net.send("move", {"dx": dx, "dy": dy})

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
