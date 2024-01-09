#
# Created Date: Monday, November 18th 2023, 11:29:23 am
# Author: C. Zhang
# Copyright (c) 2023
#

if [ "$#" -ne 4 ]; then
  echo "Script for running CUPDLP in batch mode..."
  echo " (c) Chuwen Zhang, 2023"
  echo " - Usage: <dataset directory> <output> <time limit for each instance> <eps>" 1>&2
  exit -1
fi

echo -n "choose solver (binary name) ?\n"
read solver
echo "your choice $solver"
echo -n "choose solver cmd ?\n"
read solvercmd
echo "your choice $solvercmd"
echo -n "cmd saving file name ?\n"
echo -n " - this will dump the command to run into a file\n"
read outputcmd

echo "" > $outputcmd

wdir=$(pwd)
# test set
data=$1
output=$2
timelimit=$3
precision=$4
eps=1e-$precision

name=${solver}_1e-${precision}
pdlp=$output/$name
pdlpbin=$solvercmd

mkdir -p $pdlp

cd $wdir/$pdlpsrc
for f in $(/bin/ls $data/*.mps); do

  ff=$(basename -s .mps $f)
  cmd="$pdlpbin \
   -dTimeLim $timelimit \
   -fname $data/$ff.mps \
   -dPrimalTol $eps \
   -dDualTol $eps \
   -dGapTol $eps \
   -dFeasTol $eps \
   -ifScaling 1 \
   -eLineSearchMethod 2 \
   -eRestartMethod 1 \
   -out $pdlp/$ff.json &> $pdlp/$ff.log"

  echo $cmd >> $outputcmd

done

for f in $(/bin/ls $data/*.mps.gz); do

  ff=$(basename -s .mps.gz $f)
  cmd="$pdlpbin \
   -dTimeLim $timelimit \
   -fname $data/$ff.mps \
   -dPrimalTol $eps \
   -dDualTol $eps \
   -dGapTol $eps \
   -dFeasTol $eps \
   -ifScaling 1 \
   -eLineSearchMethod 2 \
   -eRestartMethod 1 \
   -out $pdlp/$ff.json &> $pdlp/$ff.log"

  echo $cmd >> $outputcmd

done

echo "-------------------------------------"
echo "using            $solver @ $pdlpbin"
echo " - command saved to $outputcmd"
echo " - result  saved to $pdlp"
echo " - logging saved to $pdlp/*.log"
echo "-------------------------------------"