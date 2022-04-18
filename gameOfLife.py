# Michael Mathews
# Conway's Game of Life with different rules
# for CSE355, Project, ASU
# inspiration https://github.com/tdietert/pythonProjects/blob/master/GameOfLife.py
# 
# Each tick, the entire board is updated all at once
# built with tkinter buttons and changing color

import tkinter as tk
import time
from enum import Enum
import random


# ENUM to have a more clear understanding of each cell
class Cell(Enum):
    NOTHING = 'white'
    GRASS = 'green'
    BUNNIE = 'cyan'
    FOX = 'orange'
    DEAD = 'black'


class GameOfLife(tk.Frame):

    # on instantiation
    def __init__(self, parent):

        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.grid(row=0, column=0)

        self.size_x = 20
        self.size_y = 20
        self.cell_buttons = []
        self.generate_next = True
        self.tick = 0
        self.totalGrass = 0
        self.totalBunnie = 0
        self.totalFox = 0

        self.initialUI()

    """Build the UI with titles and periferals
    """
    def initialUI(self):

        self.parent.title("Michael's Bunnies of Life")

        self.build_grid()

        self.start_button = tk.Button(self.parent, text="Start", command=self.simulate_game)
        self.start_button.grid(row=1,column=1)

        self.reset_button = tk.Button(self.parent, text="Reset", state=tk.DISABLED, command=self.reset_game)
        self.reset_button.grid(row=1,column=2)

        self.tickStr = tk.StringVar()
        self.tickStr.set(str(self.tick))
        self.tick_count = tk.Label(self.parent, textvariable=self.tickStr)
        self.tick_count.grid(row=1,column=3)

        ## Labels for count 

        self.grassNum = tk.StringVar()
        self.grass_count = tk.Label(self.parent, textvariable=self.grassNum)
        self.grass_count.grid(row=1, column=4)


        self.bunnieNum = tk.StringVar()
        self.bunnie_count = tk.Label(self.parent, textvariable=self.bunnieNum)
        self.bunnie_count.grid(row=1, column=5)

        self.deadNum = tk.StringVar()
        self.dead_count = tk.Label(self.parent, textvariable=self.deadNum)
        self.dead_count.grid(row=1, column=6)

    """Starting to make the grid itself
    """
    def build_grid(self):

        self.game_frame = tk.Frame(
            self.parent, width=self.size_x+2, height=self.size_y+2, borderwidth=1, relief=tk.SUNKEN
        )
        self.game_frame.grid(row=2,column=0,columnspan=4)

        # instantiate button for choosing initial configuration
        self.cell_buttons = [[tk.Button(
            master=self.game_frame, bg="white", width=2, height=1
        )
        for i in range(self.size_x+2)]
        for j in range(self.size_y+2)]

        # add command to btn to change in setup
        for i in range(1, self.size_y+1):
            for j in range(1, self.size_x+1):
                self.cell_buttons[i][j].grid(row=i,column=j)
                self.cell_buttons[i][j]['command'] = lambda i=i, j=j:self.cell_toggle(self.cell_buttons[i][j])

    """Simulate the game with rules
    """
    def simulate_game(self):
        self.disable_buttons()

        # array of coordiantes to update accordingly
        to_grass = []
        to_bunnie = []
        to_fox = []
        to_dead = []
        to_nothing = []

        # for each btn in the grid
        for i in range(1, self.size_y+1):
            for j in range(1, self.size_x+1):
                coord = (i,j)
                
                # Rules
                color = Cell(self.cell_buttons[i][j]['bg'])
                if color is Cell.GRASS:
                    # grass generation
                    to_grass.extend(self.rule_grass_growth(coord))
                    # bunnie generation
                    to_bunnie.extend(self.rule_bunnies_generation(coord, to_bunnie))
                elif color is Cell.BUNNIE:
                    move = self.rule_bunnie_movement(coord)
                    # bunnie movement
                    to_bunnie.extend(move[0])
                    to_nothing.extend(move[1])
                    # bunnie eating
                    eat = self.rule_bunnie_eating(coord)
                    to_nothing.extend(eat)
                    # bunnie re population
                    # bunnie death
                    death = self.rule_bunnie_death(coord)
                    to_dead.extend(death[0])
                elif color is Cell.DEAD:
                    # death to grass in some time
                    pass
                else:
                    pass

        # Update grid with next generation
        for coord in to_grass:
            self.cell_buttons[coord[0]][coord[1]]['bg'] = Cell.GRASS.value
        for coord in to_nothing:
            self.cell_buttons[coord[0]][coord[1]]['bg'] = Cell.NOTHING.value
        for coord in to_bunnie:
            self.cell_buttons[coord[0]][coord[1]]['bg'] = Cell.BUNNIE.value
        for coord in to_fox:
            self.cell_buttons[coord[0]][coord[1]]['bg'] = Cell.FOX.value
        for coord in to_dead:
            self.cell_buttons[coord[0]][coord[1]]['bg'] = Cell.DEAD.value

        # zero the numbers
        self.totalBunnie = 0
        self.totalFox = 0
        self.totalGrass = 0
        self.totalDead = 0

        # update the grid numbers
        for i in range(1, self.size_y + 1):
            for j in range(1, self.size_x + 1):
                coord = (i, j)

                if self.is_equal_cell(coord, Cell.GRASS.value):
                    self.totalGrass += 1
                elif self.is_equal_cell(coord, Cell.BUNNIE.value):
                    self.totalBunnie += 1
                elif self.is_equal_cell(coord, Cell.FOX.value):
                    self.totalFox += 1
                elif self.is_equal_cell(coord, Cell.DEAD.value):
                    self.totalDead += 1
                else:
                    pass

        # Set the count to the labels
        self.grassNum.set(str(self.totalGrass))
        self.bunnieNum.set(str(self.totalBunnie))
        self.deadNum.set(str(self.totalDead))

        # ticks, do it again, stop at 50 ticks
        if self.generate_next and self.tick < 50:
            self.after(1000, self.simulate_game)
            self.tick += 1
            self.tickStr.set(str(self.tick))
        else:
            self.enable_buttons()

    #*************************
    # Rules
    #*************************

    """ Simulate the dead the state upon rules
    :param coord: the btn on the grid
    :returns: grass[], dead[], nothing[]
    """
    def rule_dead_to_grass_or_nothing(self, coord):
        grass = []
        nothing = []

        # on a tick count, convert dead to grass or nothing
        if self.tick % 4 == 0:
            if random.choice(0,1) == 0:
                grass.append(coord)
            else:
                nothing.append(coord)
        return grass, nothing

    """ Rules for grass
    Generate new grass every other tick
    :param coord: btn on the grid
    :returns: grass[]
    """
    def rule_grass_growth(self, coord):
        
        if self.tick % 2 ==0 :
            return self.getNeighbors(coord)
        else:
            return []

    """ Rules for bunnies
    when completely surrounded by grass, new bunnie appears
    and population is less than 10% of board
    :param coord: btn in the grid
    :returns: nothing[], bunnie[], dead[]
    """
    def rule_bunnies_generation(self, coord, to_b):
        bunnie = []
        # if surrounded by grass, add a bunnie
        if self.tick % 5 == 2 and self.tick < 9:
            neighbors = self.getNeighbors(coord)
            # don't share neighbors to be bunnies. every other
            for c in neighbors:
                if self.is_equal_cell(coord, Cell.GRASS.value):
                    if c in to_b:
                        return bunnie
                    else:
                        pass
                else:
                    pass
            bunnie.append(coord)
        return bunnie

    """ Rule for bunnie movement
    move in a random direction every tick
    TODO no detection of collision of bunnies
    :param coord: coordinate of the bunnie on the board
    :returns: a neighbor at random
    """
    def rule_bunnie_movement(self, coord):
        bunnie = []
        nothing = []

        # move to a random neighbor
        neighbors = self.getNeighbors(coord)

        if self.rule_bunnie_death(coord)[1]:
            pass
        else:
            bunnie.append(neighbors[random.randint(0,len(neighbors)-1)])

        nothing.append(coord)

        return bunnie, nothing

    def rule_bunnie_eating(self, coord):
        nothing = []

        # eat 4 of the 8 neighboring grass at random
        neighbors = self.getNeighbors(coord)
        for i in range(4):
            c = random.choice(neighbors)
            neighbors.remove(c)
            if self.is_equal_cell(c, Cell.GRASS.value):
                nothing.append(c)

        return nothing

    def rule_bunnie_death(self, coord):
        dead = []
        death = False

        neighbors = self.getNeighbors(coord)
        count = 0
        for c in neighbors:
            if self.is_equal_cell(c, Cell.GRASS.value):
                count += 1
        if count <= 2:
            dead.append(coord)
            death = True

        return dead, death
    
    """ Helper function to get the btns nearby coord
    Not including the btn itself

    :param coord: btn in the grid
    :returns: array of nearby coords
    """
    def getNeighbors(self, coord):
        neighbors = []
        neighbors.append(coord) # center
        neighbors.append( (coord[0]-1, coord[1]) ) # left
        neighbors.append( (coord[0]+1, coord[1]) ) # right
        neighbors.append( (coord[0], coord[1]-1) ) # up
        neighbors.append( (coord[0], coord[1]+1) ) # down
        neighbors.append( (coord[0]-1, coord[1]-1) ) # tl
        neighbors.append( (coord[0]+1, coord[1]-1) ) # tr
        neighbors.append( (coord[0]-1, coord[1]+1) ) # bl
        neighbors.append( (coord[0]+1, coord[1]+1) ) # br

        return neighbors

    def is_equal_cell(self, coord, value):
        return self.cell_buttons[coord[0]][coord[1]]['bg'] == value

    #******************************************************************************#
    # button Config
    #******************************************************************************#
    def disable_buttons(self):
        if self.cell_buttons[1][1] != tk.DISABLED:
            for i in range(0, self.size_y+2):
                for j in range(0, self.size_x + 2):
                    self.cell_buttons[i][j].configure(state=tk.DISABLED)

            self.reset_button.configure(state = tk.NORMAL)
            self.start_button.configure(state = tk.DISABLED)

    def enable_buttons(self):
        # resets game
        for i in range(0, self.size_y + 2):
            for j in range(0, self.size_x + 2):
                self.cell_buttons[i][j]['bg'] = Cell.NOTHING.value
                self.cell_buttons[i][j].configure(state = tk.NORMAL)

        self.reset_button.configure(state = tk.DISABLED)
        self.start_button.configure(state = tk.NORMAL)
        self.generate_next = True

    def cell_toggle(self, cell):
        # nothing -> grass
        if cell['bg'] == Cell.NOTHING.value:
            cell['bg'] = Cell.GRASS.value
        # grass -> bunnie
        elif cell['bg'] == Cell.GRASS.value:
            cell['bg'] = Cell.BUNNIE.value
        # bunnie -> fox
        elif cell['bg'] == Cell.BUNNIE.value:
            cell['bg'] = Cell.FOX.value
        # fox -> dead
        elif cell['bg'] == Cell.FOX.value:
            cell['bg'] = Cell.DEAD.value
        else:
            cell['bg'] = Cell.NOTHING.value

    def reset_game(self):
        self.generate_next = False
        self.tick = 0

if __name__ == '__main__':
    root = tk.Tk()
    game = GameOfLife(root)
    root.mainloop()