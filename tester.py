from maze import Maze
from robot import Robot
from enum import IntEnum
import pandas as pd
from mazeanim import MazeAnimation
import sys
import timeit
import json
import numpy as np

# global dictionaries for robot movement and sensing
dir_sensors = {'u': ['l', 'u', 'r'], 'r': ['u', 'r', 'd'],
               'd': ['r', 'd', 'l'], 'l': ['d', 'l', 'u'],
               'up': ['l', 'u', 'r'], 'right': ['u', 'r', 'd'],
               'down': ['r', 'd', 'l'], 'left': ['d', 'l', 'u']}
dir_move = {'u': [0, 1], 'r': [1, 0], 'd': [0, -1], 'l': [-1, 0],
            'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}
dir_reverse = {'u': 'd', 'r': 'l', 'd': 'u', 'l': 'r',
               'up': 'd', 'right': 'l', 'down': 'u', 'left': 'r'}


class DMode(IntEnum):
            RANDOM_FULL = 0
            RANDOM_GOALS = 1
            HEURISTIC_FULL = 2
            HEURISTIC_GOALS = 3

if 0:
    mazefiles = ['test_maze_01.txt', 'test_maze_02.txt','test_maze_03.txt','test_maze_01b.txt', 'test_maze_02b.txt', 'test_maze_03b.txt', 'test_maze_03c.txt']
    algs =[DMode.RANDOM_FULL,DMode.RANDOM_GOALS, DMode.HEURISTIC_FULL, DMode.HEURISTIC_GOALS]
    attempts = 10
else:
    algs =[DMode.RANDOM_GOALS]
    mazefiles = ["test_maze_01.txt"]
    mazeforanim = Maze(mazefiles[0])
    attempts = 1

total_trips = len(mazefiles) * len(algs)* attempts

pdcols = ['Alg','Trip','Maze', 'Run1', 'Run2', 'Score', 'Coverage']


# test and score parameters
max_time = 1000 #1000
train_score_mult = 1/30.

# Create a maze based on input argument on command line.testmaze = Maze( str(sys.argv[1]) )

# Intitialize a robot; robot receives info about maze dimensions.
#testrobot = Robot(testmaze.dim)

#create animation
animation = True
if animation:
    mazeanim = MazeAnimation(mazeforanim,[0,0],"up", 80)
    mazeanim.showmaze()

stats = []
trip = 0
start = timeit.default_timer()

for maze in mazefiles:
    testmaze = Maze(maze)
    tablenodes = np.full((1, testmaze.dim, testmaze.dim), 0, dtype=int)
    #for alg in range(len(DMode)):
    for alg in algs:
        algtrip = 0
        for eval_run in range(attempts):
           # testrobot = Robot(testmaze.dim)
            algtrip += 1
            trip += 1
            tablenodes[0].fill(0)

            testrobot = Robot(testmaze.dim,alg)
            # Record robot performance over two runs.
            runtimes = []
            total_time = 0
            for run in range(2):
                print (f"Starting run {run}.")
                # Set the robot in the start position. Note that robot position
                # parameters are independent of the robot itself.
                robot_pos = {'location': [0, 0], 'heading': 'up'}
            
                run_active = True
                hit_goal = False
                while run_active:
                    # check for end of time
                    total_time += 1
                    if total_time > max_time:
                        run_active = False
                        print ("Allotted time exceeded.")
                        break
                    # provide robot with sensor information, get actions
                    
                    #print("test position:",robot_pos['location'],"heading:",robot_pos['heading'])
                    sensing = [testmaze.dist_to_wall(robot_pos['location'], heading)
                            for heading in dir_sensors[robot_pos['heading']]]
                    
                    tablenodes[0][tuple(robot_pos['location'])] += 1

                    if 0:
                        rotation, movement, freq = testrobot.discover_map(sensing)
                    else:
                        rotation, movement, freq = testrobot.next_move(sensing)
                    #print("Tester rotation,move:",rotation,",",movement)
                    
                    # check for a reset
                    if (rotation, movement) == ('Reset', 'Reset'):
                        if run == 0 and hit_goal:
                            run_active = False
                            runtimes.append(total_time)
                            print ("Ending first run. Starting next run.")
                            break
                        elif run == 0 and not hit_goal:
                            print ("Cannot reset - robot has not hit goal yet.")
                            #continue
                            break
                        else:
                            print ("Cannot reset on runs after the first.")
                            #continue
                            break
                            
                    # perform rotation
                    if rotation == -90:
                        robot_pos['heading'] = dir_sensors[robot_pos['heading']][0]
                    elif rotation == 90:
                        robot_pos['heading'] = dir_sensors[robot_pos['heading']][2]
                    elif rotation == 0:
                        pass
                    else:
                        print ("Invalid rotation value, no rotation performed.")
                        run_active = False
                        break
                    # perform movement
                    if abs(movement) > 3:
                        print ("Movement limited to three squares in a turn.")
                        run_active = False
                        break
                    movement = max(min(int(movement), 3), -3) # fix to range [-3, 3]
                    while movement:
                        if movement > 0:
                            if testmaze.is_permissible(robot_pos['location'], robot_pos['heading']):
                                robot_pos['location'][0] += dir_move[robot_pos['heading']][0]
                                robot_pos['location'][1] += dir_move[robot_pos['heading']][1]
                                #print("robot pos:", robot_pos['location'],"heading:", robot_pos['heading'])
                                movement -= 1
                                
                            else:
                                print ("Movement stopped by wall.")
                                #print("robot pos:", robot_pos['location'],"heading:", robot_pos['heading'])
                                run_active = False
                                movement = 0
                                break
                        else:
                            rev_heading = dir_reverse[robot_pos['heading']]
                            #print("ROBOT POS BEFORE:",robot_pos['location'] )
                            if testmaze.is_permissible(robot_pos['location'], rev_heading):
                                robot_pos['location'][0] += dir_move[rev_heading][0]
                                robot_pos['location'][1] += dir_move[rev_heading][1]
                                #print("robot pos:", robot_pos['location'],"heading:", robot_pos['heading'])
                                movement += 1
                                #print("ROBOT POS AFTER:",robot_pos['location'] )
                            else:
                                print ("Movement stopped by wall.")
                                run_active = False
                                break
                                movement = 0
                    
                    if animation:
                        mazeanim.plot_move(robot_pos['heading'],robot_pos['location'],run, freq)
                    
                    # n_zeros = np.count_nonzero(tablenodes[0] != 0) 
                    # coverage = (n_zeros / (testmaze.dim * testmaze.dim)) * 100
                    # print("coverage:", coverage)
                    goal_bounds = [testmaze.dim/2 - 1, testmaze.dim/2]
                    if robot_pos['location'][0] in goal_bounds and robot_pos['location'][1] in goal_bounds:
                        hit_goal = True
                        if run != 0:
                            runtimes.append(total_time - sum(runtimes))
                            run_active = False
                            print ("Goal found; run {} completed!".format(run))
                            
                    
            # Report score if robot is successful.
            if len(runtimes) == 2:
                    print ("Task complete! Score: {:4.3f}".format(runtimes[1] + train_score_mult*runtimes[0]))
                    n_zeros = np.count_nonzero(tablenodes[0] != 0) 
                    coverage = round((n_zeros / (testmaze.dim * testmaze.dim)) * 100, 2)
                    stats.append([alg, algtrip, maze, runtimes[0], runtimes[1], round(runtimes[1] + train_score_mult*runtimes[0],2), coverage])
                    print("Trip:",trip, " from total:", total_trips)

                    n_zeros = np.count_nonzero(tablenodes[0] == 0) 

stop = timeit.default_timer()
print('Time: ', stop - start)

df = pd.DataFrame(stats, columns=pdcols)
out = df.to_json(orient='index')

with open('results.json', 'w') as f:
    f.write(out)

if animation:  
    mazeanim.window.exitonclick()