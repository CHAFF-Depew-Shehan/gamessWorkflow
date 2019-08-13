import os
import sys

# This function evenly divides hosts (nodes) across an input number of
# subprocesses to run in parallel. It constructs one or more hostfiles using
# the 'scontrol' slurm command in the shell to show the hostnames. In the case
# where more than one subprocesses are requested, it divides hosts evenly,
# sorts them by number, and distributes remainder hosts across the last
# subprocesses.
# Ex: 8 hosts (hpc3054-hpc3061) are available for 3 subprocesses
#       --> hostfile.0.nodes:
#               hpc3054
#               hpc3055
#       --> hostfile.1.nodes:
#               hpc3056
#               hpc3057
#               hpc3058
#       --> hostfile.2.nodes:
#               hpc3059
#               hpc3060
#               hpc3061
# Note that as implemented in worklow, only two subprocesses would ever be
# requested at once, and usually an even number of hosts will be available.

def getHosts(numSubprocesses):
    if numSubprocesses == 1:
        hostfile = "hostfile.0.nodes"
        os.popen("scontrol show hostnames | sort -u > " + hostfile).read()
    else:
        hosts = os.popen("scontrol show hostnames | sort -u").read().strip().split('\n')
        nh = len(hosts)
        rem = nh % numSubprocesses  # remainder of hosts that can't be divided evenly
        nhp = nh // numSubprocesses # number of hosts per subprocess, rounded down (integer division)
        nf = numSubprocesses - rem  # number of subprocesses which use nhp nodes (others use nhp+1)
        for i in range(numSubprocesses):
            hostfile = "hostfile."+str(i)+".nodes"
            with open(hostfile, "w") as hf:
                if i < (numSubprocesses-rem):
                    [print(hostname, file=hf) for hostname
                        in hosts[(nhp*i):(nhp*(i+1))]]
                else:
                    [print(hostname, file=hf) for hostname
                        in hosts[((nhp*i)+(i-nf)):((nhp*(i+1)+(i-nf)+1))]]

if __name__ == "__main__":
    getHosts(int(sys.argv[1]))
