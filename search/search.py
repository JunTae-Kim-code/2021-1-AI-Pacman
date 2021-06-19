# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]
    
def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    "*** YOUR CODE HERE ***"
    
    from game import Directions      
    
    visit=set()
    start_state = problem.getStartState()
    visit.add(start_state)
    stack = util.Stack()
    successors = problem.getSuccessors(start_state)
    
    for i in range(len(successors)):
        cur_index, cur_direc, cur_cost = successors[i]
        stack.push((cur_index, [cur_direc], cur_cost))
        
    #s = Directions.SOUTH
    #w = Directions.WEST
    #e = Directions.EAST
    #n = Directions.NORTH
    #command = []
    
    while not stack.isEmpty():
            
        cur_index, cur_direc, cur_cost = stack.pop()
        #print(stack.list)
        visit.add(cur_index)
            
        if problem.isGoalState(cur_index):
            return cur_direc
            #print("Goal!")
            #for i in range(len(cur_direc)):
            #    if cur_direc[i] == 'West':
            #        command.append(w)
            #    elif cur_direc[i] == 'South':
            #        command.append(s)
            #    elif cur_direc[i] == 'East':
            #        command.append(e)
            #    elif cur_direc[i] == 'North':
            #        command.append(n)
            #    else:
            #        print("direction is wrong!")
            #        print(command)
            #        break
            #return command
        
        successors = problem.getSuccessors(cur_index)
        
        for i in range(len(successors)):
            suc_index, suc_direc, suc_cost = successors[i]
            if (not suc_index in visit):
                stack.push((suc_index, cur_direc+[suc_direc], cur_cost+suc_cost))
    
    return cur_index
               
      
def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    #util.raiseNotDefined()   
    
    visit=set()
    
    start_state = problem.getStartState()
    visit.add(start_state)
    
    q = util.Queue()
    successors = problem.getSuccessors(start_state)
    for i in range(len(successors)):
        cur_index, cur_direc, cur_cost = successors[i]
        q.push((cur_index, [cur_direc], cur_cost))
        visit.add(cur_index)
    
    while not q.isEmpty():
            
        cur_index, cur_direc, cur_cost = q.pop()
            
        if problem.isGoalState(cur_index):
            #print("Goal!")
            return cur_direc
        
        successors = problem.getSuccessors(cur_index)
        
        for i in range(len(successors)):
            suc_index, suc_direc, suc_cost = successors[i]
            if (not suc_index in visit):
                visit.add(suc_index)
                q.push((suc_index, cur_direc+[suc_direc], cur_cost+suc_cost))    
    
    return cur_direc
    

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"     
    
    visit=set()
    
    start_state = problem.getStartState()
    visit.add(start_state)
    
    q = util.PriorityQueue()
    successors = problem.getSuccessors(start_state)
    for i in range(len(successors)):
        cur_index, cur_direc, cur_cost = successors[i]
        q.push((cur_index, [cur_direc], cur_cost), cur_cost)
    
    while not q.isEmpty():
    
        cur_index, cur_direc, cur_cost = q.pop()
        if cur_index in visit:
            continue # 일단 successors에 다넣었고 까봤는데 이미 방문했다? 이전에 더 싼 cost의 경로있었기 때문에 무시 -> 다음거 pop
        visit.add(cur_index)   
            
        if problem.isGoalState(cur_index):
            #print("Goal!")
            return cur_direc
        
        successors = problem.getSuccessors(cur_index)
        for i in range(len(successors)):
            suc_index, suc_direc, suc_cost = successors[i]
            q.push((suc_index, cur_direc+[suc_direc], cur_cost+suc_cost), cur_cost+suc_cost)
                                  
    return cur_direc
   

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    #util.raiseNotDefined()     
    
    visit=set()
    
    start_state = problem.getStartState()
    visit.add(start_state)
    
    q = util.PriorityQueue()
    successors = problem.getSuccessors(start_state)
    for i in range(len(successors)):
        cur_index, cur_direc, cur_cost = successors[i]
        h = heuristic(cur_index, problem)
        q.push((cur_index, [cur_direc], cur_cost), cur_cost+h)
    
    while not q.isEmpty():
    
        cur_index, cur_direc, cur_cost = q.pop()
        if cur_index in visit:
            continue # 일단 successors에 다넣었고 pop했는데 이미 방문했다? 이전에 더 싼 cost의 경로있었기 때문에 무시 -> 다음거 pop
        visit.add(cur_index)   
            
        if problem.isGoalState(cur_index):
            #print("Goal!")
            return cur_direc
        
        successors = problem.getSuccessors(cur_index)
        for i in range(len(successors)):
            suc_index, suc_direc, suc_cost = successors[i]
            h = heuristic(suc_index, problem)
            q.push((suc_index, cur_direc+[suc_direc], cur_cost+suc_cost), cur_cost+suc_cost+h)
                                  
    return cur_direc


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
    
