import pygame
import sys

pygame.init()
pygame.font.init()


width, height = 1000, 800
screen = pygame.display.set_mode((width, height))

# colors
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)

# traffic light colors
YELLOW_TR = (255, 255, 0)
GREEN_TR = (78, 228, 78)
RED_TR = (255, 0, 0)


# Intersection parameters
road_width = 125
traffic_light_width = road_width//2
intersection_center = (width // 2, height // 2)
intersection_trl_width = 30


def draw_intersection(screen):
    # green background
    screen.fill(GREEN)
    font = pygame.font.SysFont(None, 36)

    # drawing the vertical road
    pygame.draw.rect(screen, BLACK, (intersection_center[0] - road_width // 2, 0, road_width, height))
    # drawing the horizontal road
    pygame.draw.rect(screen, BLACK, (0, intersection_center[1] - road_width // 2, width, road_width))

    # drawing lanes for each road
    # west lane and naming it
    pygame.draw.line(screen, YELLOW, (0, intersection_center[1]), (intersection_center[0] - road_width // 2, intersection_center[1]), 2)
    text = font.render('West', True, WHITE)
    screen.blit(text, (intersection_center[0]//2, intersection_center[1] - 10))
    # east lane and naming it
    pygame.draw.line(screen, YELLOW, (intersection_center[0] + road_width // 2, intersection_center[1]), (width, intersection_center[1]), 2)
    text = font.render('East', True, WHITE)
    screen.blit(text, (intersection_center[0]//2 + intersection_center[0], intersection_center[1] - 10))
    # north lane
    pygame.draw.line(screen, YELLOW, (intersection_center[0], 0), (intersection_center[0], intersection_center[1] - road_width // 2), 2)
    text = font.render('North', True, WHITE)
    screen.blit(text, (intersection_center[0] - 30, intersection_center[1]//2))
    # south lane
    pygame.draw.line(screen, YELLOW, (intersection_center[0], intersection_center[1] + road_width // 2), (intersection_center[0], height), 2)
    text = font.render('South', True, WHITE)
    screen.blit(text, (intersection_center[0] - 30, intersection_center[1]//2 + intersection_center[1]))


def draw_traffic_lights(screen):
    # North traffic lights
    # North-straight traffic light
    north_traffic_light_pos_straight = (intersection_center[0], intersection_center[1] - road_width // 2 - intersection_trl_width)
    pygame.draw.rect(screen, RED_TR, (*north_traffic_light_pos_straight, traffic_light_width, 5))
    # North-left traffic light
    north_traffic_light_pos_left = (north_traffic_light_pos_straight[0] - traffic_light_width, north_traffic_light_pos_straight[1])
    pygame.draw.rect(screen, GREEN_TR, (*north_traffic_light_pos_left, traffic_light_width, 5))

    # South traffic lights
    # South-straight traffic light
    south_traffic_light_pos_straight = (intersection_center[0], intersection_center[1] + road_width // 2 - 5 + intersection_trl_width)
    pygame.draw.rect(screen, RED_TR, (*south_traffic_light_pos_straight, traffic_light_width, 5))
    # South-left traffic light
    south_traffic_light_pos_left = (south_traffic_light_pos_straight[0] - traffic_light_width, south_traffic_light_pos_straight[1])
    pygame.draw.rect(screen, GREEN_TR, (*south_traffic_light_pos_left, traffic_light_width, 5))

    # East traffic lights
    # East-straight traffic light
    east_traffic_light_pos_straight = (intersection_center[0] + road_width // 2 + intersection_trl_width, intersection_center[1])
    pygame.draw.rect(screen, RED_TR, (*east_traffic_light_pos_straight, 5, traffic_light_width))
    # East-left traffic light
    east_traffic_light_pos_left = (east_traffic_light_pos_straight[0], east_traffic_light_pos_straight[1] - traffic_light_width)
    pygame.draw.rect(screen, GREEN_TR, (*east_traffic_light_pos_left, 5, traffic_light_width))

    # West traffic lights
    # West-straight traffic light
    west_traffic_light_pos_straight = (intersection_center[0] - road_width // 2 - intersection_trl_width, intersection_center[1])
    pygame.draw.rect(screen, RED_TR, (*west_traffic_light_pos_straight, 5, traffic_light_width))
    # West-left traffic light
    west_traffic_light_pos_left = (west_traffic_light_pos_straight[0], west_traffic_light_pos_straight[1] - traffic_light_width)
    pygame.draw.rect(screen, GREEN_TR, (*west_traffic_light_pos_left, 5, traffic_light_width))


def draw_crossings(screen):
    # Crossing parameters for the west lane
    # crossing for the west lane
    west_crossing_x = intersection_center[0] - road_width//2 - 25
    west_crossing_y = intersection_center[1] - road_width//2
    pygame.draw.rect(screen, GRAY, (west_crossing_x, west_crossing_y, intersection_trl_width, road_width))

    # crossing for the east lane
    east_crossing_x = intersection_center[0] + road_width//2
    east_crossing_y = west_crossing_y
    pygame.draw.rect(screen, GRAY, (east_crossing_x, east_crossing_y, intersection_trl_width, road_width))

    # crossing for the north lane
    north_crossing_x = intersection_center[0] - road_width//2
    north_crossing_y = intersection_center[1] - road_width//2 - 25
    pygame.draw.rect(screen, GRAY, (north_crossing_x, north_crossing_y, road_width, 25))

    # crossing for the south lane
    south_crossing_x = north_crossing_x
    south_crossing_y = intersection_center[1] - road_width//2 + 125
    pygame.draw.rect(screen, GRAY, (south_crossing_x, south_crossing_y, road_width, 25))

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_intersection(screen)
        draw_traffic_lights(screen)
        draw_crossings(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()


pygame.quit()
sys.exit()