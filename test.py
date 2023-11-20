import pygame
import sys
import random
import time

pygame.init()
pygame.font.init()

width, height = 1000, 800
screen = pygame.display.set_mode((width, height))

# vehicle parameters
vehicle_radius = 15
vehicle_width = 15
vehicle_straight = (255, 163, 60)
vehicle_right = (255, 251, 115)
vehicle_speed = 0.25
vehicle_direction = ["straight", "right"]

# Intersection parameters and colors
road_width = 125
traffic_light_width = road_width // 2
intersection_center = (width // 2, height // 2)
intersection_trl_width = 30
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)

# crossing thresholds
west_threshold = intersection_center[0] - road_width // 2 - intersection_trl_width - 30

# traffic light parameters and colors
YELLOW_TR = (255, 255, 0)
GREEN_TR = (78, 228, 78)
RED_TR = (255, 0, 0)
traffic_lights_directions = ["north", "east", "south", "west"]
starting_traffic_light = random.choice(traffic_lights_directions)
traffic_light_change_times = {
    "RED": 7,
    "GREEN": 7,
    "YELLOW": 3
}


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
    pygame.draw.line(screen, YELLOW, (0, intersection_center[1]),
                     (intersection_center[0] - road_width // 2, intersection_center[1]), 2)
    text = font.render('West', True, WHITE)
    screen.blit(text, (intersection_center[0] // 2, intersection_center[1] - 10))
    # east lane and naming it
    pygame.draw.line(screen, YELLOW, (intersection_center[0] + road_width // 2, intersection_center[1]),
                     (width, intersection_center[1]), 2)
    text = font.render('East', True, WHITE)
    screen.blit(text, (intersection_center[0] // 2 + intersection_center[0], intersection_center[1] - 10))
    # north lane
    pygame.draw.line(screen, YELLOW, (intersection_center[0], 0),
                     (intersection_center[0], intersection_center[1] - road_width // 2), 2)
    text = font.render('North', True, WHITE)
    screen.blit(text, (intersection_center[0] - 30, intersection_center[1] // 2))
    # south lane
    pygame.draw.line(screen, YELLOW, (intersection_center[0], intersection_center[1] + road_width // 2),
                     (intersection_center[0], height), 2)
    text = font.render('South', True, WHITE)
    screen.blit(text, (intersection_center[0] - 30, intersection_center[1] // 2 + intersection_center[1]))


def draw_traffic_lights(screen, current_traffic_light, current_light_state):
    # Initialize all traffic lights to red
    north_color = RED_TR
    south_color = RED_TR
    east_color = RED_TR
    west_color = RED_TR

    # Determine the color based on current state
    if current_light_state == "GREEN":
        light_color = GREEN_TR
    elif current_light_state == "YELLOW":
        light_color = YELLOW_TR
    elif current_light_state == "RED":
        light_color = RED_TR

    # Set the color of the current traffic light
    if current_traffic_light == "north":
        north_color = light_color
    elif current_traffic_light == "south":
        south_color = light_color
    elif current_traffic_light == "east":
        east_color = light_color
    elif current_traffic_light == "west":
        west_color = light_color

    # Drawing traffic lights with the updated colors
    # North traffic light
    north_traffic_light_width = traffic_light_width * 2
    north_traffic_light_pos = (intersection_center[0] - north_traffic_light_width // 2,
                               intersection_center[1] - road_width // 2 - intersection_trl_width)
    pygame.draw.rect(screen, north_color, (*north_traffic_light_pos, north_traffic_light_width, 5))

    # South traffic light
    south_traffic_light_width = traffic_light_width * 2
    south_traffic_light_pos = (intersection_center[0] - south_traffic_light_width // 2,
                               intersection_center[1] + road_width // 2 - 5 + intersection_trl_width)
    pygame.draw.rect(screen, south_color, (*south_traffic_light_pos, south_traffic_light_width, 5))

    # East traffic light
    east_traffic_light_height = traffic_light_width * 2
    east_traffic_light_pos = (intersection_center[0] + road_width // 2 + intersection_trl_width,
                              intersection_center[1] - east_traffic_light_height // 2)
    pygame.draw.rect(screen, east_color, (*east_traffic_light_pos, 5, east_traffic_light_height))

    # West traffic light
    west_traffic_light_height = traffic_light_width * 2
    west_traffic_light_pos = (intersection_center[0] - road_width // 2 - intersection_trl_width,
                              intersection_center[1] - west_traffic_light_height // 2)
    pygame.draw.rect(screen, west_color, (*west_traffic_light_pos, 5, west_traffic_light_height))


def draw_crossings(screen):
    # Crossing parameters for the west lane
    # crossing for the west lane
    west_crossing_x = intersection_center[0] - road_width // 2 - 25
    west_crossing_y = intersection_center[1] - road_width // 2
    pygame.draw.rect(screen, GRAY, (west_crossing_x, west_crossing_y, intersection_trl_width, road_width))

    # crossing for the east lane
    east_crossing_x = intersection_center[0] + road_width // 2
    east_crossing_y = west_crossing_y
    pygame.draw.rect(screen, GRAY, (east_crossing_x, east_crossing_y, intersection_trl_width, road_width))

    # crossing for the north lane
    north_crossing_x = intersection_center[0] - road_width // 2
    north_crossing_y = intersection_center[1] - road_width // 2 - 25
    pygame.draw.rect(screen, GRAY, (north_crossing_x, north_crossing_y, road_width, 25))

    # crossing for the south lane
    south_crossing_x = north_crossing_x
    south_crossing_y = intersection_center[1] - road_width // 2 + 125
    pygame.draw.rect(screen, GRAY, (south_crossing_x, south_crossing_y, road_width, 25))


def draw_vehicle(screen, x, y, color, radius, width):
    pygame.draw.circle(screen, color, [x, y], radius, width)


def move_vehicle(screen, threshold, x, y, vehicle_speed):
    # Update the position of the vehicle if it has not yet reached the threshold
    if x < threshold:
        x += vehicle_speed
    return x, y  # Return the updated position


def main():
    running = True
    current_traffic_light_index = traffic_lights_directions.index(starting_traffic_light)
    current_traffic_light = traffic_lights_directions[current_traffic_light_index]
    current_light_state = "GREEN"
    last_change_time = pygame.time.get_ticks()

    vehicle_x = 0
    vehicle_y = intersection_center[1] + road_width // 4

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks()

        # Check if it's time to change the traffic light state
        if current_light_state == "GREEN" and current_time - last_change_time >= traffic_light_change_times[
            "GREEN"] * 1000:
            current_light_state = "YELLOW"
            last_change_time = current_time
        elif current_light_state == "YELLOW" and current_time - last_change_time >= traffic_light_change_times[
            "YELLOW"] * 1000:
            current_light_state = "RED"
            last_change_time = current_time
            # Cycle to the next traffic light
            current_traffic_light_index = (current_traffic_light_index + 1) % len(traffic_lights_directions)
            current_traffic_light = traffic_lights_directions[current_traffic_light_index]
        elif current_light_state == "RED" and current_time - last_change_time >= traffic_light_change_times[
            "RED"] * 1000:
            current_light_state = "GREEN"
            last_change_time = current_time

        vehicle_type = random.choice(vehicle_direction)

        # if vehicle_type == "straight":
        #     vehicle_color = vehicle_straight
        # else:
        #     vehicle_color = vehicle_right

        vehicle_x, vehicle_y = move_vehicle(screen, west_threshold, vehicle_x, vehicle_y, vehicle_speed)
        draw_intersection(screen)
        draw_traffic_lights(screen, current_traffic_light, current_light_state)
        draw_crossings(screen)
        draw_vehicle(screen, vehicle_x, vehicle_y, vehicle_straight, vehicle_radius, vehicle_width)
        move_vehicle(screen, west_threshold, vehicle_x, vehicle_y, vehicle_speed)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
