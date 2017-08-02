''' CacheFeederAgent

  This agent feeds the Cache tables with the outputs of the cache commands.

'''

from DIRAC                                                      import S_OK
from DIRAC.AccountingSystem.Client.ReportsClient                import ReportsClient
from DIRAC.Core.Base.AgentModule                                import AgentModule
from DIRAC.Core.DISET.RPCClient                                 import RPCClient
from DIRAC.Core.LCG.GOCDBClient                                 import GOCDBClient
from DIRAC.ResourceStatusSystem.Client.ResourceStatusClient     import ResourceStatusClient
from DIRAC.ResourceStatusSystem.Command                         import CommandCaller
from DIRAC.ResourceStatusSystem.Utilities                       import Utils
ResourceManagementIHEPClient = getattr( Utils.voimport( 'DIRAC.ResourceStatusSystem.Client.ResourceManagementIHEPClient' ), 'ResourceManagementIHEPClient' )

__RCSID__ = '$Id:  $'
AGENT_NAME = 'ResourceStatus/CacheFeederIHEPAgent'

class CacheFeederIHEPAgent( AgentModule ):
  '''
  The CacheFeederAgent feeds the cache tables for the client and the accounting.
  It runs periodically a set of commands, and stores it's results on the
  tables.
  '''

  # Too many public methods
  # pylint: disable=R0904

  def __init__( self, *args, **kwargs ):

    AgentModule.__init__( self, *args, **kwargs )

    self.commands = {}
    self.clients = {}

    self.cCaller = None
    self.rmClient = None

  def initialize( self ):

    self.am_setOption( 'shifterProxy', 'DataManager' )

    self.rmClient = ResourceManagementIHEPClient()

    self.commands[ 'JobIHEP' ] = [ { 'JobIHEP' : {} } ]
    self.commands[ 'StorageIHEP' ] = [ { 'StorageIHEP' : {} } ]
    self.commands[ 'WorkNodeIHEP' ] = [ { 'WorkNodeIHEP' : {} } ]

    # Reuse clients for the commands
    self.clients[ 'GOCDBClient' ] = GOCDBClient()
    self.clients[ 'ReportGenerator' ] = RPCClient( 'Accounting/ReportGenerator' )
    self.clients[ 'ReportsClient' ] = ReportsClient()
    self.clients[ 'ResourceStatusClient' ] = ResourceStatusClient()
    self.clients[ 'ResourceManagementIHEPClient' ] = ResourceManagementIHEPClient()
    self.clients[ 'WMSAdministrator' ] = RPCClient( 'WorkloadManagement/WMSAdministrator' )

    self.cCaller = CommandCaller

    return S_OK()

  def loadCommand( self, commandModule, commandDict ):

    commandName = commandDict.keys()[ 0 ]
    commandArgs = commandDict[ commandName ]

    commandTuple = ( '%sCommand' % commandModule, '%sCommand' % commandName )
    commandObject = self.cCaller.commandInvocation( commandTuple, pArgs = commandArgs,
                                                    clients = self.clients )

    if not commandObject[ 'OK' ]:
      self.log.error( 'Error initializing %s' % commandName )
      return commandObject
    commandObject = commandObject[ 'Value' ]

    # Set master mode
    commandObject.masterMode = True

    self.log.info( '%s/%s' % ( commandModule, commandName ) )

    return S_OK( commandObject )


  def execute( self ):

    for commandModule, commandList in self.commands.items():

      self.log.info( '%s module initialization' % commandModule )

      for commandDict in commandList:

        commandObject = self.loadCommand( commandModule, commandDict )
        if not commandObject[ 'OK' ]:
          self.log.error( commandObject[ 'Message' ] )
          continue
        commandObject = commandObject[ 'Value' ]

        results = commandObject.doCommand()

        if not results[ 'OK' ]:
          self.log.error( 'Failed to execute command', '%s: %s' % ( commandModule, results[ 'Message' ] ) )
          continue
        results = results[ 'Value' ]

        if not results:
          self.log.info( 'Empty results' )
          continue

        self.log.verbose( 'Command OK Results' )
        self.log.verbose( results )

    return S_OK()

################################################################################
# EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF
