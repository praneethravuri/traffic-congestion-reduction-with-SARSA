import pygame
import time

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1000, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Intersection Simulation")

pygame.font.init()
# Create a Font object
font = pygame.font.SysFont(None, 24)

# Load images
intersection_img = pygame.image.load('./testimages/intersection.png')
bus_img = pygame.image.load('./testimages/bus.png')
car_img = pygame.image.load('./testimages/car.png')
truck_img = pygame.image.load('./testimages/truck.png')
bike_img = pygame.image.load('./testimages/bike.png')

# Scale images if necessary
intersection_img = pygame.transform.scale(intersection_img, (width, height))

# Define initial positions for the vehicles
car_position = [0, 400]  # Starting at the left, middle of the screen

# Define the speed of the vehicles
car_speed = 5  # Adjust this value as needed

# Define traffic signal colors and positions
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
DARK_YELLOW = (100, 100, 0)
DARK_RED = (100, 0, 0)
BLACK = (0, 0, 0)

traffic_light_positions = {
    'north': (width // 2 - 15, height // 2 - 135),
    'east': (width // 2 + 50, height // 2 - 60),
    'south': (width // 2 -15, height // 2 + 20),
    'west': (width // 2 - 80, height // 2 - 60)
}

# Define stopping line position
stopping_line_position = width // 2 - 100

# Define a threshold position for stopping (somewhere before the crossing)
stop_threshold_position = stopping_line_position - 50  # Adjust this value as needed

# Initialize a flag to indicate whether the car has passed the crossing
has_passed_crossing = False

# Define signal durations
green_duration = 5
yellow_duration = 2
red_duration = 5

# Initialize all signals to RED
traffic_signals = {direction: {'color': RED, 'timer': red_duration} for direction in traffic_light_positions}

# Set the initial green signal
current_green = 'west'
traffic_signals[current_green]['color'] = GREEN  # Start with the 'north' signal as green
signal_last_changed = time.time()


def update_traffic_signals():
    global current_green, signal_last_changed
    # Check if the current signal duration has passed
    time_elapsed = time.time() - signal_last_changed
    current_color = traffic_signals[current_green]['color']

    if current_color == GREEN and time_elapsed > green_duration:
        traffic_signals[current_green]['color'] = YELLOW
        signal_last_changed = time.time()
    elif current_color == YELLOW and time_elapsed > yellow_duration:
        traffic_signals[current_green]['color'] = RED
        directions = list(traffic_light_positions.keys())
        current_green = directions[(directions.index(current_green) + 1) % len(directions)]
        traffic_signals[current_green]['color'] = GREEN
        signal_last_changed = time.time()



# Draw traffic signal box function
def draw_traffic_signal_box(position, signal_color, direction_name):
    # Check if the direction is north or south for horizontal layout
    if direction_name in ['north', 'south']:
        # Draw horizontal signal box for north and south
        pygame.draw.rect(screen, BLACK, (position[0], position[1], 60, 20))  # Wider rectangle
        light_positions = [(position[0] + 15, position[1] + 10), (position[0] + 30, position[1] + 10), (position[0] + 45, position[1] + 10)]
    else:
        # Draw vertical signal box for east and west
        pygame.draw.rect(screen, BLACK, (position[0], position[1], 20, 60))  # Taller rectangle
        light_positions = [(position[0] + 10, position[1] + 15), (position[0] + 10, position[1] + 30), (position[0] + 10, position[1] + 45)]

    # Draw the lights
    pygame.draw.circle(screen, RED if signal_color == RED else DARK_RED, light_positions[0], 8)
    pygame.draw.circle(screen, YELLOW if signal_color == YELLOW else DARK_YELLOW, light_positions[1], 8)
    pygame.draw.circle(screen, GREEN if signal_color == GREEN else DARK_GREEN, light_positions[2], 8)

    # Render the direction name text
    text_surface = font.render(direction_name, True, (255, 255, 255))
    text_w, text_h = text_surface.get_size()
    screen.blit(text_surface, (position[0] - text_w // 2 + (30 if direction_name in ['north', 'south'] else 10), position[1] + (70 if direction_name not in ['north', 'south'] else 25)))


# Main simulation loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update traffic signals
    update_traffic_signals()

    # Check if the car has passed the crossing
    if car_position[0] > stopping_line_position:
        has_passed_crossing = True

    # Move vehicles
    # If the car is before the stop threshold or if the light is not red, or if it has passed the crossing
    if car_position[0] < stop_threshold_position or traffic_signals['east']['color'] in [GREEN, YELLOW] or has_passed_crossing:
        car_position[0] += car_speed  # Move the car to the right

    # If the car is past the stop threshold and the light is red, and it has not passed the crossing, stop the car
    elif car_position[0] >= stop_threshold_position and traffic_signals['east']['color'] == RED and not has_passed_crossing:
        pass  # Stop the car

    # Reset car position if off screen
    if car_position[0] > width:
        car_position[0] = -car_img.get_width()
        has_passed_crossing = False

    # Draw intersection
    screen.blit(intersection_img, (0, 0))

    # Draw traffic lights
    for direction, position in traffic_light_positions.items():
        current_color = traffic_signals[direction]['color']
        draw_traffic_signal_box(position, current_color, direction.capitalize())

    # Draw car
    screen.blit(car_img, car_position)

    # Update display
    pygame.display.flip()

    # Control simulation speed
    pygame.time.delay(100)

# Quit Pygame
pygame.quit()
