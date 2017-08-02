import math
from datetime import datetime, timedelta
from WebAppDIRAC.Lib.WebHandler import WebHandler, asyncGen
from DIRAC.Core.DISET.RPCClient import RPCClient



class SAMHistoryHandler(WebHandler):
    
  AUTH_PROPS = "authenticated"
        
  @asyncGen
  def web_getPlotData(self):
    publisher = RPCClient('ResourceStatus/PublisherIHEP')
    
    args = self._request()
    category = args[ 'Category' ]
    elementType = args[ 'ElementType' ]
    if 'Elements' not in args:
      elements = yield self.threadTask(self.__getElementsByType, elementType, publisher)
    else:
      elements = args[ 'Elements' ]
    vo = args.get( 'VO' ) or 'all'
    fromDatetime = args[ 'From' ].replace(minute = 0)
    toDatetime = args[ 'To' ].replace(minute = 0)
    
    if category == 'TestResults':
      testHistory = yield self.threadTask(publisher.getTestHistory, elementType, elements[ 0 ], fromDatetime, toDatetime)
      if not testHistory[ 'OK' ]:
        self.finish({ 'success' : 'false', 'result' : [], 'error' : testHistory[ 'Message' ] })
        return
      testHistory = testHistory[ 'Value' ]
      if not testHistory:
        self.finish({ 'success' : 'false', 'result' : [], 'error' : 'There are no data to display.' })
        return
      data, elements, timestamps = self.__generDetailData(testHistory, fromDatetime, toDatetime)
      self.finish({ 'success' : 'true', 'result' : data, 'elements' : elements, 'timestamps' : timestamps })
    
    else:
      if elementType == 'Site':
        statusHistory = yield self.threadTask(publisher.getSiteStatusHistory, elements, vo, fromDatetime, toDatetime)
      else:
        statusHistory = yield self.threadTask(publisher.getResourceStatusHistory, elements, vo, fromDatetime, toDatetime)
      if not statusHistory[ 'OK' ]:
        self.finish({ 'success' : 'false', 'result' : [], 'error' : statusHistory[ 'Message' ] })
        return
      statusHistory = statusHistory[ 'Value' ]
      if not statusHistory:
        self.finish({ 'success' : 'false', 'result' : [], 'error' : 'There are no data to display.' })
        return
    
      if category == 'Availability':
        data, elements = self.__generSummaryData(statusHistory)
        self.finish({ 'success' : 'true', 'result' : data, 'elements' : elements })
      else:
        data, elements, timestamps = self.__generDetailData(statusHistory, fromDatetime, toDatetime)
        self.finish({'success' : 'true', 'result' : data, 'elements' : elements, 'timestamps' : timestamps })


  @asyncGen
  def web_getElements(self):
    publisher = RPCClient('ResourceStatus/PublisherIHEP')
    
    elementType = self._request()[ 'ElementType' ]
    elements = yield self.threadTask(self.__getElementsByType, elementType, publisher)
      
    data = []
    for el in elements:
      data.append(dict( value = el, text = el ))
      
    self.finish({ 'success' : 'true', 'result' : data })
    

  @asyncGen
  def web_getVOs(self):
    publisher = RPCClient('ResourceStatus/PublisherIHEP')
    
    vos = yield self.threadTask( publisher.getVOs )
    if vos[ 'OK' ]:
      vos = vos[ 'Value' ]
    else:
     self.finish( { 'success' : 'false', 'error' : vos[ 'Message' ] } )
      
    defaultVO = yield self.threadTask( publisher.getVOByGroup, self.getSessionData()[ 'user' ][ 'group' ] )
    defaultVO = defaultVO[ 'Value' ]
    
    self.finish( { 'success' : 'true', 'result' : { 'VOs' : vos, 'defaultVO' : defaultVO } } )


  def __getElementsByType(self, elementType, publisher):
    elements = []
    if 'Site' == elementType:
      elements = publisher.getSites()[ 'Value' ]
    elif 'ComputingElement' == elementType:
      elements = publisher.getComputingElements()[ 'Value' ]
      elements += publisher.getDomainSites('CLOUD')[ 'Value' ]
    elif 'StorageElement' == elementType:
      elements = publisher.getStorageElements()[ 'Value' ]
    return elements


  def __generSummaryData(self, historyData):
    summaryData = []
    
    for element, historyList in historyData.items():
      okNum = 0
      for date, status in historyList:
        if status == 'OK' or status == 'Busy':
          okNum += 1
      okRate = math.floor((float(okNum) / len(historyList)) * 10000) / 100
      summaryData.append(( element, okRate ))
      
    summaryData.sort(key = lambda e : e[ 0 ])
    elements = [ e[0] for e in summaryData ]
    data = [ e[ 1 ] for e in summaryData ]
    return data, elements
        
        
  def __generDetailData(self, historyData, fromDate, toDate):
    detailData = []
    
    interval = self.__getInterval(fromDate, toDate)
    timestamps = self.__getTimeStampsByInterval(fromDate, toDate, interval)
    dateFormat = self.__getDateFormatByInterval(interval)
    
    for element, historyList in historyData.items():
      stampIdx = 0
      showStatuses = []
      oriStatuses= []
      for date, status in historyList:
        while(stampIdx < len(timestamps) - 1 and date >= timestamps[ stampIdx + 1 ]):
          showStatuses.append(self.__combine(oriStatuses))
          stampIdx += 1
          oriStatuses = []
        oriStatuses.append(status)
      while(stampIdx < len(timestamps)):
        showStatuses.append(self.__combine(oriStatuses))
        stampIdx += 1
        oriStatuses = []
      detailData.append(( element, showStatuses ))
      
    detailData.sort(key = lambda e : e[ 0 ])
    elements = [ e[ 0 ] for e in detailData ]
    data = [ e[ 1 ] for e in detailData ]
    timestamps = map(lambda arg : arg.strftime(dateFormat), timestamps)
    return data, elements, timestamps

    
  def __combine(self, statuses):
    if len(statuses) == 0:
      return None
    if float(statuses.count('Unknown')) / len(statuses) > 0.9:
      return  -1
    if float(statuses.count('Busy')) / len(statuses) > 0.9:
      return  -2
    return math.floor(float(statuses.count('OK') + statuses.count('Busy')) / len(statuses) * 100) / 100


  def __getInterval(self, fromDate, toDate):
    interval = toDate - fromDate
    if interval > timedelta(days = 210):
      return 'month'
    if interval >timedelta(days = 7):
      return 'day'
    return 'hour'


  def __getDateFormatByInterval(self, interval):
    if 'month' == interval:
      return '%Y-%m'
    if 'day' == interval:
      return '%m-%d'
    if 'hour' == interval:
      return '%m-%d %H:00'
  
  
  def __getTimeStampsByInterval( self, fromDate, toDate, interval ):
    timestamps = []
    
    if 'month' == interval:
      fromY = fromDate.year
      fromM = fromDate.month
      stamp = datetime.strptime('%d-%d' % (fromY, fromM), '%Y-%m')
      while stamp <= toDate:
        timestamps.append(stamp)
        fromY += fromM / 12
        fromM = (fromM % 12) + 1
        stamp = datetime.strptime('%d-%d' % (fromY, fromM), '%Y-%m')
        
    elif 'day' == interval:
      stamp = datetime.strptime(fromDate.strftime('%Y-%m-%d'), '%Y-%m-%d')
      while stamp <= toDate:
        timestamps.append(stamp)
        stamp += timedelta(days = 1)
        
    elif 'hour' == interval:
      stamp = datetime.strptime(fromDate.strftime('%Y-%m-%d %H'), '%Y-%m-%d %H')
      while stamp < toDate:
        timestamps.append(stamp)
        stamp += timedelta(hours = 1)
    
    return timestamps

    
  def _request(self):
    args = {}
    
    if 'category' in self.request.arguments:
      args[ 'Category' ] = self.request.arguments[ 'category' ][ 0 ]
      
    if 'elementType' in self.request.arguments:
      args[ 'ElementType' ] = self.request.arguments[ 'elementType' ][ 0 ]
      
    if 'elements' in self.request.arguments:
      args[ 'Elements' ] = self.request.arguments[ 'elements' ]

    if 'vo' in self.request.arguments and self.request.arguments[ 'vo' ][ 0 ] != '' :
      args[ 'VO' ] = self.request.arguments[ 'vo' ][ 0 ]

    if 'from' in self.request.arguments:
      args[ 'From' ] = datetime.strptime(self.request.arguments[ 'from' ][ 0 ], '%Y-%m-%d %H:%M')
      
    if 'to' in self.request.arguments:
      args[ 'To' ] = datetime.strptime(self.request.arguments[ 'to' ][ 0 ], '%Y-%m-%d %H:%M')
    
    return args
