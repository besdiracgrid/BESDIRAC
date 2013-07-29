#!/usr/bin/env python
# -* coding:utf-8 -*-
# author: linlei

from optparse import OptionParser
import os
import sys
import os.path
import uuid
import time
from itertools import islice
import string

parser=OptionParser()
parser.add_option('--frm',dest='linefrm',help='which line will be handled first')
parser.add_option('--to',dest='lineto',help='which line will be handled at last')
parser.add_option('--dst',dest='dstfiles',help='a text that contains dst files')
#parser.add_option('--root',dest='rootfile',help='root file')
parser.add_option('--resonance',dest='resonance',help='If you want to check resonance attribute,please input its value')
parser.add_option('--expNum',dest='expNum',help='If you want to check experiment number attribute,please input its value')
parser.add_option('--bossVer',dest='bossVer',help='If you want to check boss version attribute,please input its value')
parser.add_option('--eventType',dest='eventType',help='If you want to check event type attribute,please input its value')
parser.add_option('--streamId',dest='streamId',help='If you want to check streamid attribute,please input its value')

(options,args) = parser.parse_args()
linefrm = string.atoi(options.linefrm)
lineto = string.atoi(options.lineto)
dstfiles = options.dstfiles
#rootfile = options.rootfile

#print "linefrm",linefrm
#print "lineto",lineto
#print "dstfiles",dstfiles
#print "rootfile",rootfile

checkattributes = {}
if options.resonance is not None:
    checkattributes["resonance"] = options.resonance
if options.expNum is not None:
    checkattributes["expNum"] = options.expNum
if options.bossVer is not None:
    checkattributes["bossVer"] = options.bossVer
if options.eventType is not None:
    checkattributes["eventType"] = options.eventType
if options.streamId is not None:
    checkattributes["streamId"] = options.streamId
   
#print "checkattributes:",checkattributes
#print "rootfile:",rootfile

import sys
tmp=sys.argv[0]
sys.argv=[]
sys.argv.append(tmp)
 
from n_readAttributes import DataAll,Others
from n_insertToCatalogue import insert
from n_judgeType import judgeType
from n_compare import compare


totaltime = 0
#store number of files which have been uploaded or checked
linenum = linefrm

start = time.time()
if os.path.exists(dstfiles):
    file = open(dstfiles,"r")

    #print dstfiles
    for f in islice(file,linefrm,lineto):
        dstfile = f.strip()
        #print "dstfile:",dstfile
        if os.path.exists(dstfile):
          #  print dstfile
            type = judgeType(dstfile)
            #type = judgeType(dstfile)
            #print "type of file %s is %s"%(dstfile,type)

            linenum = linenum+1

            if type=='all':
                obj = DataAll(dstfile)
            elif type=='others':
                obj = Others(dstfile)
            elif type==None:
                print "name of %s is not correct"%dstfile
                continue

            #get bossVer,eventNum,dataType,fileSize,LFN,eventType,expNum,
            #resonance,runH,runL,status,streamId,description
            attributes = obj.getAttributes()
            #print "attributes:%s"%str(attributes)
        
            if attributes=='error':
                continue
            else:
                #get Guid
                #attributes["guid"] = uuid.uuid1()

                #get Date
                now = time.localtime()
                date = time.strftime('%Y-%m-%d %H:%M:%S',now)
                attributes["date"] = date  
                #print 100*'#'
                #print attributes
                #print 100*'#'
                
                if len(checkattributes)==0:
                    insert(attributes)
                    print "OK"
                else:
                    errorlist = compare(attributes,checkattributes)
                    if len(errorlist)!=0:
                        print dstfile
                        print "Error for attributes below"
                        for key in errorlist.keys():
                            print "%s     in DFC:%s     input:%s"%(key,errorlist[key],checkattributes[key])

            
                
end = time.time()
totaltime = end - start
num = linenum - linefrm

print "The number of files you have inserted or checked :%d" %num
print "Total time is:%s"%str(totaltime)
