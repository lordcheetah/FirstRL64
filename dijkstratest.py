import math
import sys

IMPASS = 40

map = ['########################################',
       '#                 ##########           #',
       '#                 ##########           #',
       '#                 ##########           #',
       '#                 ##########           #',
       '#                         ##           #',
       '#                 #######              #',
       '#                 ##########           #',
       '#                 ################# ####',
       '############  ##################### ####',
       '############  #################     ####',
       '############  ############      ########',
       '############  ############ #############',
       '############  ############ #############',
       '############  ##########   #############',
       '###########    ########      ###########',
       '########          ######      ##########',
       '########                 ###   #########',
       '########          ###########  #########',
       '###########    #########################',
       '########################################',
       '########################################',
       '########################################']

'''X = len(map)
Y = len(map[0])

neighbors = lambda x, y : [(x2, y2) for x2 in range(x-1, x+2)
                               for y2 in range(y-1, y+2)
                               if (-1 < x <= X and
                                   -1 < y <= Y and
                                   (x != x2 or y != y2) and
                                   (0 <= x2 <= X) and
                                   (0 <= y2 <= Y))]

dmap = [[IMPASS for y in range(Y)] for x in range(X)]

for x in range(X):
    for y in range(Y):
        if map[x][y] != '#':
            dmap[x][y] = IMPASS - 1

dmap[4][9] = 0

for i in range(IMPASS):
    for x in range(X):
        for y in range(Y):
            if dmap[x][y] != IMPASS:
                lowest_val = dmap[x][y]
                for j in neighbors(x, y):
                    if dmap[x][y] > dmap[j[0]][j[1]] + 2 and lowest_val > dmap[j[0]][j[1]] + 1:
                        lowest_val = dmap[j[0]][j[1]] + 1
                dmap[x][y] = lowest_val

for i in range(X):
    print(dmap[i])

print()

for x in range(X):
    for y in range(Y):
        if dmap[x][y] != IMPASS:
            dmap[x][y] *= -1.2

for i in range(X):
    print(dmap[i])

print()

for i in range(IMPASS):
    for x in range(X):
        for y in range(Y):
            if dmap[x][y] != IMPASS:
                lowest_val = dmap[x][y]
                for j in neighbors(x, y):
                    if dmap[x][y] > dmap[j[0]][j[1]] + 2 and lowest_val > dmap[j[0]][j[1]] + 1:
                        lowest_val = dmap[j[0]][j[1]] + 1
                dmap[x][y] = math.floor(lowest_val)

for i in range(X):
    print(dmap[i])'''

DIRS= [(0,-1),
       (1,-1),
       (1, 0),
       (1, 1),
       (0, 1),
       (-1, 1),
       (-1, 0),
       (-1,-1)]


class Dimensions:
    def __init__(self, w, h):
        self.w = w
        self.h = h


