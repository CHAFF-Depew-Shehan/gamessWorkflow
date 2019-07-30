import setupTSinputs as create
import os
from math import log10, floor
import glob

def round_sig(x, sig=2):
    return round(x, sig-int(floor(log10(abs(x))))-1)

def actions(rxn, actionTextFile, actionNodes):
    # Read actions.txt for specified node and return all the necessary inputs for the createInputFile.py functions
    for node in actionNodes:
        #print('NODE: ' + str(node))
        nodeInfo = []
        with open(actionTextFile, "r") as atf:
            line = atf.readline()
            while ('$NODE='+str(node)) not in line:
                line = atf.readline()
            while '$END' not in line:
                nodeInfo.append(line.rstrip('\n'))
                line = atf.readline()

        nodeInfo, N = replaceFileNumber(rxn, nodeInfo)
        #print(nodeInfo)
        recentInputFile = evalSectionsIn(rxn,nodeInfo,N)

    return recentInputFile #,line

def replaceFileNumber(rxn, nodeInfo):
    pathNum = None
    for i, entry in enumerate(nodeInfo):
        if '_N' in entry:
            #print('FOUND "_N"!!!!!!!!!!!!!!!!!')
            splitEntry = entry.split('=')
            path = rxn + splitEntry[-1]
            path = path.replace('_N','*')
            pathNum = len(glob.glob(path)) + 1
            #print('Pathnum: ')
            #print(pathNum)
            nodeInfo[i] = nodeInfo[i].replace('_N','_'+str(pathNum))

    return nodeInfo, pathNum

def evalSectionsIn(rxn, nodeInfo, N):
    #print('N VALUE IS:')
    #print(N)
    for i, info in enumerate(nodeInfo):
        if 'DESCRIPTION' in info:
            description = info
            #print(description)
        elif 'SECTION' in info:
            count = 1 + i
            section = info
            #print(section)
            beginSection = nodeInfo.index(section) + 1
            #print('BeginSection: ' + str(beginSection))
            endSection = nodeInfo[beginSection:].index('') + beginSection
            #print('EndSection: ' + str(endSection))
            variables = nodeInfo[beginSection:endSection]

            # Change any strings into boolean or nonetypes if necesary
            for j, arg in enumerate(variables):
                if '=' in arg:
                    variables[j] = variables[j].split('=')[-1]
                    if ('None' in arg) or ('False' in arg) or ('True' in arg):
                        variables[j] = eval(variables[j])
                    if ('(' in arg) and (')' in arg):
                        #print(arg)
                        #print(N)
                        variables[j] = str(round_sig(eval(variables[j])))
            # begin searching for specific sections

            if 'CMD' in section:
                # NOTE: This section doesn't seem to be working
                oldPath = os.getcwd()
                os.chdir(rxn)
                for command in variables:
                    os.system(command)
                os.chdir(oldPath)
            elif 'HEADER' in section:
                if len(variables) != 8:
                    raise(IndexError)
                prevInpFile = rxn + variables[0]
                inpFile = rxn + variables[1]
                runtyp = variables[2]
                parameters = variables[3]
                opttolVal = variables[4]
                nstepVal = variables[5]
                npointVal = variables[6]
                maxitVal = variables[7]

                if parameters:
                    create.header(prevInpFile,inpFile,runtyp,parameters,opttol=opttolVal,nstep=nstepVal,npoint=npointVal,maxit=maxitVal)
                elif not parameters:
                    create.header(prevInpFile,inpFile,runtyp,opttol=opttolVal,nstep=nstepVal,npoint=npointVal,maxit=maxitVal)

            elif 'GEOM' in section:
                if len(variables) != 2:
                    raise(IndexError)
                prevGeomFile = rxn + variables[0]
                restart = variables[1]

                create.geom(prevGeomFile,inpFile,restart)

            elif 'IRC' in section:
                if len(variables) != 1:
                    raise(IndexError)
                prevIRCDatFile = rxn + variables[0]

                create.IRC(prevIRCDatFile,inpFile,npoint=npointVal)

            elif 'VEC' in section:
                if len(variables) != 2:
                    raise(IndexError)
                prevGeomFile = rxn + variables[0]
                restart = variables[1]

                create.vec(prevGeomFile,inpFile,restart)

            elif 'HESS' in section:
                if len(variables) != 1:
                    raise(IndexError)
                prevHessFile = rxn + variables[0]

                create.hess(prevHessFile,inpFile)

            elif 'GRAD' in section:
                if len(variables) != 1:
                    raise(IndexError)
                prevGradFile = rxn + variables[0]

                create.grad(prevGradFile,inpFile)

            elif 'VIB' in section:
                if len(variables) != 1:
                    raise(IndexError)
                prevVibFile = rxn + variables[0]
                if '.rst' not in prevVibFile:
                    raise(ValueError)

                create.vib(prevVibFile,inpFile)
    return inpFile

#actions('../R00/','actions.txt',[7])





