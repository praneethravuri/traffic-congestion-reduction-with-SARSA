from main import Main
import time
import random
from traffic_lights import TrafficLights
import os
import numpy as np


class Train:
    def __init__(self, generations, end_count):
        self.main_instance = Main()
        self.generations = generations
        self.end_count = end_count

    def reset_environment(self):
        self.main_instance.current_light_state = "RED"
        self.main_instance.starting_traffic_light = random.choice(
            self.main_instance.traffic_light_parameters["directions"])
        self.main_instance.traffic_lights = TrafficLights(self.main_instance.screen,
                                                          self.main_instance.starting_traffic_light,
                                                          self.main_instance.current_light_state,
                                                          self.main_instance.traffic_light_parameters["directions"],
                                                          self.main_instance.colors["traffic_lights"],
                                                          self.main_instance.traffic_light_width,
                                                          self.main_instance.intersection_center,
                                                          self.main_instance.road_width,
                                                          self.main_instance.intersection_trl_width,
                                                          self.main_instance.traffic_light_parameters["timings"])

        # Clear all vehicles and reset related parameters
        with self.main_instance.vehicle_list_lock:
            self.main_instance.vehicle_list.clear()
        self.main_instance.vehicle_parameters["vehicle_count"] = {"north": 0, "south": 0, "east": 0, "west": 0}
        self.main_instance.vehicle_parameters["processed_vehicles"] = {"north": 0, "south": 0, "east": 0, "west": 0}
        self.main_instance.vehicle_parameters["dti_info"] = {"north": {}, "south": {}, "east": {}, "west": {}}

        # Reset timers and counters
        self.main_instance.last_action_time = None

        # Reset reward and other metrics
        self.main_instance.total_reward = 0

        self.main_instance.initial_epsilon = 0.9

    def save_model(self):
        # Ensure the directory for saving exists
        os.makedirs('saved_models', exist_ok=True)
        # Save the Q-table
        np.save('saved_models/sarsa_q_table.npy', self.main_instance.sarsa_agent.q_table)
        print("Model saved successfully.")

    def train(self):
        for generation in range(self.generations):
            self.reset_environment()
            self.main_instance.initialize_sarsa()
            total_reward = self.main_instance.run(generation=generation + 1, training=True, end_count=self.end_count)
            time.sleep(1)
            print(f"Generation: {generation + 1} | Reward: {total_reward}")

        self.save_model()


if __name__ == "__main__":
    train_model = Train(generations=3, end_count=100)
    train_model.train()
