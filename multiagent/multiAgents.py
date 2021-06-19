# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        
        "*** YOUR CODE HERE ***"
        newGhostPos = successorGameState.getGhostPositions() # 여러 state에서의 ghost posions반환 하는듯?
        
        # print(newGhostStates[0].getPosition()) # 첫번쨰 ghoststate에서 postion인듯함
        foodlist = newFood.asList()
        #fooddist = []
        ghostdist = []
        score = 0
        
        #for food in foodlist:
        #     fooddist.append(manhattanDistance(food, newPos))
             
        if foodlist == []:
            return 10000
        
        fdist = manhattanDistance(newPos,foodlist[0])
        if fdist == 0:
            score+=100
        elif fdist<=1:
            score+=10
        elif fdist<=2:
            score+=3
        else:
            score +=9/fdist
                  
        for ghostpos in newGhostPos:
            ghostdist.append(manhattanDistance(ghostpos,newPos))
            
        gscore=0    
        for dist in ghostdist:
            if dist<=1:
                gscore-=score+1000
            elif dist<=2:
                gscore-=score+100
                
        #restfood = len(foodlist)
        #if restfood != 0:
        #    diffone = manhattanDistance(foodlist[0], newPos)
        #else:
        #    diffone = 0
        
        #if successorGameState.hasFood(x,y):
        #    foodexist = 5
        if sum(newScaredTimes):
            return successorGameState.getScore() + score + sum(newScaredTimes)
        else:
            return successorGameState.getScore() + score + gscore + sum(newScaredTimes)

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        #util.raiseNotDefined()
        def minimax(gameState,agent,depth):
            
            best = []
            
            if gameState.getLegalActions(agent) == [] or depth == self.depth: # leaf(이겼거나 졌음)거나 max depth
                return [0, self.evaluationFunction(gameState)] # ex)[0,-100] list형태로 반환

            if agent == gameState.getNumAgents() - 1: # 한바퀴 다돌았으므로 depth재조정, 다음 agent index pacman으로 지정
                depth += 1
                nextAgent = 0
            else:
                nextAgent = agent + 1

            for action in gameState.getLegalActions(agent):
                nextscore = minimax(gameState.generateSuccessor(agent,action),nextAgent,depth)
                new = [action, nextscore[1]]
                if best == []:
                    best = new
                    continue
                
                prescore = best[1]

                if agent == 0:
                    if nextscore[1] > prescore:
                        best = new
                else:
                    if nextscore[1] < prescore:
                        best = new
            return best

        return minimax(gameState,0,0)[0]
        
    

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def abminimax(gameState,agent,depth,alpha,beta):
            
            best = []
            
            if gameState.getLegalActions(agent) == [] or depth == self.depth: # leaf(이겼거나 졌음)거나 max depth
                return [0, self.evaluationFunction(gameState)] #[0,-100] list형태로 반환

            if agent == gameState.getNumAgents() - 1: # 한바퀴 다돌았으므로 depth랑 다음 agent index pacman으로 지정
                depth += 1
                nextAgent = 0
            else:
                nextAgent = agent + 1

            for action in gameState.getLegalActions(agent):
                
                if best == []:
                    nextscore = abminimax(gameState.generateSuccessor(agent,action),nextAgent,depth,alpha,beta)[1]
                    best = [action, nextscore]
                    if agent==0:
                        alpha = max(alpha, best[1])
                    else:
                        beta = min(beta, best[1])
                    continue
                
                if agent==0 and best[1]>beta:
                    return best
                elif agent!=0 and best[1]<alpha:
                    return best
                
                nextscore = abminimax(gameState.generateSuccessor(agent,action),nextAgent,depth,alpha,beta)[1]
                new = [action, nextscore]
                prescore = best[1]

                if agent == 0 and nextscore > prescore:
                    best = new
                    alpha = max(alpha, best[1])
                elif agent != 0 and nextscore < prescore:
                    best = new
                    beta = min(beta, best[1])
            return best

        return abminimax(gameState,0,0,-float("inf"),float("inf"))[0]
        
        
        #util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
