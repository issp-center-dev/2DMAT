set -e

maindir=$(cd "$(dirname $0)"; pwd)

res=0
failedlist=""

for subdir in varied_param_v1 fixed_param_v1 varied_param_v2 fixed_param_v2; do
  cd $maindir
  cd $subdir
  echo Start test on $subdir
  res=0
  sh ./do.sh || res=$?
  if [ $res -ne 0 ]; then
    failedlist="${failedlist} ${subdir}"
  fi
  echo Finish test on $subdir
  echo
done

echo Summary:

if [ -z "$failedlist" ]; then
  echo All test PASSED
  true
else
  echo SOME OF TEST FAILED:
  echo $failedlist
  false
fi
