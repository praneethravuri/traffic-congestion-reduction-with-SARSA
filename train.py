from main import Main
import pygame
import time


def train(episodes):
    environment = Main()
    environment.initialize_sarsa()

    for episode in range(episodes):
        total_reward = 0
        environment.reset_environment()
        current_state = environment.calculate_state()
        current_action = environment.sarsa_agent.choose_action(current_state)

        environment.old_dti = environment.calculate_dti()

        # Start the timer
        start_time = time.time()

        done = False
        while not done:
            # Check for elapsed time
            current_time = time.time()
            if current_time - start_time >= 60:  # 60 seconds for 1 minute
                done = True

            # Other training code here...
            # Handle Pygame events, apply actions, simulate steps, etc.

            # Print the episode number and update the display
            print(f"Episode number: {episode}")
            environment.run()

            # Limit the frame rate for visibility
            pygame.time.delay(100)

        # End of episode
        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

    # Save the model after all episodes
    environment.save_model()


if __name__ == "__main__":
    train(episodes=1)
