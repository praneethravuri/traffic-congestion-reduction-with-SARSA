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

# Scale images if necessary (assuming the images are not too large)
intersection_img = pygame.transform.scale(intersection_img, (width, height))

# Define initial positions for the vehicles
car_position = [0, 400]  # Starting at the left, middle of the screen

# Define the speed of the vehicles
car_speed = 5  # Adjust this value as needed

# Traffic signal colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
DARK_YELLOW = (100, 100, 0)
DARK_RED = (100, 0, 0)
BLACK = (0, 0, 0)

# Define traffic light positions for each direction
traffic_light_positions = {
    'north': (width // 2, height // 2 - 70),
    'east': (width // 2 + 70, height // 2),
    'south': (width // 2, height // 2 + 70),
    'west': (width // 2 - 70, height // 2)
}

# Define the stopping line position for the red light
# This is an arbitrary position close to the center of the screen
# where the car should stop if the light is red.
stopping_line_position = width // 2 - 100

# Define durations for each signal
green_duration = 5
yellow_duration = 2  # Duration of the yellow signal
red_duration = 5

# Initialize all signals to RED and set the timers
traffic_signals = {direction: {'color': RED, 'timer': red_duration} for direction in traffic_light_positions}

# Choose which signal to turn green first
current_green = 'north'
signal_last_changed = time.time()

# Function to update the traffic light logic
def update_traffic_signals():
    global current_green, signal_last_changed
    # Check if the current signal duration has passed
    time_elapsed = time.time() - signal_last_changed
    if traffic_signals[current_green]['color'] == GREEN and time_elapsed > green_duration:
        # Change the current green signal to yellow
        traffic_signals[current_green]['color'] = YELLOW
        traffic_signals[current_green]['timer'] = yellow_duration
        signal_last_changed = time.time()
    elif traffic_signals[current_green]['color'] == YELLOW and time_elapsed > yellow_duration:
        # Change the current yellow signal to red
        traffic_signals[current_green]['color'] = RED
        traffic_signals[current_green]['timer'] = red_duration
        # Move to the next signal
        directions = list(traffic_light_positions.keys())
        current_green = directions[(directions.index(current_green) + 1) % len(directions)]
        # Change the new current signal to green
        traffic_signals[current_green]['color'] = GREEN
        traffic_signals[current_green]['timer'] = green_duration
        signal_last_changed = time.time()

def draw_traffic_signal_box(position, signal_color, direction_name):
    # Draw the signal box
    pygame.draw.rect(screen, BLACK, (position[0], position[1], 20, 60))
    # Draw the lights
    pygame.draw.circle(screen, RED if signal_color == RED else DARK_RED, (position[0] + 10, position[1] + 15), 8)
    pygame.draw.circle(screen, YELLOW if signal_color == YELLOW else DARK_YELLOW, (position[0] + 10, position[1] + 30), 8)
    pygame.draw.circle(screen, GREEN if signal_color == GREEN else DARK_GREEN, (position[0] + 10, position[1] + 45), 8)
    # Render the direction name text
    text_surface = font.render(direction_name, True, (255, 255, 255))
    # Get the width and height of the text surface
    text_w, text_h = text_surface.get_size()
    # Blit the text onto the screen at the correct position
    screen.blit(text_surface, (position[0] - text_w // 2 + 10, position[1] + 70))

# Main simulation loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the traffic signals
    update_traffic_signals()

    # Move vehicles logic
    # The car can move if the light is green or has passed the stopping line
    if traffic_signals['east']['color'] in [GREEN, YELLOW] and car_position[0] < stopping_line_position:
        car_position[0] += car_speed  # Move the car to the right
    # If the light is red and the car has not reached the stopping line, it should stop
    elif traffic_signals['east']['color'] == RED and car_position[0] < stopping_line_position:
        pass  # Stop the car

    # If the car goes off the screen, reset its position to the left
    if car_position[0] > width:
        car_position[0] = -car_img.get_width()

    # Draw the intersection
    screen.blit(intersection_img, (0, 0))

    # Draw the traffic lights for each direction
    for direction, position in traffic_light_positions.items():
        current_color = traffic_signals[direction]['color']
        draw_traffic_signal_box(position, current_color, direction.capitalize())

    # Draw the car at its updated position
    screen.blit(car_img, car_position)

    # Update the display
    pygame.display.flip()

    # Wait for a short period to control the simulation speed
    pygame.time.delay(100)

# Quit Pygame
pygame.quit()
