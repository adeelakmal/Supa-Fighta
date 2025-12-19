from game.player import Player
from game.opponent import Opponent
import pygame

DEBUG = True

class Collision:
    def check_overlap(player: Player, opponent: Opponent) -> bool:
        player_hurtbox = player.get_hurtbox()
        opponent_hurtbox = opponent.get_hurtbox()
        if player_hurtbox and opponent_hurtbox:
            return player_hurtbox.colliderect(opponent_hurtbox)
        return False
    def check_collision(player: Player, opponent: Opponent) -> bool:

        player_hurtbox = player.get_hurtbox()
        player_hitbox = player.get_hitbox()
        opponent_hurtbox = opponent.get_hurtbox()
        opponent_hitbox = opponent.get_hitbox()
       
        if player_hitbox and player_hitbox.colliderect(opponent_hurtbox):
            if DEBUG and player.player_state!="parry":
                print(f"Player Wins! Player Hitbox: {player_hitbox}, Opponent Hurtbox: {opponent_hurtbox}")
            if opponent.opponent_state!="parry":
                opponent.set_state('hurt')
                opponent.set_hurt(opponent.opponent_x)
                return True
            else:
                if DEBUG:
                    print("Opponent parried the attack!")
                opponent.set_state('parry-hit')
                player.set_state('parried')
                player.recovery_until+=300
        elif opponent_hitbox and opponent_hitbox.colliderect(player_hurtbox):
            if DEBUG and opponent.opponent_state!="parry":
                print(f"Opponent Wins! Opponent Hitbox: {opponent_hitbox}, Player Hurtbox: {player_hurtbox}")
            if player.player_state!="parry":
                player.set_state('hurt')
                player.set_hurt(player.player_x)
                return True
            else:
                if DEBUG:
                    print("Player parried the attack!")
                player.set_state('parry-hit')
                opponent.set_state('parried')
                opponent.recovery_until+=300
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