def getPrevGeom(prevGeomDatFile, newInputFile, prevRunType, restart):
    # The prevGeomDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing.
    # The only types of runs which would modify a geometry would be stationary
    # point searches (saddle points and geometry optimizations) or intrinsic
    # reaction coordinate runs. Thus, these are the only .dat files considered
    # as input.
    with open(prevGeomDatFile,"r") as datFile:
        # Read to appropriate section containing $DATA info
        if (prevRunType == "SadPoint" or prevRunType == "Opt") and restart == False:
            try:
                readToString(datFile, "----- RESULTS")
            except EOFError:
                print("No results section found in file " + prevGeomDatFile)
                raise
            # Read 4 lines before geometry info
            for i in range(4):
                datFile.readline()
        elif prevRunType == "IRC":
            # Need to find the last IRC restart information section in the file
            lastPos = None
            while True:
                try:
                    readToString(datFile, " * * * IRC RESTART")
                    lastPos = datFile.tell()  # Get file object's current position
                except EOFError:
                    # Now we've reached the end of the file
                    break
            if lastPos == None:
                # An IRC restart information section was never found
                print("No restart information found in file " + prevGeomDatFile)
                raise EOFError
            else:
                # Set file object position to last IRC restart section
                datFile.seek(lastPos)
                # Read 5 lines before geometry info
                for i in range(5):
                    datFile.readline()
        elif prevRunType == "Opt" and restart == True:
            # Find step which corresponds to minimum energy and move to that step
            readOptMinEnergyStep(datFile)
            for i in range(3):
                datFile.readline()

        # Read atom position data
        while True:
            atomLine = datFile.readline().strip()
            if atomLine[0] == '-' or atomLine[0] == '$':
                break
            elif atomLine == '':
                print("End of file found while reading atom coordinates")
                raise EOFError
            a = atomLine.split()
            if len(a) != 5:
                print("Error reading atom coordinates. Read the following:")
                print(a)
                raise ValueError
            newInputFile.write("{0}  {1}  {2[0]:>13}  {2[1]:>13}  {2[2]:>13}\n".format(a[0],a[1][0],a[2:5]))
        newInputFile.write(" $END\n")
    return


def getPrevVec(prevVecDatFile, newInputFile, prevRunType, restart):
    # The prevVecDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing.
    # The only types of runs which would modify orbitals would be stationary
    # point searches (saddle points and geometry optimizations) or intrinsic
    # reaction coordinate runs. Thus, these are the only .dat files considered
    # as input.
    with open(prevVecDatFile,"r") as datFile:
        # Read to appropriate section containing $DATA info
        if (prevRunType == "SadPoint" or prevRunType == "Opt") and restart == False:
            try:
                readToString(datFile, "----- RESULTS")
            except EOFError:
                print("No results section found in file " + prevVecDatFile)
                raise
        elif prevRunType == "IRC":
            # This is different than geometry case because the $VEC section is
            # actually above the  "* * * IRC RESTART" line at the end. The real
            # issue here is that we want to make sure the $VEC and $DATA groups
            # that are being copied correspond to the same IRC point.
            # First find the last orbitals section in the file
            lastPos = None
            while True:
                try:
                    line = readToString(datFile, "ORBITALS FROM IRC POINT")
                    lastPos = datFile.tell()  # Get file object's current position
                except EOFError:
                    # Now we've reached the end of the file
                    break
            if lastPos == None:
                # No orbitals were ever found
                print("No orbitals ($VEC group) found in file " + prevVecDatFile)
                raise EOFError
            else:
                # Get current IRC point to compare with what is found for $DATA
                IRCpoint = int(line.strip().split()[4][:-1])
                # Set file object position to last orbitals section
                datFile.seek(lastPos)
                try:
                    line = readToString(datFile, "NEXTPT")
                    if IRCpoint+1 != int(line.strip().split()[-1]):
                        raise ValueError("Inconsistent orbitals and IRC data")
                except EOFError:
                    print("IRC restart group not generated for last orbitals")
                # Set file object position to last orbitals section again
                datFile.seek(lastPos)
        elif prevRunType == "Opt" and restart == True:
            # Find step which corresponds to minimum energy and move to that step
            readOptMinEnergyStep(datFile)

        try:
            line = readToString(datFile, "$VEC")
        except EOFError:
            print("Couldn't find correct $VEC group in file " + prevVecDatFile)
            raise
        while "$END" not in line:
            if line == '':
                print("Error: $VEC group cut off in file " + prevVecDatFile)
                raise EOFError
            else:
                newInputFile.write(line)
                line = datFile.readline()
        newInputFile.write(line)
    return


def getPrevGrad(prevGradDatFile, newInputFile, prevRunType, restart=True):
    # The prevGradDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing.
    # The only types of runs which would require a $GRAD group are stationary
    # point runs. Since we are only restarting optimization runs here (we
    # assume SadPoint runs have converged already), the restart flag is assumed
    # to be True.
    with open(prevGradDatFile,"r") as datFile:
        if prevRunType != "Opt" or not restart:
            raise ValueError("Only geometry optimization restarts for getPrevGrad()")
        # Find step which corresponds to minimum energy and move to that step
        readOptMinEnergyStep(datFile)
        # Read to $GRAD group (error checking done in function above)
        line = readToString(datFile, "$GRAD")
        # Read to $END and write to file
        while "$END" not in line:
            if line == '':
                print("Error: $GRAD group cut off in file " + prevHessDatFile)
                raise EOFError
            else:
                newInputFile.write(line)
                line = datFile.readline()
        newInputFile.write(line)
    return


