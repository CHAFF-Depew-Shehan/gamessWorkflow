import os
import sys

# if we have multiple commands to run, divide the nodes evenly and create the node file (hostfile)
# otherwise, the hostfile will simply be the results of executing an scontrol

def getHosts(numSubprocesses):
    if numSubprocesses == 1:
        hostfile = "hostfile.0.nodes"
        os.popen("scontrol show hostnames | sort -u > " + hostfile).read()
    else:
        hosts = os.popen("scontrol show hostnames | sort -u").read().strip().split('\n')
        nh = len(hosts)
        rem = nh % numSubprocesses
        nhp = nh // numSubprocesses
        nf = numSubprocesses - rem  # number of subprocesses which use the lower number (floor) of nodes
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
