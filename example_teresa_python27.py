# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 00:57:22 2017

@author:    Jonas Hartmann @ Gilmour group @ EMBL Heidelberg
            Renato Alves - Implementing memory

@descript:  Simple example code for the EMBL Coding Club Summer Challenge 2017,
            showing how to load and visualize a maze, as well as a very
            primitive "Teresa bot" based on random decisions.

@version:   python 2.7
"""

from __future__ import print_function

# This code uses a numpy array to represent the maze and pyplot for figures
import numpy as np
import matplotlib.pyplot as plt
from glob import glob


class ExitFound(Exception):
    pass


class GiveUp(Exception):
    pass


class Teresa(object):
    def __init__(self, maze, start=(0, 1), tries=100000, plot=None):
        self.start = start
        self.exit = (maze.shape[0] - 1, maze.shape[1] - 2)
        self.old_position = start
        self.position = start
        self.maze = maze
        self.directions = (
            (-1, 0),  # Left
            (1, 0),   # Right
            (0, -1),  # Up
            (0, 1),   # Down
        )
        self.visited = np.zeros_like(maze)
        self.visited[(0, 0)] = 0  # Prevent Teresa from leaving through the entrance
        self.tries = tries
        # As going through the maze, keep track of all the forks in the order they were visited
        # This is used to return to the previous fork in case we made a bad decision
        self.forks = []
        self.plot = plot

    def position_from_move(self, move):
        return (self.position[0] + move[0], self.position[1] + move[1])

    def get_allowed_moves(self):
        allowed = []
        for d in self.directions:
            # Check if the exit was found
            pos = self.position_from_move(d)
            if pos == self.exit:
                print("I've found the exit!")
                self.old_position = self.position
                self.position = pos
                self.show_move()
                if self.plot:
                    self.plot.pause(5)
                raise ExitFound()
            if self.maze[pos] == 1 and self.visited[pos] == 0:  # not a wall and not visited
                allowed.append(d)

        return allowed

    def dead_end(self, allowed_moves):
        if len(allowed_moves) == 0:
            return True

        return False

    def generate_move(self):
        allowed_moves = self.get_allowed_moves()

        # Randomly decide one of the four directions
        if self.dead_end(allowed_moves):
            # Roll back to last fork
            self.position = self.forks.pop()

            if len(self.get_allowed_moves()) >= 1:
                self.forks.append(self.position)

            return self.generate_move()

        move = allowed_moves[np.random.randint(0, len(allowed_moves))]

        # Apply the movement to the position
        new_position = self.position_from_move(move)

        if len(allowed_moves) >= 2:
            self.forks.append(self.position)

        # Update position
        return new_position

    def update_position(self, new_position):
        self.visited[new_position] = 1
        self.old_position = self.position
        self.position = new_position

    def show_move(self):
        if self.plot:
            self.plot.plot(*reversed(zip(self.old_position, self.position)), color="blue")
            self.plot.pause(.00001)

    def walk(self):
        while True:
            new_position = self.generate_move()

            self.update_position(new_position)

            if not self.tries:
                raise GiveUp("I'm tired - I give up!")
            else:
                self.tries -= 1

            self.show_move()


for path in glob("maze_*.txt"):
    loaded_maze = np.loadtxt(path, dtype=np.bool, delimiter=',')

    # Display the explored area
    plt.figure(figsize=(10, 10))                            # Set the figure size
    plt.imshow(loaded_maze, cmap='gray', interpolation='none')     # Show the maze
    plt.ion()                                               # Update the same window without blocking
    plt.axis('off')                                         # Switch off the axes

    teresa = Teresa(loaded_maze, plot=plt)
    try:
        teresa.walk()
    except ExitFound:
        pass
