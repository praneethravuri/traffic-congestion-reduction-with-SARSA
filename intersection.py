import pygame


class Intersection:
    def __init__(self, screen, center, road_width, intersection_colors, width, height, font):
        self.screen = screen
        self.center = center
        self.road_width = road_width
        self.intersection_colors = intersection_colors
        self.width = width
        self.height = height
        self.font = font

    def draw_road(self, position, size):
        pygame.draw.rect(self.screen, self.intersection_colors["BLACK"], (position, size))

    def draw_lane(self, start_pos, end_pos):
        pygame.draw.line(self.screen, self.intersection_colors["YELLOW"], start_pos, end_pos, 2)

    def draw_text(self, text, position):
        rendered_text = self.font.render(text, True, self.intersection_colors["WHITE"])
        self.screen.blit(rendered_text, position)

    def draw(self):
        self.screen.fill(self.intersection_colors["GREEN"])

        # Vertical and horizontal roads
        self.draw_road((self.center[0] - self.road_width // 2, 0), (self.road_width, self.height))
        self.draw_road((0, self.center[1] - self.road_width // 2), (self.width, self.road_width))

        # Lanes and labels
        self.draw_lane((0, self.center[1]), (self.center[0] - self.road_width // 2, self.center[1]))
        self.draw_text('West', (self.center[0] // 2, self.center[1] - 10))

        self.draw_lane((self.center[0] + self.road_width // 2, self.center[1]), (self.width, self.center[1]))
        self.draw_text('East', (self.center[0] // 2 + self.center[0], self.center[1] - 10))

        self.draw_lane((self.center[0], 0), (self.center[0], self.center[1] - self.road_width // 2))
        self.draw_text('North', (self.center[0] - 30, self.center[1] // 2))

        self.draw_lane((self.center[0], self.center[1] + self.road_width // 2), (self.center[0], self.height))
        self.draw_text('South', (self.center[0] - 30, self.center[1] // 2 + self.center[1]))
