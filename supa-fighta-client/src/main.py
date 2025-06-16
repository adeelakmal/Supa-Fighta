import pygame, sys, config
from game.player import Player
from server.ws_client import WSClient

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Supa Fighta")
    clock = pygame.time.Clock()

    net = WSClient(config.WS_URL)   
    player = Player(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2, net)

    try:
        running = True
        while running:
            clock.tick(config.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            player.handle_keys()

            screen.fill(config.BACKGROUND_COLOR)
            player.draw(screen)
            pygame.display.flip()

    finally:
        net.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
