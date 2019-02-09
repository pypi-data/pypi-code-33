import gym
from gym import error, spaces, utils
from gym.utils import seeding
import pandas as pd
import numpy as np
import os 
import json

'''
This environment is identical to base model, but with the addition
of penalising notifications in the cache on each standby action 
(in calcRewards) to encourage the agent to use the cache sparingly
and only when necessary.

Also penalises notifications which are cached more than 5 times.

To investigate: agent might learn to always cache first, then deliver,
simply because there is no 'bad' reward for it.. yet!

ToDo: Calculate the metrics for showing at the end of each episode (callable method)

ToDo: Each day as an episode.. for online training. Separate environment!
'''
class PushEnv1(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # ------------ load data ------------------#
        self.loaded_notifications = pd.read_csv(dir_path+'/notifications.csv' )
        # Add 'cached' identifier
        self.loaded_notifications['cached'] = False
        self.loaded_notifications['numCaches'] = 0
        # Rename index column
        self.loaded_notifications = self.loaded_notifications.rename(columns={'Unnamed: 0': 'nIndex'})
        # Drop superflous index column
        self.loaded_notifications = self.loaded_notifications.drop(['index'], axis=1)
        # Append cache column to notifications 
        self.eNotifications = np.load(dir_path+'/e_notifications.npy')
        self.eContexts = np.load(dir_path+'/e_contexts.npy')
        self.cColumns = np.load(dir_path+'/contextColumns.npy')
        
        # append columns
        self.loaded_notifications['action_context'] = ''
        
        # ----------- env vars init ----------------#
        self.shownList = []
        self.dismissedList = []
        self.cachedList = []
        self.d = False
        self.i = 0
        self.cachedI = -1 
        self.epoch = self.loaded_notifications.iloc[[0]].posted.values[0]
        
        self.actions = ['show', 'dismiss', 'cache', 'check-cache', 'standby']
        self.actionsT1 = [0, 1, 2]
        self.actionsT2 = [3, 4]
        self.actionsT3 = [4]
        self.authActions = self.actionsT1
        
        # ------------- state vars init -------------#
        self.notification = np.zeros(self.eNotifications.shape[1])
        self.context = np.zeros(self.eContexts.shape[1])
        self.recentDismissed = np.zeros(self.eNotifications.shape[1])
        self.numDismissed = 0
        self.recentShown = np.zeros(self.eNotifications.shape[1])
        self.numShown = 0
        self.recentCached = np.zeros(self.eNotifications.shape[1])
        self.numCached = 0
        
        #------------- env global vars ---------------#
        self.action_space = spaces.Discrete(len(self.actions))
        # Note: This will have to be dynamic depending on type of states
        # selected. E.g. descriptive state of lists etc.
        # Also, have to scale and normalize(?) the observation space
        # notification embeddings
        self.observation_space = spaces.Box(low=0, high=1, shape=(1, len(self.buildObservation('')[0])), dtype='float32' )
        
    def buildObservation(self, obsType):
        # Build the observation and determine which actions are possible
        # return observation, actionIndices
        obs = 0
        actions = []
        
        if obsType == 'recentList':
            obs = np.concatenate([self.notification, self.context, self.recentDismissed, np.array([self.numDismissed]), 
                                   self.recentShown, np.array([self.numShown]), self.recentCached, np.array([self.numCached])])
        else: 
            if np.all(self.notification == np.zeros(self.eNotifications.shape[1])) and len(self.cachedList) == 0:
                # no notification and cache empty
                actions = self.actionsT3
            elif np.all(self.notification == np.zeros(self.eNotifications.shape[1])) and len(self.cachedList) > 0:
                actions = self.actionsT2
            else:
                actions = self.actionsT1
                
            obs = np.concatenate([self.notification, self.context, np.array([self.numDismissed]), 
                                   np.array([self.numShown]), np.array([self.numCached])])
        return obs, actions
    
    
    def calculateEngagementRewards(self, lastEpoch, currentEpoch):
        reward = 0
        # Get all notifications in show list with removal time between lastEpoch and currentEpoch
        if len(self.shownList) > 0:
            tmp = self.restoreNotification(self.shownList)
            tmp = tmp[(tmp.removed > lastEpoch) & (tmp.removed <= currentEpoch)]
            correct = len(tmp[(tmp.action == True) & (tmp.cached == False)])
            incorrect = len(tmp[(tmp.action == False) & (tmp.cached == False)])
            
            reward += ((correct * 5) + (incorrect * -5))
            
        # Not exactly reproducable in real world context.. assumption!
        if len(self.dismissedList) > 0:
            tmp = self.restoreNotification(self.dismissedList)
            tmp = tmp[(tmp.removed > lastEpoch) & (tmp.removed <= currentEpoch)]
            correct = len(tmp[(tmp.action == False) & (tmp.cached == False)])
            incorrect = len(tmp[(tmp.action == True) & (tmp.cached == False)])
            
            reward += ((correct * 5) + (incorrect * -5))
        
        
        
        # Unique to this env!
        reward = reward - (len(self.cachedList)*0.2)
    
        # remove notifications with cached == true (these have different contexts so action not reliable!)
        # if action == true, +5... if action == false, -10
        
        # To simuluate reality - can only use 'shown' as no engagement with dismissed in-real time?
        # Unless implement the swipe system!
        # Get all notifications in the dismiss list with removal time between lastEpoch and currentEpoch
        # remove notifications with cached == true (these have different contexts so action not reliable!)
        # if action == false, +5.. if action == true, -5
        
        return reward
    
    def restoreNotification(self, array):
        return pd.DataFrame(array, columns=self.notifications.columns)
      
    def calculateImmediateRewards(self, action):
        if action == 'cache':
            if self.cachedI > -1:
                # notification coming from the cache.
                if self.notifications.loc[self.cachedI, 'numCaches'] > 15:
                    return (self.notifications.loc[self.cachedI, 'numCaches'] * -0.2)
        if action == 'check-cache':
            if len(self.cachedList) == 0:
                return -1
        if action == 'standby': 
            if len(self.cachedList) > 0:
                return -1
            
        # if notification from cache, reset
        self.cachedI = -1
        
        return 1
        
    def executeAction(self, actionIndex):
        # Possibly return short term reward for common sense actions
        action = self.actions[actionIndex]
        reward = 0
        if action == 'show':
            # Remove notification from current
            self.notification = np.zeros(self.eNotifications.shape[1])
            # add notification to the show list
            # - check if has been cached, if so, add context now shown
            # - append to shown list using nIndex not self.i (as now different)
            if self.cachedI > -1:
                tmp = self.notifications.iloc[[self.cachedI]]
                actionContext = []
                for col in self.cColumns:
                    actionContext.append(str(self.notifications.iloc[self.cachedI][col]))
                self.notifications.loc[self.cachedI, ('action_context') ] = json.dumps(actionContext)
                self.shownList.append(self.notifications.iloc[self.cachedI].tolist())
            else:
                self.shownList.append(self.notifications.iloc[self.i].tolist())
            # Update show count
            self.numShown = len(self.shownList)
            
        if action == 'dismiss':
            # Remove notification from current
            self.notification = np.zeros(self.eNotifications.shape[1])
            # add notification to the dismiss list
            # - check if has been cached, if so, add context now shown
            # - append to shown list using nIndex not self.i (as now different)
            if self.cachedI > -1:
                tmp = self.notifications.iloc[[self.cachedI]]
                actionContext = []
                for col in self.cColumns:
                    actionContext.append(str(self.notifications.iloc[self.cachedI][col]))
                self.notifications.loc[self.cachedI, ('action_context') ] = json.dumps(actionContext)
                self.dismissedList.append(self.notifications.iloc[self.cachedI].tolist())
            else:
                self.dismissedList.append(self.notifications.iloc[self.i].tolist())
            # Update dismiss count
            self.numDismissed = len(self.dismissedList)
            
        if action == 'cache':
            # Remove notification from current
            self.notification = np.zeros(self.eNotifications.shape[1])
            # add notification to the cache list
            # - check if has been cached, if so, add context now shown
            # - append to shown list using nIndex not self.i (as now different)
            if self.cachedI > -1:
                self.notifications.loc[self.cachedI, 'numCaches'] = self.notifications.loc[self.cachedI]['numCaches'] + 1
                actionContext = []
                for col in self.cColumns:
                    actionContext.append(str(self.notifications.iloc[self.cachedI][col]))
                self.notifications.loc[self.cachedI, ('action_context') ] = json.dumps(actionContext)
                self.cachedList.append(self.notifications.iloc[self.cachedI].tolist())
            else:
                self.notifications.loc[self.i, 'cached'] = True
                self.notifications.loc[self.i, 'numCaches'] = 1
                actionContext = []
                for col in self.cColumns:
                    actionContext.append(str(self.notifications.iloc[self.cachedI][col]))
                self.notifications.loc[self.i, ('action_context') ] = json.dumps(actionContext)
                self.cachedList.append(self.notifications.iloc[self.i].tolist())
            # Update cache count
            self.numCached = len(self.cachedList)
            
        if action == 'check-cache':
            # Take notification from bottom of cache (this case, top of list.. as appending) and set as current
            tmp = self.restoreNotification([self.cachedList.pop(0)])
            self.cachedI = tmp.nIndex.values[0]
            self.notification = self.eNotifications[self.cachedI]
            # (note: this means extracting notification part and concatenating with new context)
            # Decrement cache count      
            self.numCached = len(self.cachedList)
            
        if action == 'standby':
            # temp save last epoch
            lastEpoch = self.epoch
            # add to i 
            self.i += 1
            self.cachedI = -1
            if self.i < len(self.notifications):
                # set epoch
                self.epoch = self.notifications.iloc[[self.i]].posted.values[0]
                # calc rewards for all engagements between last epoch and epoch
                reward += self.calculateEngagementRewards(lastEpoch, self.epoch)
                # update current notification and context
                self.notification = self.eNotifications[self.i]
                self.context = self.eContexts[self.i]
            else:
                self.d = True
        
        
        reward += self.calculateImmediateRewards(action)
        
        return reward
        
    def step(self, action):
        reward = 0
        
        if action in self.authActions:
            # Execute action & retrieve reward
            reward = self.executeAction(action)

            # Build next observation 
            self.state, self.authActions = self.buildObservation('')
            
        else:
            print('Unauthorised action chosen.')
            
        
        return self.state, reward, self.d, self.authActions
        
        
    def reset(self):
        # returns initial state and possible actions
        
        self.i = 0
        self.cachedI = -1
        self.d = False
        # Copy loaded_notifications, as adding columns to notifications
        self.notifications = self.loaded_notifications.copy()
        self.notifications['cached'] = False
        self.epoch = self.notifications.iloc[[self.i]].posted.values[0]
        self.notification = self.eNotifications[self.i]
        self.context = self.eContexts[self.i]
        self.recentDismissed = np.zeros(self.eNotifications.shape[1])
        self.numDismissed = 0
        self.dismissedList = []
        self.recentShown = np.zeros(self.eNotifications.shape[1])
        self.numShown = 0
        self.shownList = []
        self.recentCached = np.zeros(self.eNotifications.shape[1])
        self.numCached = 0
        self.cachedList = []
        
        self.state, self.authActions = self.buildObservation('')
        
        return self.state, self.authActions
        
        
    def render(self, mode='human', close=False):
        print('do render push')