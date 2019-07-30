#!/bin/bash

#result=$(python3 testMain.py ../R47/ True)
while true; do 
results=`python3 testMain.py "../R47/" "True"`
eval "$results"
done
