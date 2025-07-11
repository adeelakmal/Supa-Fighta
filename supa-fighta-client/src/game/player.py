from animations.sprites import SpriteSheet
from animations.animation import Animator
import pygame
import config

class Player:
    def __init__(self, x, y, net):
        self.player_sprites = {
            "idel": SpriteSheet("./supa-fighta-client/assets/Idel.png").get_sprites(120, 120, 1, 5),
        }
        self.player_animations = {
            "idel": Animator(self.player_sprites["idel"], frame_rate=15, loop=True),
        }
        self.player_x = x
        self.player_y = y
        self.color = config.PLAYER_COLOR
        self.speed = 2
        self.net = net
    def handle_keys(self):
        keys = pygame.key.get_pressed()

        moved = False
        
        if keys[pygame.K_LEFT]:
            self.player_x -= self.speed
            moved = True
        if keys[pygame.K_RIGHT]:
            self.player_x += self.speed
            moved = True
        if keys[pygame.K_UP]:
            self.player_y -= self.speed
            moved = True
        if keys[pygame.K_DOWN]:
            self.player_y += self.speed
            moved = True

        # if moved:
        #     self.rect.move_ip(dx, dy)    # local prediction
        #     # tell the server; keep the payload tiny
        #     self.net.send("move", {"dx": dx, "dy": dy})
    def update(self):
        self.player_animations["idel"].update()

    def draw(self, surface):
        self.player_animations["idel"].draw(surface, (self.player_x, self.player_y))
