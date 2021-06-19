# myAgents.py
# ---------------
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

from game import Agent
from searchProblems import PositionSearchProblem

import util
import time
import search

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
def createAgents(num_pacmen, agent='MyAgent'):
    return [eval(agent)(index=i) for i in range(num_pacmen)]

class MyAgent(Agent):
    """
    Implementation of your agent.
    """
    visit_position = set()#방문 목록
    def find_each_agent_path(self, gamestate):
        """
        Returns the next action the agent will take
        """
        "*** YOUR CODE HERE ***"
        if self.flag:
            return 'Stop'
        else:
            # actions가 없으면 다음 actions 업데이트
            if self.actions == []:
                self.actions = search.bfs(eachAgentProblem(gamestate, self.index))
            # 행동할 action이 있으면 그 행동을 return하고 actions에서 제거
            if self.actions != []:
                return self.actions.pop(0)
            # 더이상 생성할 actions가 없으면 더이상 그 agent가 향할 food가 없음, 해당 agent의 flag를 true로 반환하고 Stop
            else:
                self.flag = True
                return 'Stop'        
    
    def getAction(self, state):
        return self.find_each_agent_path(state)

    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        "*** YOUR CODE HERE"
        # 각 agent생성 마다 초기화해줌 flag는 각 agent가 향할 food가 있는지 여부를 나타냄.
        self.actions = []
        self.flag = False
 

class eachAgentProblem(PositionSearchProblem):

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood() # food[x][y]로 food존재여부 알 수 있음

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

        self.agentIndex = agentIndex
        self.allfood = self.food.asList()#self.food = Grid(self.width, self.height, False), game.py grid안에 aslist있음 모든 food의 위치.
        # 매번 전체 food를 각 agent들에게 분배
        self.numFood = len(self.allfood)
        eachnumFood = self.numFood // 4 + 1 # 일부러 딱맞거나 개수보다 더많이 분배함, 어차피 indexing초과하는 것을 알아서 짤림
        self.agent_food = self.allfood[agentIndex*eachnumFood : (agentIndex+1)*eachnumFood] 


    def isGoalState(self, state):
        if state in MyAgent.visit_position:
            return False
        if self.numFood <= 4:# food개수가 적은경우 그냥 해당 위치가 food기만하면 루트가 중복되더라도 그 food로 빠르게 향하도록함
            return state in self.allfood
        if state in self.agent_food:# 자신이 분배받은 food인 경우
            MyAgent.visit_position.add(state)
            return True
        if state in self.allfood and self.euclideanDistance(state, self.startState) <= (self.agentIndex+1)**2:# 자신이 분배받은 food가 아니더라도 가깝다면 해당 food향해감
            MyAgent.visit_position.add(state)
            return True                                           
        return False # 가깝지도않고 해당 agent가 분배받은 food도 아니므로 False
        
    def euclideanDistance(self, xy1, xy2 ):
        return ((xy1[0] - xy2[0])**2  + (xy1[1] - xy2[1])**2)**0.5


"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""

class ClosestDotAgent(Agent):

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition(self.index) # self.index는 현재 agent의 agent index를 의미
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState, self.index)


        "*** YOUR CODE HERE ***"

        pacmanCurrent = [problem.getStartState(), [], 0]
        visitedPosition = set()
        # visitedPosition.add(problem.getStartState())
        fringe = util.PriorityQueue()
        fringe.push(pacmanCurrent, pacmanCurrent[2])
        while not fringe.isEmpty():
            pacmanCurrent = fringe.pop()
            if pacmanCurrent[0] in visitedPosition: # 방문했다면 굳이 안감
                continue
            else:
                visitedPosition.add(pacmanCurrent[0]) # pacmanCurrent[0]는 해당 위치
            if problem.isGoalState(pacmanCurrent[0]): # 해당 위치에 food가 있는 경우 해당action 실행
                return pacmanCurrent[1]
            else:
                pacmanSuccessors = problem.getSuccessors(pacmanCurrent[0])
            Successor = []
            for item in pacmanSuccessors:  # item: [(x,y), 'direction', cost]
                if item[0] not in visitedPosition: # 아예 visti list에 있는 경우는 그냥 skip함
                    pacmanRoute = pacmanCurrent[1].copy()
                    pacmanRoute.append(item[1])
                    sumCost = pacmanCurrent[2]
                    Successor.append([item[0], pacmanRoute, sumCost + item[2]])
            for item in Successor:
                fringe.push(item, item[2])
        return pacmanCurrent[1]

    def getAction(self, state):
        return self.findPathToClosestDot(state)[0]

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x,y = state
        if self.food[x][y] == True:
            return True
        return False