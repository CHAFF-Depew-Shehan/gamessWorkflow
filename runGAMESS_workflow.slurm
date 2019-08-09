#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=16
#SBATCH --mem-per-cpu=4GB
#SBATCH --constraint=IB
#SBATCH --time=99:59:59
#SBATCH --job-name=R47_test
#SBATCH --account=lc_ddd2
#SBATCH --partition=scavenge
#SBATCH --export=NONE #Clears out the job environment
#SBATCH --mail-user=ddepew@usc.edu
#SBATCH --mail-type=ALL

export GMS_PATH=/home/rcf-proj2/ddd2/ddepew/scripts/gamessWorkflow
export WORKFLOW_PATH=/home/rcf-proj2/ddd2/ddepew/scripts/gamessWorkflow
source /usr/usc/intel/17.2/setup.sh

echo "Starting" $SLURM_JOB_ID `date`
echo "Initiated on `hostname`"
echo ""
cd $SLURM_SUBMIT_DIR

NCPUS=$SLURM_NTASKS
PPN=$(( $NCPUS / $SLURM_JOB_NUM_NODES ))
echo "Running on $SLURM_JOB_NUM_NODES nodes: "
echo "$SLURM_NODELIST"
echo "Using $NCPUS compute processes with $PPN compute processes per node"

# Remove semaphores from previous jobs using Intel mpi commands with ipcrm
echo "Current semaphores:"
ipcs -s
I_MPI_JOB_RESPECT_PROCESS_PLACEMENT=disable
mpirun -ppn 1 ipcrm -a
I_MPI_JOB_RESPECT_PROCESS_PLACEMENT=enable
echo "After semaphore removal:"
ipcs -s


# run the program on the linux cluster
# note that the sbatch command must be submitted from the reaction directory
while [ ! -s workflow.err ]; do 
INPUTFILES=`python3 $WORKFLOW_PATH/main.py "./" 2>workflow.err`
if [ -z "$INPUTFILES" ]; then echo NO INPUT FILES; continue; fi
SAVEIFS=$IFS; IFS=$'\n'; FILEARRAY=($INPUTFILES); IFS=$SAVIFS
I=0
NCPUS=$(( $NCPUS / ${#FILEARRAY[@]} ))
for FILENAME in "${FILEARRAY[@]}"
do
    if [ $FILENAME == COMPLETED ]; then echo WORKFLOW RUNS COMPLETED; break 2; fi
    $GMS_PATH/rungms ./${FILENAME}.inp 00 $NCPUS $PPN hostfile.${I}.nodes > ./${FILENAME}.log &
    let I+=1
done
wait
done

ret=$?

if [ -n "$(find $SCRATCHDIR -type f 2>/dev/null)" ]; then
    cp -r -v $SCRATCHDIR/* $SLURM_SUBMIT_DIR  # Copy all the output and temp files
                                              # from /scratch to submit directory
fi
echo "Done   " `date`
exit $ret