def getPrevHess(prevHessDatFile, newInputFile):
    # The prevHessDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing. Note that this should only read from a RUNTYP=HESSIAN
    # dat file.

    # NOTE: Need to incorporate $HESS group for IRC restart
    with open(prevHessDatFile,"r") as datFile:
        try:
            line = readToString(datFile, "$HESS")
        except EOFError:
            print("No $HESS group found in file " + prevHessDatFile)
            raise
        while "$END" not in line:
            if line == '':
                print("Error: $HESS group cut off in file " + prevHessDatFile)
                raise EOFError
            else:
                newInputFile.write(line)
                line = datFile.readline()
        newInputFile.write(line)
    return


def getPrevIRC(prevIRCDatFile, newInputFile):
    # The prevHessDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing. Note that this should only read from a RUNTYP=IRC dat file.
    with open(prevIRCDatFile,"r") as datFile:
        # Need to find the last IRC restart information section in the file
        lastPos = None
        while True:
            try:
                readToString(datFile, " * * * IRC RESTART")
                lastPos = datFile.tell()  # Get file object's current position
            except EOFError:
                # Now we've reached the end of the file
                break
        if lastPos == None:
            # An IRC restart information section was never found
            print("No restart information found in file " + prevIRCDatFile)
            raise EOFError
        else:
            # Set file object position to last IRC restart section
            datFile.seek(lastPos)
        # Now read to beginning of $IRC group
        # Note that the string "$IRC" is used in other parts of the dat file,
        # so search for a more unique string indicating beginning of $IRC group
        try:
            line = readToString(datFile, " $IRC   PACE")
        except EOFError:
            print("Couldn't find correct $IRC group in file " + prevIRCDatFile)
            raise
        while "$END" not in line:
            if line == '':
                print("Error: $IRC group cut off in file " + prevIRCDatFile)
                raise EOFError
            else:
                newInputFile.write(line)
                line = datFile.readline()
        newInputFile.write(line)
    return


def readOptMinEnergyStep(datFileOpt)
    # For a geometry optimization run, accepts a dat file object as input and
    # reads to the step corresponding to the minimum energy. It then rewinds
    # the file so that the file object's position is immediately after the line
    # which begins "-------------------- DATA FROM NSERCH="
    # That is, a subsequent readline() would read the line which begins
    # " COORDINATES OF SYMMETRY UNIQUE ATOMS"
    # Currently, nothing is done with NSERCH step but it could be returned
    minPos = None
    while True:
        try:
            # Read to next step
            targetString = "-------------------- DATA FROM NSERCH="
            line = readToString(datFileOpt, targetString)
            tempPos = datFileOpt.tell()
            tempStep = int(line.strip().split()[4])
            # Read to this step's $GRAD group to get energy
            line = readToString(datFileOpt, "$GRAD")
            # Next line should contain the energy
            line = datFileOpt.readline()
            if line[0:2] != "E=":
                raise ValueError("Energy line not read correctly")
            tempEnergy = float(line.strip().split()[1])
            if tempEnergy < minEnergy:
                minEnergy = tempEnergy
                minPos = tempPos
                minStep = tempStep
        except EOFError:
            # Now we've reached the end of the file
            break
        except ValueError:
            raise

    if minPos == None:
        # No data was ever found
        print("No data found in geometry optimization dat file")
        raise EOFError
    else:
        # Return file object position to min energy step
        datFileOpt.seek(minPos)
        return minEnergy


def readToString(fileObject, targetString):
    # Accept a file object as input and read the file line by line until the
    # target string is found. The line containing the target string is then
    # returned. If the target string is not found, the EOFError exception is
    # raised to indicate the end of file was reached before finding the string.
    while True:
        line = fileObject.readline()
        if targetString in line:
            return line
        elif line == '':
            raise EOFError
    return


######## EXAMPLES ##########

# General notes: An IRC restart (status=4) does not require a $VEC but does require a $HESS. Starting an Opt from IRC will use the geom and $VEC, which will be properly handled by these functions, but the IRC run will not put out a $GRAD.

with open('testInputSadPoint.inp','w') as newInputFile:
    dirPath = "/home/rcf-proj2/ddd2/ZhangThynellTS/R8/"
    prevRunType = "SadPoint"  # Pulling data from a SadPoint .dat file
    restart = False       # Next run is not a restart
    getPrevGeom(dirPath+"SadPoint/TS_SadPoint.dat", newInputFile, prevRunType, restart)
    getPrevVec(dirPath+"SadPoint/TS_SadPoint.dat", newInputFile, prevRunType, restart)

with open('testInputIRC.inp','w') as newInputFile:
    dirPath = "/home/rcf-proj2/ddd2/ZhangThynellTS/R8/"
    prevRunType = "IRC"  # Pulling data from a IRC .dat file
    restart = True   # Next run is a restart
    # Note: the "TS_SadPoint.dat" name below was my mistake in naming the file when I ran it originally
    getPrevGeom(dirPath+"IRC_forward/TS_SadPoint.dat", newInputFile, prevRunType, restart)
    getPrevVec(dirPath+"IRC_forward/TS_SadPoint.dat", newInputFile, prevRunType, restart)
    getPrevHess(dirPath+"Hess_final/TS_Hess.dat", newInputFile)
    getPrevIRC(dirPath+"IRC_forward/TS_SadPoint.dat", newInputFile)

