#!/bin/bash
 
MIN_LAG=200
LAG_RANGE=300
#MAX_LAG=50
#(( LAG_RANGE = MAX_LAG - MIN_LAG ))

 
TIME=20 # total test time (in seconds)
INTERVAL=0.1 # time in between changes in latency (in seconds)
STEPS=200 # TIME / INTERVAL
 
# set up a pipe to add latency, which matches only *incoming*
# traffic from the localhost to the localhost
ipfw add 100 pipe 1 ip from 127.0.0.1 to 127.0.0.1 in
ipfw add 100 allow ip from 127.0.0.1 to 127.0.0.1 out
 
#temporary
#ipfw add 100 pipe 1 ip from any to any
#ipfw add 100 allow ip from any to any out


# set up initial random delay
(( delay = (RANDOM % LAG_RANGE) + MIN_LAG ))
echo "setting delay to" $delay "ms"
 
ipfw pipe 1 config delay ${delay}ms
 
# start ping background process and stash result in a file
ping -i 0.05 localhost > ping_out &
PING_PID=$! # remember the PID so we can kill it later
 
for ((i=0; i < STEPS; i++))
do
    sleep $INTERVAL
 
    # change the delay to a new random value
    (( delay = (RANDOM % LAG_RANGE) + MIN_LAG ))
    ipfw pipe 1 config delay ${delay}ms
 
    echo "setting delay to" $delay "ms"
done
 
# kill the ping process
#kill $PING_PID
 
# remove the pipe and the associated rule
#ipfw delete 100
ipfw pipe 1 delete
ipfw -q flush