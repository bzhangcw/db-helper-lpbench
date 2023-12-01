# /*
#  * Created Date: Monday, November 18th 2023, 11:29:23 am
#  * Author: C. Zhang
#  *
#  * Copyright (c) 2023
#  */

if [ "$#" -ne 4 ]; then
  echo "Script for running CUPDLP in batch mode..."
  echo "Usage: <dataset directory> <output> <time limit for each instance> <eps>" 1>&2
  exit -1
fi

wdir=$(pwd)
# test set
data=$1
output=$2
timelimit=$3
precision=$4
eps=1e-$precision

name=cupdlp_1e-${precision}
pdhg=$output/$name
pdhgbin=release/bin/cupdlpc

mkdir -p $pdhg

cd $wdir/$pdhgsrc
for f in $(/bin/ls $data/*.mps); do

  ff=$(basename -s .mps $f)
  cmd="$pdhgbin \
   -nIterLim 2000000 \
   -dTimeLim $timelimit \
   -fname $data/$ff.mps \
   -dPrimalTol $eps \
   -dDualTol $eps \
   -dGapTol $eps \
   -dFeasTol $eps \
   -iScalingMethod 3 \
   -ifScaling 1 \
   -eLineSearchMethod 2 \
   -eRestartMethod 1 \
   -out $pdhg/$ff.json &> $pdhg/$ff.log"

  echo $cmd 

done
