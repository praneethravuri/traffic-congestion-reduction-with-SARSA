from main import Main

def train(episodes):
    environment = Main()
    environment.initialize_sarsa()

    for episode in range(episodes):
        total_reward = 0
        environment.reset_environment()
        current_state = environment.calculate_state()
        current_action = environment.sarsa_agent.choose_action(current_state)

        # Initialize old_dti at the start of each episode
        environment.old_dti = environment.calculate_dti()

        done = False
        while not done:
            # Apply the chosen action
            environment.apply_action(current_action, environment.traffic_lights)

            # Calculate the new DTI
            new_dti = environment.calculate_dti()

            # Calculate the reward
            reward = environment.calculate_reward(environment.old_dti, new_dti)

            # Update the SARSA agent
            new_state = environment.calculate_state()
            next_action = environment.sarsa_agent.choose_action(new_state)
            environment.sarsa_agent.update(current_state, current_action, reward, new_state, next_action)

            # Update variables for the next iteration
            total_reward += reward
            environment.old_dti = new_dti
            current_state = new_state
            current_action = next_action

            # Check for the end of the episode
            if sum(environment.vehicle_parameters["processed_vehicles"].values()) > 1500:
                done = True

        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

    environment.save_model()

if __name__ == "__main__":
    train(episodes=100)
