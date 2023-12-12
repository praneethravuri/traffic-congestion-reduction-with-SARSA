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

        # the maximum number of vehicles in each lane
        self.vehicle_threshold = 10

        # not needed anymore
        self.action_changed = None
        self.last_action = None

        # Epsilon Decay Parameters
        '''
        Epsilon decay is calculated as per the number of iterations / length of reward list.
        Since the number of iterations are 10000, the epsilon decay is set in such a way that, 
        for the first 90% of the iterations, the model explores and for the next 10% of the iterations, 
         the model exploits what it has learned
        '''

        # TODO: change epsilon decay depending on the number of iterations (number of sarsa decisions)
        #   for the first 90% of the iterations, the exploration should occur
        #   for the remaining 10%, exploitation should occur
        self.initial_epsilon = 0.9  # Starting value of epsilon
        self.epsilon_decay = 0.999756  # Decay factor for each step
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

        # For train.py
        self.total_reward = 0
        self.reward_list = []

    def plot_learning_curve(self):
        # TODO: change window size for 100 (20), 1000 (50), 10000 (500) iterations
        window_size = 500  # Define the size of the window for averaging
        rewards = np.array(self.reward_list)

        # Compute the average rewards over the window
        averaged_rewards = np.convolve(rewards, np.ones(window_size) / window_size, mode='valid')

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(np.arange(len(rewards)), rewards, alpha=0.5, label='Raw Rewards')
        plt.plot(np.arange(window_size - 1, window_size - 1 + len(averaged_rewards)), averaged_rewards, color='red',
                 label='Smoothed Rewards')
        plt.title('Model Learning Curve')
        plt.xlabel('Iterations')
        plt.ylabel('Average Reward')
        plt.legend()
        plt.grid(True)
        # TODO: change the name of the graphs according to the changes
        os.makedirs('plots', exist_ok=True)
        plt.savefig(
            f'plots/alpha_0_05_gamma_0_95.png')
        plt.show()

    @staticmethod
    def calculate_avg_congestion(dti, vehicle_count):
        return {direction: (dti[direction] / vehicle_count[direction] if vehicle_count[direction] > 0 else 0)
                for direction in dti.keys()}

    def calculate_reward(self, old_dti, new_dti, old_vehicle_count, new_vehicle_count):
        old_congestion = self.calculate_avg_congestion(old_dti, old_vehicle_count)
        new_congestion = self.calculate_avg_congestion(new_dti, new_vehicle_count)

        # Calculate rewards for each lane
        lane_rewards = {"north": 0, "south": 0, "east": 0, "west": 0}
        for lane in ["north", "south", "east", "west"]:
            # calculating congestion change percentage
            if old_congestion[lane] > 0:
                congestion_change = 100 * (old_congestion[lane] - new_congestion[lane]) / old_congestion[
                    lane]
            else:
                congestion_change = 0

            if congestion_change >= 50:
                lane_rewards[lane] += 20
            elif 25 <= congestion_change < 50:
                lane_rewards[lane] += 10
            elif 0 <= congestion_change < 25:
                lane_rewards[lane] += 5
            elif congestion_change <= -50:
                lane_rewards[lane] -= 20
            elif -50 <= congestion_change < -25:
                lane_rewards[lane] -= 10
            elif -25 <= congestion_change < 0:
                lane_rewards[lane] -= 5

        return sum(lane_rewards.values())

    def apply_action(self, action, traffic_lights):
        directions = ["north", "east", "south", "west"]
        chosen_direction = directions[action]
        # if self.last_action is None or self.last_action != chosen_direction:
        #     self.action_changed = True
        # elif self.last_action == chosen_direction:
        #     self.action_changed = False
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
        # States - 3 traffic lights, 10 vehicles states, 4 lanes = (3 * 10) ** 4
        number_of_states = 30 ** 4
        # 4 actions (changing the light of each traffic light)
        number_of_actions = 4
        # TODO: alpha and gamma combinations
        #     alpha = 0.1, gamma = 0.9
        #     alpha = 0.1, gamma = 0.95
        #     alpha = 0.1, gamma = 0.99
        #     alpha = 0.05, gamma = 0.9
        #     alpha = 0.05, gamma = 0.95
        #     alpha = 0.05, gamma = 0.99
        self.sarsa_agent = SARSA(alpha=0.05, gamma=0.95, epsilon=self.initial_epsilon,
                                 number_of_states=number_of_states,
                                 number_of_actions=number_of_actions)

    def vehicle_generator(self, stop_event, vehicle_list_lock):
        while not stop_event.is_set():
            # generate a vehicle at a random time
            time.sleep(random.uniform(0.1, 0.5))
            vehicle = Vehicle(self.screen, self.vehicle_parameters["radius"], self.vehicle_parameters["width"],
                              self.vehicle_parameters["speed"],
                              self.vehicle_parameters["processed_vehicles"], self.vehicle_parameters["dti_info"])
            vehicle.generate_vehicle(self.vehicle_spawn_coords, self.vehicle_parameters["incoming_direction"],
                                     self.colors["vehicle_direction"], self.vehicle_parameters["vehicle_count"])
            with vehicle_list_lock:
                self.vehicle_list.append(vehicle)

    def display_data(self, vehicle_count, processed_vehicles, generation):

        # display the vehicle count in each lane
        count_x, count_y = 20, 20
        line_spacing = 25
        color = (0, 0, 0)
        for k, v in vehicle_count.items():
            content = f"{k.capitalize()} lane: {v}"
            count = self.font.render(content, True, color)
            self.screen.blit(count, (count_x, count_y))
            count_y += line_spacing

        # display the number of vehicles that have crossed the green light
        processed_x, processed_y = 20, count_y + line_spacing
        processed_count = self.font.render(f"Processed Vehicles: {str(sum(processed_vehicles.values()))}", True, color)
        self.screen.blit(processed_count, (processed_x, processed_y))

        # display the generation count
        if generation is not None:
            gen_x, gen_y = 20, processed_y + line_spacing
            current_gen = self.font.render(f"Generation: {generation}", True, color)
            self.screen.blit(current_gen, (gen_x, gen_y))

    def calculate_dti(self):
        ans = {}

        for main_key in self.vehicle_parameters["dti_info"].keys():
            total = 0
            for k, v in self.vehicle_parameters["dti_info"][main_key].items():
                total += v
            ans[main_key] = round(total, 2)

        return ans

    @staticmethod
    def calculate_traffic_trend(current_counts, previous_counts):
        trend = {}
        for direction in current_counts:
            if current_counts[direction] > previous_counts[direction]:
                trend[direction] = 'increasing'
            elif current_counts[direction] < previous_counts[direction]:
                trend[direction] = 'decreasing'
            else:
                trend[direction] = 'stable'
        return trend

    @staticmethod
    def predict_future_traffic(current_trend):
        prediction = {}
        for direction, trend in current_trend.items():
            if trend == 'increasing':
                prediction[direction] = 'likely to increase'
            elif trend == 'decreasing':
                prediction[direction] = 'likely to decrease'
            else:
                prediction[direction] = 'likely to remain stable'
        return prediction

    def should_take_action(self, predictions):
        for direction, prediction in predictions.items():
            if prediction == 'likely to increase' and self.vehicle_parameters["vehicle_count"][
                direction] > self.vehicle_threshold:
                return True
        return False

    def run(self, generation=None, training=False, end_count=None, action_list=None):

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
        old_vehicle_count = self.vehicle_parameters["vehicle_count"].copy()
        action_index = 0
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                current_time = pygame.time.get_ticks()
                current_traffic_light, current_light_state, current_traffic_light_colors = traffic_lights.update(
                    current_time)

                new_vehicle_count = self.vehicle_parameters["vehicle_count"].copy()
                traffic_trend = self.calculate_traffic_trend(new_vehicle_count, old_vehicle_count)
                future_traffic_prediction = self.predict_future_traffic(traffic_trend)

                # for train.py
                if training:
                    if self.should_take_action(future_traffic_prediction):
                        self.sarsa_agent.epsilon = max(self.min_epsilon, self.sarsa_agent.epsilon * self.epsilon_decay)

                        current_state = self.calculate_state()
                        current_action = self.sarsa_agent.choose_action(current_state)
                        self.apply_action(current_action, traffic_lights)

                        new_dti = self.calculate_dti()
                        reward = self.calculate_reward(old_dti, new_dti, old_vehicle_count, new_vehicle_count)
                        self.reward_list.append(reward)
                        self.total_reward += reward

                        new_state = self.calculate_state()
                        next_action = self.sarsa_agent.choose_action(new_state)
                        self.sarsa_agent.update(current_state, current_action, reward, new_state, next_action)
                        self.last_action_time = current_time
                        old_dti = new_dti

                # for model.py
                if action_list is not None and action_index < len(action_list):
                    current_action = action_list[action_index]
                    self.apply_action(current_action, traffic_lights)
                    action_index += 1

                old_vehicle_count = new_vehicle_count

                intersection.draw()
                traffic_lights.draw()
                crossing.draw()

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

                self.display_data(self.vehicle_parameters["vehicle_count"],
                                  self.vehicle_parameters["processed_vehicles"], generation)

                pygame.display.flip()

                if training:
                    if len(self.reward_list) > end_count:
                        return self.total_reward

        except Exception as e:
            print(f"Error during main loop: {e}", end='\r')
            traceback.print_exc()

        finally:
            stop_event.set()
            vehicle_gen_thread.join()
            # self.plot_learning_curve()

        try:
            pygame.quit()
            sys.exit()
        except pygame.error as e:
            print(f"Error quitting Pygame: {e}")

        sys.exit()


if __name__ == "__main__":
    main = Main()
    main.run()
