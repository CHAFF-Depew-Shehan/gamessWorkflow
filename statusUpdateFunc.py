import io
import mmap
import glob
import variables
import re
import os
import sys
from pathlib import Path

def grep(pattern, file_path):
    # Used to search for a specific string pattern in a given file
    try:
        with open(file_path, "r") as f:
            line = f.readline()
            while pattern not in line:
                line = f.readline()
                if line == '':
                    break
    except FileNotFoundError:
        line = ''

    return line

    #with io.open(file_path, "r", encoding="utf-8") as f:
    #    return re.search(pattern, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ))

def dfs(graph, start, rxnPath, visited=None,recent=None):
#   debug = open("debug.out","a+")
    if visited is None:
        visited = set()
#        recent = set()
    if evalNode(rxnPath,start):
        visited.add(start)
#       print(start, file=debug)

#    if not graph[start]:
#        #print('FOUND STATUS')
#        recent.add(start)

        for next in graph[start] - visited:
            dfs(graph, next, rxnPath, visited, recent)
#   print('Status: ' + str(visited), file=debug)
#   debug.close()
    return visited

def evalNode(rxnPath,node):
    # This function works closely with the 'search' dictionary in variables.py
    search = variables.search[node]
#   debug = open("debug.out","a+")
#   print(search, file=debug)
    searchType = search[0]
    searchTarget = search[1]
    searchFolder = search[2]
    #if '_N' in searchFolder:
    #    variables.SP_HF_count[searchFolder] = len(matches)
    if searchType is 'fldr':
#       print("Searching path (folder):", file=debug)
#       print(rxnPath+searchFolder+searchTarget, file=debug)
        path = rxnPath+searchFolder+searchTarget
        try:
            matches = glob.glob(path)
            nodeExists = (len(matches)>=1)
            if '*' in searchTarget:
                variables.SP_HF_count[searchFolder] = len(matches)
        except:
            nodeExists = False
    elif searchType is 'word':
        path = rxnPath+searchFolder
#       print("Searching path (word):", file=debug)
#       print(rxnPath+searchFolder, file=debug)
        line = grep(searchTarget,path)
        nodeExists = (len(line)>=1)

    # Any final conditions that can still change the status
    if len(search) > 3:
        for cond in search[3:]:
#           print(cond, file=debug)
            try:
                if eval(cond):
                    nodeExists = True
                else:
                    nodeExists = False
            except:
#               print('WARNING: Exception was found for conditions: ' + cond, file=debug)
                nodeExists = False
#   print('Search Target: ' + searchTarget + ' is ' + str(nodeExists), file=debug)
#   debug.close()

#    if '*' in path:
#            variables.counts[path] = len(matches)
#
#    if len(search) > 3:
#        searchCond = []
#        for cond in search[3:-1]:
#            searchCond.append(cond)
#    else:
#        searchCond = True
#
#    if search[0] is 'fldr':
#        glob.glob(rxnPath + search[2] + search
#
#    elif search[0] is 'word':
    return nodeExists





def findStatus(rxn, side=False):
    # This function finds the status of job 'rxn'

    ## Reactions main directory
    #if './' not in rxn:
    #    rxnPath = './' + rxn + '/'
    #else:
    #    rxnPath = rxn + '/'

    status = []
    #status_rhs = None
    #status_lhs = None
    #status_init = None

#   debug = open("debug.out","a+")
    if side:
        #print('RIGHT HAND SIDE:', file=debug)
        rhs = dfs(variables.al_rhs,6,rxn)
        #print(rhs, file=debug)

        #print('LEFT HAND SIDE:', file=debug)
        lhs = dfs(variables.al_lhs,6,rxn)
        #print(lhs, file=debug)
        for value in rhs:
            if not variables.al_rhs[value]:
                status.append(value)
        for value in lhs:
            if not variables.al_lhs[value]:
                status.append(value)
        #status = [status_lhs, status_rhs]

        # If leaf nodes DNE, raise error
        #if status_rhs == None or status_lhs==None:
        #    raise ValueError("No Leaf Node Found")

    else:
        init = dfs(variables.al_init,0,rxn)
        for value in init:
            if not variables.al_init[value]:
                status.append(value)
        #status = [status_init]

        ## If leaf nodes DNE, raise error
        #if status_init == None:
        #    raise ValueError("No Leaf Node Found")

#   debug.close()

    #if not status:
    # exit code, no next steps
    return status
#rxn = '../R4/'
#status = findStatus(rxn,side=True)


    # "N" dictionary keeps track of number of similarly named folders within given node
    #N_dict = {2: 0, 5:0, 6:0, 9:0, 10:0, 17:0}



    # Recursively find using provided adjacency list







    # Dictionary entries follow: {##: [['<SEARCH_TERM_1>','<PATH_TO_FILE_OR_FOLDER>'],['<SEARCH_TERM_N>','<PATH_TO_FILE_OR_FOLDER>']], ...}
    #dictionarySearchTerms = { 1: ['SadPoint*','/'], 2: ['SUCCESSFUL','/SadPoint/TS_SadPoint.dat'], 3: []}



    # DFS Search through all nodes for current input

    # create 'code' for next input




#with open('testInputHeader.inp','w') as newInputFile:
#    getHeader('./R56/Hess_init/R56.inp',newInputFile,'OPT_LHS')







######### Hess Input ##########
######### SadPoint Input ##########
######### IRC Input ##########

######### EXAMPLES ##########
#
#with open('testInputSadPoint.inp','w') as newInputFile:
#    dirPath = "/home/rcf-proj2/ddd2/ZhangThynellTS/R8/"
#    runType = "SadPoint"  # Pulling data from a SadPoint .dat file
#    restart = False       # Next run is not a restart
#    getPrevGeom(dirPath+"SadPoint/TS_SadPoint.dat", newInputFile, runType, restart)
#    getPrevVec(dirPath+"SadPoint/TS_SadPoint.dat", newInputFile, runType, restart)
#
#with open('testInputIRC.inp','w') as newInputFile:
#    dirPath = "/home/rcf-proj2/ddd2/ZhangThynellTS/R8/"
#    runType = "IRC"  # Pulling data from a IRC .dat file
#    restart = True   # Next run is a restart
#    # Note: the "TS_SadPoint.dat" name below was my mistake in naming the file when I ran it originally
#    getPrevGeom(dirPath+"IRC_forward/TS_SadPoint.dat", newInputFile, runType, restart)
#    getPrevVec(dirPath+"IRC_forward/TS_SadPoint.dat", newInputFile, runType, restart)
#    getPrevHess(dirPath+"Hess_final/TS_Hess.dat", newInputFile)
#    getPrevIRC(dirPath+"IRC_forward/TS_SadPoint.dat", newInputFile)


#for i in list(range(0,31)):
#    if i in [2,3]:
#        continue
#    print('Node: ' + str(i))
#    print(evalNode('../R38/',i))





