import status
from setupRun import processNodes
from hosts import getHosts
import sys

# CHANGELOG 07/23/19
#   -- due to modification in setupRun.py, allowed for newInputFile variable to
#       be a list of strings; then each new input file is printed in a
#       rungamessline for execution in case of multiple status nodes
# CHANGELOG 07/29/19
#   -- removed side from inputs and argument to findStatus()
# CHANGELOG 08/08/19
#   -- changed what is printed in case all workflow runs are finished; instead
#       of an 'exit 0' command, the string 'COMPLETED' is printed and the code
#       exits
#   -- the getHosts() function was added as implemented in hosts.py, accepting
#       the number of subprocesses which must be run in parallel, inferred
#       from the length of the list returned by the "processNodes()" function
#   -- incorporated error handling in case no input files are returned from
#       processNodes() function, raising a ValueError
#   -- changed the output of the main function to print the stripped input
#       file names; note that these include relative paths but the file name
#       does not have the ".inp" extension

def main(rxn):
    rxnStatus = status.findStatus(rxn)
    # NOTE: This must be kept current as new nodes are added and the "final 2"
    # nodes change from 33 and 34
    if 33 in rxnStatus and 34 in rxnStatus:
        print('COMPLETED')
        return

    newInputFile = processNodes(rxn,'/home/rcf-40/smparmar/hpc/smparmar/GIT/gamessWorkflow/nodes.txt',rxnStatus)

    numSubprocesses = len(newInputFile)
    if numSubprocesses == 0:
        raise ValueError("No input files were created!! Check results from completed runs")
    else:
        getHosts(len(newInputFile))

    [print(inpFile.strip(".inp")) for inpFile in newInputFile]
    #rungamessline = '$GMS_PATH/rungms ' + inpFile + ' 00 $NCPUS $PPN > ' + inpFile.replace('.inp','.log')
    return

if __name__ == "__main__":
    main(sys.argv[1])
