from main import Main
import pygame
import threading
import sys
import traceback
from intersection import Intersection
from crossing import Crossing
from traffic_lights import TrafficLights
from vehicle import Vehicle
from sarsa import SARSA
import os
import numpy as np


class Train:
    def __init__(self):
        self.environment = Main()
        self.total_reward = 0
        self.old_dti = {"north": 0, "south": 0, "east": 0, "west": 0}
        self.new_dti = {"north": 0, "south": 0, "east": 0, "west": 0}
        self.width = self.environment.width
        self.height = self.environment.height
        self.road_width = self.environment.road_width
        self.screen = self.environment.screen
        self.traffic_light_width = self.environment.traffic_light_width
        self.intersection_center = self.environment.intersection_center
        self.intersection_trl_width = self.environment.intersection_trl_width

        self.colors = self.environment.colors
        self.vehicle_parameters = self.environment.vehicle_parameters
        self.traffic_light_parameters = self.environment.traffic_light_parameters

        self.thresholds = self.environment.thresholds
        self.starting_traffic_light = self.environment.starting_traffic_light

        self.vehicle_spawn_coords = self.environment.vehicle_spawn_coords
        self.vehicle_turning_points = self.environment.vehicle_turning_points

        self.test_total = self.environment.test_total

        self.vehicle_list = self.environment.vehicle_list
        self.vehicle_list_lock = self.environment.vehicle_list_lock

        self.font = self.environment.font
        self.current_light_state = self.environment.current_light_state

        self.traffic_lights = self.environment.traffic_lights

        self.sarsa_agent = self.environment.sarsa_agent
        self.environment.initialize_sarsa()

        self.last_action_time = self.environment.last_action_time

    def run(self):
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
        vehicle_gen_thread = threading.Thread(target=self.environment.vehicle_generator,
                                              args=(stop_event, vehicle_list_lock))
        vehicle_gen_thread.start()

        # Main loop
        running = True
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                current_time = pygame.time.get_ticks()
                current_traffic_light, current_light_state, current_traffic_light_colors = traffic_lights.update(
                    current_time)

                # Draw the intersection, traffic lights, and crossing
                intersection.draw()
                traffic_lights.draw()
                crossing.draw()

                # Process and draw vehicles
                with vehicle_list_lock:
                    for vehicle in self.vehicle_list:
                        vehicle.move(self.vehicle_list, current_traffic_light, current_light_state, self.thresholds,
                                     self.vehicle_turning_points, current_traffic_light_colors)
                        vehicle.draw()
                        if vehicle.kill_vehicle(self.width, self.height):
                            self.vehicle_list.remove(vehicle)

                        has_crossed, crossed_direction = vehicle.crossed_threshold()
                        if has_crossed:
                            self.vehicle_parameters["vehicle_count"][crossed_direction] -= 1

                self.environment.display_data(self.vehicle_parameters["vehicle_count"],
                                              self.vehicle_parameters["processed_vehicles"])

                pygame.display.flip()

        except Exception as e:
            print(f"Error during main loop: {e}")
            traceback.print_exc()
            sys.exit(1)

        # Clean up and exit
        stop_event.set()
        vehicle_gen_thread.join()
        pygame.quit()
        sys.exit()

    def train_model(self, episodes):
        self.environment.reset_environment()
        self.environment.initialize_sarsa()

        for episode in range(episodes):
            total_reward = 0
            self.environment.reset_environment()
            current_state = self.environment.calculate_state()
            current_action = self.environment.sarsa_agent.choose_action(current_state)


if __name__ == "__main__":
    train = Train()
    train.run()
    train.train_model(episodes=10)
