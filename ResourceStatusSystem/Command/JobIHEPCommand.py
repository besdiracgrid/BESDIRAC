""" JobIHEPCommand

  The JobIHEPCommand class is a command class to know about present jobs efficiency

"""

from DIRAC                                                         import S_OK, S_ERROR
from DIRAC.Core.DISET.RPCClient                                    import RPCClient
from DIRAC.ResourceStatusSystem.Command.Command                    import Command
from DIRAC.ResourceStatusSystem.Utilities                          import CSHelpers
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementIHEPClient import ResourceManagementIHEPClient

__RCSID__ = '$Id:  $'

class JobIHEPCommand( Command ):
  """
    Job "master" Command.
  """

  def __init__( self, args = None, clients = None ):

    super( JobIHEPCommand, self ).__init__( args, clients )

    if 'WMSAdministrator' in self.apis:
      self.wmsAdmin = self.apis[ 'WMSAdministrator' ]
    else:
      self.wmsAdmin = RPCClient( 'WorkloadManagement/WMSAdministrator' )

    if 'ResourceManagementIHEPClient' in self.apis:
      self.rmIHEPClient = self.apis[ 'ResourceManagementIHEPClient' ]
    else:
      self.rmIHEPClient = ResourceManagementIHEPClient()

  def _storeCommand( self, result ):
    """
      Stores the results of doNew method on the database.
    """

    for jobDict in result:

      resQuery = self.rmIHEPClient.addOrModifyJobCache( jobDict[ 'Site' ],
                                                    jobDict[ 'MaskStatus' ],
                                                    jobDict[ 'Efficiency' ],
                                                    jobDict[ 'Running' ],
                                                    jobDict[ 'Waiting' ],
                                                    jobDict[ 'Done' ],
                                                    jobDict[ 'Failed' ],
                                                    jobDict[ 'Completed' ],
                                                    jobDict[ 'Stalled' ],
                                                    jobDict[ 'Status' ])
      if not resQuery[ 'OK' ]:
        return resQuery
    return S_OK()

  def _prepareCommand( self ):
    """
      JobIHEPCommand requires one arguments:
      - name : <str>
    """

    if not 'name' in self.args:
      return S_ERROR( '"name" not found in self.args' )
    name = self.args[ 'name' ]

    return S_OK( name )

  def doNew( self, masterParams = None ):
    """
      Gets the parameters to run, either from the master method or from its
      own arguments.

      It contacts the WMSAdministrator with a list of site names, or a single
      site.

      If there are jobs, are recorded and then returned.
    """

    if masterParams is not None:
      name = masterParams
    else:
      params = self._prepareCommand()
      if not params[ 'OK' ]:
        return params
      name = params[ 'Value' ]

    resultMask = self.wmsAdmin.getSiteMask()
    if not resultMask[ 'OK' ]:
      return resultMask
    resultMask = resultMask[ 'Value' ]

    # selectDict, sortList, startItem, maxItems
    # Returns statistics of Last day !
    results = self.wmsAdmin.getSiteSummaryWeb( { 'Site' : name }, [], 0, 0 )
    if not results[ 'OK' ]:
      return results
    results = results[ 'Value' ]

    if not 'ParameterNames' in results:
      return S_ERROR( 'Wrong result dictionary, missing "ParameterNames"' )
    params = results[ 'ParameterNames' ]

    if not 'Records' in results:
      return S_ERROR( 'Wrong formed result dictionary, missing "Records"' )
    records = results[ 'Records' ]

    uniformResult = []
    siteJobs = {}

    for record in records:

      # This returns a dictionary with the following keys
      # 'Site', 'GridType', 'Country', 'Tier', 'MaskStatus', 'Received',
      # 'Checking', 'Staging', 'Waiting', 'Matched', 'Running', 'Stalled',
      # 'Done', 'Completed', 'Failed', 'Efficiency', 'Status'
      jobDict = dict( zip( params , record ))
      siteJobs[ jobDict.pop( 'Site' ) ] = jobDict

#       # We cast efficiency to a float
#       jobDict[ 'Efficiency' ] = float( jobDict[ 'Efficiency' ] )

#       uniformResult.append( jobDict )

    for site in name:
      recordDict = {}
      recordDict[ 'Site' ] = site
      if siteJobs.has_key( site ):
        recordDict[ 'MaskStatus' ] = siteJobs[ site ][ 'MaskStatus' ]
        recordDict[ 'Running' ] = siteJobs[ site ][ 'Running' ]
        recordDict[ 'Waiting' ] = siteJobs[ site ][ 'Waiting' ] + siteJobs[ site ][ 'Checking' ]
        recordDict[ 'Done' ] = siteJobs[ site ][ 'Done' ]
        recordDict[ 'Failed' ] = siteJobs[ site ][ 'Failed' ]
        recordDict[ 'Completed' ] = siteJobs[ site ][ 'Completed' ]
        recordDict[ 'Stalled' ] = siteJobs[ site ][ 'Stalled' ]
        recordDict[ 'Efficiency' ] = float( siteJobs[ site ][ 'Efficiency' ] )
        recordDict[ 'Status' ] = siteJobs[ site ][ 'Status' ]
      else:
        if site in resultMask:
          recordDict[ 'MaskStatus' ] = 'Active'
        else:
          recordDict[ 'MaskStatus' ] = 'Banned'
        recordDict[ 'Running' ] = 0
        recordDict[ 'Waiting' ] = 0
        recordDict[ 'Done' ] = 0
        recordDict[ 'Failed' ] = 0
        recordDict[ 'Completed' ] = 0
        recordDict[ 'Stalled' ] = 0
        recordDict[ 'Efficiency' ] = 0.0
        recordDict[ 'Status' ] = 'Idle'

      uniformResult.append( recordDict )

    storeRes = self._storeCommand( uniformResult )
    if not storeRes[ 'OK' ]:
      return storeRes

    return S_OK( uniformResult )

  def doCache( self ):
    """
      Method that reads the cache table and tries to read from it. It will
      return a list of dictionaries if there are results.
    """

    params = self._prepareCommand()
    if not params[ 'OK' ]:
      return params
    name = params[ 'Value' ]

    result = self.rmIHEPClient.selectJobCache( name )
    if result[ 'OK' ]:
      result = S_OK( [ dict( zip( result[ 'Columns' ], res ) ) for res in result[ 'Value' ] ] )

    return result

  def doMaster( self ):
    """
      Master method.

      Gets all sites and calls doNew method.
    """

    siteNames = CSHelpers.getSites()
    if not siteNames[ 'OK' ]:
      return siteNames
    siteNames = siteNames[ 'Value' ]

    jobsResults = self.doNew( siteNames )
    if not jobsResults[ 'OK' ]:
      self.metrics[ 'failed' ].append( jobsResults[ 'Message' ] )

    return S_OK( self.metrics )

################################################################################
#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF
