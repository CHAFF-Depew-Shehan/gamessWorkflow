# Included Functions:
# header()
# geom()
# vec()
# hess()
# IRC()
# readToString()

def header(prevInpFile, newInputFile, runtyp, *parameters, opttol="0.0001", nstep="20", npoint="15"):
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

    with open(prevInpFile,"r") as inpFile:
        # Read until the charge and multiplicity information is found
        try:
            line = readToString(inpFile, "ICHARG")
        except EOFError:
            print("No Charge or Multiplicity found in given input file:" + prevInpFile)
            raise
        line = line.strip().split()
        # Save charge and mult information
        charge = line[1][-1]
        mult = line[2][-1]
        # Read until reaction line is found
        try:
            line = readToString(inpFile, "$DATA")
        except EOFError:
            print("No Data Section found in given input file:" + prevInpFile)
            raise
        rxnInfo = inpFile.readline()

    # Write very first two line associated with the runtyp
    # Hessian
    if runtyp == 'HESSIAN':
        newInputFile.write( "! Hessian calculation for transition state\n!\n")
        newInputFile.write(" $CONTRL SCFTYP=RHF DFTTYP=M06-2X RUNTYP=HESSIAN ISPHER=1 MAXIT=60 $END\n")
        specLines = False
    # SadPoint
    elif runtyp == 'SADPOINT':
        newInputFile.write( "! Saddle point optimization for transition state\n!\n")
        newInputFile.write(" $CONTRL SCFTYP=RHF DFTTYP=M06-2X RUNTYP=SADPOINT ISPHER=1 MAXIT=60 $END\n")
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
        newInputFile.write(" $CONTRL SCFTYP=RHF DFTTYP=M06-2X RUNTYP=IRC ISPHER=1 MAXIT=60 $END\n")
        specLines = " $STATPT OPTTOL=" + opttol + " NSTEP=" + nstep + " HESS=READ $END\n $IRC    NPOINT=" + npoint + " SADDLE=.TRUE. STRIDE=0.1 FORWRD=." + forwrd + ". $END\n"
    # Optimization
    elif "OPT" in runtyp:
        if "LHS" in runtyp:
            side = "Left Hand Side"
        elif "RHS" in runtyp:
            side = "Right Hand Side"
        newInputFile.write( "! Optimization Zhang Thynell " + side + "\n!\n")
        newInputFile.write(" $CONTRL SCFTYP=RHF DFTTYP=M06-2X RUNTYP=OPTIMIZE ISPHER=1 MAXIT=60 $END\n")
        specLines = " $STATPT OPTTOL=" + opttol + " NSTEP=" + nstep + " HESS=READ $END\n"

    # Write rest of header information
    newInputFile.write(" $CONTRL ICHARGE=" + charge + " MULT=" + mult + " $END\n")
    newInputFile.write("--$CONTRL EXETYP=CHECK $END\n $SYSTEM MWORDS=50 TIMLIM=1380 PARALL=.TRUE. $END\n $BASIS  GBASIS=ACCT $END\n $SCF    DIRSCF=.TRUE. DAMP=.TRUE. $END\n")
    # THIS ONLY WORKS WHENS TARTING FROM SADPOINT
    #NOTE: specLines = " $GUESS GUESS=MOREAD $END\n" (?)

    # Write the runtyp specific lines
    print(specLines)
    if specLines:
        newInputFile.write(specLines)

    newInputFile.write(" $PCM    IEF=-3 SOLVNT=INPUT EPS=11.50 EPSINF=2.0449 SMD=.TRUE.\n         SOLA=0.229 SOLB=0.265 SOLC=0.0 SOLG=61.24 SOLH=0.0 SOLN=1.43 $END\n $TESCAV METHOD=1 MTHALL=2 NTSALL=240 $END\n")

    # Write in any optional arguments
    if parameters:
        for line in parameters:
            newInputFile.write(line)

    # Begin $DATA group
    newInputFile.write(" $DATA\n" + rxnInfo + "C1\n")

def geom(prevGeomDatFile, newInputFile, runType, restart):
    # The prevGeomDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing.
    # The only types of runs which would modify a geometry would be stationary
    # point searches (saddle points and geometry optimizations) or intrinsic
    # reaction coordinate runs. Thus, these are the only .dat files considered
    # as input.
    with open(prevGeomDatFile,"r") as datFile:
        # Read to appropriate section containing $DATA info
        if (runType == "SadPoint" or runType == "Opt") and restart == False:
            try:
                readToString(datFile, "----- RESULTS")
            except EOFError:
                print("No results section found in file " + prevGeomDatFile)
                raise
            # Read 4 lines before geometry info
            for i in range(4):
                datFile.readline()
        elif runType == "IRC":
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
        elif runType == "Opt" and restart == True:
            # Still need to program this
            raise NotImplementedError

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


def vec(prevVecDatFile, newInputFile, runType, restart):
    # The prevVecDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing.
    # The only types of runs which would modify orbitals would be stationary
    # point searches (saddle points and geometry optimizations) or intrinsic
    # reaction coordinate runs. Thus, these are the only .dat files considered
    # as input.
    with open(prevVecDatFile,"r") as datFile:
        # Read to appropriate section containing $DATA info
        if (runType == "SadPoint" or runType == "Opt") and restart == False:
            try:
                readToString(datFile, "----- RESULTS")
            except EOFError:
                print("No results section found in file " + prevVecDatFile)
                raise
        elif runType == "IRC":
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
        elif runType == "Opt" and restart == True:
            # Still need to program this
            raise NotImplementedError

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

#def grad(prev

def hess(prevHessDatFile, newInputFile):
    # The prevHessDatFile is a string indicating the file name and path.
    # The newInputFile is a file object that has been opened previously
    # for writing. Note that this should only read from a RUNTYP=HESSIAN
    # dat file.
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


def IRC(prevIRCDatFile, newInputFile):
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

