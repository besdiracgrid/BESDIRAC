import math
from DIRAC                                                         import S_OK
from DIRAC.WorkloadManagementSystem.DB.JobDB import JobDB
from DIRAC.ResourceStatusSystem.Command.Command                    import Command
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementIHEPClient import ResourceManagementIHEPClient


class WorkNodeIHEPCommand( Command ):

  def __init__( self, args = None, clients = None ):
    super( WorkNodeIHEPCommand, self ).__init__( args, clients )

    if 'JobDB' in self.apis:
      self.jobDB = self.apis[ 'JobDB' ]
    else:
      self.jobDB = JobDB()

    if 'ResourceManagementIHEPClient' in self.apis:
      self.rmIHEPClient = self.apis[ 'ResourceManagementIHEPClient' ]
    else:
      self.rmIHEPClient = ResourceManagementIHEPClient()


  def _storeCommand( self, result):
    """
      Stores the results of doNew method on the database.
    """

    for hostDict in result:
      resQuery = self.rmIHEPClient.addOrModifyWorkNodeCache( host = hostDict[ 'Host' ],
                                                     site = hostDict[ 'Site' ],
                                                     done = hostDict[ 'Done' ],
                                                     failed = hostDict[ 'Failed' ],
                                                     efficiency = hostDict[ 'Efficiency' ] )
      if not resQuery[ 'OK' ]:
        return resQuery
    return S_OK()


  def doNew( self, masterParams = None ):

    hosts = masterParams

    sql = """
select JP.Value, J.Status, J.Site, count(*) from Jobs J, JobParameters JP
where J.JobID = JP.JobID and JP.Name = 'HostName'
and J.EndExecTime >= DATE_SUB(UTC_TIMESTAMP(),INTERVAL 24 HOUR)
group by JP.Value, J.Status
"""

    jobDB = JobDB()
    queryRes = jobDB._query(sql)
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]

    hostJobs = {}

    for record in records:
      hostName = record[ 0 ]
      status = record[ 1 ]
      if(status != 'Done' and status != 'Failed'): continue
      if hostName not in hostJobs:
        hostJobs[ hostName ] = { 'Site' : record[ 2 ], 'Done' : 0, 'Failed' : 0 }
      hostJobs[ hostName ][ record[ 1 ] ] = record[ 3 ]

    uniformResult = []

    for host, hostDict in hostJobs.items():
      hostDict[ 'Host' ] = host
      try:
        hosts.remove(host)
      except ValueError:
        pass
      if hostDict[ 'Done' ] == 0 and hostDict[ 'Failed' ] == 0:
        hostDict[ 'Efficiency' ] = 0.0
      else:
        hostDict[ 'Efficiency' ] = math.floor(float( hostDict[ 'Done' ] ) / ( hostDict[ 'Done' ] + hostDict[ 'Failed' ] ) *1000) / 10
      uniformResult.append( hostDict )

    if len(hosts) != 0:
      deleteRes = self.rmIHEPClient.deleteWorkNodeCache(host = hosts)
      if not deleteRes[ 'OK' ]:
        return deleteRes

    storeRes = self._storeCommand( uniformResult )
    if not storeRes[ 'OK' ]:
      return storeRes

    return S_OK( uniformResult )


  def doMaster( self ):
    """
      Master method.

      Gets all sites and calls doNew method.
    """

    queryRes = self.rmIHEPClient.selectWorkNodeCache(meta = { 'columns' : [ 'Host' ] })
    if not queryRes[ 'OK' ]:
      return queryRes
    records = queryRes[ 'Value' ]

    hosts = [ record[ 0 ] for record in records ]
    jobsResults = self.doNew(hosts)
    if not jobsResults[ 'OK' ]:
      self.metrics[ 'failed' ].append( jobsResults[ 'Message' ] )

    return S_OK( self.metrics )
