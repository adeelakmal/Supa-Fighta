import pygame, sys, config, argparse
from game.stateManager import GameState
from game_display import GameDisplay
from player_manager import load_player_credentials
from settings_store import load_display_resolution, save_display_resolution

def main(PlayerDataFile="player_credentials.json"):
    pygame.init()
    config.PLAYER_DATA_FILE = PlayerDataFile
    credentials = load_player_credentials(PlayerDataFile)
    config.PLAYER_ID = credentials.get("playerId") if credentials else None
    config.PLAYER_TOKEN = credentials.get("playerToken") if credentials else None
    game_display = GameDisplay(load_display_resolution())
    pygame.display.set_caption("Supa Fighta")
    clock = pygame.time.Clock() 
    gameState = GameState(game_display, save_display_resolution)
    ws_client = None
   
    try:
        running = True
        while running:
            clock.tick(config.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    gameState.handle_event(
                        game_display.to_logical_event(event)
                    )

            gameState.update()
            game_display.logical_surface.fill(config.BACKGROUND_COLOR)
            gameState.draw(game_display.logical_surface)
            game_display.present()
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        current_state = gameState.current_state()
        if hasattr(current_state, 'player') and current_state.player is not None:
            if hasattr(current_state.player, 'net') and current_state.player.net is not None:
                print("Closing WebSocket connection...")
                current_state.player.net.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supa Fighta Client")
    parser.add_argument(
        "--datafile",
        default="player_credentials.json",
        help="Path to player credentials file",
    )
    args = parser.parse_args()
    main(args.datafile)
