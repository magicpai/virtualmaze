import random
import itertools
import copy
import numpy as np
from enum import IntEnum
from operator import itemgetter


class Robot(object):
    def __init__(self, maze_dim, alg = 0):
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

        # self.dmode = {"RANDOM_FULL": 0, "RANDOM_GOALS": 1, "HEURISTIC_FULL": 2, "HEURISTIC_GOALS": 3}

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

        class DMode(IntEnum):
            RANDOM_FULL = 0
            RANDOM_GOALS = 1
            HEURISTIC_FULL = 2
            HEURISTIC_GOALS = 3

        self.dmode = DMode(alg)

        #print(self.dmode)
    

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

        if not self.run2:
            self.fill_map_heuristic(sensors)
            if (0 not in self.maps[self.Page.visits]) or (list(self.pos['node']) in self.goals and self.dmode in [self.dmode.RANDOM_GOALS, self.dmode.HEURISTIC_GOALS]):

                    self.run2 = True
                    self.pos["node"] = self.start
                    self.pos["heading"] = self.start_heading
                    self.timesteps_counter = self.path_start_to_goal(self.pos["node"], self.pos["heading"], self.goals)
                    return "Reset", "Reset", 0

        # print("nodes_to_check:", self.nodes_to_check)

        # pick top most node with lowest f_cost from the list
        if self.timesteps_counter == 0:

            timesteps = []

            for idx, node in enumerate(self.open_nodes):

                if( list(node) in self.goals and self.dmode in [self.dmode.RANDOM_GOALS, self.dmode.HEURISTIC_GOALS]):
                  node_to_go = node
                  break

                if self.dmode in [ self.dmode.HEURISTIC_FULL,
                                self.dmode.HEURISTIC_GOALS
                                ]:
                    timestep = (self.path_start_to_goal(self.pos["node"], 
                                self.pos["heading"], [node])
                                + self.maps[self.Page.h1][tuple(node)]
                                )
                    if not timesteps:
                        timesteps.append({"node":node, "timestep": timestep})
                    if timestep < timesteps[0]["timestep"]:
                        timesteps.clear()
                        timesteps.append({"node":node, "timestep": timestep})
                    if timestep == timesteps[0]["timestep"]:
                        timesteps.append({"node":node, "timestep": timestep})


                else:
                    timestep = self.path_start_to_goal(
                        self.pos["node"], self.pos["heading"], [node]
                        )
                    if not timesteps:
                        timesteps.append({"node":node, "timestep": timestep})
                    if timestep < timesteps[0]["timestep"]:
                        timesteps.clear()
                        timesteps.append({"node":node, "timestep": timestep})
                    if timestep == timesteps[0]["timestep"]:
                        timesteps.append({"node":node, "timestep": timestep})

            if timesteps:
                node_to_go = random.choice(timesteps)["node"]
            # print("node_to_go:", node_to_go)

            self.timesteps_counter = self.path_start_to_goal(
                self.pos["node"], self.pos["heading"], [node_to_go]
            )

        rotation, movement, heading, move_to = self.timesteps[len(self.timesteps) - 
                                                self.timesteps_counter]
        self.timesteps_counter -= 1

        print("moves:", self.pos["node"], " to ", move_to)
        self.pos["node"] = move_to
        self.pos["heading"] = heading
        self.maps[self.Page.visits][tuple(move_to)] += 1

        #print("nodes seen:", len (self.nodes_to_check), "nodes visited:", np.count_nonzero(self.maps[self.Page.visits]))

        # for item in self.nodes_to_check:print(item)

        return rotation, movement, self.maps[self.Page.visits][tuple(move_to)]

    def fill_map_heuristic(self, sensors):

        ## Populate number of open edges in the maze table as indicated by the sensor.
        ## Initial Maze shows all 0 to begin with all gates closed before start sensing.
        ## Skip distance 0 as it is already set to 0 during initialisation
        ## Fill g and f cost

        self.maps[self.Page.nstatus1][tuple(self.pos["node"])] = self.nstatus["done"]

        for idx,item in enumerate(self.open_nodes):
            if item == self.pos["node"]:
                self.open_nodes.pop(idx)

        for idx, dist in enumerate(sensors):

            heading = self.dir_sensors[self.pos["heading"]][idx]

            for i in range(dist):  # skipped if sensor gives 0 distance
                current_node = list(np.array(self.pos["node"]) + 
                (i * np.array(self.dir_move[heading])))

                if (self.maps[self.Page.walls][tuple(current_node)] & self.dir_int[heading]) == 0:
                    self.maps[self.Page.walls][tuple(current_node)] += self.dir_int[heading]

                next_node = list(np.array(current_node) + np.array(self.dir_move[heading]))

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
                    #print("next_node:", next_node)

                    self.maps[self.Page.nstatus1][tuple(next_node)] = self.nstatus["open"]

                else:  # "only update the maze"
                    if ( self.maps[self.Page.walls][tuple(next_node)] & 
                        self.dir_int[self.dir_reverse[heading]]) == 0:
                        self.maps[self.Page.walls][tuple(next_node)] += self.dir_int[self.dir_reverse[heading]]
        
        return

    def path_start_to_goal(self, start, direction, goals):

        # print("--------------------------------------------------")
        # print("path from ",start, "to", goals, "heading:", direction)
        # print("--------------------------------------------------")
        # self.run2_moves_idx = 0
        # self.run2 = FALSE
        self.reset_heuristic()

        #print("walls:", self.maps[self.Page.walls])
        # print("start:", start, "goals:", goals)

        routes = []
        node = start
        all_routes_checked = False

        class Nodetype(IntEnum):
            CLOSED = 0
            OPEN = 1
            GOAL = 2

        self.generate_h_cost(goals, self.maps[self.Page.h2])
        
        g_cost = 0
        f_lowest = self.maps[self.Page.h2][tuple(node)] + g_cost
        self.maps[self.Page.f2][tuple(node)] = f_lowest
        self.maps[self.Page.nstatus2][tuple(node)] = self.nstatus["done"]

        routes.append(
            {
                "path": [start],
                "end_heading": direction,
                "rotation": 0,
                "movement": 0,
                "g_cost": g_cost,
                "f_cost": f_lowest,
                "moves": [],
                "nodetype": Nodetype.OPEN,
            }
        )
        routes_idx = 0
        hit_goal = False

        while not all_routes_checked:

            fork = 0
            copy_route = copy.deepcopy(routes[routes_idx])

            # create possible routes with forks
            for heading in self.dir_move.keys():
                # skip node not permissible given the heading
                if self.maps[self.Page.walls][tuple(node)] & self.dir_int[heading] == 0:
                    continue

                next_node = list(np.array(node) + np.array(self.dir_move[heading]))

                # skip node already evaluated before
                if (
                    self.maps[self.Page.nstatus2][tuple(next_node)]
                    == self.nstatus["done"]
                ):
                    continue

                fork += 1

                if fork > 1:
                    routes.append(copy.deepcopy(copy_route))
                    routes_idx = -1

                routes[routes_idx]["path"].append(next_node)
                prev_rotation = routes[routes_idx]["rotation"]

                try:
                    rotation = self.rotation[
                        self.dir_sensors[routes[routes_idx]["end_heading"]].index(
                            heading
                        )
                    ]
                    reversed_rotation = self.rotation[
                        self.dir_sensors[
                            self.dir_reverse[routes[routes_idx]["end_heading"]]
                        ].index(heading)
                    ]
                except:
                    rotation = 180  # indicator for backward movement
                    reversed_rotation = None

                if routes[routes_idx]["end_heading"] == heading:
                    routes[routes_idx]["movement"] += 1
                    if routes[routes_idx]["movement"] > self.max_move:
                        if prev_rotation == 180:
                            routes[routes_idx]["moves"].append(
                                (
                                    0,
                                    -self.max_move,
                                    self.dir_reverse[routes[routes_idx]["end_heading"]],
                                    node,
                                )
                            )
                        else:
                            routes[routes_idx]["moves"].append(
                                (
                                    prev_rotation,
                                    self.max_move,
                                    routes[routes_idx]["end_heading"],
                                    node,
                                )
                            )
                            routes[routes_idx]["rotation"] = 0
                        routes[routes_idx]["movement"] = 1
                        routes[routes_idx]["g_cost"] += 1
                else:
                    if routes[routes_idx]["movement"] == 0:
                        routes[routes_idx]["rotation"] = rotation
                    else:
                        if prev_rotation == 180:
                            routes[routes_idx]["moves"].append(
                                (
                                    0,
                                    -routes[routes_idx]["movement"],
                                    self.dir_reverse[routes[routes_idx]["end_heading"]],
                                    node,
                                )
                            )
                            routes[routes_idx]["rotation"] = reversed_rotation
                        else:
                            routes[routes_idx]["moves"].append(
                                (
                                    prev_rotation,
                                    routes[routes_idx]["movement"],
                                    routes[routes_idx]["end_heading"],
                                    node,
                                )
                            )
                            routes[routes_idx]["rotation"] = rotation

                    routes[routes_idx]["movement"] = 1
                    routes[routes_idx]["g_cost"] += 1

                routes[routes_idx]["end_heading"] = heading
                routes[routes_idx]["f_cost"] = (
                    routes[routes_idx]["g_cost"]
                    + self.maps[self.Page.h2][tuple(next_node)]
                )

                if next_node in goals:
                    routes[routes_idx]["nodetype"] = Nodetype.GOAL
                    if routes[routes_idx]["rotation"] == 180:  # prev_rotation ==
                        routes[routes_idx]["moves"].append(
                            (
                                0,
                                -routes[routes_idx]["movement"],
                                self.dir_reverse[routes[routes_idx]["end_heading"]],
                                next_node,
                            )
                        )
                    else:
                        routes[routes_idx]["moves"].append(
                            (
                                routes[routes_idx]["rotation"],
                                routes[routes_idx]["movement"],
                                routes[routes_idx]["end_heading"],
                                next_node,
                            )
                        )
                    hit_goal = True
                    lowest_f = routes[routes_idx]["f_cost"]
                else:
                    routes[routes_idx]["nodetype"] = Nodetype.OPEN

            # print("Node:", node, " is done")
            self.maps[self.Page.nstatus2][tuple(node)] = self.nstatus["done"]

            if fork == 0:  # remove path with dead end
                del routes[routes_idx]

            if not routes:
                break

            routes_idx = -1
            f_min = 1000  # set to max steps

            # find routewith minimum f_cost
            for idx, item in enumerate(routes):
                # print("route:", idx,"\n",item)
                if item["nodetype"] == Nodetype.GOAL:
                    continue
                if item["f_cost"] < f_min:
                    if hit_goal and (item["f_cost"] > lowest_f):
                        continue
                    f_min = item["f_cost"]
                    routes_idx = idx

            # find last node in the route with minimum f_cost to be discovered further
            if routes_idx != -1:
                node = routes[routes_idx]["path"][-1]
            # print("all_routes NOT checked")
            else:
                all_routes_checked = True
                # print("all_routes_checked")

            copy_route = []

        min_g = None
        routes_idx = -1
        for idx, route in enumerate(routes):
            # print("route:",idx,"\n",route)
            if route["nodetype"] == Nodetype.GOAL:
                if min_g is None:
                    min_g = route["g_cost"]
                    routes_idx = idx
                if min_g > route["g_cost"]:
                    min_g = route["g_cost"]
                    routes_idx = idx

        if routes_idx != -1:
            self.timesteps = copy.deepcopy(routes[routes_idx]["moves"])
            # print("lenght of timesteps:", len(self.timesteps))
            # print ("timesteps: \n", self.timesteps)
            # print("*********************************************************")
            #
        #print("timesteps:", len(self.timesteps))
        return len(self.timesteps)

    def reset_heuristic(self):

        self.maps[self.Page.h2].fill(0)
        self.maps[self.Page.g2].fill(0)
        self.maps[self.Page.f2].fill(0)
        self.maps[self.Page.nstatus2].fill(False)

        return
