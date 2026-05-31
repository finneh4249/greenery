#!/bin/bash
NUMBER=$(($RANDOM % 23))

for ((run=1; run <= NUMBER + 1; run++))
do
  echo `python3 ~/greenery/fortune.py` > ~/greenery/file.txt
  /usr/bin/git -C ~/greenery/ add . -A
  /usr/bin/git -C ~/greenery/ commit -m "`python3 ~/greenery/fortune.py -sn 32`"
done

