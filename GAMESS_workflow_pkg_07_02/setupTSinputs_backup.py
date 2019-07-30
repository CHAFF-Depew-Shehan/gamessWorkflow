import sys

def header(prevInpFile, newInputFile, runtyp, *parameters, opttol="0.0001", nstep="20", npoint="15",maxit="60"):
    # The prevInpFile is a string indicating the file name and path
    # the newInputFile is a file object that has been opened previously
    # for writing
    # The runtyp is simply the input for RUNTYP (i.e. HESSIAN, SADPOINT, OPTIMIZE_LHS, OP    # TIMIZE_RHS, IRC_backward, IRC_forward)
    # *parameters are any lines (must include the entire string from $PARAMETER to
    # $END) the user would like to add into the header
    # **kwargs include OPTTOL, NSTEP, NPOINT
    # Every run requires a header, with several generic parameters along
    # with run specific parameters and any additional parameters the users
    # wishes to add in
    if opttol is None:
        opttol = "0.0001"
    if nstep is None:
        nstep="20"
    if npoint is None:
        npoint="15"
    if maxit is None:
        maxit="60"

    with open(prevInpFile,"r") as inpFile, open(newInputFile, "w+") as newInputFile:
        # Read until the charge and multiplicity information is found
        try:
            line = readToString(inpFile, "ICHARG")
        except EOFError:
            print("No Charge or Multiplicity found in given input file:" + prevInpFile, file=sys.stderr)
            raise
        line = line.strip().split()
        # Save charge and mult information
        charge = line[1][-1]
        mult = line[2][-1]
        # Read until reaction line is found
        try:
            line = readToString(inpFile, "$DATA")
        except EOFError:
            print("No Data Section found in given input file:" + prevInpFile, file=sys.stderr)
            raise
        rxnInfo = inpFile.readline()

        # Write very first two line associated with the runtyp
        # Hessian
        if runtyp == 'HESSIAN':
            newInputFile.write( "! Hessian calculation for transition state\n!\n")
            newInputFile.write(" $CONTRL SCFTYP=RHF DFTTYP=M06-2X RUNTYP=HESSIAN ISPHER=1 MAXIT=" + maxit + " $END\n")
            specLines = False
        # SadPoint
        elif runtyp == 'SADPOINT':
            newInputFile.write( "! Saddle point optimization for transition state\n!\n")
            newInputFile.write(" $CONTRL SCFTYP=RHF DFTTYP=M06-2X RUNTYP=SADPOINT ISPHER=1 MAXIT=" + maxit + " $END\n")
            specLines = " $GUESS  GUESS=MOREAD $END\n $STATPT OPTTOL=" + opttol + " NSTEP=" + nstep + " HESS=READ $END\n"
        # IRC
        elif "IRC" in runtyp:
            if "backward" in runtyp:
                direction = "backward"
                forwrd = "FALSE"
            elif "forward" in runtyp:
                direction = "forward"
                forwrd = "TRUE"
            newInputFile.write("! Intrinsic reaction coordinate (" + direction + ") run from transition state\n!\n")
            newInputFile.write(" $CONTRL SCFTYP=RHF DFTTYP=M06-2X RUNTYP=IRC ISPHER=1 MAXIT=" + maxit + " $END\n")
            specLines = " $STATPT OPTTOL=" + opttol + " NSTEP=" + nstep + " HESS=READ $END\n $IRC    NPOINT=" + npoint + " SADDLE=.TRUE. STRIDE=0.1 FORWRD=." + forwrd + ". $END\n"
        # Optimization
        elif "OPT" in runtyp:
            if "LHS" in runtyp:
                side = "Left Hand Side"
            elif "RHS" in runtyp:
                side = "Right Hand Side"
            newInputFile.write( "! Optimization Zhang Thynell " + side + "\n!\n")
            newInputFile.write(" $CONTRL SCFTYP=RHF DFTTYP=M06-2X RUNTYP=OPTIMIZE ISPHER=1 MAXIT=" + maxit + " $END\n")
            specLines = " $STATPT OPTTOL=" + opttol + " NSTEP=" + nstep + " HESS=READ $END\n"

        # Write rest of header information
        newInputFile.write(" $CONTRL ICHARG=" + charge + " MULT=" + mult + " $END\n")
        newInputFile.write("--$CONTRL EXETYP=CHECK $END\n $SYSTEM MWORDS=50 TIMLIM=1380 PARALL=.TRUE. $END\n $BASIS  GBASIS=ACCT $END\n $SCF    DIRSCF=.TRUE. DAMP=.TRUE. $END\n")
        # THIS ONLY WORKS WHENS TARTING FROM SADPOINT
        #NOTE: specLines = " $GUESS GUESS=MOREAD $END\n" (?)

        # Write the runtyp specific lines
        if specLines:
            newInputFile.write(specLines)

        newInputFile.write(" $PCM    IEF=-3 SOLVNT=INPUT EPS=11.50 EPSINF=2.0449 SMD=.TRUE.\n         SOLA=0.229 SOLB=0.265 SOLC=0.0 SOLG=61.24 SOLH=0.0 SOLN=1.43 $END\n $TESCAV MTHALL=2 NTSALL=240 $END\n")

        # Write in any optional arguments
        #print(parameters)

        if parameters:
            for line in parameters:
                newInputFile.write(line+'\n')

        # Begin $DATA group
        newInputFile.write(" $DATA\n" + rxnInfo + "C1\n")

