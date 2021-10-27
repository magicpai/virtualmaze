### Capstone Project for Udacity's Machine Learning Engineer Nanodegree
# Robot Motion Planning
## Plot and Navigate a Virtual Maze
by Paima Marbun


### Description
This project is based on Micromouse competition where a small robot should find autonomously the fastest possible path from predetermined starting node to one of the goals located in the center of an unknown maze. The maze is typically made up of a 16x16 grid of nodes with or without walls on its four edges. The robot can explore and discover the walls in the first run to map out the maze and detect the goals. From the learning of the first run the robot is expected to know the fastest path to one of the goals in the maze center and it attempts to reach it the second run. 

### Project Requirements
* Python 3.8
* Numpy
* Turtle
* Panda

For full detail of the project, please see 'report.pdf'. 

#### Code

* robot.py - This is the core of the robot controller.
* alg_tester.py - Providing various run1 algorithms tests and repetition test as random selection is a part included in the solutions
* tester.py - This script is run to test the robot’s ability to navigate the mazes.
* mazeanim.py - Providing animation of robot movements using turtle module. 
* maze.py - This script is used to construct each maze and interacts with the robot whenever it is moving or checking its sensors.
* showmaze.py - This script creates a visual layout of each maze.

#### Maze Files

* test_maze_01.txt - Test Maze 1. Dimensions: 12*12
* test_maze_02.txt - Test Maze 2. Dimensions: 14*14
* test_maze_03.txt - Test Maze 3. Dimensions: 16*16
* test_maze_04.txt - Test Maze 4. Dimensions: 12*12
* test_maze_05.txt - Test Maze 5. Dimensions: 14*14
* test_maze_06.txt - Test Maze 6. Dimensions: 16*16
* test_maze_07.txt - Test Maze 7. Dimensions: 16*16
* test_maze_08.txt - Test Maze 8. Dimensions: 16*16

#### Supplementary Files
* all_results.json - store dataframe results in json 
* analysis.ipynb - jupyter notebook for statistical analysis
