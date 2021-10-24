import random
import itertools
import copy
import numpy as np
from enum import IntEnum


class Robot(object):
    def __init__(self, maze_dim, alg='', logger=None):
        """
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        """

        self.dir_sensors = {
            "u": ["l", "u", "r"],
            "r": ["u", "r", "d"],
            "d": ["r", "d", "l"],
            "l": ["d", "l", "u"],
            "up": ["l", "u", "r"],
            "right": ["u", "r", "d"],
            "down": ["r", "d", "l"],
            "left": ["d", "l", "u"],
        }
        self.dir_move = {"u": [0, 1], "r": [1, 0], "d": [0, -1], "l": [-1, 0]}
        self.dir_reverse = {
            "u": "d",
            "r": "l",
            "d": "u",
            "l": "r",
            "up": "d",
            "right": "l",
            "down": "u",
            "left": "r",
        }
        self.turtle_move = {"u": 90, "r": 0, "d": -90, "l": 180}
        self.rotation = [-90, 0, 90]

        self.dir_int = {
            "u": 1,
            "r": 2,
            "d": 4,
            "l": 8,
            "up": 1,
            "right": 2,
            "down": 4,
            "left": 8,
        }

        self.nstatus = {"closed": 0, "open": 1, "done": 2}

        self.maze_dim = maze_dim

        self.maze_center = [(self.maze_dim / 2) - 1, self.maze_dim / 2]

        self.start = [0, 0]
        self.goals = [
            [product[0], product[1]]
            for product in itertools.product(self.maze_center, repeat=2)
        ]
        self.start_heading = "u"
        self.max_move = 3
        self.pos = {"node": self.start, "heading": self.start_heading}

        self.max_move = 3

        class Page(IntEnum):
            walls = 0
            h1 = 1
            g1 = 2
            f1 = 3
            nstatus1 = 4
            visits = 5
            h2 = 6
            g2 = 7
            f2 = 8
            nstatus2 = 9

        self.Page = Page

        self.maps = np.full(
            (len(self.Page), self.maze_dim, self.maze_dim), 0, dtype=int
        )
        self.generate_h_cost(self.goals, self.maps[self.Page.h1])

        #self.algs = ["SHORT_100","SHORT_80" "SHORT_GOALS", "HEURISTC_100", "HEURISTIC_80", "HEURISTIC_GOALS"]

        self.algs = {"SHORT_100": 100, "SHORT_90": 90, "SHORT_80": 80, "SHORT_70": 70, "SHORT_GOALS": 0, "HEURISTIC_100": 100, "HEURISTIC_90": 90, "HEURISTIC_80": 80, "HEURISTIC_70": 70, "HEURISTIC_GOALS": 0}

        if alg in self.algs.keys():
            self.alg = alg
        else:
            self.alg = "SHORT_80"

        self.coverage = 0
    
        self.f_max = 0
        self.goal_found = False
        self.run2 = False

        # set f_cost = h_cost + g_cost for start-node
        self.maps[self.Page.f1][tuple(self.pos["node"])] = (
            self.maps[self.Page.h1][tuple(self.pos["node"])]
            + self.maps[self.Page.g1][tuple(self.pos["node"])]
        )

        self.maps[self.Page.nstatus1][tuple(self.pos["node"])] = self.nstatus["done"]

        self.timesteps = []
        self.timesteps_counter = 0

        # set g_cost 0 for start
        self.maps[self.Page.g1][tuple(self.pos["node"])] = 0

        # set f_cost = h_cost + g_cost for start-node
        self.maps[self.Page.f1][tuple(self.pos['node'])] = (
            self.maps[self.Page.h1][tuple(self.pos['node'])] + 
            self.maps[self.Page.g1][tuple(self.pos['node'])]
        )

        self.maps[self.Page.visits][tuple(self.pos['node'])] = 1

        # list of to be checked nodes sorted by lowest f_cost
        self.open_nodes = []
        self.open_nodes.append(self.pos["node"])

        #enable or disable debug logging
        self.debug_logging = False
        self.logger = None
        if self.debug_logging and logger:
            self.logger = logger


    def generate_h_cost(self, goals, heuristic=[]):

        dist = []
        for x in range(self.maze_dim):
            for y in range(self.maze_dim):
                dist = []
                for goal in goals:
                    div, rem = divmod(abs(goal[0] - x), self.max_move)
                    distx = div + 1 if rem != 0 else div
                    div, rem = divmod(abs(goal[1] - y), self.max_move)
                    disty = div + 1 if rem != 0 else div
                    dist.append(distx + disty)
                    heuristic[x][y] = min(dist)

        return

    def next_move(self, sensors):
        """
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        """
        rotation = 0
        movement = 0

        if (self.pos['node'] in self.goals) and (not self.goal_found):
            self.goal_found = True

        if not self.run2:
            self.fill_map_heuristic(sensors)
            if self.is_goal_cov_reached():
                self.run2 = True
                self.pos["node"] = self.start
                self.pos["heading"] = self.start_heading
                self.timesteps_counter = self.find_best_path(self.pos["node"], self.pos["heading"], self.goals)
                return "Reset", "Reset"


        # pick top most node with lowest f_cost from the list
        if self.timesteps_counter == 0:

            timesteps = []
            node_to_go =  None

            for idx, node in enumerate(self.open_nodes):

               # print("node under checked:", node)
                #if( list(node) in self.goals and self.alg in ["SHORT_GOALS", "HEURISTIC_GOALS"]):
                if node in self.goals:
                    node_to_go = node
                 # print("go to goal", node)
                    break

                if self.alg in ["HEURISTIC_100", "HEURISTIC_90", "HEURISTIC_80", "HEURISTIC_70", "HEURISTIC_GOALS"]:
                    timestep = (self.find_best_path(self.pos["node"], 
                                self.pos["heading"], [node])
                                + self.maps[self.Page.h1][tuple(node)]
                                )
                else:
                    timestep = self.find_best_path(
                        self.pos["node"], self.pos["heading"], [node]
                        )
                    
                if not timesteps:
                    timesteps.append({"node":node, "timestep": timestep})
                    continue
                if timestep < timesteps[0]["timestep"]:
                    timesteps.clear()
                    timesteps.append({"node":node, "timestep": timestep})
                if timestep == timesteps[0]["timestep"]:
                    timesteps.append({"node":node, "timestep": timestep})

            if node_to_go is None:
                if timesteps:
                    node_to_go = random.choice(timesteps)["node"]
                else:
                    print("all nodes are explored but goal is not found so robot stays at the current position")
                    return 0,0
            
            self.timesteps_counter = self.find_best_path(self.pos["node"], self.pos["heading"], [node_to_go])

        rotation, movement, heading, move_to = self.timesteps[
            len(self.timesteps) - self.timesteps_counter
            ]
        self.timesteps_counter -= 1

        if self.logger:
            self.logger.debug(f"move from {self.pos['node']} to {move_to}, heading: {heading}, rot: {rotation}, mov: {movement}")
        self.pos["node"] = move_to
        self.pos["heading"] = heading
        self.maps[self.Page.visits][tuple(move_to)] += 1

        return rotation, movement

    def is_goal_cov_reached(self):

        if self.logger:
            self.logger.debug(f"Run1 algorithm: {self.algs[self.alg]}, coverage: {self.coverage}, GOAL FOUND: {self.goal_found}")
        if (self.algs[self.alg] <= self.coverage) and self.goal_found:
            return True
        else:
            return False

            
    
    def fill_map_heuristic(self, sensors):

        ## Populate number of open edges in the maze table as indicated by the sensor.
        ## Initial Maze shows all 0 to begin with all gates closed before start sensing.
        ## Skip distance 0 as it is already set to 0 during initialisation
        ## Fill g and f cost

        self.maps[self.Page.nstatus1][tuple(self.pos["node"])] = self.nstatus["done"]

        node_done = np.count_nonzero(self.maps[self.Page.nstatus1] == self.nstatus["done"]) 
        
        self.coverage = round((node_done / (self.maze_dim * self.maze_dim)) * 100, 1)

        for idx,item in enumerate(self.open_nodes):
            if item == self.pos["node"]:
                self.open_nodes.pop(idx)

        for idx, dist in enumerate(sensors):

            heading = self.dir_sensors[self.pos["heading"]][idx]

            for i in range(dist):  # skipped if sensor gives 0 distance
                current_node = (np.array(self.pos["node"]) + 
                (i * np.array(self.dir_move[heading]))).tolist()

                if (self.maps[self.Page.walls][tuple(current_node)] & self.dir_int[heading]) == 0:
                    self.maps[self.Page.walls][tuple(current_node)] += self.dir_int[heading]

                next_node = (np.array(current_node) + np.array(self.dir_move[heading])).tolist()

                if (self.maps[self.Page.nstatus1][tuple(next_node)]== self.nstatus["closed"]):
                    if (self.maps[self.Page.walls][tuple(next_node)] & self.dir_int[self.dir_reverse[heading]]) == 0:
                        self.maps[self.Page.walls][tuple(next_node)] += self.dir_int[self.dir_reverse[heading]]

                    # calculate g-cost for each permissible node
                    self.maps[self.Page.g1][tuple(next_node)] = (
                        self.maps[self.Page.g1][tuple(current_node)] + 1
                    )

                    # calculate f-cost accordingly
                    self.maps[self.Page.f1][tuple(next_node)] = (
                        self.maps[self.Page.h1][tuple(next_node)]
                        + self.maps[self.Page.g1][tuple(next_node)]
                    )

                    self.open_nodes.append(next_node)

                    self.maps[self.Page.nstatus1][tuple(next_node)] = self.nstatus["open"]

                else:  # "only update the maze"
                    if ( self.maps[self.Page.walls][tuple(next_node)] & 
                        self.dir_int[self.dir_reverse[heading]]) == 0:
                        self.maps[self.Page.walls][tuple(next_node)] += self.dir_int[self.dir_reverse[heading]]
        
        return

    def find_best_path(self, start, heading, goals):
        
        open_nodes = []
        goal_found = False
        single_goal_node =[]

        parents = np.ndarray(shape=(self.maze_dim, self.maze_dim), dtype=object)

        curr_node = start
        curr_heading = heading

        self.reset_pathfinder_maps()
        self.generate_h_cost(goals, self.maps[self.Page.h2])

        # set g_cost 0 for start node
        self.maps[self.Page.g2][tuple(curr_node)] = 0

        # calculate f_cost = g_cost + h_cost for start node
        self.maps[self.Page.f2][tuple(curr_node)] = self.maps[self.Page.g2][tuple(curr_node)] + self.maps[self.Page.h2][tuple(curr_node)]
        # add start node to open list
        open_nodes.append(curr_node)
        self.maps[self.Page.nstatus2][tuple(curr_node)] = self.nstatus["open"]

        if self.logger:
            self.logger.debug(f"Find best path from {start} to {goals}")

        while not goal_found:
            for heading in self.dir_move.keys():
                distance = self.dist_to_wall(curr_node, heading)
            # cap distance until self.max_move
                if distance > self.max_move:
                    distance = self.max_move
                
                for i in range(1, distance + 1):
                    next_node = (np.array(curr_node) + (i * np.array(self.dir_move[heading]))).tolist()
                    
                    # skip neighbour node if already evaluated(done)
                    if self.maps[self.Page.nstatus2][tuple(next_node)] == self.nstatus["done"]:
                        break
                    
                    # update g_cost if new calculated value smaller than stored or no value stored before
                    if (self.maps[self.Page.g2][tuple(next_node)] > (self.maps[self.Page.g2][tuple(curr_node)] + 1 + i )) or (self.maps[self.Page.nstatus2][tuple(next_node)] == self.nstatus["closed"]):
                        
                        self.maps[self.Page.g2][tuple(next_node)] = self.maps[self.Page.g2][tuple(curr_node)] + 1 + i
                        # calculate f_cost = g_cost + h_cost for start node
                        self.maps[self.Page.f2][tuple(next_node)] = self.maps[self.Page.g2][tuple(next_node)] + self.maps[self.Page.h2][tuple(next_node)]
                        # add parent node of the current node in the table
                        parents[tuple(next_node)] = curr_node
                        # add  node to open list
                    if self.maps[self.Page.nstatus2][tuple(next_node)] == self.nstatus["closed"]:
                        open_nodes.append(next_node)
                        self.maps[self.Page.nstatus2][tuple(next_node)] = self.nstatus["open"]
                    # check 
                    if list(next_node) in goals:
                        goal_found = True
                        single_goal_node = next_node
                        break

            # out of for loop
            if goal_found:
                continue

            # mark node already evaluates as done and removed from open_nodes list
            self.maps[self.Page.nstatus2][tuple(curr_node)] = self.nstatus["done"]
            for idx,node in enumerate(open_nodes):
                if node == curr_node:
                    open_nodes.pop(idx)

            min_f_nodes = []
            for node in open_nodes:
                f_cost = self.maps[self.Page.f2][tuple(node)]
                h_cost = self.maps[self.Page.h2][tuple(node)]
                if not min_f_nodes:
                    min_f_nodes.append({"node":node, "f_cost": f_cost, "h_cost": h_cost})
                else:
                    if f_cost < min_f_nodes[0]["f_cost"]:
                        min_f_nodes.clear()
                        min_f_nodes.append({"node":node, "f_cost": f_cost, "h_cost": h_cost})
                    elif f_cost == min_f_nodes[0]["f_cost"]:
                        if h_cost < min_f_nodes[0]["h_cost"]:
                            min_f_nodes.clear()
                            min_f_nodes.append({"node":node, "f_cost": f_cost, "h_cost": h_cost})
                        elif h_cost == min_f_nodes[0]["h_cost"]:
                            min_f_nodes.append({"node":node, "f_cost": f_cost, "h_cost": h_cost})
            
            curr_node = random.choice(min_f_nodes)["node"]

        # out of while loops , now find best path
        path = []
        parent_node = single_goal_node
        path.append(parent_node)
        timestep = 0

        while True:
            parent_node = parents[tuple(parent_node)]
            path.insert(0,parent_node)
            if parent_node == start:
                break
            timestep += 1
        
        for idx,node in enumerate(path[:-1]):
            next_node = path[idx+1]
            direction, movement = self.get_head_mov(next_node,node)
            try:
                rotation = self.rotation[self.dir_sensors[curr_heading].index(direction)]
                curr_heading = direction
            except:
                rotation = 0  # indicator for backward movement
                movement = - movement
                curr_heading = self.dir_reverse[direction]
            
            #curr_heading = direction self.dir_reverse
            #self.timesteps.append({"rotation": rotation, "movement": movement})
            self.timesteps.append((rotation, movement,curr_heading, next_node))
            
        #print("length of timesteps:", len(self.timesteps), " timesteps:", self.timesteps)

        return len(self.timesteps)


    def dist_to_wall(self, node, heading):
        """
        Returns a number designating the number of open cells to the nearest
        wall in the indicated direction. Cell is input as a list. Directions
        may be input as a single letter 'u', 'r', 'd', 'l', or complete words
        'up', 'right', 'down', 'left'.
        """

        sensing = True
        distance = 0
        curr_node = node.copy() # make copy to preserve original
        while sensing:
            # check if  permissible 
            if self.maps[self.Page.walls][tuple(curr_node)] & self.dir_int[heading] != 0:
                distance += 1
                curr_node[0] += self.dir_move[heading][0]
                curr_node[1] += self.dir_move[heading][1]
            else:
                sensing = False

        return distance

    def get_head_mov(self, target, start):

        dist_vec = (np.array(target) - np.array(start)).tolist()
        if dist_vec[0] == 0 and dist_vec[1] > 0:
            heading = "u"
            movement = dist_vec[1]
        elif dist_vec[0] == 0 and dist_vec[1] < 0:
            heading = "d"
            movement = dist_vec[1]
        elif dist_vec[0] > 0 and dist_vec[1] == 0:
            heading = "r"
            movement = dist_vec[0]
        elif dist_vec[0] < 0 and dist_vec[1] == 0:
            movement = dist_vec[0]
            heading = "l"
        else:
            print("not possible to move straight")
            heading = "unknown"
            movement = 0
        
        return heading, abs(movement)
        

    def reset_pathfinder_maps(self):

        self.maps[self.Page.h2].fill(0)
        self.maps[self.Page.g2].fill(0)
        self.maps[self.Page.f2].fill(0)
        self.maps[self.Page.nstatus2].fill(False)

        self.timesteps = []
        self.timesteps_counter = 0

        return
