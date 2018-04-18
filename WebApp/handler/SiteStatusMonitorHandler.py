import json, math
from DIRAC                      import S_OK
from WebAppDIRAC.Lib.WebHandler import WebHandler, WErr, WOK, asyncGen
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.Interfaces.API.DiracAdmin import DiracAdmin


class SiteStatusMonitorHandler( WebHandler ):

  AUTH_PROPS = "authenticated"

  @asyncGen
  def web_getSelectionData( self ):
    publisher = RPCClient( 'ResourceStatus/PublisherIHEP' )

    callback = {}
    ret = { 'success' : 'true', 'result' : callback }

    data = self.getSessionData()
    vo = yield self.threadTask( publisher.getVOByGroup, data[ 'user' ][ 'group' ] )
    vo = vo[ 'Value' ]
    if vo != '':
      ret[ 'defaultVO' ] = vo

    allSites = yield self.threadTask( publisher.getSites )
    if allSites[ 'OK' ]:
      if vo != '':
        sites = []
        for site in allSites[ 'Value' ]:
          if vo in publisher.getSiteVO( site )[ 'Value' ]:
            sites.append( [ site ] )
      else:
        sites = [ [ site ] for site in allSites[ 'Value' ] ]
    else:
      sites = [ [ 'Error happened on service side' ] ]

    types = yield self.threadTask( publisher.getDomains )
    if types[ 'OK' ]:
      types = [ [ type ] for type in types[ 'Value' ] ]
    else:
      types = [ [ 'Error happened on service side' ] ]

    mask = [ [ 'Active' ], [ 'Banned' ] ]

    vos = yield self.threadTask( publisher.getVOs )
    if vos[ 'OK' ]:
      vos = [ [ vo ] for vo in vos[ 'Value' ] ]
    else:
      vos = [ [ 'Error happened on service side' ] ]

    callback[ 'site' ] = sites
    callback[ 'type' ] = types
    callback[ 'mask' ] = mask
    callback[ 'vo' ] = vos

    self.finish( ret )


  @asyncGen
  def web_getMainData( self ):
    publisher = RPCClient( 'ResourceStatus/PublisherIHEP' )

    sitesDict = {}

    sites = yield self.threadTask( publisher.getSites )
    if not sites[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : sites[ 'Message' ] } )
      return
    sites = sites[ 'Value' ]

    sitesType = self.__getSitesType( sites )

    sitesMask = yield self.threadTask( self.__getSitesMaskStatus, sites )
    if not sitesMask[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : sitesMask[ 'Message' ] } )
      return
    sitesMask = sitesMask[ 'Value' ]

    sitesVO= yield self.threadTask( self.__getSitesVO, sites )
    if not sitesVO[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : sitesVO[ 'Message' ] } )
      return
    sitesVO = sitesVO[ 'Value' ]

    for site in sites:
      sitesDict[ site ]= {}
      sitesDict[ site ][ 'SiteType' ] = sitesType[ site ]
      sitesDict[ site ][ 'MaskStatus' ] = sitesMask[ site ]
      sitesDict[ site ][ 'VO' ] = sitesVO[ site ]

    req = self._request()

    selectedSites = req.get( 'Site' )
    selectedType = req.get( 'SiteType' )
    selectedMask = req.get( 'MaskStatus' )
    selectedVOs = req.get( 'VO' )

    sitesDict = yield self.threadTask( self.__siteFilte, sitesDict, selectedSites, selectedType, selectedMask, selectedVOs )

    if not sitesDict:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : 'There are no data to display' } )
      return

    summarys = []

    samSummary = yield self.threadTask( publisher.getSitesSAMSummary, sitesDict.keys(), selectedVOs )
    if not samSummary[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : samSummary[ 'Message' ] } )
      return 
    summarys.append( samSummary[ 'Value' ] )

    storageSummary = yield self.threadTask( publisher.getSitesStorageSummary, sitesDict.keys() )
    if not storageSummary[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : storageSummary[ 'Message' ] } )
      return 
    summarys.append( storageSummary[ 'Value' ] )

    jobSummary = yield self.threadTask( publisher.getSitesJobSummary, sitesDict.keys() )
    if not jobSummary[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : jobSummary[ 'Message' ] } )
      return 
    summarys.append( jobSummary[ 'Value' ] )

    wnSummary = yield self.threadTask( publisher.getSitesWNSummary, sitesDict.keys() )
    if not wnSummary[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : wnSummary[ 'Message' ] } )
      return 
    summarys.append( wnSummary[ 'Value' ] )

    for summary in summarys:
      for site, summaryDict in summary.items():
        sitesDict[ site ].update( summaryDict )

    callback = []

    for siteName, siteDict in sitesDict.items():
      siteDict[ 'Site' ] = siteName
      callback.append( siteDict )

    self.finish( { 'success' : 'true', 'result' : callback, 'total' : len( callback ) } )


  @asyncGen        
  def web_getSAMData( self ):
    publisher = RPCClient( 'ResourceStatus/PublisherIHEP' )

    req = self._request()
    site = req[ 'Site' ][ -1 ].encode()
    if req.has_key( 'VO' ):
      vo = req[ 'VO' ][ -1 ].encode()
    else:
      vo = 'all'

    samSummary = yield self.threadTask( publisher.getSAMSummary, site, vo )
    if not samSummary[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : samSummary[ 'Message' ] } )
      return
    samSummary = samSummary[ 'Value' ]

    callback = []
    columns = []
    for elementName, samDict in samSummary.items():
      columns += samDict.keys()
      samDict[ 'ElementName' ] = elementName
      callback.append( samDict )
    columns = list( set( columns ) )
    columns.remove( 'ElementType' )
    columns.remove( 'Status' )

    self.finish( { 'success' : 'ture', 'result' : callback, 'columns' : columns, 'total' : len( callback ) } )


  @asyncGen
  def web_getSAMDetail( self ):
    publisher = RPCClient( 'ResourceStatus/PublisherIHEP' )

    elementName = self.request.arguments[ 'elementName' ][ -1 ]
    testType = self.request.arguments[ 'testType' ][ -1 ]

    samDetail = yield self.threadTask( publisher.getSAMDetail, elementName, testType )
    if not samDetail[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : samDetail[ 'Message' ] } )
      return
    samDetail = samDetail[ 'Value' ]

    samDetail[ 'SubmissionTime' ] = samDetail[ 'SubmissionTime' ].strftime( '%Y-%m-%d %H:%M' ) + ' UTC'
    if samDetail[ 'CompletionTime' ]:
      samDetail[ 'CompletionTime' ] = samDetail[ 'CompletionTime' ].strftime( '%Y-%m-%d %H:%M' ) + ' UTC'
    if samDetail[ 'ApplicationTime' ]:
      samDetail[ 'ApplicationTime' ] = str( samDetail[ 'ApplicationTime' ] ) + ' seconds'
    for key in samDetail:
      samDetail[ key ] = samDetail[ key ] or '-'

    self.finish( { 'success' : 'ture', 'result' : samDetail } )


  @asyncGen        
  def web_getWorkNodeData( self ):
    publisher = RPCClient( 'ResourceStatus/PublisherIHEP' )

    req = self._request()
    site = req[ 'Site' ][ -1 ].encode()

    wnsInfo = yield self.threadTask( publisher.getSiteWNsInfo, site )
    if not wnsInfo[ 'OK' ]:
      self.finish( { 'success' : 'false', 'result' : [], 'total' : 0, 'error' : wnsInfo[ 'Message' ] } )
      return
    wnsInfo = wnsInfo[ 'Value' ]

    totalRunning = 0
    totalDone = 0
    totalFailed = 0
    for record in wnsInfo:
      totalDone += record[ 'Done' ]
      totalFailed += record[ 'Failed' ]  
    if totalDone == 0 and totalFailed == 0:
      efficiency = ''
    else:
      efficiency = math.floor(float(totalDone) / (totalDone + totalFailed) * 1000) /10

    wnsInfo.append({ 'Host' : 'total',
                    'Done' : totalDone,
                    'Failed' : totalFailed,
                    'Efficiency' : efficiency })

    self.finish( { 'success' : 'ture', 'result' : wnsInfo, 'total' : len( wnsInfo ) } )


  def __siteFilte( self, sitesDict, selectedSites = None, selectedType = None, selectedMask = None, selectedVOs = None ):
    for siteName, siteDict in sitesDict.items():

      if selectedSites is not None and siteName not in selectedSites:
        del sitesDict[ siteName ]
        continue

      siteType = siteDict[ 'SiteType' ]
      if selectedType is not None and siteType not in selectedType:
        del sitesDict[ siteName ]
        continue

      siteMask = siteDict[ 'MaskStatus' ]
      if selectedMask is not None and siteMask not in selectedMask:
        del sitesDict[ siteName ]
        continue

      siteVO = siteDict[ 'VO' ]
      if selectedVOs is not None and siteVO:
        isSelected = False
        for vo in siteVO:
          if vo in selectedVOs:
            isSelected = True
            break                   
        if not isSelected:
          del sitesDict[ siteName ]

    return sitesDict


  def __getSitesType( self, sitesName ):
    sitesType = {}

    for siteName in sitesName:
      sitesType[ siteName ] = siteName.split( '.' )[ 0 ]

    return sitesType


  def __getSitesMaskStatus( self, sitesName ):
    diracAdmin = DiracAdmin()
    activeSites = diracAdmin.getSiteMask()
