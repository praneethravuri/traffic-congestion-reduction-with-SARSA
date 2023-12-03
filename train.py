from main import Main
import time


def train(generations):
    main_instance = Main()

    for generation in range(generations):
        main_instance.reset_environment()
        main_instance.initialize_sarsa()
        total_reward = main_instance.run()
        time.sleep(1)
        print(f"Generation: {generation + 1} | Reward: {total_reward}")

    main_instance.save_model()


if __name__ == "__main__":
    train(generations=100)
