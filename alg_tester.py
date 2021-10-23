from maze import Maze
from robot import Robot
from enum import IntEnum
import pandas as pd
from mazeanim import MazeAnimation
import sys
import timeit
import time
import json
import numpy as np
from pathlib import Path

# global dictionaries for robot movement and sensing
dir_sensors = {'u': ['l', 'u', 'r'], 'r': ['u', 'r', 'd'],
               'd': ['r', 'd', 'l'], 'l': ['d', 'l', 'u'],
               'up': ['l', 'u', 'r'], 'right': ['u', 'r', 'd'],
               'down': ['r', 'd', 'l'], 'left': ['d', 'l', 'u']}
dir_move = {'u': [0, 1], 'r': [1, 0], 'd': [0, -1], 'l': [-1, 0],
            'up': [0, 1], 'right': [1, 0], 'down': [0, -1], 'left': [-1, 0]}
dir_reverse = {'u': 'd', 'r': 'l', 'd': 'u', 'l': 'r',
               'up': 'd', 'right': 'l', 'down': 'u', 'left': 'r'}

eps_path = "./eps/"
basic_log = False

if __name__ == '__main__':
    '''
    This script tests and animate a robot based on the code in robot.py on a 
    maze given as an argument when running the script. Particular Algorithm for
    run1 can also be selected.
    '''

    if 0:
        mazefiles = ['test_maze_01.txt', 'test_maze_02.txt','test_maze_03.txt','test_maze_04.txt', 'test_maze_05.txt', 'test_maze_06.txt', 'test_maze_07.txt','test_maze_08.txt']
        algs = ["SHORT_100", "SHORT_90", "SHORT_80", "SHORT_70","SHORT_GOALS", "HEURISTIC_100", "HEURISTIC_90", "HEURISTIC_80", "HEURISTIC_70", "HEURISTIC_GOALS"]
        attempts = 100
    else:
        #algs = ["SHORT_100", "SHORT_GOALS", "HEURISTC_100","HEURISTIC_GOALS"]
        algs = ["SHORT_GOALS"]
        #mazefiles = ["test_maze_01.txt", "test_maze_02.txt", "test_maze_03.txt"]
        #attempts = 20
        #algs = ["SHORT_GOALS"]
        mazefiles = ["test_maze_01.txt"]
        attempts = 1

    pdcols = ['Alg','Trip','Maze', 'Run1', 'Run2', 'Score', 'Coverage']

    #create animation
    animation = True

    stats = []
    total_trips = len(mazefiles) * len(algs)* attempts
    trip = 0
    start = timeit.default_timer()

    # test and score parameters
    max_time = 1000 #1000
    train_score_mult = 1/30.

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

                if animation:
                    mazeanim = MazeAnimation(testmaze,[0,0],"up", 50)
                    mazeanim.showmaze()
                # Record robot performance over two runs.
                runtimes = []
                total_time = 0
                for run in range(2):
                    print (f"Starting run {run}.")
                    # Set the robot in the start position. Note that robot position
                    # parameters are independent of the robot itself.
                    robot_pos = {'location': [0, 0], 'heading': 'up'}
                    tablenodes[0][tuple(robot_pos['location'])] = 1
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
                        
                        if basic_log:
                            print("test position:",robot_pos['location'],"heading:",robot_pos['heading'])
                        sensing = [testmaze.dist_to_wall(robot_pos['location'], heading)
                                for heading in dir_sensors[robot_pos['heading']]]
                        
                        #tablenodes[0][tuple(robot_pos['location'])] += 1

                        rotation, movement = testrobot.next_move(sensing)
                        
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
                                    
                                    if basic_log:
                                        print("robot new pos:", robot_pos['location'],"heading:", robot_pos['heading'])
                                    movement -= 1
                                    
                                else:
                                    print ("Movement stopped by wall.")
                                    if basic_log:
                                        print("robot new pos:", robot_pos['location'],"heading:", robot_pos['heading'])
                                    run_active = False
                                    movement = 0
                                    break
                            else:
                                rev_heading = dir_reverse[robot_pos['heading']]
                                if testmaze.is_permissible(robot_pos['location'], rev_heading):
                                    robot_pos['location'][0] += dir_move[rev_heading][0]
                                    robot_pos['location'][1] += dir_move[rev_heading][1]
                                    
                                    if basic_log:
                                        print("robot new pos:", robot_pos['location'],"heading:", robot_pos['heading'])
                                    movement += 1

                                else:
                                    print ("Movement stopped by wall.")
                                    run_active = False
                                    break
                                    movement = 0
                        
                        tablenodes[0][tuple(robot_pos['location'])] += 1

                        if animation:
                            mazeanim.plot_move(robot_pos['heading'],robot_pos['location'],run, tablenodes[0][tuple(robot_pos['location'])])

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
                        coverage = round((n_zeros / (testmaze.dim * testmaze.dim)) * 100, 1)
                        score = round(runtimes[1] + train_score_mult*runtimes[0],2)
                        stats.append([alg, algtrip, maze, runtimes[0], runtimes[1], score, coverage])
                        print("Trip:",trip, " from total:", total_trips)
                        n_zeros = np.count_nonzero(tablenodes[0] == 0)
                        if animation:
                            summary_text = {"maze":maze, "alg": alg, "run1":runtimes[0], "coverage":coverage, "run2":runtimes[1], "score":score}
                            mazeanim.plot_summary(summary_text)
                            mazeanim.window.getcanvas().postscript(file= eps_path + "trip" + str(trip) + ".eps")
                            #mazeanim.window.clear()
                            #mazeanim.window.reset()
                        

                # clean up before to next attempt
                del testrobot
        # clean up before to next maze
        del testmaze
        del tablenodes

    stop = timeit.default_timer()
    print('Time: ', stop - start)

    df = pd.DataFrame(stats, columns=pdcols)
    out = df.to_json(orient='index')

    with open('results.json', 'w') as f:
        f.write(out)

    if animation:
        mazeanim.window.exitonclick()