#    wmsAdmin = RPCClient( 'WorkloadManagement/WMSAdministrator' )
#    activeSites = wmsAdmin.getSiteMask()

    if not activeSites[ 'OK' ]:
      return activeSites
    activeSites = activeSites[ 'Value' ]

    sitesStatus = {}

    for siteName in sitesName:
      if siteName in activeSites:
        sitesStatus[ siteName ] = 'Active'
      else:
        sitesStatus[ siteName ] = 'Banned'

    return S_OK( sitesStatus )


  def __getSitesVO( self, sitesName ):
    publisher = RPCClient( 'ResourceStatus/PublisherIHEP' )

    sitesVO = {}

    for siteName in sitesName:
      vo = publisher.getSiteVO( siteName )
      if not vo[ 'OK' ]:
        return vo
      sitesVO[ siteName ] = vo[ 'Value' ]

    return S_OK( sitesVO )


  def _request(self):
    req = {}

    if 'site' in self.request.arguments:
      site = list(json.loads(self.request.arguments[ 'site' ][ -1 ]))
      if len(site) > 0:
        req[ 'Site' ] = site

    if 'type' in self.request.arguments:
      type = list(json.loads(self.request.arguments[ 'type' ][ -1 ]))
      if len(type) > 0:
        req[ 'SiteType' ] = type

    if 'mask' in self.request.arguments:
      status = list(json.loads(self.request.arguments[ 'mask' ][ -1 ]))
      if len(status) > 0:
        req[ 'MaskStatus' ] = status

    if 'vo' in self.request.arguments:
      vo = list(json.loads(self.request.arguments[ 'vo' ][ -1 ]))
      if len(vo) > 0:
        req[ 'VO' ] = vo

    return req
