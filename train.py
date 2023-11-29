from main import Main


def train(episodes):
    environment = Main()
    environment.initialize_sarsa()

    for episode in range(episodes):
        total_reward = 0
        environment.reset_environment()
        current_state = environment.calculate_state()
        current_action = environment.sarsa_agent.choose_action(current_state)
        done = False

        while not done:
            old_dti = environment.calculate_dti()  # Capture the old DTI

            # Apply the chosen action
            environment.apply_action(current_action, environment.traffic_lights)

            new_dti = environment.calculate_dti()  # Calculate the new DTI

            # Calculate the reward based on the old and new DTI values
            reward = environment.calculate_reward(old_dti, new_dti)

            # Get the new state after the action has been applied
            new_state = environment.calculate_state()

            # Choose the next action based on the new state
            next_action = environment.sarsa_agent.choose_action(new_state)

            # Update the SARSA agent
            environment.sarsa_agent.update(current_state, current_action, reward, new_state, next_action)

            # Update variables for the next iteration
            total_reward += reward
            current_state = new_state
            current_action = next_action

            # Check if the training episode should end
            if sum(environment.vehicle_parameters["processed_vehicles"].values()) > 1500:
                done = True

        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

    # Save the trained model
    environment.save_model()


if __name__ == "__main__":
    train(episodes=100)
