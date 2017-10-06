# main.py --- 
# 
# Filename: main.py
# Description: 
# 
# Author:    Yu Lu
# Email:     yulu@utexas.edu
# Github:    https://github.com/SuperYuLu 
# 
# Created: Wed Sep 20 15:34:21 2017 (-0500)
# Version: 
# Last-Updated: Thu Oct  5 19:25:54 2017 (-0500)
#           By: superlu
#     Update #: 238
# 


from optPumping import optPumping
from Constant import input
import numpy as np
from plot import plotPop

def main(Dline,
         excited_hpf_state,
         I1,
         I2,
         polorization1,
         polorization2,
         totalTime,
         dt,
         plot = False):

    p = optPumping(Dline, excited_hpf_state, polorization1, polorization2)

    # Initialization of population dictionary 
    popG = {} # Ground states population dictionary, dic of list of 2d array
    popE = {} # Excited states population dictionary, dic of list of 2d array
    numSteps = int(totalTime / dt)
    
    for i in range(0, numSteps):
        if i == 0:
            # Initial states
            popG['F1'] = [p.pop_Ground['F1']]
            popG['F2'] = [p.pop_Ground['F2']]
            for f in p.eStates:
                popE[f] = [p.pop_Excited[f]]
        else:
            newPopG = p.calGroundPop(popG, popE, i-1, I1, I2, dt)
            newPopE = p.calExcitedPop(popG, popE, i-1, I1, I2, dt)
            for f in p.eStates:
                popE[f].append(newPopE[f])
            popG['F1'].append(newPopG['F1'])
            popG['F2'].append(newPopG['F2'])
            unitCheck = p.checkUniformity(newPopG, newPopE)
            if abs( unitCheck- 1) > 0.1:
                print("Total population: ", unitCheck, " off too much, cycle: ", i)
                return 0 
    clock = np.linspace(0, totalTime, numSteps) * 1e9

    print(
        '--------------------------------------------------\n',\
        'F = 1, m = -1, pop =', popG['F1'][-1][0][0], '\n',\
        'F = 1, m = -0, pop =', popG['F1'][-1][0][1], '\n',\
        'F = 1, m = 1, pop =', popG['F1'][-1][0][2], '\n',\
        'F = 2, m = -2, pop =', popG['F2'][-1][0][0], '\n',\
        'F = 2, m = -1, pop =', popG['F2'][-1][0][1], '\n',\
        'F = 2, m = 0, pop =', popG['F2'][-1][0][2], '\n',\
        'F = 2, m = 1, pop =', popG['F2'][-1][0][3], '\n',\
        'F = 2, m = 2, pop =', popG['F2'][-1][0][4], '\n')
    
    #print("Total population: ", p.checkUniformity(G1,G2,E0, E1, E2, E3) )
    if plot:
        params = {
            "clock": clock,
            "Dline": Dline,
            "eStates": p.eStates,
            "polorization1": polorization1,
            "polorization2": polorization2,
            "I1": I1,
            "I2": I2,
            "popG": popG,
            "popE": popE
            }
        
        plotPop(**params)
       
if __name__ == "__main__":
    main(**input)
    
        
        
