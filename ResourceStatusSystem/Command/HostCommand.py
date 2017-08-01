from DIRAC                                                         import S_OK
from DIRAC.WorkloadManagementSystem.DB.JobDB import JobDB
from DIRAC.ResourceStatusSystem.Command.Command                    import Command
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementClient import ResourceManagementClient



class HostCommand( Command ):
    
  def __init__( self, args = None, clients = None ):
    super( HostCommand, self ).__init__( args, clients )
    
    if 'JobDB' in self.apis:
      self.jobDB = self.apis[ 'JobDB' ]
    else:
      self.jobDB = JobDB()
      
    if 'ResourceManagementClient' in self.apis:
      self.rmClient = self.apis[ 'ResourceManagementClient' ]
    else:
      self.rmClient = ResourceManagementClient()
      
      
  def _storeCommand( self, result):
    """
      Stores the results of doNew method on the database.
    """
    
    for hostDict in result:
      resQuery = self.rmClient.addOrModifyHostCache( host = hostDict[ 'Host' ],
                                                     site = hostDict[ 'Site' ],
                                                     running = hostDict[ 'Running' ],
                                                     done = hostDict[ 'Done' ],
                                                     failed = hostDict[ 'Failed' ],
                                                     efficiency = hostDict[ 'Efficiency' ] )
      if not resQuery[ 'OK' ]:
        return resQuery
    return S_OK()

 
  def doNew( self, masterParams = None ):
    
    sql = """
select JP.Value, J.Status, J.Site, count(*) from Jobs J, JobParameters JP 
where J.JobID = JP.JobID and JP.Name = 'HostName' 
and J.LastUpdateTime >= DATE_SUB(UTC_TIMESTAMP(),INTERVAL 24 HOUR) 
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
      if hostName not in hostJobs:
        hostJobs[ hostName ] = { 'Site' : record[ 2 ], 'Running' : 0, 'Done' : 0, 'Failed' : 0 }
      hostJobs[ hostName ][ record[ 1 ] ] = record[ 3 ]
    
    uniformResult = []
    
    for host, hostDict in hostJobs.items():
      hostDict[ 'Host' ] = host
      if hostDict[ 'Done' ] == 0 and hostDict[ 'Failed' ] == 0:
        hostDict[ 'Efficiency' ] = 0
      else:
        hostDict[ 'Efficiency' ] = float( hostDict[ 'Done' ] ) / ( hostDict[ 'Done' ] + hostDict[ 'Failed' ] )
      uniformResult.append( hostDict )
      
    storeRes = self._storeCommand( uniformResult )
    if not storeRes[ 'OK' ]:
      return storeRes

    return S_OK( uniformResult )
      
      
  def doMaster( self ):
    """
      Master method.
      
      Gets all sites and calls doNew method.
    """
    
    jobsResults = self.doNew()
    if not jobsResults[ 'OK' ]:
      self.metrics[ 'failed' ].append( jobsResults[ 'Message' ] )
      
    return S_OK( self.metrics )       
