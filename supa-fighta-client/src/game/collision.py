from game.player import Player
from game.opponent import Opponent
import pygame

DEBUG = True

class Collision:
    def check_collision(player: Player, opponent: Opponent) -> bool:

        player_hurtbox = player.get_hurtbox()
        player_hitbox = player.get_hitbox()
        opponent_hurtbox = opponent.get_hurtbox()
        opponent_hitbox = opponent.get_hitbox()
       
        if player_hitbox and player_hitbox.colliderect(opponent_hurtbox):
            if DEBUG:
                print(f"Player Wins! Player Hitbox: {player_hitbox}, Opponent Hurtbox: {opponent_hurtbox}")
            return True
        elif opponent_hitbox and opponent_hitbox.colliderect(player_hurtbox):
            if DEBUG:
                print(f"Opponent Wins! Opponent Hitbox: {opponent_hitbox}, Player Hurtbox: {player_hurtbox}")
            return True
        return False
    def debug_draw(surface: pygame.Surface, player: Player, opponent: Opponent):
        player_hurtbox = player.get_hurtbox()
        player_hitbox = player.get_hitbox()
        opponent_hurtbox = opponent.get_hurtbox()
        opponent_hitbox = opponent.get_hitbox()

        if player_hurtbox:
            pygame.draw.rect(surface, (0, 255, 0), player_hurtbox, 1)
        if player_hitbox:
            pygame.draw.rect(surface, (255, 0, 0), player_hitbox, 1)
        if opponent_hurtbox:
            pygame.draw.rect(surface, (0, 255, 0), opponent_hurtbox, 1)
        if opponent_hitbox:
            pygame.draw.rect(surface, (255, 0, 0), opponent_hitbox, 1)