def geom(prevGeomDatFile, newInputFile, restart):
    # The prevGeomDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing.
    # The only types of runs which would modify a geometry would be stationary
    # point searches (saddle points and geometry optimizations) or intrinsic
    # reaction coordinate runs. Thus, these are the only .dat files considered
    # as input.
    with open(prevGeomDatFile,"r") as datFile, open(newInputFile,"a") as inpFile:
        # Read to appropriate section containing $DATA info
        # Extract file name from full (or relative) path
        prevFilename = prevGeomDatFile.split('/')[-1]
        if ("SadPoint" in prevFilename or "Opt" in prevFilename) and restart == False:
            try:
                readToString(datFile, "----- RESULTS")
            except EOFError:
                #print("No results section found in file " + prevGeomDatFile)
                raise
            # Read 4 lines before geometry info
            for i in range(4):
                datFile.readline()
        elif "IRC" in prevFilename:
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
                #print("No restart information found in file " + prevGeomDatFile)
                raise EOFError
            else:
                # Set file object position to last IRC restart section
                datFile.seek(lastPos)
                # Read 5 lines before geometry info
                for i in range(5):
                    datFile.readline()
        elif "Opt" in prevFilename and restart == True:
            # Find step which corresponds to minimum energy and move to that step
            readOptMinEnergyStep(datFile)
            for i in range(3):
                datFile.readline()
        elif ("SadPoint" in prevFilename and restart == True) or "Hess" in prevFilename:
            # Copying directly from $DATA section of a previous input file
            try:
                readToString(datFile, " $DATA")
            except EOFError:
                #print("Could not find $DATA group in file " + prevGeomDatFile)
                raise
            # Read 2 lines before geometry info
            for i in range(2):
                datFile.readline()
        else:
            raise ValueError('Incorrect file for reading geometry')

        # Read atom position data
        while True:
            atomLine = datFile.readline().strip()
            if atomLine[0] == '-' or atomLine[0] == '$':
                break
            elif atomLine == '':
                #print("End of file found while reading atom coordinates")
                raise EOFError
            a = atomLine.split()
            if len(a) != 5:
                #print("Error reading atom coordinates. Read the following:")
                #print(a)
                raise ValueError
            inpFile.write("{0}  {1}  {2[0]:>13}  {2[1]:>13}  {2[2]:>13}\n".format(a[0],a[1][0],a[2:5]))
        inpFile.write(" $END\n")
    return


def vec(prevVecDatFile, newInputFile, restart):
    # The prevVecDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing.
    # The only types of runs which would modify orbitals would be stationary
    # point searches (saddle points and geometry optimizations) or intrinsic
    # reaction coordinate runs. Thus, these are the only .dat files considered
    # as input.
    with open(prevVecDatFile,"r") as datFile, open(newInputFile,"a") as inpFile:
        # Extract file name from full (or relative) path
        prevFilename = prevVecDatFile.split('/')[-1]
        # Read to appropriate section containing $DATA info
        if ("SadPoint" in prevFilename or "Opt" in prevFilename) and restart == False:
            try:
                readToString(datFile, "----- RESULTS")
            except EOFError:
                #print("No results section found in file " + prevVecDatFile)
                raise
        elif "IRC" in prevFilename:
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
                #print("No orbitals ($VEC group) found in file " + prevVecDatFile)
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
                    raise
                    #print("IRC restart group not generated for last orbitals")
                # Set file object position to last orbitals section again
                datFile.seek(lastPos)
        elif "Opt" in prevFilename and restart == True:
            # Find step which corresponds to minimum energy and move to that step
            readOptMinEnergyStep(datFile)
        elif ("SadPoint" in prevFilename and restart == True) or "Hess" in prevFilename:
            pass #continue
        else:
            raise ValueError('Incorrect file for reading $VEC group')

        try:
            line = readToString(datFile, "$VEC")
        except EOFError:
            #print("Couldn't find correct $VEC group in file " + prevVecDatFile)
            raise
        while "$END" not in line:
            if line == '':
                #print("Error: $VEC group cut off in file " + prevVecDatFile)
                raise EOFError
            else:
                inpFile.write(line)
                line = datFile.readline()
        inpFile.write(line)
    return


