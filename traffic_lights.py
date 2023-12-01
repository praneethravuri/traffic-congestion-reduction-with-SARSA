import pygame


class TrafficLights:
    def __init__(self, screen, current_traffic_light, current_light_state, traffic_lights_directions, trl_colors,
                 traffic_light_width, intersection_center, road_width, intersection_trl_width,
                 traffic_light_change_times):
        self.screen = screen
        self.current_traffic_light = current_traffic_light
        self.current_traffic_light_index = traffic_lights_directions.index(self.current_traffic_light)
        self.current_light_state = current_light_state
        self.traffic_lights_directions = traffic_lights_directions
        self.trl_colors = trl_colors
        self.traffic_light_width = traffic_light_width
        self.intersection_center = intersection_center
        self.road_width = road_width
        self.intersection_trl_width = intersection_trl_width
        self.traffic_light_change_times = traffic_light_change_times
        self.last_change_time = pygame.time.get_ticks()

    def draw_traffic_light(self, direction, color):
        if direction == "north":
            width = self.traffic_light_width * 2 - self.road_width // 2
            position = (self.intersection_center[0] - width // 2 - self.road_width // 4,
                        self.intersection_center[1] - self.road_width // 2 - self.intersection_trl_width - 5)
            size = (width, 10)
        elif direction == "south":
            width = self.traffic_light_width * 2 - self.road_width // 2
            position = (self.intersection_center[0] - width // 2 + self.road_width // 4,
                        self.intersection_center[1] + self.road_width // 2 - 5 + self.intersection_trl_width)
            size = (width, 10)
        elif direction == "east":
            height = self.traffic_light_width * 2 - self.road_width // 2
            position = (self.intersection_center[0] + self.road_width // 2 + self.intersection_trl_width,
                        self.intersection_center[1] - height // 2 - self.road_width // 4)
            size = (10, height)
        elif direction == "west":
            height = self.traffic_light_width * 2 - self.road_width // 2
            position = (self.intersection_center[0] - self.road_width // 2 - self.intersection_trl_width - 10,
                        self.intersection_center[1] - height // 2 + self.road_width // 4)
            size = (10, height)

        pygame.draw.rect(self.screen, color, (*position, *size))

    def draw(self):
        light_color = self.trl_colors[self.current_light_state + "_TR"]

        # Set the color of the current traffic light
        colors = {dr: self.trl_colors["RED_TR"] for dr in ["north", "south", "east", "west"]}
        colors[self.current_traffic_light] = light_color

        # Drawing traffic lights for all directions
        for direction, color in colors.items():
            self.draw_traffic_light(direction, color)

    def update(self, current_time):
        time_diff = current_time - self.last_change_time
        time_limit = self.traffic_light_change_times[self.current_light_state] * 1000

        if time_diff >= time_limit:
            if self.current_light_state == "GREEN":
                self.current_light_state = "YELLOW"
            elif self.current_light_state == "YELLOW":
                self.current_light_state = "RED"
                # Move to next traffic light
                self.current_traffic_light_index = (self.current_traffic_light_index + 1) % len(
                    self.traffic_lights_directions)
            elif self.current_light_state == "RED":
                self.current_light_state = "GREEN"

            self.last_change_time = current_time

        self.current_traffic_light = self.traffic_lights_directions[self.current_traffic_light_index]

        current_traffic_light_colors = {direction: "RED" for direction in self.traffic_lights_directions}
        current_traffic_light_colors[self.current_traffic_light] = self.current_light_state

        # print(f"Traffic light color: {current_traffic_light_colors}")

        return self.current_traffic_light, self.current_light_state, current_traffic_light_colors

    def change_light(self, direction):
        # Change the current traffic light to the specified direction
        if direction in self.traffic_lights_directions:
            self.current_traffic_light = direction
            self.current_traffic_light_index = self.traffic_lights_directions.index(direction)
            self.current_light_state = "GREEN"  # Assuming you want to change it directly to green
            self.last_change_time = pygame.time.get_ticks()

    # Inside the TrafficLights class:
    def reset(self):
        self.current_traffic_light = self.traffic_lights_directions[0]  # or whatever the initial light should be
        self.current_light_state = "RED"  # or your initial state
        self.last_change_time = pygame.time.get_ticks()
        # Reset any other state variables here
