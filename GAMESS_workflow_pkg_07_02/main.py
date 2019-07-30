import statusUpdateFunc as search
import actions as act
import sys
def main(rxn,side):
    #print(rxn, file=sys.stderr)
    #print(side, file=sys.stderr)
    status = search.findStatus(rxn,side)
    #print('STATUS: ', file=sys.stderr)
    #print(status, file=sys.stderr)
    if 31 in status and 32 in status:
        isComplete = True
        print('exit 0')
        return
    else:
        isComplete = False
    newInputFile = act.actions(rxn,'/home/rcf-proj2/ddd2/ddepew/gamess/testing/GAMESS_workflow_pkg_07_02/actions.txt',status)

    rungamessline = '$GMS_PATH/rungms ' + newInputFile + ' 00 $NCPUS $PPN > ' + newInputFile.replace('.inp','.log')
    print(rungamessline)
    return rungamessline

if __name__ == "__main__":
    main(sys.argv[1], eval(sys.argv[2]))
