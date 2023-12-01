import pygame
import random
import uuid


class Vehicle:
    def __init__(self, screen, radius, width, speed, processed_vehicles, dti_info):
        self.screen, self.radius, self.width, self.speed = screen, radius, width, speed
        self.x, self.y, self.direction, self.color = None, None, None, None
        self.moving, self.out_going_direction, self.lane, self.threshold = True, None, None, None
        self.has_crossed_threshold, self.id = False, uuid.uuid4()
        self.processed_vehicles = processed_vehicles
        self.start_stop_time = None
        self.dti_info = dti_info
        self.can_move = None

    def generate_vehicle(self, vehicle_spawn_coords, vehicle_incoming_direction, vehicle_direction_color,
                         vehicle_count):
        self.direction = random.choice(vehicle_incoming_direction)
        vehicle_count[self.direction] += 1
        self.lane = self.direction
        self.x, self.y = vehicle_spawn_coords[self.direction]
        self.out_going_direction = random.choice(["straight", "left", "right"])
        self.color = vehicle_direction_color[self.out_going_direction]

    def change_speed(self, axis, increment):
        if axis == "x":
            self.x += self.speed if increment else -self.speed
        elif axis == "y":
            self.y += self.speed if increment else -self.speed

    def handle_turn(self, turn_direction, current_turning_point):
        # left turn logic and conditions
        if turn_direction == "left":
            if self.direction == "west":
                if self.x < current_turning_point:
                    self.change_speed('x', True)
                else:
                    self.change_speed('y', False)
            elif self.direction == "east":
                if self.x > current_turning_point:
                    self.change_speed('x', False)
                else:
                    self.change_speed('y', True)

            elif self.direction == "north":
                if self.y < current_turning_point:
                    self.change_speed('y', True)
                else:
                    self.change_speed('x', True)

            elif self.direction == "south":
                if self.y > current_turning_point:
                    self.change_speed('y', False)
                else:
                    self.change_speed('x', False)

        # right turn logic and conditions
        elif turn_direction == "right":
            if self.direction == "west":
                if self.x < current_turning_point:
                    self.change_speed('x', True)
                else:
                    self.change_speed('y', True)
            elif self.direction == "east":
                if self.x > current_turning_point:
                    self.change_speed('x', False)
                else:
                    self.change_speed('y', False)
            elif self.direction == "north":
                if self.y < current_turning_point:
                    self.change_speed('y', True)
                else:
                    self.change_speed('x', False)

            elif self.direction == "south":
                if self.y > current_turning_point:
                    self.change_speed('y', False)
                else:
                    self.change_speed('x', True)

        # go straight logic and conditions
        else:
            if self.direction == "west":
                self.change_speed('x', True)
            elif self.direction == "east":
                self.change_speed('x', False)
            elif self.direction == "north":
                self.change_speed('y', True)
            else:
                self.change_speed('y', False)

    def get_position(self):
        if self.direction in ["north", "south"]:
            return self.y
        else:
            return self.x

    def move(self, vehicle_list, current_traffic_light, current_light_state, thresholds, vehicle_turning_points,
             current_traffic_light_colors):

        # taking the threshold of the vehicles depending on its outgoing direction and lane
        self.can_move = True
        self.threshold = thresholds.get(self.direction)
        if self.threshold is None:
            print(f"Threshold not set for direction {self.direction}")
            return

        light_state_for_direction = current_traffic_light_colors.get(self.direction, "GREEN")

        if light_state_for_direction in ["RED", "YELLOW"]:
            for other_vehicle in vehicle_list:
                if other_vehicle.direction == self.direction and other_vehicle.id != self.id:
                    distance = self.get_position() - other_vehicle.get_position()
                    if self.direction in ["west", "north"] and distance < 0 and abs(distance) < self.radius * 3:
                        self.can_move = False
                        break
                    elif self.direction in ["east", "south"] and distance > 0 and abs(distance) < self.radius * 3:
                        self.can_move = False
                        break

        if not self.can_move:
            return

        prev_x, prev_y = self.x, self.y

        # taking the turning points of the vehicles depending on its outgoing direction
        if self.out_going_direction == "left":
            current_turning_point = vehicle_turning_points["left"][self.direction]
        elif self.out_going_direction == "right":
            current_turning_point = vehicle_turning_points["right"][self.direction]
        else:
            current_turning_point = None

        # For vehicle coming from the west
        if self.direction == "west":
            if (current_traffic_light == "west" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.x > self.threshold):
                self.handle_turn(self.out_going_direction, current_turning_point)
            else:
                if self.x < self.threshold:
                    self.change_speed('x', True)

        # For vehicle coming from the east
        elif self.direction == "east":
            if (current_traffic_light == "east" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.x < self.threshold):
                self.handle_turn(self.out_going_direction, current_turning_point)
            else:
                if self.x > self.threshold:
                    self.change_speed('x', False)

        # For vehicle coming from the north
        elif self.direction == "north":
            if (current_traffic_light == "north" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.y > self.threshold):
                self.handle_turn(self.out_going_direction, current_turning_point)
            else:
                if self.y < self.threshold:
                    self.change_speed('y', True)

        # For vehicle coming from the south
        elif self.direction == "south":
            if (current_traffic_light == "south" and current_light_state == 'GREEN') or (
                    current_light_state in ["YELLOW", "RED"] and self.y < self.threshold):
                self.handle_turn(self.out_going_direction, current_turning_point)
            else:
                if self.y > self.threshold:
                    self.change_speed('y', False)

        if (self.x, self.y) == (prev_x, prev_y):
            if self.id not in self.dti_info[self.direction]:
                self.dti_info[self.direction][self.id] = 1  # Initialize if not present
            else:
                self.dti_info[self.direction][self.id] += 1  # Increment if already present

        return self.x, self.y

    def draw(self):
        pygame.draw.circle(self.screen, self.color, [self.x, self.y], self.radius, self.width)

    def kill_vehicle(self, width, height):
        # Check if the vehicle is out of bounds
        out_of_bounds = self.x < 0 or self.x > width or self.y < 0 or self.y > height
        return out_of_bounds

    def crossed_threshold(self):
        if not self.has_crossed_threshold:
            crossed = False
            if self.direction == "west" and self.x > self.threshold:
                crossed = True
            elif self.direction == "east" and self.x < self.threshold:
                crossed = True
            elif self.direction == "north" and self.y > self.threshold:
                crossed = True
            elif self.direction == "south" and self.y < self.threshold:
                crossed = True

            if crossed:
                self.has_crossed_threshold = True
                self.processed_vehicles[self.direction] += 1
                # delete the delay of a vehicle if it has crossed the threshold
                if self.id in self.dti_info[self.direction]:
                    del self.dti_info[self.direction][self.id]
                return True, self.direction

        return False, None