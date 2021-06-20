from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='DefensiveReflexAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers.  isRed is True if the red team is being created, and
    will be False if the blue team is being created.
    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """
    return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
    """
    A base class for reflex agents that chooses score-maximizing actions
    """

    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)


        values = [self.evaluate(gameState, a) for a in actions]


        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())

        if foodLeft <= 2:
            bestDist = 9999
            for action in actions:
                successor = self.getSuccessor(gameState, action)
                pos2 = successor.getAgentPosition(self.index)
                dist = self.getMazeDistance(self.start, pos2)
                if dist < bestDist:
                    bestAction = action
                    bestDist = dist
            return bestAction

        return random.choice(bestActions)

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)
        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.  They can be either
        a counter or a dictionary.
        """
        return {'successorScore': 1.0}

    def OpponentRegion(self, gameState):
        curpos = gameState.getAgentPosition(self.index)
        if gameState.isOnRedTeam:
            if not gameState.isRed(curpos):
                return True
            return False
        else:
            if not gameState.isBlue(curpos):
                return True
            return False
        
    def isGhost(self, gameState, Agentindex):
        ghost = []
        if gameState.isOnRedTeam(self.index):
            for blue in gameState.getBlueTeamIndices():
                if not gameState.isRed(gameState.getAgentPosition(blue)):
                    ghost.append(blue)
        else:# self가 blue인 경우
            for red in gameState.getRedTeamIndices():
                if gameState.isRed(gameState.getAgentPosition(red)):
                    ghost.append(red)
        
        return Agentindex in ghost

class OffensiveReflexAgent(ReflexCaptureAgent):
    
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action) # succesor game state
        #features['successorScore'] = self.getScore(successor)
        foodList = self.getFood(successor).asList()
        
        curpos = successor.getAgentState(self.index).getPosition()
        features['numOffood'] = len(foodList)
        
        if len(foodList):
            minFoodDist = min([self.getMazeDistance(curpos, food) for food in foodList])
            features['FoodDist'] =  minFoodDist
        
        opponent = [oppo for oppo in self.getOpponents(successor)] # oppo는 상대 agent index
        opponent_ghost = []
    
        for oppo in opponent:# 적들중 ghost상태이면서 scared상태가 아닌 ghost만
            if self.isGhost(successor, oppo) and not successor.getAgentState(oppo).scaredTimer:
                opponent_ghost.append(oppo) # 각 opponent의 index
        
        dangerdist = []
        for danger in  opponent_ghost:
            dangerdist.append(self.getMazeDistance(curpos, successor.getAgentState(danger).getPosition()))
        
        if dangerdist:
            mindangerdist = min(dangerdist)
            features['ghostdist'] = mindangerdist # 최소로 하는 이유는 최악의 상황고려 
            if mindangerdist <= 2:
                features['Run'] = 1   # 매우 위험 상태이므로 도망쳐야함
            if mindangerdist <= 9:
                carrying = gameState.getAgentState(self.index).numCarrying
                features['Risk'] = 20*carrying//mindangerdist # 지니고있는 food가 많을 수록 risk커짐
        else:
            features['ghostdist'] = 100 # 일단 임의의 값
            
        if successor.getAgentPosition(self.index) == gameState.getInitialAgentPosition(self.index):
            # 죽어서 리스폰하게 되는 경우
            features['DEAD'] = 1
        
        if action == Directions.STOP: # 멈춰있는 경우
            features['Stop'] = 1
        
        reverse = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        features['reverse'] = 0
        if action == reverse:
            features['reverse'] = 1  
        
        powerpellet = self.getCapsules(gameState)
        if powerpellet:
            features['numOfpowerpellet'] = len(powerpellet)
            features['powerdist'] = min([self.getMazeDistance(curpos, pp) for pp in powerpellet]) 
            
        possible_action = successor.getLegalActions(self.index)
        numOfaction = len(possible_action)
        reverseaction = {"East": "West", "West": "East", "South": "North", "North": "South", "Stop":"Stop"}
        
        if dangerdist and mindangerdist<5:
            if numOfaction<3:
                features['noroad'] = 1
            elif numOfaction == 3:
                for i in range(4):
                    if numOfaction < 3:
                        features['noroad'] = 1
                    else:
                        curreverse = reverseaction[action]
                        for act in possible_action:
                            if act != 'Stop' and act != curreverse:
                                noriskaction = act
                        successor = successor.generateSuccessor(self.index, noriskaction)
                        possible_action = successor.getLegalActions(self.index)
                        numOfaction = len(possible_action)
        
        
        return features
    
    def getWeights(self, gameState, action):
        
        successor = self.getSuccessor(gameState, action)
        curpos = successor.getAgentState(self.index).getPosition()
        height = gameState.data.layout.height
        width = gameState.data.layout.width
        
        if self.red:
            half_width = width//2-1
        else:
            half_width = width//2
            
        change_door = []
        for i in range(height):
            if not gameState.getWalls()[half_width][i]:
                change_door.append((half_width, i))
        change_dist = []
        for i in change_door:
            change_dist.append(self.getMazeDistance(curpos, i))
        
        minchangedist = min(change_dist) # 하프라인까지 거리가 멀수록 risk커짐
        
        return {'numOffood': -100 , 'FoodDist': -4, 'ghostdist': 1, 'Run': -15,'DEAD': -1000,
                'Stop': -400, 'reverse': -50 ,'Risk': -minchangedist, 'numOfpowerpellet': -1000, 'powerdist': -8, 'noroad': -1000}
    
        
