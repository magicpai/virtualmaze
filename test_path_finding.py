from maze import Maze
from robot import Robot
from enum import IntEnum
import pandas as pd
from mazeanim import MazeAnimation
import sys
import timeit
import json
import numpy as np
import itertools


testmaze = Maze('test_maze_08.txt')
testrobot = Robot(testmaze.dim)

mazeanim = MazeAnimation(testmaze,[0,0],"up", 60)
mazeanim.showmaze()

mazeanim.window.exitonclick()

#print("walls from Maze", testmaze.walls)

#testrobot.maps[testrobot.Page.walls]= testmaze.walls

#print("walls from robot", testrobot.maps[testrobot.Page.walls])


#maze_center = [(testmaze.dim/ 2) - 1, testmaze.dim / 2]

#goals = [[product[0], product[1]] for product in itertools.product(maze_center, repeat=2)]

#result = testrobot.path_finding([0,0], "u", goals )

#print("results:", result)

