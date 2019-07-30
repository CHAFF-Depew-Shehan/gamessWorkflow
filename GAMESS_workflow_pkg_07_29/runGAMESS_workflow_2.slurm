#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=16
#SBATCH --mem-per-cpu=2GB
#SBATCH --constraint=IB
#SBATCH --time=99:59:59
#SBATCH --job-name=Workflow_R47_Take2
#SBATCH --account=lc_ddd2
#SBATCH --partition=scavenge
#SBATCH --export=NONE #Clears out the job environment
#SBATCH --mail-user=ddepew@usc.edu
#SBATCH --mail-type=ALL

#find . -type f -name slurm\* -exec rm {} \;

export GMS_PATH=/home/rcf-proj2/ddd2/ddepew/gamess/src
export WORKFLOW_PATH=/home/rcf-proj2/ddd2/ddepew/gamess/testing/GAMESS_workflow_pkg_07_29
source /usr/usc/intel/17.2/setup.sh

#The following should contain your program and any arguments
#inputfile="Opt_LHS"      # G03 Input file

#outputfile="test.out"           # G03 Output file


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
commands=`python3 $WORKFLOW_PATH/main.py "./" "True" 2>workflow.err`
SAVEIFS=$IFS; IFS=$'\n'; commandArray=($commands); IFS=$SAVIFS
for nextCommand in "${commandArray[@]}"
do
    eval "$nextCommand"
done
done

ret=$?

cp -v $SCRATCHDIR/* $SLURM_SUBMIT_DIR  # Copy all the output and temp files
                                    ## from /scratch to submit directory
echo "Done   " `date`
exit $ret
