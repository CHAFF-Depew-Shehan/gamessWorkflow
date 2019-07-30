#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=2GB
#SBATCH --constraint=IB
#SBATCH --time=00:59:59
#SBATCH --job-name=Workflow_R47_Take1
#SBATCH --account=lc_ddd2
#SBATCH --partition=scavenge
#SBATCH --export=NONE #Clears out the job environment
#SBATCH --mail-user=ddepew@usc.edu
#SBATCH --mail-type=ALL

#find . -type f -name slurm\* -exec rm {} \;

export GMS_PATH=/home/rcf-proj2/ddd2/ddepew/gamess/src
export WORKFLOW_PATH=/home/rcf-proj2/ddd2/ddepew/gamess/testing/GAMESS_workflow_pkg_07_02
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

#echo "Inputfile: ${inputfile}.inp"
#echo "Outfile: $outputfile"

# run the program on the linux cluster using Linda
# NOTE: the "rungms" script was modified to strip the directories off the input file
while true; do 
results=`python3 $WORKFLOW_PATH/testMain.py "/home/rcf-proj2/ddd2/ddepew/gamess/testing/R47_run1/" "False" 2>test.stderr`
eval "$results"
done

ret=$?

cp -v $SCRATCHDIR/* $SLURM_SUBMIT_DIR  # Copy all the output and temp files
                                    ## from /scratch to submit directory
echo "Done   " `date`
exit $ret
