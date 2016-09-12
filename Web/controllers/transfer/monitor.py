#-*- coding: utf-8 -*-

from dirac.lib.base import *
from dirac.lib.webBase import defaultRedirect
import dirac.lib.credentials as credentials
from dirac.lib.diset import getRPCClient

from DIRAC import gLogger

from BESDIRAC.TransferSystem.DB.TransferDB import TransRequestEntryWithID
from BESDIRAC.TransferSystem.DB.TransferDB import TransFileListEntryWithID

class MonitorController(BaseController):

  def index(self):
    return render("/transfer/monitor.mako")

  @jsonify
  def reqs(self):
    result_of_reqs = {'num': 0, 'data': []}
    #username = str(credentials.getUsername())
    RPC = getRPCClient("Transfer/TransferRequest")
    cond = {}
    res = RPC.statustotal(cond)
    if not res["OK"]:
      return result_of_reqs
    result_of_reqs["num"] = res["Value"]

    # get start/limit
    start = 0
    limit = result_of_reqs["num"]
    orderby = ["id:DESC"]

    if request.params.has_key("start"):
      start = int(request.params["start"])
    if request.params.has_key("limit"):
      limit = int(request.params["limit"])

    res = RPC.statuslimit(cond, orderby, start, limit)
    if not res["OK"]:
      gLogger.error(res)
      return result_of_reqs
    result = res["Value"]

    # handle the datetime
    # convert datetime to string
    def quickconv(d):
      from  datetime import datetime
      # submit time is the 5th.
      return dict(zip(TransRequestEntryWithID._fields, tuple(r.strftime("%Y-%m-%d %H:%M [UTC]") if isinstance(r, datetime) else r for r in d )))
    result = map(quickconv, result)

    result_of_reqs["data"] = result

    return result_of_reqs

  @jsonify
  def req(self):
    result_of_files = {'num': 0, 'data': []}
    if not request.params.has_key("req_id"):
      return result_of_files
    try:
      reqid = int(request.params["req_id"])
    except ValueError:
      return result_of_files

    RPC = getRPCClient("Transfer/TransferRequest")
    cond = {"trans_req_id": reqid}
    res = RPC.show(cond)
    if not res["OK"]:
      return result_of_files
    result = res["Value"]

    def quickconv(d):
      from  datetime import datetime
      # submit time is the 5th.
      return dict(zip(TransFileListEntryWithID._fields, tuple(r.strftime("%Y-%m-%d %H:%M [UTC]") if isinstance(r, datetime) else r for r in d )))
    result = map(quickconv, result)

    result_of_files["num"] = len(result)
    result_of_files["data"] = result

    return result_of_files
