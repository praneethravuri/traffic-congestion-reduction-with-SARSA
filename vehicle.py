import pygame
import random
import uuid


class Vehicle:
    def __init__(self, screen, radius, width, speed, processed_vehicles, dti_info):
        # initializing the variables
        self.screen, self.radius, self.width, self.speed = screen, radius, width, speed
        self.x, self.y, self.direction, self.color = None, None, None, None
        self.moving, self.out_going_direction, self.lane, self.threshold = True, None, None, None
        self.has_crossed_threshold, self.id = False, uuid.uuid4()
        self.processed_vehicles = processed_vehicles
        self.start_stop_time = None
        self.dti_info = dti_info
        self.can_move = None
        self.stop_time = None

    def generate_vehicle(self, vehicle_spawn_coords, vehicle_incoming_direction, vehicle_direction_color,
                         vehicle_count):
        # setting the spawn direction of the vehicle
        self.direction = random.choice(vehicle_incoming_direction)
        vehicle_count[self.direction] += 1
        self.lane = self.direction
        # using the vehicle spawn coordinates to spawn the vehicle according to the direction
        self.x, self.y = vehicle_spawn_coords[self.direction]
        # setting the color and outgoing direction of the vehicle
        # determines if the vehicle is going to turn left, right, or go straight
        self.out_going_direction = random.choice(["straight", "left", "right"])
        # depending on its outgoing direction, its color is set
        self.color = vehicle_direction_color[self.out_going_direction]

    def change_speed(self, axis, increment):
        # depending on the outgoing direction and its spawn direction
        # the speed of the vehicle is increase or decreased
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

        # defining a value for a vehicle to move
        self.can_move = True

        # taking the threshold of the vehicles depending on its outgoing direction and lane
        self.threshold = thresholds.get(self.direction)

        # defining the turning points for a vehicle
        # if the vehicle is going straight, there is no turning point
        if self.out_going_direction in ["left", "right"]:
            current_turning_point = vehicle_turning_points[self.out_going_direction].get(self.direction)
        else:
            current_turning_point = None

        # defining the stop and go conditions for a vehicle to move
        # if the traffic light is green, the vehicle is free to move
        # if the traffic light is either red or yellow, the car is free to move upto the threshold of that direction
        go_condition = current_traffic_light == self.direction and current_light_state == "GREEN"

        # limiting_thresholds tell us the point to which the vehicle is allowed to move
        # if the traffic light in that direction is red or yellow
        limiting_thresholds = {
            "west": self.x > self.threshold,
            "east": self.x < self.threshold,
            "south": self.y < self.threshold,
            "north": self.y > self.threshold
        }

        # if the traffic light is red or yellow, and the vehicle has not reached the threshold
        # the vehicle's speed is increased until it reaches the threshold
        keep_moving_condition = current_light_state in ["YELLOW", "RED"] and limiting_thresholds[self.direction]

        # getting the direction whose traffic light is now green
        light_state_for_direction = current_traffic_light_colors.get(self.direction, "GREEN")

        # stopping the vehicle if there is another vehicle in front of it
        # both the vehicles should be in the same lane
        if light_state_for_direction in ["RED", "YELLOW"] and not self.has_crossed_threshold:
            for other_vehicle in vehicle_list:
                if other_vehicle.direction == self.direction and other_vehicle.id != self.id:
                    distance = self.get_position() - other_vehicle.get_position()
                    if self.direction in ["west", "north"] and distance < 0 and abs(distance) < self.radius * 3:
                        self.can_move = False
                        break
                    elif self.direction in ["east", "south"] and distance > 0 and abs(distance) < self.radius * 3:
                        self.can_move = False
                        break

        # if the vehicle has stopped in the lane for which the lane's traffic light is yellow or red
        # its wait time is calculated
        # once the vehicle starts moving, its wait time is not calculated
        # each vehicle in each lane's wait time is calculate and added to the dti_info dictionary
        if not self.can_move:
            if self.stop_time is None:
                self.stop_time = pygame.time.get_ticks()
            if pygame.time.get_ticks() - self.stop_time >= 1000:
                self.dti_info[self.direction].setdefault(self.id, 0)
                self.dti_info[self.direction][self.id] += 1
                self.stop_time = pygame.time.get_ticks()
            return
        else:
            self.stop_time = None

        # keep moving the vehicle if the signal is green
        # keep moving the vehicle if the signal is red or yellow and the vehicle has not crossed the threshold
        # keep moving the vehicle once it crosses the threshold
        if self.direction == "west":
            if go_condition or (self.has_crossed_threshold and not keep_moving_condition):
                self.handle_turn(self.out_going_direction, current_turning_point)
            elif not self.has_crossed_threshold:
                if self.x < self.threshold:
                    self.change_speed('x', True)

        elif self.direction == "east":
            if go_condition or (self.has_crossed_threshold and not keep_moving_condition):
                self.handle_turn(self.out_going_direction, current_turning_point)
            elif not self.has_crossed_threshold:
                if self.x > self.threshold:
                    self.change_speed('x', False)

        elif self.direction == "north":
            if go_condition or (self.has_crossed_threshold and not keep_moving_condition):
                self.handle_turn(self.out_going_direction, current_turning_point)
            elif not self.has_crossed_threshold:
                if self.y < self.threshold:
                    self.change_speed('y', True)

        elif self.direction == "south":
            if go_condition or (self.has_crossed_threshold and not keep_moving_condition):
                self.handle_turn(self.out_going_direction, current_turning_point)
            elif not self.has_crossed_threshold:
                if self.y > self.threshold:
                    self.change_speed('y', False)

        # return the coordinates of the vehicle to draw it on the screen
        return self.x, self.y

    def draw(self):
        pygame.draw.circle(self.screen, self.color, [self.x, self.y], self.radius, self.width)

    # once the vehicle is off the screen
    # it is removed from the vehicle thread list
    def kill_vehicle(self, width, height):
        # Check if the vehicle is out of bounds
        out_of_bounds = self.x < 0 or self.x > width or self.y < 0 or self.y > height
        return out_of_bounds

    # this function is used to check whether the vehicle has crossed the threshold or not
    # this is useful to count the number of processed vehicles (vehicles that have crossed the threshold
    # when the light is green)
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

            # once the vehicle has crossed the threshold
            # it is removed from the vehicle thread list
            # this removed vehicle's delay time is no longer required to calculate the delay time indicator
            # hence its wait time is removed from the dti_info dictionary
            if crossed:
                self.has_crossed_threshold = True
                self.processed_vehicles[self.direction] += 1
                # delete the delay of a vehicle if it has crossed the threshold
                if self.id in self.dti_info[self.direction]:
                    del self.dti_info[self.direction][self.id]
                return True, self.direction

        return False, None
