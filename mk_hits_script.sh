#!/bin/bash
read -p "Enter Directory Name:" dirname

for j in {0..9950..50}; do
  mkdir ~/DAOD/$dirname/hits_$j
  cd ~/DAOD/$dirname/hits_$j
  cat ~/DAOD/pbs2.sh > hits_script.txt
  echo "cd ~/DAOD/$dirname/hits_$j" >> hits_script.txt
  echo 'asetup 21.0.77,Athena,here' >> hits_script.txt
  echo "Sim_tf.py --conditionsTag=OFLCOND-MC16-SDR-14 --geometryVersion=ATLAS-R2-2016-01-00-01_VALIDATION --runNumber=284500 --simulator=ATLFASTII --outputHITSFile=hits.root --inputEVNTFile=../evgen/evgen.root --maxEvents=50 --skipEvents $j" >> hits_script.txt
  chmod +x hits_script.txt
done
