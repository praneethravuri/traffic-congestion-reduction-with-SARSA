import pygame


class Crossing:

    def __init__(self, screen, intersection_center, road_width, intersection_trl_width, intersection_colors):
        self.screen = screen
        self.intersection_center = intersection_center
        self.intersection_colors = intersection_colors
        self.road_width = road_width
        self.intersection_trl_width = intersection_trl_width

    def draw_crossing(self, position, size):
        # drawing the crossing
        pygame.draw.rect(self.screen, self.intersection_colors["GRAY"], (position, size))

    def draw(self):
        # Crossing parameters for west and east lanes
        west_crossing_x = self.intersection_center[0] - self.road_width // 2 - 25 - 5
        east_crossing_x = self.intersection_center[0] + self.road_width // 2
        crossing_y = self.intersection_center[1] - self.road_width // 2

        # Crossing parameters for north and south lanes
        crossing_x = self.intersection_center[0] - self.road_width // 2
        north_crossing_y = self.intersection_center[1] - self.road_width // 2 - 25
        south_crossing_y = self.intersection_center[1] + self.road_width // 2

        # Draw crossings for each lane
        self.draw_crossing((west_crossing_x, crossing_y), (self.intersection_trl_width, self.road_width))
        self.draw_crossing((east_crossing_x, crossing_y), (self.intersection_trl_width, self.road_width))
        self.draw_crossing((crossing_x, north_crossing_y), (self.road_width, 25))
        self.draw_crossing((crossing_x, south_crossing_y), (self.road_width, 25))
