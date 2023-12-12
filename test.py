import matplotlib.pyplot as plt
import numpy as np
import os


# Function to create a simulated learning curve
def create_learning_curve(iterations=10000):
    # Randomly choose points in the iteration for the trend changes
    first_trend_change = np.random.randint(1000, 4000)
    second_trend_change = np.random.randint(5000, 7000)

    # Generate a random walk with a clear upward trend over time
    rewards = np.random.normal(0, 10, iterations).cumsum()

    # Apply random trends at different points
    rewards[:first_trend_change] += np.linspace(0, -np.random.uniform(20, 50), first_trend_change)
    rewards[first_trend_change:second_trend_change] += np.linspace(-np.random.uniform(20, 50),
                                                                   np.random.uniform(20, 50),
                                                                   second_trend_change - first_trend_change)
    rewards[second_trend_change:] += np.linspace(np.random.uniform(20, 50), np.random.uniform(50, 100),
                                                 iterations - second_trend_change)

    # Introduce noise to make the graph realistic
    noise = np.random.normal(0, np.random.uniform(3, 7), iterations)
    rewards += noise

    # Apply a moving average to smooth the graph
    smoothed_rewards = np.convolve(rewards, np.ones(150) / 150, mode='valid')

    # Plot the results
    plt.figure(figsize=(14, 7))
    plt.plot(rewards, label='Raw Rewards', color='blue', alpha=0.3)
    plt.plot(np.arange(len(smoothed_rewards)), smoothed_rewards, label='Smoothed Rewards', color='red')
    plt.title('Rewards vs Iterations')
    plt.xlabel('Iterations')
    plt.ylabel('Reward')
    plt.legend()
    plt.grid(True)
    os.makedirs('plots', exist_ok=True)
    plt.savefig(
        f'plots/6.png')
    plt.show()


# Call the function to create and display the learning curve
create_learning_curve()
