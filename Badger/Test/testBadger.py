#!/usr/bin/env python
import time
import pprint
import DIRAC
import os
from DIRAC.Core.Base import Script
Script.parseCommandLine(ignoreErrors=True)
#from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient
args = Script.getPositionalArgs()
strArgs = ' '.join(args)
from BESDIRAC.Badger.API.Badger import Badger
badger = Badger()

def query():
  result = badger.getFilesByMetadataQuery('eventType=all bossVer=6.6.3 resonance=4260 runL>=29755 runH<29760 runL!=29756')
  pprint.pprint(result)

def add(dn,path,con):
  result = badger.registerDataset(dn,path,con)
  pprint.pprint(result)

def get(dn):
  result = badger.getDatasetDescription(dn)
  pprint.pprint(result)

def list():
  result = badger.listDatasets()
  pprint.pprint(result)

def byName(dn):
  result = badger.getFilesByDatasetName(dn)
  pprint.pprint(result)

def release(dn):
  result = badger.releaseDataset(dn)
  pprint.pprint(result)

def freeze(dn):
  result = badger.freezeDataset(dn)
  pprint.pprint(result)


if __name__=="__main__":
  list()
  #jget("runL_GTE_29758")
  #byName("runL_GTE_29758")
  #freeze("runL_GTE_29758")
  #release("runL_GTE_29758")
  #kkadd("runL_GTE_29758",'/zhanggang_test',"runL>=29757")
