from game.player import Player
import pygame

DEBUG = True

class Collision:
    def __init__(self, players: list[Player]):
        self.players = players

    def check_collisions(self):
        player1, player2 = self.players
        if self.is_colliding(player1, player2):
            self.handle_collision(player1, player2)

    def is_colliding(self, player1: Player, player2: Player) -> bool:
        rect1 = pygame.Rect(player1.player_x, player1.player_y, 120, 120)
        rect2 = pygame.Rect(player2.player_x, player2.player_y, 120, 120)
        return rect1.colliderect(rect2)

    def handle_collision(self, player1: Player, player2: Player):
        if DEBUG:
            print(f"Collision detected between Player {id(player1)} and Player {id(player2)}")
        # Simple collision response: stop movement
        if player1.velocity > 0:  # Moving right
            player1.player_x = player2.player_x - 120
        elif player1.velocity < 0:  # Moving left
            player1.player_x = player2.player_x + 120
        if player2.velocity > 0:  # Moving right
            player2.player_x = player1.player_x - 120
        elif player2.velocity < 0:  # Moving left
            player2.player_x = player1.player_x + 120