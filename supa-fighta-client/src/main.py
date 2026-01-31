import pygame, sys, config, argparse
from game.stateManager import GameState
from player_manager import load_player_id

def main(PlayerDataFile="player_data.dat"):
    pygame.init()
    config.PLAYER_ID = load_player_id(PlayerDataFile)
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Supa Fighta")
    clock = pygame.time.Clock() 
    gameState = GameState()
   
    try:
        running = True
        while running:
            clock.tick(config.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    gameState.handle_event(event)

            gameState.update()
            gameState.draw(screen)

            pygame.display.flip()
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supa Fighta Client")
    parser.add_argument("--datafile", default="player_data.dat", help="Path to player data file")
    args = parser.parse_args()
    main(args.datafile)
