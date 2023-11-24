import pygame
import random


class Vehicle:
    def __init__(self, screen, radius, width, speed):
        self.screen = screen
        self.radius = radius
        self.width = width
        self.speed = speed
        self.x = None
        self.y = None
        self.direction = None
        self.color = None
        self.moving = True
        self.out_going_direction = None
        self.lane = None
        self.threshold = None
        self.has_crossed_threshold = False
        self.previous_x = None
        self.previous_y = None
        # self.vehicle_gap = 2*self.radius + self.radius//2

    def generate_vehicle(self, vehicle_spawn_coords, vehicle_incoming_direction, vehicle_direction_color,
                         vehicle_count):
        self.direction = random.choice(vehicle_incoming_direction)
        vehicle_count[self.direction] += 1
        self.lane = self.direction
        self.x, self.y = vehicle_spawn_coords[self.direction]
        self.out_going_direction = random.choice(["straight", "left", "right"])
        self.color = vehicle_direction_color[self.out_going_direction]

    def move(self, current_traffic_light, current_light_state, thresholds, vehicle_turning_points, vehicle_list):
        # self.previous_x = self.x
        # self.previous_y = self.y
        # too_close = any(self.is_too_close(other_vehicle) for other_vehicle in vehicle_list if
        #                 other_vehicle.direction == self.direction)
        # self.speed = self.speed * 0.5 if too_close else self.speed
        self.threshold = thresholds[self.direction]
        if self.out_going_direction == "left":
            current_turning_point = vehicle_turning_points["left"][self.direction]
        else:
            current_turning_point = vehicle_turning_points["right"][self.direction]

        # For vehicle coming from the west
        if self.direction == "west":
            if (current_traffic_light == "west" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.x > self.threshold):
                if self.out_going_direction == "straight":
                    self.x += self.speed
                elif self.out_going_direction == "left":
                    if self.x < current_turning_point:
                        self.x += self.speed
                    else:
                        self.y -= self.speed
                else:
                    if self.x < current_turning_point:
                        self.x += self.speed
                    else:
                        self.y += self.speed
            else:
                if self.x < self.threshold:
                    self.x += self.speed

        # For vehicle coming from the east
        elif self.direction == "east":
            if (current_traffic_light == "east" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.x < self.threshold):
                if self.out_going_direction == "straight":
                    self.x -= self.speed
                elif self.out_going_direction == "left":
                    if self.x > current_turning_point:
                        self.x -= self.speed
                    else:
                        self.y += self.speed

                else:
                    if self.x > current_turning_point:
                        self.x -= self.speed
                    else:
                        self.y -= self.speed
            else:
                if self.x > self.threshold:
                    self.x -= self.speed

        # For vehicle coming from the north
        elif self.direction == "north":
            if (current_traffic_light == "north" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.y > self.threshold):
                if self.out_going_direction == "straight":
                    self.y += self.speed
                elif self.out_going_direction == "left":
                    if self.y < current_turning_point:
                        self.y += self.speed
                    else:
                        self.x += self.speed
                else:
                    if self.y < current_turning_point:
                        self.y += self.speed
                    else:
                        self.x -= self.speed
            else:
                if self.y < self.threshold:
                    self.y += self.speed

        # For vehicle coming from the south
        elif self.direction == "south":
            if (current_traffic_light == "south" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.y < self.threshold):
                if self.out_going_direction == "straight":
                    self.y -= self.speed
                elif self.out_going_direction == "left":
                    if self.y > current_turning_point:
                        self.y -= self.speed
                    else:
                        self.x -= self.speed
                else:
                    if self.y > current_turning_point:
                        self.y -= self.speed
                    else:
                        self.x += self.speed
            else:
                if self.y > self.threshold:
                    self.y -= self.speed

        # for other_vehicle in vehicle_list:
        #     if self.is_too_close(other_vehicle):
        #         self.x = self.previous_x
        #         self.y = self.previous_y
        #         break

        return self.x, self.y

    # def is_too_close(self, other_vehicle):
    #     """
    #     Check if the current vehicle is too close to another vehicle.
    #     """
    #     if other_vehicle is self:
    #         return False  # Skip self
    #
    #     if self.direction != other_vehicle.direction:
    #         return False  # Check only vehicles in the same lane
    #
    #     distance = ((self.x - other_vehicle.x) ** 2 + (self.y - other_vehicle.y) ** 2) ** 0.5
    #     return distance < self.vehicle_gap

    def draw(self):
        pygame.draw.circle(self.screen, self.color, [self.x, self.y], self.radius, self.width)

    def kill_vehicle(self, width, height):
        # Check if the vehicle is out of bounds
        out_of_bounds = self.x < 0 or self.x > width or self.y < 0 or self.y > height
        return out_of_bounds

    def crossed_threshold(self):
        if not self.has_crossed_threshold:
            if self.direction == "west" and self.x > self.threshold:
                self.has_crossed_threshold = True
                return True, self.direction

            elif self.direction == "east" and self.x < self.threshold:
                self.has_crossed_threshold = True
                return True, self.direction

            elif self.direction == "north" and self.y > self.threshold:
                self.has_crossed_threshold = True
                return True, self.direction

            elif self.direction == "south" and self.y < self.threshold:
                self.has_crossed_threshold = True
                return True, self.direction

        return False, None
