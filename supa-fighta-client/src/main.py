import pygame, sys, config
from server.ws_client import WSClient
from game.stateManager import GameState
from player_manager import load_player_id

def main():
    pygame.init()
    config.PLAYER_ID = load_player_id()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Supa Fighta")
    clock = pygame.time.Clock()    
    net = WSClient(config.WS_URL)   
    gameState = GameState(net)
    
   
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
        net.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