class DefensiveReflexAgent(ReflexCaptureAgent):
    
    def __init__(self, index, timeForComputing = .1): # captureAgents.CaptureAgent 의 def __init__그대로 가져옴
        self.index = index
        self.red = None
        self.agentsOnTeam = None
        self.distancer = None
        self.observationHistory = []
        self.timeForComputing = timeForComputing
        
        self.display = None
        
        self.situation = 'DefensiveSituation'
    
    def getFeatures(self, gameState, action): # 상황에 따라 다른 feature 사용
        self.curRegion = self.OpponentRegion(gameState) # 적위치면 True 아니면 False
        
        opponent = [gameState.getAgentState(oppo) for oppo in self.getOpponents(gameState)]
        invader = [oppo for oppo in opponent if oppo.isPacman] # invader들
        
        if self.situation == 'DefensiveSituation':
            if invader: # defense상태일때 침입자가 있는 경우
                return self.getFeatures_usual(gameState, action)
            self.situation = 'OffensiveSituation'
            return self.getFeatures_Offensive(gameState, action)
        
        if self.situation == 'OffensiveSituation':
            if invader:
                self.situation = 'DefensiveSituation'
                return self.getFeatures_usual(gameState, action)
            return self.getFeatures_Offensive(gameState, action)
        
    
    def getWeights(self, gameState, action): # 상황에 따라 다른 weight 사용
        
        if self.situation == 'DefensiveSituation':
            return self.getWeights_usual(gameState, action)
        elif self.situation == 'OffensiveSituation':
            return self.getWeights_Offensive(gameState, action)
    
    def getFeatures_Offensive(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action) # succesor game state
        #features['successorScore'] = self.getScore(successor)
        foodList = self.getFood(successor).asList()
        
        curpos = successor.getAgentState(self.index).getPosition()
        features['numOffood'] = len(foodList)
        
        if len(foodList):
            minFoodDist = min([self.getMazeDistance(curpos, food) for food in foodList])
            features['FoodDist'] =  minFoodDist
        
        opponent = [oppo for oppo in self.getOpponents(successor)] # oppo는 상대 agent index
        opponent_ghost = []
    
        for oppo in opponent:# 적들중 ghost상태이면서 scared상태가 아닌 ghost만
            if self.isGhost(successor, oppo) and not successor.getAgentState(oppo).scaredTimer:
                opponent_ghost.append(oppo) # 각 opponent의 index
        
        dangerdist = []
        for danger in  opponent_ghost:
            dangerdist.append(self.getMazeDistance(curpos, successor.getAgentState(danger).getPosition()))
        
        if dangerdist:
            mindangerdist = min(dangerdist)
            features['ghostdist'] = mindangerdist # 최소로 하는 이유는 최악의 상황고려 
            if mindangerdist <= 2:
                features['Run'] = 1   # 매우 위험 상태이므로 도망쳐야함
            if mindangerdist <= 9:
                carrying = gameState.getAgentState(self.index).numCarrying
                features['Risk'] = 20*carrying//mindangerdist # 지니고있는 food가 많을 수록 risk커짐
        else:
            features['ghostdist'] = 100 # 일단 임의의 값
            
        if successor.getAgentPosition(self.index) == gameState.getInitialAgentPosition(self.index):
            # 죽어서 리스폰하게 되는 경우
            features['DEAD'] = 1
        
        if action == Directions.STOP: # 멈춰있는 경우
            features['Stop'] = 1
        
        reverse = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        features['reverse'] = 0
        if action == reverse:
            features['reverse'] = 1  
            
        powerpellet = self.getCapsules(gameState)
        if powerpellet:
            features['numOfpowerpellet'] = len(powerpellet)
            features['powerdist'] = min([self.getMazeDistance(curpos, pp) for pp in powerpellet])      
            
        possible_action = successor.getLegalActions(self.index)
        numOfaction = len(possible_action)
        reverseaction = {"East": "West", "West": "East", "South": "North", "North": "South", "Stop":"Stop"}
        
        if dangerdist and mindangerdist<5:
            if numOfaction<3:
                features['noroad'] = 1
            elif numOfaction == 3:
                for i in range(4):
                    if numOfaction < 3:
                        features['noroad'] = 1
                    else:
                        curreverse = reverseaction[action]
                        for act in possible_action:
                            if act != 'Stop' and act != curreverse:
                                noriskaction = act
                        successor = successor.generateSuccessor(self.index, noriskaction)
                        possible_action = successor.getLegalActions(self.index)
                        numOfaction = len(possible_action)  
        
        return features
    
    def getWeights_Offensive(self, gameState, action):
        
        successor = self.getSuccessor(gameState, action)
        curpos = successor.getAgentState(self.index).getPosition()
        height = gameState.data.layout.height
        width = gameState.data.layout.width
        
        if self.red:
            half_width = width//2-1
        else:
            half_width = width//2
            
        change_door = []
        for i in range(height):
            if not gameState.getWalls()[half_width][i]:
                change_door.append((half_width, i))
        change_dist = []
        for i in change_door:
            change_dist.append(self.getMazeDistance(curpos, i))
        
        minchangedist = min(change_dist) # 하프라인까지 거리가 멀수록 risk커짐
        
        return {'numOffood': -100 , 'FoodDist': -4, 'ghostdist': 1, 'Run': -15,'DEAD': -1000,
                'Stop': -400, 'reverse': -50 ,'Risk': -minchangedist, 'numOfpowerpellet': -1000, 'powerdist': -8, 'noroad': -1000}
    
    def getFeatures_usual(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        curstate = successor.getAgentState(self.index)
        curpos = curstate.getPosition()
        
        features['onDefense'] = 1
        if curstate.isPacman:
            features['onDefense'] = 0
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)] # 적 위치
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None] # 적들중 pacman상태인 녀석들
        features['numInvaders'] = len(invaders)
        if len(invaders) > 0:
            dists = [self.getMazeDistance(curpos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

        if action == Directions.STOP: features['stop'] = 1
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction] # 해당 agent의 왔던 경로를 되돌아가는 듯 game.configuration.direction
        if action == rev: 
            features['reverse'] = 1
        
        return features
    
    def getWeights_usual(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}