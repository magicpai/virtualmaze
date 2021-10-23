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
        
        # Initialize node size and left corner coordinate and drawing screen 
        self.sq_size = sq_size
        self.origin = self.maze.dim * self.sq_size / -2
        self.window = turtle.Screen()
        
        self.wally = turtle.Turtle()
        self.wally.speed(0)
        self.wally.pensize(3)
        self.wally.hideturtle()
        self.wally.penup()
        
        self.mapper = turtle.Turtle()
        self.mapper.shape('turtle')
        self.mapper.speed(0)
        self.mapper.color('blue')
        self.mapper.pensize(2)
        self.mapper.penup()
        self.mapper.hideturtle()

        self.writer = turtle.Turtle()
        self.writer.hideturtle()
        self.writer.speed(0)
        self.writer.up()
        
        self.mapper_font= ('Arial', 10)
        self.finisher_font= ('Arial', 12)
        self.mapper_text_clr = 'blue'
        self.finisher_text_clr = 'green'
        self.mapper_circle = 8

        self.finisher = turtle.Turtle()
        self.finisher.shape('turtle')
        self.finisher.speed(0)
        self.finisher.color('green')
        self.finisher.pensize(4)
        self.finisher.penup()
        self.finisher.hideturtle()

        self.timestep = 0

    def showmaze(self, heuristic = None):
        # iterate through squares one by one to decide where to draw walls
        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                # to plot heuristic value
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
                    
                    self.wally.goto(self.origin-40, self.origin + self.sq_size * y + self.sq_size / 3 )
                    self.wally.down()
                    self.wally.write(y,font=('Arial', 20), align='left')
                    self.wally.penup()

     
        # skip other plotting than walls
        # return

        # mark the start
        self.wally.color('black', 'blue')
        self.wally.hideturtle()

        
        # mark the goals
        self.wally.color('black', 'red')
        self.wally.hideturtle()
        for goal in self.goals:
            self.wally.up()
            self.wally.goto((self.origin + self.sq_size*5/8) + (self.sq_size * goal[0]), (self.origin + self.sq_size*2/4) + (self.sq_size * goal[1]))
            #wally.goto((origin + sq_size*5/8) + (sq_size * goal[0]), (origin + sq_size*2/4) + (sq_size * goal[1]))
            
            self.wally.down()
            self.wally.begin_fill()
            self.wally.circle(5)
            self.wally.end_fill()
        
        self.wally.up()
        
        self.mapper.setpos(self.origin + self.start[0] * self.sq_size + self.sq_size/2, self.origin + self.start[1] * self.sq_size + self.sq_size/2)
        self.mapper.setheading(self.turtle_move[self.heading])
        self.mapper.showturtle()
    
        self.writer.color(self.mapper_text_clr,'white')
        self.writer.goto(self.origin + self.start[0]*self.sq_size + self.sq_size/4, self.origin + self.start[1]*self.sq_size +self.sq_size/8)
        self.writer.down()
        self.writer.write(1,font=self.mapper_font, align='left')
        self.mapper.penup()
        
        self.finisher.setpos(self.origin + self.start[0] * self.sq_size + self.sq_size/2 + 4, self.origin + self.start[1] * self.sq_size + self.sq_size/2)
        self.finisher.setheading(self.turtle_move[self.heading])
        
        
    def plot_move(self,heading,move_to,run,freq):
        
        self.heading = heading
        
        if run == 0:
            # skip this only to plot optimal path for run2
            #return
            self.mapper.pendown()
            self.mapper.setheading(self.turtle_move[heading])
            self.mapper.goto(self.origin + self.sq_size/2 + self.sq_size * move_to[0], self.origin + self.sq_size/2 + self.sq_size * move_to[1])
            
            self.writer.penup()
            self.writer.color(self.mapper_text_clr,'white')
            self.writer.goto(self.origin + move_to[0]*self.sq_size + self.sq_size/4, self.origin + move_to[1]*self.sq_size + self.sq_size/8)
            self.writer.begin_fill()
            self.writer.circle(self.mapper_circle)
            self.writer.end_fill()
            self.writer.write(freq,font=self.mapper_font, align='left')
            self.mapper.penup()
        else:
            self.mapper.hideturtle()
            self.finisher.showturtle()
            self.finisher.pendown()
            self.finisher.setheading(self.turtle_move[heading])
            self.finisher.goto(self.origin + self.sq_size/2 + 4 + self.sq_size * move_to[0], self.origin + self.sq_size/2 + self.sq_size * move_to[1])

            self.timestep += 1
            self.writer.color(self.finisher_text_clr, 'white')
            self.writer.penup()
            self.writer.goto(self.origin + self.sq_size/2 + 8 + self.sq_size * move_to[0], self.origin + self.sq_size/2 + self.sq_size * move_to[1])
            self.writer.write(self.timestep,font=self.finisher_font, align='left')
            self.finisher.penup()


    def plot_summary (self, summary_text):
        # plot maze file
        self.wally.penup()
        self.wally.goto(self.origin, self.origin + self.maze.dim * self.sq_size + self.sq_size / 2 )
        self.wally.down()
        self.wally.write("maze: "+ summary_text["maze"],font=('Arial', 16), align='left')
        self.wally.penup()
        # plot algorithm
        self.wally.goto(self.origin, self.origin + self.maze.dim * self.sq_size + 5)
        self.wally.down()
        self.wally.write("run1 algorithm: "+ summary_text["alg"],font=('Arial', 16), align='left')
        self.wally.penup()
        # plot run1 timesteps
        self.wally.goto(self.origin + (self.maze.dim * self.sq_size)/2, self.origin + self.maze.dim * self.sq_size + self.sq_size / 2)
        self.wally.down()
        self.wally.write("run1 ts: "+ str(summary_text["run1"]),font=('Arial', 16), align='left')
        self.wally.penup()
        # plot run2 timesteps
        self.wally.goto(self.origin + (self.maze.dim * self.sq_size)/2, self.origin + self.maze.dim * self.sq_size + 5)
        self.wally.down()
        self.wally.write("run2 ts: "+ str(summary_text["run2"]),font=('Arial', 16), align='left')
        self.wally.penup()
        # plot coverage
        self.wally.goto(self.origin + (self.maze.dim * self.sq_size) - 125, self.origin + self.maze.dim * self.sq_size + self.sq_size / 2)
        self.wally.down()
        self.wally.write("coverage: "+ str(summary_text["coverage"])+"%",font=('Arial', 16), align='left')
        self.wally.penup()
        # plot score
        self.wally.goto(self.origin + (self.maze.dim * self.sq_size) - 125, self.origin + self.maze.dim * self.sq_size + 5)
        self.wally.down()
        self.wally.write("score: "+ str(summary_text["score"]),font=('Arial', 16), align='left')
        self.wally.penup()
        return
