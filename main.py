import pygame
import random
import threading
import time
import sys
import traceback
from intersection import Intersection
from crossing import Crossing
from traffic_lights import TrafficLights
from vehicle import Vehicle
from sarsa import SARSA
import os
import numpy as np
import matplotlib.pyplot as plt


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
            "speed": 1,

            "incoming_direction": ["north", "east", "south", "west"],
            "vehicle_count": {"north": 0, "south": 0, "east": 0, "west": 0},
            "processed_vehicles": {"north": 0, "south": 0, "east": 0, "west": 0},
            "dti_info": {"north": {}, "south": {}, "east": {}, "west": {}}
        }

        self.traffic_light_parameters = {
            "directions": ["north", "east", "south", "west"],
            "timings": {
                "RED": 10,
                "GREEN": 10,
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

        # Epsilon Decay Parameters
        self.initial_epsilon = 0.9  # Starting value of epsilon
        self.epsilon_decay = 0.9995  # Decay factor for each step
        self.min_epsilon = 0.1  # Minimum value of epsilon

        # font object
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 36)

        self.current_light_state = "RED"
        self.traffic_lights = TrafficLights(self.screen, self.starting_traffic_light, self.current_light_state,
                                            self.traffic_light_parameters["directions"], self.colors["traffic_lights"],
                                            self.traffic_light_width,
                                            self.intersection_center, self.road_width, self.intersection_trl_width,
                                            self.traffic_light_parameters["timings"])

        self.sarsa_agent = None
        self.initialize_sarsa()

        self.last_action_time = None

        self.total_reward = 0
        self.reward_list = []

    def plot_average_rewards(self):
        window_size = 50
        average_rewards = [np.mean(self.reward_list[i:i + window_size]) for i in range(0, len(self.reward_list), window_size)]
        plt.figure()
        plt.plot(average_rewards)
        plt.xlabel('Time (in windows of {} steps)'.format(window_size))
        plt.ylabel('Average Reward')
        plt.title('Average Reward Over Time')
        os.makedirs('plots', exist_ok=True)
        plt.savefig('plots/average_rewards_plot.png')
        plt.close()

    @staticmethod
    def calculate_reward(old_dti, new_dti):
        max_reward = 10
        max_penalty = -10

        delay_before = sum(old_dti.values())
        delay_after = sum(new_dti.values())

        if delay_before == 0:
            if delay_after > 0:
                # Introducing delay where there was none should be penalized
                return max_penalty
            else:
                # Maintaining no congestion could be a neutral or slightly positive outcome
                return 1  # or some small positive value
        else:
            improvement = delay_before - delay_after
            if improvement > 0:
                # Scale the reward based on the percentage improvement
                reward = (improvement / delay_before) * max_reward
            elif improvement < 0:
                # Scale the penalty based on the percentage worsening
                penalty_ratio = abs(improvement) / delay_before
                reward = penalty_ratio * max_penalty
            else:
                # No change in delay
                reward = 0

        return reward

    def apply_action(self, action, traffic_lights):
        directions = ["north", "east", "south", "west"]
        chosen_direction = directions[action]
        traffic_lights.change_light(chosen_direction)
        self.last_action_time = pygame.time.get_ticks()

    def calculate_state(self):
        dti_values = self.calculate_dti()
        # Sort directions based on DTI values
        sorted_directions = sorted(dti_values, key=dti_values.get, reverse=True)
        # Encode the sorted directions into state
        state = [str(sorted_directions.index(direction)) for direction in ["north", "east", "south", "west"]]
        # Convert to integer state
        return int(''.join(state))

    def initialize_sarsa(self):
        # Define the number of states and actions
        # States - 3 traffic lights, 5 vehicles states, 4 lanes = (3 * 5) ** 4
        number_of_states = 15 ** 4
        # 4 actions
        number_of_actions = 4
        self.sarsa_agent = SARSA(alpha=0.1, gamma=0.9, epsilon=self.initial_epsilon,
                                 number_of_states=number_of_states,
                                 number_of_actions=number_of_actions)

    def vehicle_generator(self, stop_event, vehicle_list_lock):
        while not stop_event.is_set():
            time.sleep(random.uniform(0.1, 0.5))
            vehicle = Vehicle(self.screen, self.vehicle_parameters["radius"], self.vehicle_parameters["width"],
                              self.vehicle_parameters["speed"],
                              self.vehicle_parameters["processed_vehicles"], self.vehicle_parameters["dti_info"])
            vehicle.generate_vehicle(self.vehicle_spawn_coords, self.vehicle_parameters["incoming_direction"],
                                     self.colors["vehicle_direction"], self.vehicle_parameters["vehicle_count"])
            with vehicle_list_lock:
                self.vehicle_list.append(vehicle)

    def display_data(self, vehicle_count, processed_vehicles):
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

    def calculate_dti(self):
        ans = {}

        for main_key in self.vehicle_parameters["dti_info"].keys():
            total = 0
            for k, v in self.vehicle_parameters["dti_info"][main_key].items():
                total += v
            ans[main_key] = round(total, 2)

        return ans

    def reset_environment(self):
        self.current_light_state = "RED"
        self.starting_traffic_light = random.choice(self.traffic_light_parameters["directions"])
        self.traffic_lights = TrafficLights(self.screen, self.starting_traffic_light, self.current_light_state,
                                            self.traffic_light_parameters["directions"], self.colors["traffic_lights"],
                                            self.traffic_light_width,
                                            self.intersection_center, self.road_width, self.intersection_trl_width,
                                            self.traffic_light_parameters["timings"])

        # Clear all vehicles and reset related parameters
        with self.vehicle_list_lock:
            self.vehicle_list.clear()
        self.vehicle_parameters["vehicle_count"] = {"north": 0, "south": 0, "east": 0, "west": 0}
        self.vehicle_parameters["processed_vehicles"] = {"north": 0, "south": 0, "east": 0, "west": 0}
        self.vehicle_parameters["dti_info"] = {"north": {}, "south": {}, "east": {}, "west": {}}

        # Reset timers and counters
        self.last_action_time = None

        # Reset reward and other metrics
        self.total_reward = 0

        self.initial_epsilon = 0.9

    def save_model(self):
        # Ensure the directory for saving exists
        os.makedirs('saved_models', exist_ok=True)
        # Save the Q-table
        np.save('saved_models/sarsa_q_table.npy', self.sarsa_agent.q_table)
        print("Model saved successfully.")

    def run(self):

        screen = pygame.display.set_mode((self.width, self.height))

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

        vehicle_list_lock = threading.Lock()
        stop_event = threading.Event()

        vehicle_gen_thread = threading.Thread(target=self.vehicle_generator,
                                              args=(stop_event, vehicle_list_lock))
        try:
            vehicle_gen_thread.start()
        except RuntimeError as e:
            print(f"Error starting thread: {e}")

        # Main loop
        old_dti = self.calculate_dti()
        running = True
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                current_time = pygame.time.get_ticks()
                current_traffic_light, current_light_state, current_traffic_light_colors = traffic_lights.update(
                    current_time)

                if self.sarsa_agent.epsilon > self.min_epsilon:
                    self.sarsa_agent.epsilon *= self.epsilon_decay

                if self.last_action_time is None or (current_time - self.last_action_time) >= 500:
                    current_state = self.calculate_state()
                    current_action = self.sarsa_agent.choose_action(current_state)
                    self.apply_action(current_action, traffic_lights)

                    new_dti = self.calculate_dti()
                    reward = self.calculate_reward(old_dti, new_dti)
                    print(f"Reward: {reward}")
                    self.reward_list.append(reward)
                    self.total_reward += reward

                    new_state = self.calculate_state()
                    next_action = self.sarsa_agent.choose_action(new_state)
                    self.sarsa_agent.update(current_state, current_action, reward, new_state, next_action)
                    self.last_action_time = current_time
                    old_dti = new_dti

                intersection.draw()
                traffic_lights.draw()
                crossing.draw()

                # Process and draw vehicles
                with vehicle_list_lock:
                    for vehicle in self.vehicle_list:  # Note the use of self here
                        vehicle.move(self.vehicle_list, current_traffic_light, current_light_state, self.thresholds,
                                     self.vehicle_turning_points, current_traffic_light_colors)
                        vehicle.draw()
                        if vehicle.kill_vehicle(self.width, self.height):
                            self.vehicle_list.remove(vehicle)

                        has_crossed, crossed_direction = vehicle.crossed_threshold()
                        if has_crossed:
                            self.vehicle_parameters["vehicle_count"][crossed_direction] -= 1

                self.display_data(self.vehicle_parameters["vehicle_count"],
                                  self.vehicle_parameters["processed_vehicles"])

                pygame.display.flip()

                if sum(self.vehicle_parameters["processed_vehicles"].values()) > 100000:
                    running = False

        except Exception as e:
            print(f"Error during main loop: {e}", end='\r')
            traceback.print_exc()

        finally:
            stop_event.set()
            vehicle_gen_thread.join()
            self.plot_average_rewards()

        try:
            pygame.quit()
            sys.exit()
        except pygame.error as e:
            print(f"Error quitting Pygame: {e}")

        sys.exit()


if __name__ == "__main__":
    main = Main()
    main.run()
