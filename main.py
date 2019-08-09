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

def main(rxn):
    #print(rxn, file=sys.stderr)
    status = search.findStatus(rxn)
    #print('STATUS: ', file=sys.stderr)
    #print(status, file=sys.stderr)
    if 31 in status and 32 in status:
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
