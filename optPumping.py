# Functions.py --- 
# 
# Filename: Functions.py
# Description: 
# 
# Author:    Yu Lu
# Email:     yulu@utexas.edu
# Github:    https://github.com/SuperYuLu 
# 
# Created: Sun Sep 17 16:36:41 2017 (-0500)
# Version: 
# Last-Updated: Thu Sep 28 18:50:48 2017 (-0500)
#           By: superlu
#     Update #: 256
# 


#from Constant import *    
#from TransitionStrength import *
import numpy as np 
class optPumping:
    
    
    def __init__(self, Dline,  pumpPol1, pumpPol2):
        
        if Dline == 'D1':
            from TransitionStrength import TransStrengthD1 as TransStrength
            from TransitionStrength import DecayStrengthD1 as DecayStrength
        elif Dline == 'D2':
            from TransitionStrength import TransStrengthD2 as TransStrength
            from TransitionStrength import DecayStrengthD2 as DecayStrength
        else:
            print('Unavaliable D line transition !')
        # I don't think this is necessary
        #self.TransStrength = TransStrength
        #self.DecayStrength = DecayStrength

        
        # Initialize pump matrix 
        try:
            self.pumpMatrix1 = eval('TransStrength.' + pumpPol1) # select pumping matrix based on polarization
            self.pumpMatrix2 = eval('TransStrength.' + pumpPol2) # select pumping matrix based on polarization
        except AttributeError:
            print("Incorrect polorization name, please chose one of the following:\n\
            sigmaPlus, sigmaMinux, pi\n")

        # Initialize pump beam polorization
        self.pumpPol1 = pumpPol1 # Polorization for pumping beam F1 --> Excited states
        self.pumpPol2 = pumpPol2 # Polorization for pumping beam F2 --> Excited states

        # Initialize decay matrix
        self.decayMatrix = DecayStrength # 
        
        # Initialize polarization list
        self.pol = TransStrength.polarization

        # Initialize D line
        self.Dline = Dline
        
        # Number of excited hyperfine states F
        self.numEStates = len(DecayStrength.numSubStates)

        # Excited hyperfine states name
        self.eStates = TransStrength.eStates
        
        # Transition energy levels 
        self.pumpTransLevel = TransStrength.transition
        self.decayTransLevel = DecayStrength.transition
        
        # Initialize ground level population
        self.pop_Ground ={
            'F1': np.ones([1,3]) * 3./8,
            'F2': np.ones([1,5]) * 5./8
            }

        # Initialize excited level population
        self.pop_Excited = {}
        for s,n in zip(DecayStrength.eStates, DecayStrength.numSubStates):
            self.pop_Excited[s] = np.zeros([1, n])
        
        # Calculate overal factor for dipole matrix
        self.dipoleFactor = self.dipoleScaleFactor()

        # Calculate atom-light scattering rate
        
        
    def dipoleScaleFactor(self): 
        totTransElement  = 0 # For Li D2, should be 37393.75, use for unit test 
        for trans in self.decayMatrix.transition:
            for pol in self.decayMatrix.polarization:
                totTransElement = totTransElement + \
                                  eval('self.decayMatrix.' + pol + '.' + trans + '.sum()');
        from Constant import gamma 
        factor  = gamma / totTransElement
        return factor

    
    def vectorizeMatrix(self,mtx): # accumulate matrix columns to rows 
        return mtx.sum(axis = 1)

    
    def calGroundPop(self, popGround, popExcited, idx, I1, I2, dt):
        G1 = popGround['F1'][idx]
        G2 = popGround['F2'][idx]
        newG1 = np.zeros([1, len(G1[0])])
        newG2 = np.zeros([1, len(G2[0])])
        
        for es in self.eStates:
            print(popExcited[es][idx].shape)
            newG1 += -self.vectorizeMatrix(eval("self.pumpMatrix1.F1_D2_" + es)).T * G1 * I1\
                     + np.dot(popExcited[es][idx], eval("self.decayMatrix.sigmaPlus." + es + "_" + self.Dline + "_F1"))\
                     + np.dot(popExcited[es][idx], eval("self.decayMatrix.sigmaMinus." + es + "_" + self.Dline + "_F1"))\
                     + np.dot(popExcited[es][idx], eval("self.decayMatrix.pi." + es + "_" + self.Dline + "_F1"))
            newG2 += -self.vectorizeMatrix(eval("self.pumpMatrix1.F1_D2_" + es)).T * G2 * I2\
                     + np.dot(popExcited[es][idx], eval("self.decayMatrix.sigmaPlus." + es + "_" + self.Dline + "_F2"))\
                     + np.dot(popExcited[es][idx], eval("self.decayMatrix.sigmaMinus." + es + "_" + self.Dline + "_F2"))\
                     + np.dot(popExcited[es][idx], eval("self.decayMatrix.pi." + es + "_" + self.Dline + "_F2"))
        newG1 = G1 + newG1 * self.dipoleFactor * dt  
        newG2 = G2 + newG2 * self.dipoleFactor * dt
        pop['F1'] = newG1
        pop['F2'] = newG2
        return pop

    def calExcitedPop(self, popGround, popExcited, idx, I1, I2, dt):
        newE = {}
        for es in self.eStates: # loop thru excited states names
            newE[es] = np.zeros([1, len(popExcited[es][idx][0])])
        for p in self.pol:
            for gs,I, pumpMatrix in zip(['F1', 'F2'], [I1, I2], [self.pumpMatrix1, self.pumpMatrix2]):
                for es in self.eStates: # loop thru excited hyperfine states names 
                # 3.0 factor is to compensate repeating sum of polarization
                    newE[es] += np.dot(popGround[gs][idx], eval("pumpMatrix." + gs + "_" + self.Dline + "_" + es)) / 3.0 * I\
                            - self.vectorizeMatrix(eval("self.decayMatrix." + p + "." + es + "_" + self.Dline + "_" + gs)).T * popExcited[es][idx]
        for es in self.eStates:
            newE[es] = popExcited[es][idx] + newE[es][idx] * self.dipoleFactor * dt
        return newE
                
    
    
    def checkUniformity(self, popGround,  popExcited):
        
        return popGround['F1'].sum() + G2.sum() + sum([popExcited[str(x)].sum() for x in popExcited])
    