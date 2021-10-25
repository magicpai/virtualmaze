import turtle
import itertools

class MazeAnimation():
    '''
    This class will plot graph and summary for robot's movement animation.
    '''
    
    def __init__(self, maze, start,heading, sq_size):
        '''
        Object Intantiation requires Maze information, robot start position plus
        heading as well the size of node to be displayed on the screen. 
        '''
        
        # translate robot heading to turtle heading
        self.turtle_move = {'up':90 , 'right': 0, 'down': -90, 'left': 180,
                           'u': 90, 'r': 0, 'd': -90, 'l': 180}

        # store maze walls and goal area in the center
        self.maze = maze
        self.maze_center = [(self.maze.dim/2)-1, self.maze.dim/2]
        self.goals = [[product[0], product[1]] for product in itertools.product(self.maze_center, repeat=2)]
        
        # store robot position and heading
        self.start = start
        self.heading = heading
        
        # Initialize node size and left corner coordinate of the maze
        self.sq_size = sq_size
        self.origin = self.maze.dim * self.sq_size / -2
        
        # Intialize the window and drawing turtle.
        self.window = turtle.Screen()
        self.wally = turtle.Turtle()
        self.wally.shape("turtle")
        self.wally.color('black')
        self.wally.speed(0)
        self.wally.pensize(3)
        self.wally.hideturtle()
        self.wally.penup()

        #Turtle for textwriting
        self.writer = turtle.Turtle()
        self.writer.speed(0)
        self.writer.pensize(1)
        self.writer.hideturtle()
        self.writer.penup()

        # Set few font style and colors
        self.run1_font= ('Arial', 10)
        self.run2_font= ('Arial', 12)
        self.run1_color = 'blue'
        self.run2_color = 'green'
        self.text_circle = 8

        #Turtle for finisher
        self.finisher = turtle.Turtle()
        self.finisher.shape("turtle")
        self.finisher.speed(0)
        self.finisher.pensize(3)
        self.finisher.hideturtle()
        self.finisher.penup()
        self.finisher.color(self.run2_color)


        # Set few font style and colors
        self.run1_font= ('Arial', 10)
        self.run2_font= ('Arial', 14)
        self.run1_color = 'blue'
        self.run2_color = 'green'
        self.summary_font = ('Arial', 16)
        self.summary_color = ("brown")
        self.text_circle = 8
        
        # to record timesteps for run2
        self.timestep = 0

    def showmaze(self, heuristic = None):
        '''
        Plot walls, x/y axis, start and goal marker on the screen.
        Heuristic value plotting is optional.
        '''
        # iterate through squares one by one to decide where to draw walls
        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                # Plot heuristic value
                if heuristic is not None:
                    h_value = heuristic[x][y]
                    self.wally.color('blue')
                    self.wally.penup()
                    self.wally.goto(self.origin + self.sq_size/2 + self.sq_size * x, self.origin + self.sq_size/2 + self.sq_size * y)
                    self.wally.down()
                    self.wally.write(h_value,font=('Arial', 20), align='left')
                    self.wally.penup()
                    self.wally.color('black')
                if not self.maze.is_permissible([x,y], 'up'):
                    self.wally.goto(self.origin + self.sq_size * x, self.origin + self.sq_size * (y+1))
                    self.wally.setheading(0)
                    self.wally.pendown()
                    self.wally.forward(self.sq_size)
                    self.wally.penup()
                if not self.maze.is_permissible([x,y], 'right'):
                    self.wally.goto(self.origin + self.sq_size * (x+1), self.origin + self.sq_size * y)
                    self.wally.setheading(90)
                    self.wally.pendown()
                    self.wally.forward(self.sq_size)
                    self.wally.penup()
                # onself.ly check bottom wall if on lowest row
                if y == 0 and not self.maze.is_permissible([x,y], 'down'):
                    self.wally.goto(self.origin + self.sq_size * x, self.origin)
                    self.wally.setheading(0)
                    self.wally.pendown()
                    self.wally.forward(self.sq_size)
                    self.wally.penup()
                    # plot x-horizontal coordinate
                    self.wally.goto(self.origin + self.sq_size * x +self.sq_size / 3, self.origin - 40)
                    self.wally.down()
                    self.wally.write(x,font=('Arial', 20), align='left')
                    self.wally.penup()
                # only check left wall if on leftmost column
                if x == 0 and not self.maze.is_permissible([x,y], 'left'):
                    self.wally.goto(self.origin, self.origin + self.sq_size * y)
                    self.wally.setheading(90)
                    self.wally.pendown()
                    self.wally.forward(self.sq_size)
                    self.wally.penup()
                    # plot y-vertical coordinate
                    self.wally.goto(self.origin-40, self.origin + self.sq_size * y + self.sq_size / 3 )
                    self.wally.down()
                    self.wally.write(y,font=('Arial', 20), align='left')
                    self.wally.penup()

        # mark the start
        self.wally.color('black', 'blue')
        self.wally.hideturtle()
    
        # mark the goals
        self.wally.color('black', 'red')
        self.wally.hideturtle()
        for goal in self.goals:
            self.wally.penup()
            self.wally.goto((self.origin + self.sq_size*5/8) + (self.sq_size * goal[0]), (self.origin + self.sq_size*2/4) + (self.sq_size * goal[1]))
            self.wally.down()
            self.wally.begin_fill()
            self.wally.circle(5)
            self.wally.end_fill()
        
        # Display number of visit in the robot's start position
        self.writer.goto(self.origin + self.start[0]*self.sq_size + self.sq_size/4, self.origin + self.start[1]*self.sq_size +self.sq_size/8)
        self.writer.down()
        self.writer.write(1,font=self.run1_font, align='left')
        self.writer.penup()
        
        # Display turtle in the starting position
        self.wally.penup()
        self.wally.setpos(self.origin + self.start[0] * self.sq_size + self.sq_size/2, self.origin + self.start[1] * self.sq_size + self.sq_size/2)
        self.wally.setheading(self.turtle_move[self.heading])
        self.wally.color("blue")
        self.wally.showturtle()

        # hide and place finisher turtle in the start position
        self.finisher.setpos(self.origin + self.start[0] * self.sq_size + self.sq_size/2 + 4, self.origin + self.start[1] * self.sq_size + self.sq_size/2)
        self.finisher.setheading(self.turtle_move[self.heading])

        return 
        
        
    def plot_move(self,heading,move_to,run,freq):
        '''
        This function plots robot movement from node to node in run1 and run
        together with number of robot visit in the center of each node.
        '''
        
        self.heading = heading

        # plot for each run
        if run == 0:
            self.wally.color(self.run1_color)
            self.wally.pensize(1)
            self.wally.pendown()
            self.wally.setheading(self.turtle_move[heading])
            # goto center of given node
            pos_in_screen = (self.origin + self.sq_size/2 + self.sq_size * move_to[0], self.origin + self.sq_size/2 + self.sq_size * move_to[1])
            self.wally.goto(pos_in_screen)
            
            # goto slightly center of each node and plot number of visits
            self.writer.goto(self.origin + move_to[0]*self.sq_size + self.sq_size/4, self.origin + move_to[1]*self.sq_size + self.sq_size/8)
            self.writer.color(self.run1_color,'white')
            self.writer.begin_fill()
            self.writer.circle(self.text_circle)
            self.writer.end_fill()
            self.writer.write(freq,font=self.run1_font, align='left')
            self.writer.penup()

        else:

            self.wally.hideturtle()
            self.finisher.showturtle()
            self.finisher.pendown()
            self.finisher.setheading(self.turtle_move[heading])
            # goto to center of given node
            pos_in_screen = (self.origin + self.sq_size/2 + 4 + self.sq_size * move_to[0], self.origin + self.sq_size/2 + self.sq_size * move_to[1])
            self.finisher.goto(pos_in_screen)

            #increment each timestep done by the robot
            self.timestep += 1
            self.writer.color(self.run2_color, 'white')
            self.writer.penup()
            self.writer.goto(self.origin + self.sq_size/2 + 8 + self.sq_size * move_to[0], self.origin + self.sq_size/2 + self.sq_size * move_to[1])
            self.writer.write(self.timestep,font=self.run2_font, align='left')
            self.writer.penup()

        return


    def plot_summary (self, summary_text):
        '''
        Plot given summary text file on top of maze walls.
        '''
        self.writer.color(self.summary_color)

        # plot maze file
        self.writer.penup()
        self.writer.goto(self.origin, self.origin + self.maze.dim * self.sq_size + self.sq_size / 2 )
        self.writer.down()
        self.writer.write("maze: "+ summary_text["maze"],font=self.summary_font, align='left')
        self.writer.penup()
        # plot algorithm
        self.writer.goto(self.origin, self.origin + self.maze.dim * self.sq_size + 5)
        self.writer.down()
        self.writer.write("run1 algorithm: "+ summary_text["alg"],font=self.summary_font, align='left')
        self.writer.penup()
        # plot run1 timesteps
        self.writer.goto(self.origin + (self.maze.dim * self.sq_size)/2, self.origin + self.maze.dim * self.sq_size + self.sq_size / 2)
        self.writer.down()
        self.writer.write("run1 ts: "+ str(summary_text["run1"]),font=self.summary_font, align='left')
        self.writer.penup()
        # plot run2 timesteps
        self.writer.goto(self.origin + (self.maze.dim * self.sq_size)/2, self.origin + self.maze.dim * self.sq_size + 5)
        self.writer.down()
        self.writer.write("run2 ts: "+ str(summary_text["run2"]),font=self.summary_font, align='left')
        self.writer.penup()
        # plot coverage
        self.writer.goto(self.origin + (self.maze.dim * self.sq_size) - 125, self.origin + self.maze.dim * self.sq_size + self.sq_size / 2)
        self.writer.down()
        self.writer.write("coverage: "+ str(summary_text["coverage"])+"%",font=self.summary_font, align='left')
        self.writer.penup()
        # plot score
        self.writer.goto(self.origin + (self.maze.dim * self.sq_size) - 125, self.origin + self.maze.dim * self.sq_size + 5)
        self.writer.down()
        self.writer.write("score: "+ str(summary_text["score"]),font=self.summary_font, align='left')
        self.writer.penup()
        
        return
