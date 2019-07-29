#!/usr/bin/env python

import socket, subprocess, time

hostname = socket.gethostname()

commands = """
ls /cvmfs/juno.ihep.ac.cn
version=`more /etc/redhat-release|tr -cd "[0-9][.]"`
version1=${version%.*}
version2=${version1%.*}
export LD_LIBRARY_PATH=/cvmfs/juno.ihep.ac.cn/sl6_amd64_gcc44/common/lib:/usr/lib64/:$LD_LIBRARY_PATH
if [ $version2 -gt 6 ]; then
  echo "use sl7 juno software version"
  export CMTCONFIG=amd64_linux26
  source /cvmfs/juno.ihep.ac.cn/sl7_amd64_gcc48/Release/J17v1r1/setup.sh
else
  echo "use sl6 juno software version"
  export CMTCONFIG=Linux-x86_64
  source /cvmfs/juno.ihep.ac.cn/sl6_amd64_gcc44/J17v1r1/setup.sh
fi
python /cvmfs/juno.ihep.ac.cn/sl6_amd64_gcc44/J17v1r1/offline/Examples/Tutorial/share/tut_detsim.py gun
"""

start = time.time()
subp = subprocess.Popen( ['bash', '-c', commands], stdout = subprocess.PIPE, stderr = subprocess.PIPE )
stdout, stderr = subp.communicate()
runningTime = time.time() - start

print 'Host Name :', hostname
print 'Running Time :', runningTime
print '\n'
if stdout:
    print '==============================Standard Output==============================\n'
    print stdout
    print '\n'
if stderr:
    print '==============================Standard Error===============================\n'
    print stderr
