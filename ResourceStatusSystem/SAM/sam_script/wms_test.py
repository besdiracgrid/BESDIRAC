#!/usr/bin/env python

import socket, time

start = time.time()
hostname = socket.gethostname()
runningTime = time.time() - start

print 'hello, ' + hostname + '\n'
print 'Running Time :', runningTime
