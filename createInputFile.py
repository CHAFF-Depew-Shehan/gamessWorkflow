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
        if 'Opt' in newInputFile:
            nstep="50"
        else:
            nstep="20"
    if npoint is None:
        npoint="15"
    if maxit is None:
        maxit="60"

    with open(prevInpFile,"r") as inpFile, open(newInputFile, "w+") as newInputFile:
        # Read in parameters from $CONTRL group that will be consistent for this reaction
        contrlParams = {"SCFTYP": "", "DFTTYP": "", "ISPHER": "", "ICHARG": "", "MULT": ""}
        for param in contrlParams.keys():
            inpFile.seek(0)
            try:
                line = readToString(inpFile, param)
                contrlParams[param] = next((s for s in line.strip().split() if param in s), None) + " "
            except EOFError:
                pass
        # Check if the charge and multiplicity information is found
        if contrlParams["ICHARG"] == "" or contrlParams["MULT"] == "":
            print("No Charge or Multiplicity found in given input file:" + prevInpFile, file=sys.stderr)
            raise ValueError()
        # Read until reaction line is found
        try:
            inpFile.seek(0)
            line = readToString(inpFile, "$DATA")
        except EOFError:
            print("No Data Section found in given input file:" + prevInpFile, file=sys.stderr)
            raise
        rxnInfo = inpFile.readline()

        # Write commented header information and save runtyp-specific lines
        if runtyp == 'HESSIAN':
            newInputFile.write( "! Hessian calculation for transition state\n!\n")
            specLines = " $GUESS  GUESS=MOREAD $END\n"
            if contrlParams["DFTTYP"] == "DFTTYP=wB97X-D ":
                specLines += " $FORCE  METHOD=SEMINUM $END\n"
        elif runtyp == 'SADPOINT':
            newInputFile.write( "! Saddle point optimization for transition state\n!\n")
            specLines = " $GUESS  GUESS=MOREAD $END\n $STATPT OPTTOL=" + opttol + " NSTEP=" + nstep + " HESS=READ $END\n"
        elif "IRC" in runtyp:
            if "backward" in runtyp:
                direction = "backward"
                forwrd = "FALSE"
            elif "forward" in runtyp:
                direction = "forward"
                forwrd = "TRUE"
            runtyp="IRC"
            newInputFile.write("! Intrinsic reaction coordinate (" + direction + ") run from transition state\n!\n")
            specLines = " $STATPT OPTTOL=" + opttol + " NSTEP=" + nstep + " HESS=READ $END\n $IRC    NPOINT=" + npoint + " SADDLE=.TRUE. STRIDE=0.1 FORWRD=." + forwrd + ". $END\n"
            # NOTE that the $GUESS group is omitted for IRC runs because it is
            # not needed for restart (i.e. abnormal) runs. It is included as a
            # parameter for the initial IRC_forward and IRC_backward runs in
            # nodes.txt, however.
        elif "OPT" in runtyp:
            if "LHS" in runtyp:
                side = "Left Hand Side"
            elif "RHS" in runtyp:
                side = "Right Hand Side"
            else:
                side = False
            runtyp="OPTIMIZE"
            if side:
                newInputFile.write( "! Optimization of Reaction " + side + "\n!\n")
            specLines = " $GUESS  GUESS=MOREAD $END\n $STATPT OPTTOL=" + opttol + " NSTEP=" + nstep + " $END\n"

        # Write rest of header information
        newInputFile.write(" $CONTRL " + contrlParams["SCFTYP"]
                                + contrlParams["DFTTYP"] + contrlParams["ISPHER"]
                                + "RUNTYP=" + runtyp + " MAXIT=" + maxit + " $END\n")
        newInputFile.write(" $CONTRL " + contrlParams["ICHARG"] + contrlParams["MULT"] + "$END\n")
        newInputFile.write(" $SYSTEM MWORDS=50 TIMLIM=1420 PARALL=.TRUE. $END\n")

        # Search for commonly used groups that are consistent across reactions
        searchGroups = ["$BASIS", "$SCF"]
        for group in searchGroups:
            inpFile.seek(0)
            try:
                line = readToString(inpFile, group)
                while "$END" not in line:
                    if line == '':
                        print("Error: No $END for " + group + " group in file " + prevInpFile, file=sys.stderr)
                        raise ValueError
                    else:
                        newInputFile.write(line)
                        line = inpFile.readline()
                newInputFile.write(line)
            except EOFError:
                pass
            except ValueError:
                raise

        # Write the runtyp specific lines
        if specLines:
            newInputFile.write(specLines)

        # If a solvent is used, write its associated groups
        searchGroups = ["$PCM", "$TESCAV"]
        for group in searchGroups:
            inpFile.seek(0)
            try:
                line = readToString(inpFile, group)
                while "$END" not in line:
                    if line == '':
                        print("Error: No $END for " + group + " group in file " + prevInpFile, file=sys.stderr)
                        raise ValueError
                    else:
                        newInputFile.write(line)
                        line = inpFile.readline()
                newInputFile.write(line)
            except EOFError:
                pass
            except:
                raise

        # Write in any optional arguments
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
                print("No results section found in file " + prevGeomDatFile, file=sys.stderr)
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
                print("No restart information found in file " + prevGeomDatFile, file=sys.stderr)
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
                print("Could not find $DATA group in file " + prevGeomDatFile, file=sys.stderr)
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
                print("End of file found while reading atom coordinates", file=sys.stderr)
                raise EOFError
            a = atomLine.split()
            if len(a) != 5:
                print("Error reading atom coordinates. Read the following:", file=sys.stderr)
                print(a, file=sys.stderr)
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
                print("No results section found in file " + prevVecDatFile, file=sys.stderr)
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
                print("No orbitals ($VEC group) found in file " + prevVecDatFile, file=sys.stderr)
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
                    print("IRC restart group not generated for last orbitals", file=sys.stderr)
                # Set file object position to last orbitals section again
                datFile.seek(lastPos)
        elif "Opt" in prevFilename and restart == True:
            # Find step which corresponds to minimum energy and move to that step
            readOptMinEnergyStep(datFile)
        elif ("SadPoint" in prevFilename and restart == True) or "Hess" in prevFilename:
            pass
        else:
            raise ValueError('Incorrect file for reading $VEC group')

        try:
            line = readToString(datFile, "$VEC")
        except EOFError:
            print("Couldn't find correct $VEC group in file " + prevVecDatFile, file=sys.stderr)
            raise
        while "$END" not in line:
            if line == '':
                print("Error: $VEC group cut off in file " + prevVecDatFile, file=sys.stderr)
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
            pass
        else:
            raise ValueError("Only Opt and SadPoint restarts for getPrevGrad()")

        # Read to $GRAD group
        try:
            line = readToString(datFile, "$GRAD")
        except EOFError:
            print("Couldn't find correct $GRAD group in file " + prevVecDatFile, file=sys.stderr)
            raise
        # Read to $END and write to file
        while "$END" not in line:
            if line == '':
                print("Error: $GRAD group cut off in file " + prevHessDatFile, file=sys.stderr)
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
                print("No restart information found in file " + prevIRCDatFile, file=sys.stderr)
                raise EOFError
            else:
                # Set file object position to last IRC restart section
                datFile.seek(lastPos)

        try:
            line = readToString(datFile, "$HESS")
        except EOFError:
            print("No $HESS group found in file " + prevHessDatFile, file=sys.stderr)
            raise
        while "$END" not in line:
            if line == '':
                print("Error: $HESS group cut off in file " + prevHessDatFile, file=sys.stderr)
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
            print("No restart information found in file " + prevIRCDatFile, file=sys.stderr)
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
            print("Couldn't find correct $IRC group in file " + prevIRCDatFile, file=sys.stderr)
            raise
        while "$END" not in line:
            if line == '':
                print("Error: $IRC group cut off in file " + prevIRCDatFile, file=sys.stderr)
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
            print("Couldn't find $VIB group in restart file " + prevVibDatFile, file=sys.stderr)
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
    minEnergy = float("inf")
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
        print("No data found in geometry optimization dat file", file=sys.stderr)
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