class DijkstraMap:
    ''' Constructor.
    goalX x-position of cell that map will 'roll down' to
    goalY y-position of cell that map will 'roll down' to
    mapWidth width of the map
    mapHeight height of the map
    passableCallback a function with two parameters (x, y) that returns true if a map cell is passable'''

    def __init__(self, goalX, goalY, mapWidth, mapHeight, passableCallback):
        self._map=[]
        self._goals=[]
        self._goals.append((goalX, goalY))

        self._dimensions=Dimensions(mapWidth, mapHeight)

        self._dirs = []
        self._dirs = DIRS

        self._passableCallback=passableCallback

    ''' Establish values for all cells in map.
        call after DijkstraMap(goalX, goalY, mapWidth, mapHeight, passableCallback)'''

    def compute(self):
        if len(self._goals) < 1: return
        elif len(self._goals) == 1: return self._singlegoalcompute(self._goals[0][0], self._goals[0][1])
        else: return self._manygoalcompute()

    def _manygoalcompute(self):
        stillupdating=[]
        for i in self._dimensions.w:
            self._map[i]=[]
            stillupdating[i]=[]
            for j in self._dimensions.h:
                stillupdating[i][j]=True
                self._map[i][j]=sys.maxsize

        for v in self._goals:
            self._map[v.x][v.y]=0

        passes = 0
        while True:
            nochange=True
            for i in stillupdating:
                for j in stillupdating[i]:
                    if self._passableCallback(i, j):
                        cellChanged = False
                        low=sys.maxsize
                        for v in self._dirs:
                            tx=(i+v[0])
                            ty=(j+v[1])
                            if 0 < tx <= self._dimensions.w and 0 < ty <= self._dimensions.h:
                                val=self._map[tx][ty]
                                if val and val < low:
                                    low=val

                        if self._map[i][j] > low+2:
                            self._map[i][j] = low+1
                            cellChanged = True
                            nochange = False

                        if not cellChanged and self._map[i][j] < 1000:
                            stillupdating[i][j] = None
                    else:
                        stillupdating[i][j] = None

            passes+=1

    def _singlegoalcompute(self, gx, gy):
        self._map = [[sys.maxsize for j in range(self._dimensions.h)] for i in range(self._dimensions.w)]

        self._map[gx][gy]=0

        val = 1
        wq = []
        pq = []
        ds = self._dirs

        wq.insert(0, (gx, gy))

        while True:
            while len(wq) > 0:
                t = wq.pop()
                for d in ds:
                    x = t[0] + d[0]
                    y = t[1] + d[1]
                    if 0 <= x < self._dimensions.w and 0 <= y < self._dimensions.h:
                        if self._passableCallback(x, y) and self._map[x][y] > val:
                            self._map[x][y] = val
                            pq.insert(0, (x, y))

            if len(pq) < 1:
                break
            val += 1
            while len(pq) > 0:
                wq.insert(0, pq.pop())

    ''' Add new goal position.
        Inserts a new cell to be used as a goal.
        gx the new x-value of the goal cell
        gy the new y-value of the goal cell'''
    def addGoal(self, gx, gy):
        self._goals.insert(0, (gx, gy))

    ''' Remove all goals.
        Will delete all goal cells. You must insert another goal before computing.
        You can specify one goal to be inserted after the goal remove takes place.
        The method only checks that the coordinates are provided before setting the new goal cell.
        gx Will use this value as the x-coordinate of a new goal cell to be inserted
        gy Will use this value as the y-coordinate of a new goal cell to be inserted'''

    def removeGoals(self, gx, gy):
        self._goals.clear()
        if gx and gy: self._goals.insert(0, (gx, gy))

    ''' Output map values to console.
        For debugging, will send a comma separated output of cell values to the console.
        returnString Will return the output in addition to sending it to console if true.'''

    def writeMapToConsole(self, returnString):
        ls = ''

        if returnString: ls=''
        for y in self._dimensions.h:
            s=''
            for x in self._dimensions.w:
                s=s + self._map[x][y] + ','

            print(s)
            if returnString: ls=ls + s + '\n'

        if returnString: return ls

    ''' Get Width of map.
        return w width of map'''
    def getWidth(self):
        return self._dimensions.w

    ''' Get Height of map.
        return h height of map'''
    def getHeight(self):
        return self._dimensions.h

    ''' Get Dimensions as table.
        dimensions A table of width and height values
        dimensions.w width of map
        dimensions.h height of map'''
    def getDimensions(self):
        return self._dimensions

    ''' Get the map table.
        map A 2d array of map values, access like map[x][y]'''
    def getMap(self):
        return self._map

    ''' Get the x-value of the goal cell.
        :return x x-value of goal cell'''
    def getGoalX(self):
        return self._goals[0].x

    ''' Get the y-value of the goal cell.
        :return y y-value of goal cell'''
    def getGoalY(self):
        return self._goals[0].y

    ''' Get the goal cell as a table.
        goal table containing goal position
        goal.x x-value of goal cell'''
    def getGoal(self):
        return self._goals[0]

    ''' Get the direction of the goal from a given position
        x x-value of current position
        y y-value of current position
        xDir X-Direction towards goal. Either -1, 0, or 1
        yDir Y-Direction towards goal. Either -1, 0, or 1'''
    def dirTowardsGoal(self, x, y):
        low=self._map[x][y]
        if low==0:
            return None
        dir=None
        for v in self._dirs:
            tx=(x+v[0])
            ty=(y+v[1])
            if 0 < tx <= self._dimensions.w and 0 < ty <= self._dimensions.h:
                val = self._map[tx][ty]
                if val < low:
                    low = val
                    dir = v

        if dir:
            return dir[1], dir[2]
        return None

    ''' Run a callback function on every cell in the map
        callback A function with x and y parameters that will be run on every cell in the map'''
    def iterateThroughMap(self, callback):
        for y in self._dimensions.h:
            for x in self._dimensions.w:
                callback(x,y)


def dijkCalbak(x, y):
    return (map[x][y] == ' ')

dmap = DijkstraMap(4, 9, 23, 40, dijkCalbak)
dmap.compute()
for i in range(dmap.getWidth()):
    print(dmap.getMap()[i])