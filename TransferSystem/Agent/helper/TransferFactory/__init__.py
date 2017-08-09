#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: lintao

import subprocess

import DIRAC
from DIRAC import gLogger

class TransferFactory(object):
  PROTOCOL = ["DIRACFTS", "DIRACDMS"]

  def generate(self, protocol, info):
    gLogger.info("Load Module:")
    gLogger.info("BESDIRAC.TransferSystem.Agent.helper.TransferFactory.TransferBy%s"%(protocol))

    try:
      mod = __import__("BESDIRAC.TransferSystem.Agent.helper.TransferFactory.TransferBy%s"%(protocol),
          globals(),
          locals(),
          ["%sTransferWorker"%(protocol)]
          )
      TR = getattr(mod, "%sTransferWorker"%(protocol))
    except Exception as e:
      gLogger.error('Load transfer protocol "%s" error: %s' % (protocol, e))
      return None

    tr = TR()
    tr.create_popen(info)
    return tr


gTransferFactory = TransferFactory()
