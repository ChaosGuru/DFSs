#!/bin/bash

trap "kill 0" EXIT

for i in {30000..30010}
do
    if ! ss -tulwn | grep ":$i" 
    then
        python chunk_kun.py "$i" &
    fi
done

wait

# ss -tulwn
# ps -eaf
# kill pid