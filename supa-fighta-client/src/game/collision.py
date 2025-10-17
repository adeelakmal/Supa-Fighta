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