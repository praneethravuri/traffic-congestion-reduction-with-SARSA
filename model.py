import numpy as np
from main import Main


class Model:
    def __init__(self, q_table_filename):
        self.q_table_filename = q_table_filename
        self.q_table = None
        self.best_actions = None
        self.main_instance = Main()

    def load_q_table(self):
        # Load the Q-table from a .npy file.
        self.q_table = np.load(self.q_table_filename)

    def determine_best_actions(self):
        # Determine the best action for each state based on the Q-table.
        if self.q_table is not None:
            self.best_actions = np.argmax(self.q_table, axis=1)
        else:
            raise ValueError("Q-table not loaded")

    def implement_in_simulation(self):
        # Implement the best actions in the simulation environment.
        # This method needs to be tailored to the specific simulation environment.
        if self.best_actions is None:
            raise ValueError("Best actions not determined. Call determine_best_actions() first.")

        action_list = []
        for state in range(len(self.best_actions)):
            action_list.append(self.best_actions[state])

        self.main_instance.run(action_list=action_list, training=True)


# Usage
if __name__ == "__main__":
    q_table_file = "saved_models/sarsa_q_table.npy"
    model = Model(q_table_file)

    model.load_q_table()
    model.determine_best_actions()

    model.implement_in_simulation()
