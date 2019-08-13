import statusUpdateFunc as search
import actions as act
from hosts import getHosts
import sys

# CHANGELOG 07/23/19
#   -- due to modification in actions.py, allowed for newInputFile variable to
#       be a list of strings; then each new input file is printed in a
#       rungamessline for execution in case of multiple action nodes
# CHANGELOG 07/29/19
#   -- removed side from inputs and argument to findStatus()
# CHANGELOG 08/08/19
#   -- changed what is printed in case all workflow runs are finished; instead
#       of an 'exit 0' command, the string 'COMPLETED' is printed and the code
#       exits
#   -- the getHosts() function was added as implemented in hosts.py, accepting
#       the number of subprocesses which must be run in parallel, inferred
#       from the length of the list returned by the "actions()" function
#   -- incorporated error handling in case no input files are returned from
#       actions() function, raising a ValueError
#   -- changed the output of the main function to print the stripped input
#       file names; note that these include relative paths but the file name
#       does not have the ".inp" extension

def main(rxn):
    #print(rxn, file=sys.stderr)
    status = search.findStatus(rxn)
    #print('STATUS: ', file=sys.stderr)
    #print(status, file=sys.stderr)
    if 33 in status and 34 in status:
    # NOTE: This must be kept current as new nodes are added and the "final 2"
    # nodes change from 31 and 32
        print('COMPLETED')
        return

    newInputFile = act.actions(rxn,'/home/rcf-proj2/ddd2/ddepew/gamess/src/scripts/gamessWorkflow/actions.txt',status)

    numSubprocesses = len(newInputFile)
    if numSubprocesses == 0:
        raise ValueError("No input files were created!! Check results from completed runs")
    else:
        getHosts(len(newInputFile))

    [print(inpFile.strip(".inp")) for inpFile in newInputFile]
#       rungamessline = '$GMS_PATH/rungms ' + inpFile + ' 00 $NCPUS $PPN > ' + inpFile.replace('.inp','.log')
#       print(rungamessline)
    return

if __name__ == "__main__":
    main(sys.argv[1])
