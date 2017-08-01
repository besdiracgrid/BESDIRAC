""" StorageCommand
 
  The StorageCommand class is a command class to know about the storage capacity.
  
"""

import math
from DIRAC                                                         import S_OK, gConfig
from DIRAC.DataManagementSystem.DB.FileCatalogDB                   import FileCatalogDB
from DIRAC.ResourceStatusSystem.Command.Command                    import Command
from DIRAC.ResourceStatusSystem.Utilities                          import CSHelpers
from BESDIRAC.ResourceStatusSystem.Client.ResourceManagementClient import ResourceManagementClient



class StorageCommand( Command ):
  """
    StorageCommand
  """
    
  def __init__( self, args = None, clients = None ):
    super( StorageCommand, self ).__init__( args, clients )
        
    if 'ResourceManagementClient' in self.apis:
      self.rmClient = self.apis[ 'ResourceManagementClient' ]
    else:
      self.rmClient = ResourceManagementClient()
            
    if 'FileCatalogDB' in self.apis:
      self.fcDB = self.apis[ 'FileCatalogDB' ]
    else:
      self.fcDB = FileCatalogDB()
    
  def _storeCommand( self, result):
    """
      Stores the results of doNew method on the database.
    """
    
    for storageDict in result:
      print storageDict
      resQuery = self.rmClient.addOrModifyStorageCache( sE = storageDict[ 'SE' ],
                                                        occupied = storageDict[ 'Occupied' ],
                                                        free = storageDict[ 'Free' ],
                                                        usage = storageDict[ 'Usage' ] )
      if not resQuery[ 'OK' ]:
        return resQuery
    return S_OK()
        
            
  def doNew( self, masterParams = None ):
    """
      It searches FileCatalogDB to find out occupied storage.
    """
    
    ses = masterParams
    
    seMaxStorage = {}
    for se in ses:
      maxStorage = gConfig.getValue('/Resources/StorageElements/%s/Capacity' % se, 0) * 1 << 40
      seMaxStorage[ se ] = maxStorage

    sqlStr = """select SE.SEName, sum(F.Size) from 
    FC_Replicas R, FC_Files F, FC_StorageElements SE 
    where R.FileID=F.FileID and R.SEID=SE.SEID 
    group by R.SEID;"""
        
    result = self.fcDB._query(sqlStr)
    if not result[ 'OK' ]:
      return result
    result = result[ 'Value' ]

    seOccupied = {}
    for se, occupied in result:
      seOccupied[ se ] = int(occupied)
            
    uniformResult = []
    for se in ses:
      max = seMaxStorage.get(se, 0)
      occupied = seOccupied.get(se, 0)
      if max == 0:
        usage = 0.0
        free = 0
      else:
	usage = math.floor(float(occupied) / max * 1000) / 10
        free = max - occupied
      uniformResult.append( { 'SE' : se, 'Occupied' : occupied, 'Free' : free, 'Usage' : usage } )

    storeRes = self._storeCommand( uniformResult )
    if not storeRes[ 'OK' ]:
      return storeRes
        
    return S_OK( result )
            
    
  def doMaster(self):
    """
      Master method
      
      Gets all ses and call doNew method
    """
      
    ses = CSHelpers.getStorageElements()
    if not ses[ 'OK' ]:
      return ses
         
    storageResults = self.doNew( ses[ 'Value' ] )
    if not storageResults[ 'OK' ]:
      self.metrics[ 'failed' ].append( storageResults[ 'Message' ] )
            
    return S_OK( self.metrics )
