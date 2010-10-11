#!/usr/bin/env python

import re

class Actions(object):
    d = {(-1,0):'Up', (1,0):'Down', (0,-1):'Left', (0,1):'Right'}
    def __init__(self, up=False, down=False, left = False, right = False):
        actions = []
        if up:
            actions.append((-1,0))
        if down:
            actions.append((1,0))
        if left:
            actions.append((0,-1))
        if right:
            actions.append((0,1))
        self.actions = tuple(actions)

    def __str__(self):
        return '( ' + ', '.join([Actions.d[a] for a in self.actions]) + ' )'

        
class Labyrinth(object):
    def __init__(self, lab):
        if isinstance(lab, tuple):
            self.m = lab[0]
            self.n = lab[1]
            self.cells = [self.n * [0] for x in range(self.m)]
        elif isinstance(lab, str):
            rows = lab.split()
            if len(set([len(r) for r in rows])) != 1:
                raise Exception, 'all the rows must have the same length'
            self.m = len(rows)
            self.n = len(rows[0])
            cells = [self.n * [0] for x in range(self.m)]
            for i,row in enumerate(rows):
                js = [m.start() for m in re.finditer(re.escape('.'), row)]
                for j in js:
                    cells[i][j] = 1
            self.cells = cells
        else:
            raise Exception, 'lab must be a tuple or string'

        self.get_action_space()
        
    def __str__(self):
        lines = []
        for row in self.cells:
            lines.append(''.join([('x','.')[r] for r in row]))
        return '\n'.join(lines)

    def get_action_space(self):
        actions = [self.n * [None] for x in range(self.m)]
        m = self.m
        n = self.n
        # First check the interior
        for i in range(1,m-1):
            for j in range(1,n-1):
                actions[i][j] = Actions(up = self.cells[i-1][j] == 1,
                                        down = self.cells[i+1][j] == 1,
                                        left = self.cells[i][j-1] == 1,
                                        right = self.cells[i][j+1] == 1)
        # First column
        j = 0
        for i in range(1,m-1):
            actions[i][j] = Actions(up = self.cells[i-1][j] == 1,
                                    down = self.cells[i+1][j] == 1,
                                    right = self.cells[i][j+1] == 1)
        # Last column
        j = self.n - 1
        for i in range(1,m-1):
            actions[i][j] = Actions(up = self.cells[i-1][j] == 1,
                                    down = self.cells[i+1][j] == 1,
                                    left = self.cells[i][j-1] == 1)
        # First row
        i = 0
        for j in range(1,n-1):
            actions[i][j] = Actions(down = self.cells[i+1][j] == 1,
                                    left = self.cells[i][j-1] == 1,
                                    right = self.cells[i][j+1] == 1)
        # Last row
        i = m - 1
        for j in range(1,n-1):
            actions[i][j] = Actions(up = self.cells[i-1][j] == 1,
                                    left = self.cells[i][j-1] == 1,
                                    right = self.cells[i][j+1] == 1)
        # The four corners
        actions[0][0] = Actions(down = self.cells[1][0] == 1,
                                right = self.cells[0][1] == 1)
        actions[m-1][0] = Actions(up = self.cells[m-2][0] == 1,
                                  right = self.cells[m-1][1] == 1)
        actions[0][n-1] = Actions(down = self.cells[1][n-1] == 1,
                                        left = self.cells[0][n-2] == 1)
        actions[m-1][n-1] = Actions(up = self.cells[m-2][n-2] == 1,
                                    left = self.cells[m-1][n-2] == 1)
        self.actions = actions

        
if __name__ == '__main__':
    print 'Testing path planning algorithms...'
    lab = '''\
xxxxxx
x..xxx
xx...x
xxx.xx
x...xx
xxxxxx'''
    l = Labyrinth(lab)
    print l
    print l.actions[4][2]
