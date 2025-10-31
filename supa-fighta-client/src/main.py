import pygame, sys, config
from game.stateManager import GameState

def main():
    pygame.init()
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
    main()
