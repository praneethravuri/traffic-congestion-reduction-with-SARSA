import pygame
import random
import threading
import time
import sys
from intersection import Intersection
from crossing import Crossing
from traffic_lights import TrafficLights
from vehicle import Vehicle


class Main:
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

        self.colors = {
            "intersection": {
                "BLACK": (0, 0, 0),
                "GREEN": (26, 93, 26),
                "RED": (255, 0, 0),
                "YELLOW": (255, 255, 0),
                "GRAY": (128, 128, 128),
                "WHITE": (255, 255, 255),
                "BROWN": (185, 148, 112)
            },
            "traffic_lights": {
                "YELLOW_TR": (255, 255, 0),
                "GREEN_TR": (78, 228, 78),
                "RED_TR": (255, 0, 0)
            },
            "vehicle_direction": {
                "straight": (255, 163, 60),
                "left": (135, 196, 255),
                "right": (255, 75, 145)
            }
        }

        self.vehicle_parameters = {
            "radius": 12,
            "width": 12,
            "gap": 12,
            "speed": 0.25,
            "incoming_direction": ["north", "east", "south", "west"],
            "vehicle_count": {"north": 0, "south": 0, "east": 0, "west": 0},
            "wait_times": {"north": [], "south": [], "east": [], "west": []},
            "processed_vehicles": {"north": 0, "south": 0, "east": 0, "west": 0},
        }

        self.traffic_light_parameters = {
            "directions": ["north", "east", "south", "west"],
            "timings": {
                "RED": 5,
                "GREEN": 5,
                "YELLOW": 2
            }
        }

        self.thresholds = {
            "west": self.intersection_center[0] - self.road_width // 2 - self.intersection_trl_width - 30,
            "east": self.intersection_center[
                        0] - self.road_width // 2 + self.road_width + self.intersection_trl_width + 30,
            "north": self.intersection_center[1] - self.road_width // 2 - self.intersection_trl_width - 30,
            "south": self.intersection_center[1] + self.road_width - 15
        }

        self.starting_traffic_light = random.choice(self.traffic_light_parameters["directions"])

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

        # threading parameters
        self.vehicle_list = []
        self.vehicle_list_lock = threading.Lock()

        # font object
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 36)

        # sarsa metrics

        # delay time indicator
        self.dti = 0

    def vehicle_generator(self, stop_event, vehicle_list_lock):
        while not stop_event.is_set():
            vehicle = Vehicle(self.screen, self.vehicle_parameters["radius"], self.vehicle_parameters["width"],
                              self.vehicle_parameters["speed"], self.vehicle_parameters["wait_times"],
                              self.vehicle_parameters["processed_vehicles"])
            vehicle.generate_vehicle(self.vehicle_spawn_coords, self.vehicle_parameters["incoming_direction"],
                                     self.colors["vehicle_direction"], self.vehicle_parameters["vehicle_count"])
            with vehicle_list_lock:
                self.vehicle_list.append(vehicle)
            time.sleep(0.5)

    def display_data(self, vehicle_count, processed_vehicles, dti):
        x, y = 20, 20
        line_spacing = 25
        color = (0, 0, 0)
        for k, v in vehicle_count.items():
            content = f"{k.capitalize()} lane: {v}"
            text = self.font.render(content, True, color)
            self.screen.blit(text, (x, y))
            y += line_spacing

        x_1, y_1 = 20, y + line_spacing
        text_2 = self.font.render(f"Processed Vehicles: {str(sum(processed_vehicles.values()))}", True, color)
        self.screen.blit(text_2, (x_1, y_1))

        x_2, y_2 = 20, y_1 + line_spacing
        if dti != 0:
            text_3 = self.font.render(f"DTI: {dti}", True, color)
            self.screen.blit(text_3, (x_2, y_2))
        else:
            text_3 = self.font.render("DTI: 0", True, color)
            self.screen.blit(text_3, (x_2, y_2))

    # METRIC - 1
    def calculate_dti(self):
        lane_delay_times = {direction: round(sum(values), 2) for direction, values in
                            self.vehicle_parameters["wait_times"].items()}

        # METRIC - 2
        lane_vehicle_count = {direction: len(values) for direction, values in
                              self.vehicle_parameters["wait_times"].items()}

        total_delay_time = sum(lane_delay_times.values())
        total_waiting_vehicles = sum(lane_vehicle_count.values())

        if total_waiting_vehicles > 0:
            self.dti = round(total_delay_time / total_waiting_vehicles, 3)

    def run(self):

        # Set up the display
        screen = pygame.display.set_mode((self.width, self.height))

        # Create Intersection, Crossing, and Traffic Lights
        intersection = Intersection(screen, self.intersection_center, self.road_width, self.colors["intersection"],
                                    self.width, self.height, self.font)
        crossing = Crossing(screen, self.intersection_center, self.road_width, self.intersection_trl_width,
                            self.colors["intersection"])
        current_light_state = "GREEN"
        traffic_lights = TrafficLights(screen, self.starting_traffic_light, current_light_state,
                                       self.traffic_light_parameters["directions"], self.colors["traffic_lights"],
                                       self.traffic_light_width,
                                       self.intersection_center, self.road_width, self.intersection_trl_width,
                                       self.traffic_light_parameters["timings"])

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
                                     self.vehicle_turning_points, current_time)
                        vehicle.draw()
                        if vehicle.kill_vehicle(self.width, self.height):
                            self.vehicle_list.remove(vehicle)

                        has_crossed, crossed_direction = vehicle.crossed_threshold()
                        if has_crossed:
                            self.vehicle_parameters["vehicle_count"][crossed_direction] -= 1

                self.calculate_dti()
                self.display_data(self.vehicle_parameters["vehicle_count"],
                                  self.vehicle_parameters["processed_vehicles"], self.dti)
                # total_delay = sum([sum(times) for times in self.vehicle_parameters["wait_times"].values()])

                # SECOND METRIC!!!
                # waiting_vehicles = sum([len(times) for times in self.vehicle_parameters["wait_times"].values()])
                #
                # if waiting_vehicles > 0:
                #     print(f"DTI: {total_delay}")

                # print(self.vehicle_parameters["wait_times"])

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
    main = Main()
    main.run()