def grad(prevGradDatFile, newInputFile, restart=True):
    # The prevGradDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing.
    # The only types of runs which would require a $GRAD group are stationary
    # point runs. Since we are only restarting optimization runs here (we
    # assume SadPoint runs have converged already), the restart flag is assumed
    # to be True.
    with open(prevGradDatFile,"r") as datFile, open(newInputFile,"a") as inpFile:
        # Extract file name from full (or relative) path
        prevFilename = prevGradDatFile.split('/')[-1]
        if "Opt" in prevFilename and restart:
            # Find step which corresponds to minimum energy and move to that step
            readOptMinEnergyStep(datFile)
        elif "SadPoint" in prevFilename and restart:
            # Take $GRAD group from input file
            pass #continue
        else:
            raise ValueError("Only Opt and SadPoint restarts for getPrevGrad()")

        # Read to $GRAD group
        try:
            line = readToString(datFile, "$GRAD")
        except EOFError:
            #print("Couldn't find correct $GRAD group in file " + prevVecDatFile)
            raise
        # Read to $END and write to file
        while "$END" not in line:
            if line == '':
                #print("Error: $GRAD group cut off in file " + prevHessDatFile)
                raise EOFError
            else:
                inpFile.write(line)
                line = datFile.readline()
        inpFile.write(line)
    return


def hess(prevHessDatFile, newInputFile):
    # The prevHessDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing.

    with open(prevHessDatFile,"r") as datFile, open(newInputFile,"a") as inpFile:
        # Extract file name from full (or relative) path
        prevFilename = prevHessDatFile.split('/')[-1]
        if "IRC" in prevFilename:
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
                #print("No restart information found in file " + prevIRCDatFile)
                raise EOFError
            else:
                # Set file object position to last IRC restart section
                datFile.seek(lastPos)

        try:
            line = readToString(datFile, "$HESS")
        except EOFError:
            #print("No $HESS group found in file " + prevHessDatFile)
            raise
        while "$END" not in line:
            if line == '':
                #print("Error: $HESS group cut off in file " + prevHessDatFile)
                raise EOFError
            else:
                inpFile.write(line)
                line = datFile.readline()
        inpFile.write(line)
    return


def IRC(prevIRCDatFile, newInputFile, npoint="15"):
    # The prevIRCDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing. Note that this should only read from a RUNTYP=IRC dat file.
    # First accommodate default "None" to change to 15
    if npoint is None:
        npoint = "15"
    with open(prevIRCDatFile,"r") as datFile, open(newInputFile,"a") as inpFile:
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
            #print("No restart information found in file " + prevIRCDatFile)
            raise EOFError
        else:
            # Set file object position to last IRC restart section
            datFile.seek(lastPos)
        # Now read to beginning of $IRC group
        # Note that the string "$IRC" is used in other parts of the dat file,
        # so search for a more unique string indicating beginning of $IRC group
        try:
            line = readToString(datFile, " $IRC   PACE")
            if "??" in line:
                line = line.replace("??",npoint)
        except EOFError:
            #print("Couldn't find correct $IRC group in file " + prevIRCDatFile)
            raise
        while "$END" not in line:
            if line == '':
                #print("Error: $IRC group cut off in file " + prevIRCDatFile)
                raise EOFError
            else:
                inpFile.write(line)
                line = datFile.readline()
        inpFile.write(line)
    return

def vib(prevVibDatFile, newInputFile):
    # The prevVibDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing. Note that this should only read from a RUNTYP=HESSIAN rst file.
    with open(prevVibDatFile,"r") as datFile, open(newInputFile,"a") as inpFile:
        try:
            line = readToString(datFile, " $VIB")
        except EOFError:
            #print("Couldn't find $VIB group in restart file " + prevVibDatFile)
            raise
        while line != '' and 'E=        0.0000000000' not in line:
            # Only read up to lines with converged energies
            inpFile.write(line)
            line = datFile.readline()
        inpFile.write(" $END\n")
    return


def readOptMinEnergyStep(datFileOpt):
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
        #print("No data found in geometry optimization dat file")
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

#with open('testInputSadPoint.inp','w') as newInputFile:
#    dirPath = "/home/rcf-proj2/ddd2/ZhangThynellTS/R8/"
#    prevRunType = "SadPoint"  # Pulling data from a SadPoint .dat file
#    restart = False       # Next run is not a restart
#    getPrevGeom(dirPath+"SadPoint/TS_SadPoint.dat", newInputFile, prevRunType, restart)
#    getPrevVec(dirPath+"SadPoint/TS_SadPoint.dat", newInputFile, prevRunType, restart)
#
#with open('testInputIRC.inp','w') as newInputFile:
#    dirPath = "/home/rcf-proj2/ddd2/ZhangThynellTS/R8/"
#    prevRunType = "IRC"  # Pulling data from a IRC .dat file
#    restart = True   # Next run is a restart
#    # Note: the "TS_SadPoint.dat" name below was my mistake in naming the file when I ran it originally
#    getPrevGeom(dirPath+"IRC_forward/TS_SadPoint.dat", newInputFile, prevRunType, restart)
#    getPrevVec(dirPath+"IRC_forward/TS_SadPoint.dat", newInputFile, prevRunType, restart)
#    getPrevHess(dirPath+"Hess_final/TS_Hess.dat", newInputFile)
#    getPrevIRC(dirPath+"IRC_forward/TS_SadPoint.dat", newInputFile)

