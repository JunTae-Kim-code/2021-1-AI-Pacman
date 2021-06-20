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

class ReflexCaptureAgent(CaptureAgent): # opponent region, isGhost함수를 제외하고 baseline.py에서 그대로 가져옴
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
        actions = gameState.getLegalActions(self.index) # 벽이 아닌 이동할 수 있는 곳에대한 action들을 원소로 갖는 list


        values = [self.evaluate(gameState, a) for a in actions] # 가능한 action들에 대해서 각 action을 실행했을 때 나타나는 상황에서
                                                                # 얻어지는 features들과 weights들의 곱을 score로 반영


        maxValue = max(values) # 각 score들중 가장 큰 값
        bestActions = [a for a, v in zip(actions, values) if v == maxValue] # 가장 큰 score를 갖는 action들을 원소로하는 list 

        foodLeft = len(self.getFood(gameState).asList()) # gameState상황에서 남아있는 food들의 개수

        if foodLeft <= 2: # 남은 food가 2개 이하면
            bestDist = 9999 # bestDist를 9999
            for action in actions: # 가능한 모든 action
                successor = self.getSuccessor(gameState, action) # 현재 state에서 해당 action취했을 때 얻어지는 다음 gamestate
                pos2 = successor.getAgentPosition(self.index) # successorState에서 위치좌표
                dist = self.getMazeDistance(self.start, pos2) # 현재위치와 다음위치간의 거리
                if dist < bestDist: 
                    bestAction = action 
                    bestDist = dist
            return bestAction # 즉 가능한 action들 중 가장 가까운 dist를 갖는 위치로 이동하도록함

        return random.choice(bestActions) # 남은 food가 3개 이상이면 가장 score가 높은 action들 중 랜덤으로 고름

    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """
        successor = gameState.generateSuccessor(self.index, action) # 해당 index의 agent가 주어진 action을 했을 때 나타나는 다음 gameState
        pos = successor.getAgentState(self.index).getPosition() # successor State에서 해당 index의 agent의 위치 좌표
        if pos != nearestPoint(pos): # 해당위치좌표가 해당 위치좌표 각각 반올림해준것과 다르다면
            return successor.generateSuccessor(self.index, action) # 다음 successorState를 찾도록함
        else:
            return successor # 현재 얻은 successorState반환

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)
        return features * weights # 얻어낸 feature와 weight곱으로 score를 결정

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
    
    def OpponentRegion(self, gameState): # 적위치인지 아닌지 확인한는 함수
        curpos = gameState.getAgentPosition(self.index) # 현재위치좌표
        if gameState.isOnRedTeam: # red team일 경우
            if not gameState.isRed(curpos): # 현재 red지역에 있지 않은 경우
                return True # 적팀에 있으므로 True 반환
            return False # 자신의 영역이므로 False 반환
        else: # blue team인 경우
            if not gameState.isBlue(curpos): # 현재 blue영역에 있지 않을 때 
                return True # 적영역이므로 True 반환
            return False # 자신의 영역이므로 False 반환
        
    def isGhost(self, gameState, Agentindex): 
        ghost = []
        if gameState.isOnRedTeam(self.index): # 해당 index의 agent가 red팀인 경우 
            for blue in gameState.getBlueTeamIndices(): # blue는 적 블루팀 위치
                if not gameState.isRed(gameState.getAgentPosition(blue)): # 적이 red의 영역에 있지 않은경우 그 적은 ghost임
                    ghost.append(blue) # 따라서 ghost list에 추가함
        else:# 해당 index의 agent가 blue팀인 경우
            for red in gameState.getRedTeamIndices(): # red는 적 red팀 위치 
                if gameState.isRed(gameState.getAgentPosition(red)): # 적 red가 red영역에 있는 경우 
                    ghost.append(red) # 해당 적은 ghost이므로 ghost list에 추가함
        
        return Agentindex in ghost # input으로 들어오 agent가 ghost인지 아닌지 True or False 반환

class OffensiveReflexAgent(ReflexCaptureAgent):
    
    def getFeatures(self, gameState, action): # 위의 class에 ReflexCaptureAgent에도 getFeatures와 getWeights함수가있지만 따로여기서 새로정의.
        features = util.Counter()
        successor = self.getSuccessor(gameState, action) # succesor game state
        #features['successorScore'] = self.getScore(successor)
        foodList = self.getFood(successor).asList() # 남은 food좌표
        
        curpos = successor.getAgentState(self.index).getPosition() # 현재 위치
        features['numOffood'] = len(foodList) # 남은 food개수 feature로 등록
        
        if len(foodList): # food가 있으면
            minFoodDist = min([self.getMazeDistance(curpos, food) for food in foodList]) # 각 food들과 현재 agent위치 거리 다구해서 그중 최소거리
            features['FoodDist'] =  minFoodDist # 해당 최소거리 feature로 등록
        
        opponent = [oppo for oppo in self.getOpponents(successor)] # 상대 agent index들 원소로 갖는 list
        opponent_ghost = []
    
        for oppo in opponent:# 적들중 ghost상태이면서 scared상태가 아닌 ghost만
            if self.isGhost(successor, oppo) and not successor.getAgentState(oppo).scaredTimer: # 적 agent들이 scared상태가 아닌 ghost라면
                opponent_ghost.append(oppo) # opponent_ghost list에 추가
        
        dangerdist = []
        for danger in  opponent_ghost: # danger는 적 유령
            dangerdist.append(self.getMazeDistance(curpos, successor.getAgentState(danger).getPosition())) # 모든 적유령 거리 원소로 갖는 list
        
        if dangerdist: # 적유령이 있어서 dangerdist 리스트의 원소가 있다면
            mindangerdist = min(dangerdist) # 유령들과의 거리중 최소거리, 최소로 하는 이유는 최악의 상황고려하는 것임
            features['ghostdist'] = mindangerdist # 최소거리를 feature로 등록
            if mindangerdist <= 2: # 만약 적 유령이 2이하로 가깝다면
                features['Run'] = 1   # 매우 위험 상태이므로 도망쳐야함 따라서 관련 feature로 등록
            if mindangerdist <= 9: # # 만약 적 유령이 9이하로 가깝다면
                carrying = gameState.getAgentState(self.index).numCarrying # 해당 agent가 지니고 있는 food 개수
                features['Risk'] = 20*carrying//mindangerdist # 지니고있는 food가 많을 수록 유령과 가까울 수록 risk커짐, 따라서 관련 feature 등록
        else:
            features['ghostdist'] = 10 # 만약 유령상태인 적이 없다면 ghostdist feature를 10으로 등록
            
        if successor.getAgentPosition(self.index) == gameState.getInitialAgentPosition(self.index): # 만약 다음 상태의 위치가 리스폰되는 위치라면
            # 죽어서 리스폰하게 되는 경우임
            features['DEAD'] = 1 # 관련 feature 등록
        
        if action == Directions.STOP: # 멈춰있는 경우
            features['Stop'] = 1 # 관련 feature 등록
        
        reverse = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction] # 역방향 딕셔너리값에 해당 행동 넣음, 즉 역방향 값이 나옴
        features['reverse'] = 0 # 우선 해당 feature값 0으로 두고
        if action == reverse: # 만약 action이 역방향이라면
            features['reverse'] = 1 # 관련 feature를 1로 함
        
        powerpellet = self.getCapsules(gameState) # powerpellet의 좌표를 원소로하는 list
        if powerpellet: # powerpellet이 있다면
            features['numOfpowerpellet'] = len(powerpellet) #powerpellet개수 관련 feature로 등록
            features['powerdist'] = min([self.getMazeDistance(curpos, pp) for pp in powerpellet])  # powerpellet과 거리중 최소거리 feature로 등록 
            
        possible_action = successor.getLegalActions(self.index) # 벽이아니어서 이동 가능한 곳에 관한 action들을 원소로 하는 list
        numOfaction = len(possible_action) # 가능한 action 개수, 최대 5개임(동서남북 stop)
        reverseaction = {"East": "West", "West": "East", "South": "North", "North": "South", "Stop":"Stop"} # 역방향 dictionary
        
        if dangerdist and mindangerdist<5: # 만약 적 유령이 거리 4이하로 쫓아오는 중일 때
            if numOfaction<3: # succesor상황에서 가능한 action이 2개일 때 (stop은 항상 가능하므로 사실상 다시왔던길로 돌아오는길만 가능, 즉 막힌길이라는 의미)
                features['noroad'] = 1 # 막힌 길 관련 feature 등록
            elif numOfaction == 3: # 가능한 action수가 3인경우
                for i in range(4): # 혹시 모르므로 4번의 다음 상황을 더 탐색해봄
                    if numOfaction < 3: # 탐색중 한번이라도 가능한 action수가 2개이하라면 
                        features['noroad'] = 1 # 막혔으므로 관련 feature 등록
                    else: # 가능한 action이 3개 이상인 경우
                        curreverse = reverseaction[action] # 역방향 list 
                        for act in possible_action: # 가능한 action
                            if act != 'Stop' and act != curreverse: # 만약 해당 action이 멈추는 거도 아니고 왔던길 되돌아오는거도 아니면
                                noriskaction = act # ghost에게 쫓기는 입장에서 도망치는 적절한 행동이므로 noriskaction 
                        successor = successor.generateSuccessor(self.index, noriskaction) # noriskaction을 취했을 때 다음상황
                        possible_action = successor.getLegalActions(self.index) # noriskaction을 취했을 때 다음상황에서 가능한 action
                        numOfaction = len(possible_action) # noriskaction을 취했을 때 다음상황에서 가능한 action수 
        
        
        return features
    
    def getWeights(self, gameState, action):
        
        successor = self.getSuccessor(gameState, action)
        curpos = successor.getAgentState(self.index).getPosition()
        height = gameState.data.layout.height # 맵의 높이
        width = gameState.data.layout.width # 맵의 너비
        
        if self.red:
            half_width = width//2-1 # red면 왼쪽으로 한칸가까우므로 2로 나누고 1빼줌
        else:
            half_width = width//2 # 블루진영 고려하면 그냥 2로 나눔
            
        change_door = [] # 자기 홈영역 넘어가는 거리 리스트
        for i in range(height):
            if not gameState.getWalls()[half_width][i]: # 홈영역 높이중 벽이 없는 경우, 즉 넘어갈 수 있는 경우
                change_door.append((half_width, i)) # 리스트에 저장
        change_dist = []
        for i in change_door: #  i는 홈영역 넘어가는 곳 입구 위치
            change_dist.append(self.getMazeDistance(curpos, i)) # 현재위치와 넘어가는 곳 위치 거리 모두 저장
        
        minchangedist = min(change_dist) # 하프라인 입구까지 거리가 멀수록 risk커짐, 최소거리를 저장하고 weight에 사용 
        
        return {'numOffood': -100 , 'FoodDist': -4, 'ghostdist': 1, 'Run': -15,'DEAD': -1000,
                'Stop': -400, 'reverse': -50 ,'Risk': -minchangedist, 'numOfpowerpellet': -1000, 'powerdist': -8, 'noroad': -1000} # weight 등록
    
        
class DefensiveReflexAgent(ReflexCaptureAgent):
    
    def __init__(self, index, timeForComputing = .1): # situation을 제외하고 나머지는 captureAgents.CaptureAgent 의 def __init__그대로 가져옴
        self.index = index
        self.red = None
        self.agentsOnTeam = None
        self.distancer = None
        self.observationHistory = []
        self.timeForComputing = timeForComputing
        
        self.display = None
        
        self.situation = 'DefensiveSituation' # 초기상태는 defensivesituation으로 설정
    
    def getFeatures(self, gameState, action): # 상황에 따라 다른 feature 사용하도록 하는 함수
        self.curRegion = self.OpponentRegion(gameState) # 적위치면 True 아니면 False
        
        opponent = [gameState.getAgentState(oppo) for oppo in self.getOpponents(gameState)] # 현재 적들의 index list
        invader = [oppo for oppo in opponent if oppo.isPacman] # 현재 적들이 pacman인경우 침입한 것임, 침입자 list
        
        if self.situation == 'DefensiveSituation': # DefensiveSituation 상태인 경우
            if invader: # defense상태일때 침입자가 있는 경우
                return self.getFeatures_usual(gameState, action) # defense 관련 feature로써 getFeatures_usual return
            self.situation = 'OffensiveSituation' # 만약 침입자가 없으면 OffensiveSituation으로 상태바꾸고
            return self.getFeatures_Offensive(gameState, action) # offense 관련 feature로 getFeatures_Offensive 리턴
        
        if self.situation == 'OffensiveSituation': # OffensiveSituation상태일 때
            if invader: # 침입자있으면
                self.situation = 'DefensiveSituation' # DefensiveSituation으로 상태바꾸고
                return self.getFeatures_usual(gameState, action) # defense 관련 feature인 getFeatures_usual 리턴 
            return self.getFeatures_Offensive(gameState, action) # 침입자 없으면 offense 관련 feature인 getFeatures_Offensive리턴
        
    
    def getWeights(self, gameState, action): # 상황에 따라 다른 weight 사용
        
        if self.situation == 'DefensiveSituation': # DefensiveSituation 상태인 경우
            return self.getWeights_usual(gameState, action) # defense 관련 weight로써 getWeights_usual 반환
        elif self.situation == 'OffensiveSituation': # OffensiveSituation 상태인 경우
            return self.getWeights_Offensive(gameState, action) # offense 관련 weight로써 getWeights_Offensive 리턴
    
    def getFeatures_Offensive(self, gameState, action): # offensive관련 feature
        features = util.Counter()
        successor = self.getSuccessor(gameState, action) # succesor game state
        #features['successorScore'] = self.getScore(successor)
        foodList = self.getFood(successor).asList() # 남은 food좌표
        
        curpos = successor.getAgentState(self.index).getPosition() # 현재 위치
        features['numOffood'] = len(foodList) # 남은 food개수 feature로 등록
        
        if len(foodList): # food가 있으면
            minFoodDist = min([self.getMazeDistance(curpos, food) for food in foodList]) # 각 food들과 현재 agent위치 거리 다구해서 그중 최소거리
            features['FoodDist'] =  minFoodDist # 해당 최소거리 feature로 등록
        
        opponent = [oppo for oppo in self.getOpponents(successor)] # 상대 agent index들 원소로 갖는 list
        opponent_ghost = []
    
        for oppo in opponent:# 적들중 ghost상태이면서 scared상태가 아닌 ghost만
            if self.isGhost(successor, oppo) and not successor.getAgentState(oppo).scaredTimer: # 적 agent들이 scared상태가 아닌 ghost라면
                opponent_ghost.append(oppo) # opponent_ghost list에 추가
        
        dangerdist = []
        for danger in  opponent_ghost: # danger는 적 유령
            dangerdist.append(self.getMazeDistance(curpos, successor.getAgentState(danger).getPosition())) # 모든 적유령 거리 원소로 갖는 list
        
        if dangerdist: # 적유령이 있어서 dangerdist 리스트의 원소가 있다면
            mindangerdist = min(dangerdist) # 유령들과의 거리중 최소거리, 최소로 하는 이유는 최악의 상황고려하는 것임
            features['ghostdist'] = mindangerdist # 최소거리를 feature로 등록
            if mindangerdist <= 2: # 만약 적 유령이 2이하로 가깝다면
                features['Run'] = 1   # 매우 위험 상태이므로 도망쳐야함 따라서 관련 feature로 등록
            if mindangerdist <= 9: # # 만약 적 유령이 9이하로 가깝다면
                carrying = gameState.getAgentState(self.index).numCarrying # 해당 agent가 지니고 있는 food 개수
                features['Risk'] = 20*carrying//mindangerdist # 지니고있는 food가 많을 수록 유령과 가까울 수록 risk커짐, 따라서 관련 feature 등록
        else:
            features['ghostdist'] = 10 # 만약 유령상태인 적이 없다면 ghostdist feature를 10으로 등록
            
        if successor.getAgentPosition(self.index) == gameState.getInitialAgentPosition(self.index): # 만약 다음 상태의 위치가 리스폰되는 위치라면
            # 죽어서 리스폰하게 되는 경우임
            features['DEAD'] = 1 # 관련 feature 등록
        
        if action == Directions.STOP: # 멈춰있는 경우
            features['Stop'] = 1 # 관련 feature 등록
        
        reverse = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction] # 역방향 딕셔너리값에 해당 행동 넣음, 즉 역방향 값이 나옴
        features['reverse'] = 0 # 우선 해당 feature값 0으로 두고
        if action == reverse: # 만약 action이 역방향이라면
            features['reverse'] = 1 # 관련 feature를 1로 함
        
        powerpellet = self.getCapsules(gameState) # powerpellet의 좌표를 원소로하는 list
        if powerpellet: # powerpellet이 있다면
            features['numOfpowerpellet'] = len(powerpellet) #powerpellet개수 관련 feature로 등록
            features['powerdist'] = min([self.getMazeDistance(curpos, pp) for pp in powerpellet])  # powerpellet과 거리중 최소거리 feature로 등록 
            
        possible_action = successor.getLegalActions(self.index) # 벽이아니어서 이동 가능한 곳에 관한 action들을 원소로 하는 list
        numOfaction = len(possible_action) # 가능한 action 개수, 최대 5개임(동서남북 stop)
        reverseaction = {"East": "West", "West": "East", "South": "North", "North": "South", "Stop":"Stop"} # 역방향 dictionary
        
        if dangerdist and mindangerdist<5: # 만약 적 유령이 거리 4이하로 쫓아오는 중일 때
            if numOfaction<3: # succesor상황에서 가능한 action이 2개일 때 (stop은 항상 가능하므로 사실상 다시왔던길로 돌아오는길만 가능, 즉 막힌길이라는 의미)
                features['noroad'] = 1 # 막힌 길 관련 feature 등록
            elif numOfaction == 3: # 가능한 action수가 3인경우
                for i in range(4): # 혹시 모르므로 4번의 다음 상황을 더 탐색해봄
                    if numOfaction < 3: # 탐색중 한번이라도 가능한 action수가 2개이하라면 
                        features['noroad'] = 1 # 막혔으므로 관련 feature 등록
                    else: # 가능한 action이 3개 이상인 경우
                        curreverse = reverseaction[action] # 역방향 list 
                        for act in possible_action: # 가능한 action
                            if act != 'Stop' and act != curreverse: # 만약 해당 action이 멈추는 거도 아니고 왔던길 되돌아오는거도 아니면
                                noriskaction = act # ghost에게 쫓기는 입장에서 도망치는 적절한 행동이므로 noriskaction 
                        successor = successor.generateSuccessor(self.index, noriskaction) # noriskaction을 취했을 때 다음상황
                        possible_action = successor.getLegalActions(self.index) # noriskaction을 취했을 때 다음상황에서 가능한 action
                        numOfaction = len(possible_action) # noriskaction을 취했을 때 다음상황에서 가능한 action수 
        
        
        return features
    
    def getWeights_Offensive(self, gameState, action): # offensive 관련 weight
        
        successor = self.getSuccessor(gameState, action)
        curpos = successor.getAgentState(self.index).getPosition()
        height = gameState.data.layout.height # 맵의 높이
        width = gameState.data.layout.width # 맵의 너비
        
        if self.red:
            half_width = width//2-1 # red면 왼쪽으로 한칸가까우므로 2로 나누고 1빼줌
        else:
            half_width = width//2 # 블루진영 고려하면 그냥 2로 나눔
            
        change_door = [] # 자기 홈영역 넘어가는 거리 리스트
        for i in range(height):
            if not gameState.getWalls()[half_width][i]: # 홈영역 높이중 벽이 없는 경우, 즉 넘어갈 수 있는 경우
                change_door.append((half_width, i)) # 리스트에 저장
        change_dist = []
        for i in change_door: #  i는 홈영역 넘어가는 곳 입구 위치
            change_dist.append(self.getMazeDistance(curpos, i)) # 현재위치와 넘어가는 곳 위치 거리 모두 저장
        
        minchangedist = min(change_dist) # 하프라인 입구까지 거리가 멀수록 risk커짐, 최소거리를 저장하고 weight에 사용 
        
        return {'numOffood': -100 , 'FoodDist': -4, 'ghostdist': 1, 'Run': -15,'DEAD': -1000,
                'Stop': -400, 'reverse': -50 ,'Risk': -minchangedist, 'numOfpowerpellet': -1000, 'powerdist': -8, 'noroad': -1000} # weight 등록
    
    def getFeatures_usual(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        curstate = successor.getAgentState(self.index)
        curpos = curstate.getPosition()
        
        features['onDefense'] = 1
        if curstate.isPacman: # 현재 pacman상태면 공격중이므로 
            features['onDefense'] = 0 # onDefense feature를 0으로 둠
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)] # 적 위치 리스트
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None] # 적들중 pacman이면서 위치가 있는 녀석들로 침입자 리스트 생성
        features['numInvaders'] = len(invaders) # 침입자들 수 feature로 저장
        if len(invaders) > 0: # 침입자가 존재하면
            dists = [self.getMazeDistance(curpos, a.getPosition()) for a in invaders] # 침입자와의 거리 리스트
            features['invaderDistance'] = min(dists) # 최소거리 feature로 저장

        if action == Directions.STOP: features['stop'] = 1 # action이 Stop인경우 관련 feature로 등록
        rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction] # game.configuration.direction, 역방향 딕셔너리값에 해당 행동 넣음, 즉 역방향 값이 나옴
        if action == rev: features['reverse'] = 1 # 만약 action이 역방향이면 관련 feature등록
        
        return features
    
    def getWeights_usual(self, gameState, action): # weight 등록
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}