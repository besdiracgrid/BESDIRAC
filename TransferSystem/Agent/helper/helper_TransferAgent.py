# -*- coding: utf-8 -*-

import datetime
import random

from DIRAC import gLogger, gConfig, S_OK, S_ERROR
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog

from BESDIRAC.TransferSystem.DB.TransferDB import TransRequestEntryWithID
from BESDIRAC.TransferSystem.DB.TransferDB import TransFileListEntryWithID

from BESDIRAC.TransferSystem.Agent.helper.TransferFactory import gTransferFactory

from BESDIRAC.AccountingSystem.Client.Types.DataTransfer import DataTransfer

class helper_TransferAgent(object):

  def __init__(self, transferAgent, gTransferDB):
    self.transferAgent =transferAgent
    self.transferDB = gTransferDB
    gLogger.info("Creating File Catalog")
    self.fileCatalog = FileCatalog()

  def helper_add_transfer(self, result):
    if not result:
      gLogger.error("There is no infomation")
      return False

    res = self.transferDB.get_TransferRequest(condDict={
                                                      "id": result.trans_req_id
                                                      })
    if not res["OK"]:
      return False
    req_list = res["Value"]
    if len(req_list) != 1:
      return False
    req =  TransRequestEntryWithID._make(req_list[0])

    # construct the info
    info = {"id": result.id,
            "LFN": result.LFN,
            "srcSE": req.srcSE,
            "dstSE": req.dstSE,
            "retransfer": -1,
            "error": ""}
    # Add the Transfer
    worker = gTransferFactory.generate(req.protocol, info)
    if worker is None:
      return True
    self.transferAgent.transfer_worker.append(worker)
    # Change the status
    self.helper_status_update(
        self.transferDB.tables["TransferFileList"],
        result.id,
        {"status":"transfer", 
          "start_time":datetime.datetime.utcnow()})
    # Add Accounting:
    d = {}
    d["User"] = req.username
    d["Source"] = req.srcSE
    d["Destination"] = req.dstSE
    d["Protocol"] = req.protocol
    d["FinalStatus"] = "OK"
    d["TransferSize"] = 0 # TODO
    r = self.fileCatalog.getFileSize(result.LFN)
    if r["OK"]:
      if r["Value"]["Successful"]:
        d["TransferSize"] = r["Value"]["Successful"][result.LFN]
    d["TransferTime"] = 1 # 1s 
    d["TransferOK"] = 1
    d["TransferTotal"] = 1
    acct_dt = DataTransfer()
    acct_dt.setValuesFromDict(d)
    acct_dt.setNowAsStartAndEndTime()
    # save it 
    worker.acct_dt = acct_dt

    return True

  def helper_remove_transfer(self, worker):
    info = worker.info
    gLogger.info("File.id = %d -> finish" % info["id"])
    self.helper_status_update(
        self.transferDB.tables["TransferFileList"],
        info["id"],
        {"status":"finish", 
          "finish_time": datetime.datetime.utcnow()})
    # Accounting
    acct_dt = worker.acct_dt
    acct_dt.setEndTime()
    # TODO
    d = {}
    td = acct_dt.endTime-acct_dt.startTime
    td_s = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
    d["TransferTime"] = td_s # 1s 
    if info["error"]:
      d["FinalStatus"] = "FAILED"
      d["TransferOK"] = 0
    else:  
      d["FinalStatus"] = "OK"
      d["TransferOK"] = 1

    acct_dt.setValuesFromDict(d)

    acct_dt.commit()
    gLogger.info("Submit Accounting Data")
    
  def helper_check_request(self):
    """
      check if the *transfer* request are ok.
      if the whole files are *finish*, then this request
      will become *finish*.
    """
    infoDict = {"status": "transfer"}
    res = self.transferDB.get_TransferRequest(condDict = infoDict)
    if not res["OK"]:
      return
    reqlist = map(TransRequestEntryWithID._make, res["Value"])
    for req in reqlist:
      res = self.transferDB._query(
          'select count(*) from %(table)s where trans_req_id = %(id)d and status not in %(status_list)s' % {
             "table": self.transferDB.tables["TransferFileList"], 
             "id": req.id,
             "status_list": '("finish", "kill")' # XXX finish or kill means this request is ok.
             }
          )
      if not res["OK"]:
        # TODO
        continue
      count = res["Value"][0][0]
      if count == 0:
        # if all status is finish,
        # the req status --> finish
        gLogger.info("req.id %d change from %s to finish" % (req.id, req.status))
        self.helper_status_update(
            self.transferDB.tables["TransferRequest"],
            req.id,
            {"status":"finish"})
    return 

  def helper_get_new_request(self):
    # 1. get the *new* File in the <<Transfer File List>>.
    #    if we get, goto <<Add New Transfer>>
    already_load_status = False
    result_new_file = self.helper_get_new_File()
    # 1.1 2014.04.20
    #     They want to the other requests are also loaded,
    #     so I have to not return immediately
    if result_new_file:
      already_load_status = True
    # 2. if we can't get, use should get a *new* request
    #    from the <<Transfer Request>>.
    #    if we can't get, return False. STOP
    self.helper_check_request()
    result = self.helper_get_new_request_entry()
    if result:
      # 3. add the filelist in the dataset to the << Transfer File List >>
      condDict = {"name":result.dataset}  
      res = self.transferDB.get_Dataset(condDict)
      if not res["OK"]:
        gLogger.error(res)
        return None
      filelist = res["Value"]
      # update the status in << Request >>
      if len(filelist) > 0:
        req_status = "transfer"
      else:
        req_status = "finish"
      self.helper_status_update(self.transferDB.tables["TransferRequest"],
                                result.id,
                                {"status":req_status})
      self.transferDB.insert_TransferFileList(result.id, filelist)
    # 4. get the *new* File Again.
    # 5. can't get, return False. STOP
    # 4.prelude
    #    If already loaded, return the last result
    if already_load_status and result_new_file:
      return result_new_file
      
    result = self.helper_get_new_File()
    return result

  def helper_get_new_request_entry(self):
    """
    TransRequestEntryWithID(
      id=1L, 
      username='lintao', 
      dataset='my-dataset', 
      srcSE='IHEP-USER', 
      dstSE='IHEPD-USER', 
      submit_time=datetime.datetime(2013, 3, 13, 20, 9, 34), 
      status='new')
    """
    condDict = {"status": "new"}
    res = self.transferDB.get_TransferRequest(condDict)
    if not res["OK"]:
      return None
    req_list = res["Value"]
    len_req = len(req_list)
    if len_req:
      # random select
      tmp_idx = random.randint(0, len_req-1)
      return TransRequestEntryWithID._make(req_list[tmp_idx])
    pass

  def helper_get_new_File(self):
    """
    >>> helper.helper_get_new_File()
    TransFileListEntryWithID(
      id=1L, 
      LFN='/path/does/not/exist', 
      trans_req_id=1L, 
      start_time=None, 
      finish_time=None, 
      status='new')
    """
    condDict = {"status": "new"}
    res = self.transferDB.get_TransferFileList(condDict)
    if not res["OK"]:
      gLogger.error(res)
      return None
    filelist = res["Value"]
    gLogger.info("Filelist:")
    gLogger.info(filelist)
    len_files = len(filelist)
    if  len_files > 0:
      tmp_idx = random.randint(0, len_files-1)
      gLogger.info("get file entry index randomly: %d/%d"%(tmp_idx, len_files))
      gLogger.info("get file entry", filelist[tmp_idx])
      return TransFileListEntryWithID._make(filelist[tmp_idx])
    return None

  def helper_status_update(self, table, id, toUpdate):
    res = self.transferDB.updateFields(
                              table,
                              updateDict = toUpdate,
                              condDict = {"id":id},
                              )
    print res

  def helper_error_report(self, worker, reason):
    self.helper_status_update(self.transferDB.tables["TransferFileList"],
                              worker.info["id"],
                              {"error": reason})

  def check_worker_status(self, worker):
    """check whether the file transfer is kill(in DB)"""
    res = self.transferDB.getFields(self.transferDB.tables["TransferFileList"],
                                    outFields = ["status"],
                                    condDict = {"id":worker.info["id"]})
    if not res["OK"]:
      gLogger.error(res)
      return

    if not res["Value"]:
      return

    if len(res["Value"]) != 1:
      gLogger.error[res]
      return 

    status = res["Value"][0][0]
    if status == "kill":
      gLogger.info("check worker should be killed: ", status)
      worker.proc.kill()

if __name__ == "__main__":
  from DIRAC.Core.Base import Script
  Script.parseCommandLine( ignoreErrors = True )

  from BESDIRAC.TransferSystem.DB.TransferDB import TransferDB 
  gTransferDB = TransferDB()
  transferAgent = gTransferDB
  transferAgent.transfer_worker = []
  helper = helper_TransferAgent(transferAgent, gTransferDB)
  entry = helper.helper_get_new_File()
  print helper.helper_get_new_request_entry()

  if entry:
    print helper.helper_status_update( table = "TransferFileList", 
                                       id = entry.id,
                                       toStatus = {"status":"transfer"})

  print helper.helper_check_request()
  print helper.helper_add_transfer(entry)
  print transferAgent.transfer_worker

  pass
