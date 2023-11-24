import pygame
import random
import threading
import time
import sys


class Intersection:
    def __init__(self, screen, center, road_width, intersection_colors, width, height, font):
        self.screen = screen
        self.center = center
        self.road_width = road_width
        self.intersection_colors = intersection_colors
        self.width = width
        self.height = height
        self.font = font

    def draw_road(self, position, size):
        pygame.draw.rect(self.screen, self.intersection_colors["BLACK"], (position, size))

    def draw_lane(self, start_pos, end_pos):
        pygame.draw.line(self.screen, self.intersection_colors["YELLOW"], start_pos, end_pos, 2)

    def draw_text(self, text, position):
        rendered_text = self.font.render(text, True, self.intersection_colors["WHITE"])
        self.screen.blit(rendered_text, position)

    def draw(self):
        self.screen.fill(self.intersection_colors["GREEN"])

        # Vertical and horizontal roads
        self.draw_road((self.center[0] - self.road_width // 2, 0), (self.road_width, self.height))
        self.draw_road((0, self.center[1] - self.road_width // 2), (self.width, self.road_width))

        # Lanes and labels
        self.draw_lane((0, self.center[1]), (self.center[0] - self.road_width // 2, self.center[1]))
        self.draw_text('West', (self.center[0] // 2, self.center[1] - 10))

        self.draw_lane((self.center[0] + self.road_width // 2, self.center[1]), (self.width, self.center[1]))
        self.draw_text('East', (self.center[0] // 2 + self.center[0], self.center[1] - 10))

        self.draw_lane((self.center[0], 0), (self.center[0], self.center[1] - self.road_width // 2))
        self.draw_text('North', (self.center[0] - 30, self.center[1] // 2))

        self.draw_lane((self.center[0], self.center[1] + self.road_width // 2), (self.center[0], self.height))
        self.draw_text('South', (self.center[0] - 30, self.center[1] // 2 + self.center[1]))


class Crossing:

    def __init__(self, screen, intersection_center, road_width, intersection_trl_width, intersection_colors):
        self.screen = screen
        self.intersection_center = intersection_center
        self.intersection_colors = intersection_colors
        self.road_width = road_width
        self.intersection_trl_width = intersection_trl_width

    def draw_crossing(self, position, size):
        pygame.draw.rect(self.screen, self.intersection_colors["GRAY"], (position, size))

    def draw(self):
        # Crossing parameters for west and east lanes
        west_crossing_x = self.intersection_center[0] - self.road_width // 2 - 25 - 5
        east_crossing_x = self.intersection_center[0] + self.road_width // 2
        crossing_y = self.intersection_center[1] - self.road_width // 2

        # Crossing parameters for north and south lanes
        crossing_x = self.intersection_center[0] - self.road_width // 2
        north_crossing_y = self.intersection_center[1] - self.road_width // 2 - 25
        south_crossing_y = self.intersection_center[1] + self.road_width // 2

        # Draw crossings for each lane
        self.draw_crossing((west_crossing_x, crossing_y), (self.intersection_trl_width, self.road_width))
        self.draw_crossing((east_crossing_x, crossing_y), (self.intersection_trl_width, self.road_width))
        self.draw_crossing((crossing_x, north_crossing_y), (self.road_width, 25))
        self.draw_crossing((crossing_x, south_crossing_y), (self.road_width, 25))


class TrafficLights:
    def __init__(self, screen, current_traffic_light, current_light_state, traffic_lights_directions, trl_colors,
                 traffic_light_width, intersection_center, road_width, intersection_trl_width,
                 traffic_light_change_times):
        self.screen = screen
        self.current_traffic_light = current_traffic_light
        self.current_traffic_light_index = traffic_lights_directions.index(self.current_traffic_light)
        self.current_light_state = current_light_state
        self.traffic_lights_directions = traffic_lights_directions
        self.trl_colors = trl_colors
        self.traffic_light_width = traffic_light_width
        self.intersection_center = intersection_center
        self.road_width = road_width
        self.intersection_trl_width = intersection_trl_width
        self.traffic_light_change_times = traffic_light_change_times
        self.last_change_time = pygame.time.get_ticks()

    def draw_traffic_light(self, direction, color):
        if direction == "north":
            width = self.traffic_light_width * 2 - self.road_width // 2
            position = (self.intersection_center[0] - width // 2 - self.road_width // 4,
                        self.intersection_center[1] - self.road_width // 2 - self.intersection_trl_width - 5)
            size = (width, 10)
        elif direction == "south":
            width = self.traffic_light_width * 2 - self.road_width // 2
            position = (self.intersection_center[0] - width // 2 + self.road_width // 4,
                        self.intersection_center[1] + self.road_width // 2 - 5 + self.intersection_trl_width)
            size = (width, 10)
        elif direction == "east":
            height = self.traffic_light_width * 2 - self.road_width // 2
            position = (self.intersection_center[0] + self.road_width // 2 + self.intersection_trl_width,
                        self.intersection_center[1] - height // 2 - self.road_width // 4)
            size = (10, height)
        elif direction == "west":
            height = self.traffic_light_width * 2 - self.road_width // 2
            position = (self.intersection_center[0] - self.road_width // 2 - self.intersection_trl_width - 10,
                        self.intersection_center[1] - height // 2 + self.road_width // 4)
            size = (10, height)

        pygame.draw.rect(self.screen, color, (*position, *size))

    def draw(self):
        light_color = self.trl_colors[self.current_light_state + "_TR"]

        # Set the color of the current traffic light
        colors = {dir: self.trl_colors["RED_TR"] for dir in ["north", "south", "east", "west"]}
        colors[self.current_traffic_light] = light_color

        # Drawing traffic lights for all directions
        for direction, color in colors.items():
            self.draw_traffic_light(direction, color)

    def update(self, current_time):
        time_diff = current_time - self.last_change_time
        time_limit = self.traffic_light_change_times[self.current_light_state] * 1000

        if time_diff >= time_limit:
            if self.current_light_state == "GREEN":
                self.current_light_state = "YELLOW"
            elif self.current_light_state == "YELLOW":
                self.current_light_state = "RED"
                # Move to next traffic light
                self.current_traffic_light_index = (self.current_traffic_light_index + 1) % len(
                    self.traffic_lights_directions)
            elif self.current_light_state == "RED":
                self.current_light_state = "GREEN"

            self.last_change_time = current_time

        self.current_traffic_light = self.traffic_lights_directions[self.current_traffic_light_index]
        return self.current_traffic_light, self.current_light_state


class Vehicle:
    def __init__(self, screen, radius, width, speed):
        self.screen = screen
        self.radius = radius
        self.width = width
        self.speed = speed
        self.x = None
        self.y = None
        self.direction = None
        self.color = None
        self.moving = True
        self.out_going_direction = None
        self.lane = None
        self.threshold = None
        self.has_crossed_threshold = False

    def generate_vehicle(self, vehicle_spawn_coords, vehicle_incoming_direction, vehicle_direction_color,
                         vehicle_count):
        self.direction = random.choice(vehicle_incoming_direction)
        vehicle_count[self.direction] += 1
        self.lane = self.direction
        self.x, self.y = vehicle_spawn_coords[self.direction]
        self.out_going_direction = random.choice(["straight", "left", "right"])
        self.color = vehicle_direction_color[self.out_going_direction]

    def move(self, current_traffic_light, current_light_state, thresholds, vehicle_turning_points):
        self.threshold = thresholds[self.direction]
        if self.out_going_direction == "left":
            current_turning_point = vehicle_turning_points["left"][self.direction]
        else:
            current_turning_point = vehicle_turning_points["right"][self.direction]

        # For vehicle coming from the west
        if self.direction == "west":
            if (current_traffic_light == "west" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.x > self.threshold):
                if self.out_going_direction == "straight":
                    self.x += self.speed
                elif self.out_going_direction == "left":
                    if self.x < current_turning_point:
                        self.x += self.speed
                    else:
                        self.y -= self.speed
                else:
                    if self.x < current_turning_point:
                        self.x += self.speed
                    else:
                        self.y += self.speed
            else:
                if self.x < self.threshold:
                    self.x += self.speed

        # For vehicle coming from the east
        elif self.direction == "east":
            if (current_traffic_light == "east" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.x < self.threshold):
                if self.out_going_direction == "straight":
                    self.x -= self.speed
                elif self.out_going_direction == "left":
                    if self.x > current_turning_point:
                        self.x -= self.speed
                    else:
                        self.y += self.speed

                else:
                    if self.x > current_turning_point:
                        self.x -= self.speed
                    else:
                        self.y -= self.speed
            else:
                if self.x > self.threshold:
                    self.x -= self.speed

        # For vehicle coming from the north
        elif self.direction == "north":
            if (current_traffic_light == "north" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.y > self.threshold):
                if self.out_going_direction == "straight":
                    self.y += self.speed
                elif self.out_going_direction == "left":
                    if self.y < current_turning_point:
                        self.y += self.speed
                    else:
                        self.x += self.speed
                else:
                    if self.y < current_turning_point:
                        self.y += self.speed
                    else:
                        self.x -= self.speed
            else:
                if self.y < self.threshold:
                    self.y += self.speed

        # For vehicle coming from the south
        elif self.direction == "south":
            if (current_traffic_light == "south" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.y < self.threshold):
                if self.out_going_direction == "straight":
                    self.y -= self.speed
                elif self.out_going_direction == "left":
                    if self.y > current_turning_point:
                        self.y -= self.speed
                    else:
                        self.x -= self.speed
                else:
                    if self.y > current_turning_point:
                        self.y -= self.speed
                    else:
                        self.x += self.speed
            else:
                if self.y > self.threshold:
                    self.y -= self.speed

        return self.x, self.y

    def draw(self):
        pygame.draw.circle(self.screen, self.color, [self.x, self.y], self.radius, self.width)

    def kill_vehicle(self, width, height):
        # Check if the vehicle is out of bounds
        out_of_bounds = self.x < 0 or self.x > width or self.y < 0 or self.y > height
        return out_of_bounds

    def crossed_threshold(self):
        if not self.has_crossed_threshold:
            if self.direction == "west" and self.x > self.threshold:
                self.has_crossed_threshold = True
                return True, self.direction

            elif self.direction == "east" and self.x < self.threshold:
                self.has_crossed_threshold = True
                return True, self.direction

            elif self.direction == "north" and self.y > self.threshold:
                self.has_crossed_threshold = True
                return True, self.direction

            elif self.direction == "south" and self.y < self.threshold:
                self.has_crossed_threshold = True
                return True, self.direction

        return False, None


class SARSA:
    def __init__(self):

        try:
            pygame.init()
            pygame.font.init()
        except pygame.error as e:
            print(f"Error initializing Pygame: {e}")

        self.width, self.height = 1000, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        # Intersection parameters and colors
        # width of the road
        self.road_width = 150
        # width of the traffic light
        self.traffic_light_width = self.road_width // 2
        # center of the intersection
        self.intersection_center = (self.width // 2, self.height // 2)
        # distance from the center of the intersection to the center of the traffic light
        self.intersection_trl_width = self.road_width // 5

        self.intersection_colors = {
            "BLACK": (0, 0, 0),
            "GREEN": (26, 93, 26),
            "RED": (255, 0, 0),
            "YELLOW": (255, 255, 0),
            "GRAY": (128, 128, 128),
            "WHITE": (255, 255, 255),
            "BROWN": (185, 148, 112)
        }

        # crossing thresholds
        self.thresholds = {
            "west": self.intersection_center[0] - self.road_width // 2 - self.intersection_trl_width - 30,
            "east": self.intersection_center[
                        0] - self.road_width // 2 + self.road_width + self.intersection_trl_width + 30,
            "north": self.intersection_center[1] - self.road_width // 2 - self.intersection_trl_width - 30,
            "south": self.intersection_center[1] + self.road_width - 15
        }

        # traffic light parameters and colors
        self.trl_colors = {
            "YELLOW_TR": (255, 255, 0),
            "GREEN_TR": (78, 228, 78),
            "RED_TR": (255, 0, 0)
        }

        self.traffic_lights_directions = ["north", "east", "south", "west"]
        # creating the starting point for the traffic light rotation
        self.starting_traffic_light = random.choice(self.traffic_lights_directions)
        self.traffic_light_change_times = {
            "RED": 5,
            "GREEN": 5,
            "YELLOW": 2
        }

        # vehicle parameters
        self.vehicle_radius = 12
        self.vehicle_width = 12
        self.vehicle_gap = 12
        # vehicle speed
        self.vehicle_speed = 0.25
        # direction of a vehicle after the traffic light turns green
        self.vehicle_direction_color = {
            "straight": (255, 163, 60),
            "left": (135, 196, 255),
            "right": (255, 75, 145)
        }
        # the direction from which a vehicle is generated
        self.vehicle_incoming_direction = ["north", "east", "south", "west"]
        # vehicle spawn coordinates
        self.vehicle_spawn_coords = {
            "west": [0, self.intersection_center[1] + self.road_width // 4],
            "east": [2 * self.intersection_center[0], self.intersection_center[1] - self.road_width // 4],
            "north": [self.intersection_center[0] - self.road_width // 4, 0],
            "south": [self.intersection_center[0] + self.road_width // 4, 2 * self.intersection_center[1]]
        }

        self.vehicle_turning_points = {
            "left": {
                "west": self.intersection_center[0] + self.road_width // 4,
                "north": self.intersection_center[1] + self.road_width // 4,
                "east": self.intersection_center[0] - self.road_width // 4,
                "south": self.intersection_center[1] - self.road_width // 4
            },
            "right": {
                "west": self.intersection_center[0] - self.road_width // 4,
                "north": self.intersection_center[1] - self.road_width // 4,
                "east": self.intersection_center[0] + self.road_width // 4,
                "south": self.intersection_center[1] + self.road_width // 4
            }
        }
        self.vehicle_count = {"north": 0, "south": 0, "east": 0, "west": 0}
        self.vehicle_list = []
        self.font = pygame.font.SysFont(name=None, size=36)
        self.vehicle_list_lock = threading.Lock()

    def vehicle_generator(self, stop_event, vehicle_list_lock):
        while not stop_event.is_set():
            vehicle = Vehicle(self.screen, self.vehicle_radius, self.vehicle_width, self.vehicle_speed)
            vehicle.generate_vehicle(self.vehicle_spawn_coords, self.vehicle_incoming_direction,
                                     self.vehicle_direction_color, self.vehicle_count)
            with vehicle_list_lock:
                self.vehicle_list.append(vehicle)
            time.sleep(0.5)

    def display_vehicle_count(self, vehicle_count):
        x, y = 20, 20
        line_spacing = 25
        color = (0, 0, 0)
        for k, v in vehicle_count.items():
            content = f"{k.capitalize()} lane: {v}"
            text = self.font.render(content, True, color)
            self.screen.blit(text, (x, y))
            y += line_spacing

    def run(self):

        # Set up the display
        screen = pygame.display.set_mode((self.width, self.height))

        # Create Intersection, Crossing, and Traffic Lights
        intersection = Intersection(screen, self.intersection_center, self.road_width, self.intersection_colors,
                                    self.width, self.height, self.font)
        crossing = Crossing(screen, self.intersection_center, self.road_width, self.intersection_trl_width,
                            self.intersection_colors)
        current_light_state = "GREEN"
        traffic_lights = TrafficLights(screen, self.starting_traffic_light, current_light_state,
                                       self.traffic_lights_directions, self.trl_colors, self.traffic_light_width,
                                       self.intersection_center, self.road_width, self.intersection_trl_width,
                                       self.traffic_light_change_times)

        # Vehicle management
        vehicle_list_lock = threading.Lock()
        stop_event = threading.Event()

        # Start the vehicle generator thread
        vehicle_gen_thread = threading.Thread(target=self.vehicle_generator,
                                              args=(stop_event, vehicle_list_lock))
        try:
            vehicle_gen_thread.start()
        except RuntimeError as e:
            print(f"Error starting thread: {e}")

        # Main loop
        running = True
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                current_time = pygame.time.get_ticks()
                current_traffic_light, current_light_state = traffic_lights.update(current_time)

                # Draw the intersection, traffic lights, and crossing
                intersection.draw()
                traffic_lights.draw()
                crossing.draw()

                # Process and draw vehicles
                with vehicle_list_lock:
                    for vehicle in self.vehicle_list:  # Note the use of self here
                        vehicle.move(current_traffic_light, current_light_state, self.thresholds,
                                     self.vehicle_turning_points, self.vehicle_list)
                        vehicle.draw()
                        if vehicle.kill_vehicle(self.width, self.height):
                            self.vehicle_list.remove(vehicle)

                        has_crossed, crossed_direction = vehicle.crossed_threshold()
                        if has_crossed:
                            self.vehicle_count[crossed_direction] -= 1

                # print(self.vehicle_count)
                self.display_vehicle_count(self.vehicle_count)
                pygame.display.flip()
        except Exception as e:
            print(f"Error during main loop: {e}")
            sys.exit(1)

        # Clean up and exit
        stop_event.set()
        vehicle_gen_thread.join()
        try:
            pygame.quit()
            sys.exit()
        except pygame.error as e:
            print(f"Error quitting Pygame: {e}")


if __name__ == "__main__":
    sarsa = SARSA()
    sarsa.run()
