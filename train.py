from main import Main
import pygame


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
        done = True
        while done:
            print(f"Episode number: {episode+1}")

            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = False

            # Apply the chosen action
            environment.apply_action(current_action, environment.traffic_lights)

            # Inside the train function, within the while not done loop
            # environment.simulate_step()
            # print("simulate step")

            # Simulate environment's step here
            # This should include moving vehicles and updating DTI

            # Calculate the new DTI
            new_dti = environment.calculate_dti()
            print(f"new_dti: {new_dti}")

            # Calculate the reward
            reward = environment.calculate_reward(environment.old_dti, new_dti)
            print(f"Reward: {reward}")

            # Update the SARSA agent
            new_state = environment.calculate_state()
            next_action = environment.sarsa_agent.choose_action(new_state)
            environment.sarsa_agent.update(current_state, current_action, reward, new_state, next_action)

            # Update variables for the next iteration
            total_reward += reward
            environment.old_dti = new_dti
            current_state = new_state
            current_action = next_action

            # Update the display
            episode_over = environment.run()

            if episode_over:
                print(f"Episode {episode + 1} completed.")
                done = False
            else:
                print(f"Episode {episode + 1} ended prematurely.")
                done = False

            # Limit the frame rate for visibility
            pygame.time.delay(100)

            # if sum(environment.vehicle_parameters["processed_vehicles"].values()) > 1:
            #     print("here")
            #     done = True

        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

    environment.save_model()


if __name__ == "__main__":
    train(episodes=10)
