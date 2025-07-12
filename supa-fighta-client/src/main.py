import pygame, sys, config
from game.player import Player
from server.ws_client import WSClient
from game.stateManager import GameState

def main():
    pygame.init()
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

            # screen.fill(config.BACKGROUND_COLOR)
            # player.draw(screen)
            pygame.display.flip()

    finally:
        net.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
