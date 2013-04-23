#!/bin/bash
data=football
intervals="86400 43200 7200 3600 1800 600 300 120 60 30 2"
intervals="300 120 60 30 2"
min_anons="100 200 300 400 500"
buddy_sets="1 2 4 8 16 32 64 128 256"
parallel=48
for interval in $intervals; do
  for buddy_set in $buddy_sets; do
    for min_anon in $min_anons; do
      echo $interval $buddy_set $min_anon
      python anon_sim.py \
        -i $data \
        -s 604800 \
        -e 1209600 \
        -r $interval \
        -t rank \
        -x dynamic_split \
        -z $buddy_set \
        -m $min_anon \
        --output $data.$interval.$buddy_set.$min_anon.data \
        > $data.$interval.$buddy_set.$min_anon.out &
      while [[ $(jobs | grep Running | wc -l) -eq $parallel ]]; do
        sleep 30
      done
    done
  done
done
wait
