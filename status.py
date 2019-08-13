import io
import mmap
import glob
import re
import os
import sys
from pathlib import Path

# Hard-coded (see README) adjacency lists (al) for decision tree
adjacency = {0:set([1, 2]), 1:set([3,4,5]), 2:set([]), 3:set([]), 4:set([6,7,8]), 5:set([]), 6:set([9,10,11,12]), 7:set([]),8:set([]),9:set([]),10:set([13,15,17]),11:set([14,16,18]),12:set([]),13:set([21,22]),14:set([19,20]),15:set([]),16:set([]),17:set([]),18:set([]),19:set([]),20:set([24,26]),21:set([23,25]),22:set([]),23:set([29,30]),24:set([27,28]),25:set([]),26:set([]),27:set([]),28:set([32,34,36]),29:set([31,33,35]),30:set([]),31:set([]),32:set([]),33:set([]),34:set([]),35:set([]),36:set([])}

# Dictionary of search terms revelant for finding each status (i.e. {##: [['<SEARCH_TERM_1>','<PATH_TO_FILE_OR_FOLDER>'],['<SEARCH_TERM_N>','<PATH_TO_FILE_OR_FOLDER>']], ...})

search = {0: ['fldr','SadPoint',''],
        1:['word','SUCCESSFUL','SadPoint/TS_SadPoint.dat'],
        2:['word','FAILURE TO LOCATE STATIONARY POINT', 'SadPoint/TS_SadPoint.log'],
        3:['fldr','Hess_final','not Path(path).is_file()'],
        4:['fldr','Hess_final',''],
        5:['fldr','Hess_final', '', 'not Path(path).is_dir()'],
        6:['word','1 IMAGINARY FREQUENCY','Hess_final/TS_Hess.log'],
        7:['word','IMAGINARY FREQUENCY','Hess_final/TS_Hess.log','int(line.strip()[0])>=2'],
        8:['word','ABNORMALLY','Hess_final/TS_Hess.log'],
        9:['fldr','IRC_backward', '', 'not Path(path).is_dir()'],
        10:['fldr','IRC_backward',''],
        11:['fldr','IRC_forward',''],
        12:['fldr','IRC_forward', '', 'not Path(path).is_dir()'],
        13:['word',' NORMALLY','IRC_backward/TS_IRCb.log', 'nodeExists and (grep("STOPPING BECAUSE GRADIENT IS BELOW OPTTOL", "IRC_backward/TS_IRCb.log")=="")'],
        14:['word',' NORMALLY','IRC_forward/TS_IRCf.log','nodeExists and (grep("STOPPING BECAUSE GRADIENT IS BELOW OPTTOL", "IRC_forward/TS_IRCf.log")=="")'],
        15:['word','ABNORMALLY','IRC_backward/TS_IRCb.log','nodeExists and (grep("STOPPING BECAUSE GRADIENT IS BELOW OPTTOL", "IRC_backward/TS_IRCb.log")=="")'],
        16:['word','ABNORMALLY','IRC_forward/TS_IRCf.log','nodeExists and (grep("STOPPING BECAUSE GRADIENT IS BELOW OPTTOL", "IRC_forward/TS_IRCf.log")=="")'],
        17:['word','STOPPING BECAUSE GRADIENT IS BELOW OPTTOL','IRC_backward/TS_IRCb.log'],
        18:['word','STOPPING BECAUSE GRADIENT IS BELOW OPTTOL','IRC_forward/TS_IRCf.log'],
        19:['fldr','Opt_RHS','','not Path(path).is_dir()'],
        20:['fldr','Opt_RHS',''],
        21:['fldr','Opt_LHS',''],
        22:['fldr','Opt_LHS','','not Path(path).is_dir() '],
        23:['word','SUCCESSFUL','Opt_LHS/TS_OptLHS.dat','Path("/Opt_LHS/README").is_file()'],
        24:['word','SUCCESSFUL','Opt_RHS/TS_OptRHS.dat','Path("/Opt_RHS/README").is_file()'],
        25:['word','FAILURE TO LOCATE STATIONARY POINT','Opt_LHS/TS_OptLHS.log','not Path("/Opt_LHS/README").is_file()'],
        26:['word','FAILURE TO LOCATE STATIONARY POINT','Opt_RHS/TS_OptRHS.log','not Path("/Opt_RHS/README").is_file()'],
        27:['fldr','Hess_RHS','','not Path(path).is_dir()'],
        28:['fldr','Hess_RHS',''],
        29:['fldr','Hess_LHS',''],
        30:['fldr','Hess_LHS','','not Path(path).is_dir()'],
        31:['word','ABNORMALLY','Hess_LHS/TS_Hess.log'],
        32:['word','ABNORMALLY','Hess_RHS/TS_Hess.log'],
        33:['word','NORMALLY','Hess_LHS/TS_Hess.log','not "IMAGINARY" in line'],
        34:['word','NORMALLY','Hess_RHS/TS_Hess.log','not "IMAGINARY" in line'],
        35:['word','IMAGINARY FREQUENCY','Hess_LHS/TS_Hess.log'],
        36:['word','IMAGINARY FREQUENCY','Hess_RHS/TS_Hess.log']
        }

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


def dfs(graph, start, rxnPath, visited=None):
    if visited is None:
        visited = set()
    if evalNode(rxnPath,start):
        visited.add(start)
        for next in graph[start] - visited:
            dfs(graph, next, rxnPath, visited)
    return visited

def evalNode(rxnPath,node):
    # This function works closely with the 'search' dictionary
    searchType = search[node][0]
    searchTarget = search[node][1]
    searchFolder = search[node][2]
    if searchType is 'fldr':
        path = rxnPath+searchFolder+searchTarget
        try:
            matches = glob.glob(path)
            nodeExists = (len(matches)>=1)
        except:
            nodeExists = False
    elif searchType is 'word':
        path = rxnPath+searchFolder
        line = grep(searchTarget,path)
        nodeExists = (len(line)>=1)

    # Any final conditions that can still change the status
    if len(search[node]) > 3:
        for cond in search[node][3:]:
            try:
                if eval(cond):
                    nodeExists = True
                else:
                    nodeExists = False
            except:
                print('WARNING: Exception was found for conditions: ' + cond, file=sys.stderr)
                raise
    return nodeExists

def findStatus(rxn):
    # This function finds the status of job 'rxn'

    ## Reactions main directory
    #if './' not in rxn:
    #    rxnPath = './' + rxn + '/'
    #else:
    #    rxnPath = rxn + '/'

    status = []

    paths = dfs(adjacency,0,rxn)
    for value in paths:
        if not adjacency[value]:
            status.append(value)

    # If leaf nodes DNE, raise error
    if status == []:
        raise ValueError("No Leaf Node Found")

    return status
