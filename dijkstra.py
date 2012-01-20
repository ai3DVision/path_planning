import operator
import Queue

import networkx as nx

# From http://norvig.com/python-iaq.html
class PriorityQueue_old(object):
    "A queue in which the minimum element (as determined by cmp) is first."
    def __init__(self, items=None, cmp=operator.lt):
        self.A = []
        self.cmp = cmp
        if items: 
            self.extend(items)
      
    def __len__(self): return len(self.A)

    def append(self, item):
        A, cmp = self.A, self.cmp
        A.append(item)
        i = len(A) - 1
        while i > 0 and cmp(item, A[i//2]):
            A[i], i = A[i//2], i//2
        A[i] = item

    def extend(self, items):
        for item in items: 
            self.append(item)

    def pop(self):
        A = self.A
        if len(A) == 1: return A.pop()
        e = A[0]
        A[0] = A.pop()
        self.heapify(0)
        return e

    def heapify(self, i):
        "Assumes A is an array whose left and right children are heaps,"
        "move A[i] into the correct position.  See CLR&S p. 130"
        A, cmp = self.A, self.cmp
        left, right, N = 2*i + 1, 2*i + 2, len(A)-1
        if left <= N and cmp(A[left], A[i]):
            smallest = left
        else:
            smallest = i
        if right <= N and cmp(A[right], A[smallest]):
            smallest = right
        if smallest != i:
            A[i], A[smallest] = A[smallest], A[i]
            self.heapify(smallest)

class PriorityQueue(object):
    "A queue in which the minimum element (as determined by cmp) is first."
    def __init__(self, items=None):
        self.A = []
        self.values = {}
        #self.cmp = cmp
        self.cmp = lambda x,y: self.values[x] < self.values[y]
        if items: 
            self.extend(items)
      
    def __len__(self): return len(self.A)

    def append(self, item, value):
        A, cmp = self.A, self.cmp
        A.append(item)
        self.values[item] = value
        i = len(A) - 1
        while i > 0 and cmp(item, A[i//2]):
            A[i], i = A[i//2], i//2
        A[i] = item

    ## def update(self, item, value):
    ##     try:
    ##         self.heapify(self.A.index(item))
    ##     except ValueError:
    ##         pass
    ##     else:
    ##         self.values[item] = value

    def update(self, item, value):
        try:
            self.A.remove(item)
        except ValueError:
            pass
        else:
            self.append(item, value)
        
    def pop(self):
        A = self.A
        if len(A) == 1: 
            self.values.popitem()
            return A.pop()
        e = A[0]
        A[0] = A.pop()
        self.values.pop(e)
        self.heapify(0)
        return e

    def heapify(self, i):
        "Assumes A is an array whose left and right children are heaps,"
        "move A[i] into the correct position.  See CLR&S p. 130"
        A, cmp = self.A, self.cmp
        left, right, N = 2*i + 1, 2*i + 2, len(A)-1
        if left <= N and cmp(A[left], A[i]):
            smallest = left
        else:
            smallest = i
        if right <= N and cmp(A[right], A[smallest]):
            smallest = right
        if smallest != i:
            A[i], A[smallest] = A[smallest], A[i]
            self.heapify(smallest)
            
def forward_search(G, x_I, x_G, verbose=False):
    """ Compute a path between two nodes of a graph.

    The search is implimented as a forward search, based on the algorithm
    of Figure 2.4 (p. 28) of LaValle's book.

    Parameters
    ----------
    G: Graph to search
    x_I: Initial vertice in the Graph
    x_G: Goal vertice

    Returns
    -------
    If a path is found, a list with the plan for going from x_I to x_G.
    If a path is not found, None
    """

    print 'Initial state:', x_I, 'Goal:', x_G
    pred = {x_I:None}
    fringe = Queue.Queue()
    fringe.put(x_I)
    while fringe.not_empty:
        x = fringe.get()
        if x == x_G:
            print 'success!'
            # We obtain the path from pred at the end. It is also used as a
            # list of visited states
            path = [x_G]
            p = x_G
            while 1:
                p = pred[p]
                if p is not None:
                    path.append(p)
                else:
                    path.reverse()
                    return path    
        for node in G[x]:
            if node not in pred:
                pred[node] = x
                fringe.put(node)
            else:
                pass 
        if verbose:
            print pred
            print fringe.queue
            print '##################################################'

    print 'Failure :('
    return None

def dijkstra(G, x_I, x_G, verbose=False):
    """ Compute the shortes path between two nodes of a graph using Dijkstra.

    The attribute 'weinght' of the edges is used to find the shortest path.
    
    Parameters
    ----------
    G: Graph to search
    x_I: Initial vertice in the Graph
    x_G: Goal vertice

    Returns
    -------
    If a path is found, a list with the plan for going from x_I to x_G.
    If a path is not found, None
    """

    print 'Initial state:', x_I, 'Goal:', x_G
    pred = {x_I:None}
    cost_to_come = {x_I:0}
    #fringe = PriorityQueue([(x_I, 0)], lambda x,y: x[1] < y[1])
    fringe = PriorityQueue()
    fringe.append(x_I, 0)
    while len(fringe) > 0:
        x = fringe.pop()
        if x == x_G:
            print 'success!'
            # We obtain the path from pred at the end. It is also used as a
            # list of visited states
            path = [x_G]
            p = x_G
            while 1:
                p = pred[p]
                if p is not None:
                    path.append(p)
                else:
                    path.reverse()
                    return path    
        for y in G[x]:
            w = G.get_edge_data(x, y)['weight']
            if y not in pred:
                pred[y] = x
                cost_to_come[y] = cost_to_come[x] + w
                fringe.append(y, cost_to_come[y])
            else:
                if cost_to_come[y] > cost_to_come[x] + w:
                    cost_to_come[y] = cost_to_come[x] + w
                    fringe.update(y, cost_to_come[y])
                    pred[y] = x
        if verbose:
            print 'Removed from queue:', x 
            print pred
            print 'Queue', fringe.A
            print 'values', fringe.values
            print '##################################################'

    print 'Failure :('
    return None


def simple_graph():
    G = nx.Graph()
    G.add_nodes_from(range(1,7))
    G.add_edge(1, 2, weight=7)
    G.add_edge(1, 3, weight=9)
    G.add_edge(1, 6, weight=14)
    G.add_edge(2, 3, weight=10)
    G.add_edge(2, 4, weight=15)
    G.add_edge(3, 4, weight=11)
    G.add_edge(3, 6, weight=2)
    G.add_edge(4, 5, weight=6)
    G.add_edge(5, 6, weight=9)

    return G

def path_cost(G, path):

    w = 0
    for x, y in zip(path[:-1], path[1:]):
        if not y in G.neighbors(x):
            print 'Not a path!'
            return None
        w += G.get_edge_data(y, x)['weight']

    return w

def experiment_1():
    print 'Running experiment 1'
    G = simple_graph()
    start, goal = 1, 5
    path = forward_search(G, start, goal, verbose=True)
    print 'The shortest path is', path
    
    ## G = nx.gnp_random_graph(1000, 0.05)
    ## start = 0
    ## goal = max(G.nodes())
    ## path = forward_search(G, start, goal, verbose=False)
    ## path_nx = nx.shortest_path(G, start, goal)
    ## print path
    ## print path_nx
    return locals()

def experiment_2():
    start = 0
    goal = 99
    n_trials = 1000
    fails = 0
    while n_trials > 0:
        G = nx.gnp_random_graph(1000, 0.05)
        if not nx.is_connected(G):
            print 'Not connected'
            continue
        n_trials -= 1
        path_1 = nx.shortest_path(G, start, goal)
        path_2 = forward_search(G, start, goal)
        if len(path_1) != len(path_2):
            fails += 1
    print fails
    return locals()

def experiment_3():
    print 'Running experiment 3'
    ## G = simple_graph()
    ## start, goal = 1, 5
    ## path = dijkstra(G, start, goal, verbose=True)
    ## print path

    n_trials = 1000
    for _ in range(n_trials):
        G = nx.gnp_random_graph(25, 0.1)
        if not nx.is_connected(G):
            continue
        for e1, e2 in G.edges_iter():
            G.edge[e1][e2]['weight'] = random.randint(1,100)
        start = 0
        goal = max(G.nodes())
        path = dijkstra(G, start, goal, verbose=False)
        path_nx = nx.dijkstra_path(G, start, goal)
        print path
        print path_nx
        if len(path) != len(path_nx):
            print 'Error'
            print path_cost(G, path)
            print path_cost(G, path_nx)
            nx.write_gpickle(G, 'G.gpickle')
            break

    
    return locals()

def experiment_4():
    G = nx.Graph()
    G.add_edge(0, 11, weight=91)
    G.add_edge(1, 11, weight=72)
    G.add_edge(1, 13, weight=96)
    G.add_edge(2, 13, weight=49)
    G.add_edge(2, 6, weight=63)
    G.add_edge(2, 3, weight=31)
    G.add_edge(3, 9, weight=98)
    G.add_edge(3, 7, weight=1)
    G.add_edge(3, 12, weight=59)
    G.add_edge(4, 7, weight=6)
    G.add_edge(4, 9, weight=6)
    G.add_edge(4, 8, weight=95)
    G.add_edge(5, 11, weight=44)
    G.add_edge(6, 11, weight=53)
    G.add_edge(8, 10, weight=2)
    G.add_edge(8, 12, weight=48)
    G.add_edge(9, 12, weight=32)
    G.add_edge(10, 14, weight=16)
    G.add_edge(11, 13, weight=86)
    
    path_nx = nx.dijkstra_path(G, 0, 14)
    path = dijkstra(G, 0, 14, True)
    if path_cost(G, path) > path_cost(G, path_nx):
        print 'Error'
    else:
        print 'Correct'
        
    return locals()
    
if __name__ == '__main__':
    import sys
    import random
    
    if len(sys.argv) == 2:
        n = sys.argv[1]
    else:
        n = '1'
    f_name = 'experiment_' + n
    f = getattr(sys.modules[__name__], f_name, None)
    if f:
        d = f()
        locals().update(d)
    else:
        print 'Function %s does not exist' % f_name
    
