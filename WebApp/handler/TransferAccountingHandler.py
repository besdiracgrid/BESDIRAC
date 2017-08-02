from WebAppDIRAC.Lib.WebHandler import WebHandler, WErr
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.Core.DISET.TransferClient import TransferClient
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.ConfigurationSystem.Client.Helpers.Registry import getVOForGroup
import tempfile
import datetime
import simplejson
from hashlib import md5
from DIRAC import S_OK, S_ERROR, gLogger, gConfig
from DIRAC.Core.Utilities import Time, List
from DIRAC.AccountingSystem.Client.ReportsClient   import ReportsClient

class TransferAccountingHandler(WebHandler):

    AUTH_PROPS = "authenticated"

    def __init__(self, *args, **kwargs ):
        super( TransferAccountingHandler, self ).__init__( *args, **kwargs )
        sessionData = self.getSessionData()
        self.user = sessionData['user'].get( 'username', '' )
        self.group = sessionData['user'].get( 'group', '' )
        self.vo = getVOForGroup( self.group )
        self.fc = FileCatalog( vo = self.vo )

        self.log.always(self.user)
        self.log.always(self.group)
        self.log.always(self.vo)
        self.log.always(self.fc)

    def web_getPilotList(self):
        '''
        self.log.debug(self.request.arguments)
        typeName = None
        if self.request.arguments.get("typeName", None):
            typeName = self.request.arguments["typeName"][0]

        typeName="DataTransfer"
        rep=RPCClient("Accounting/ReportGenerator")
        res=rep.listReports(typeName)
        self.log.always(res)
        if res["OK"]:
            data = simplejson.dumps(res['Value'])
        self.log.always(data)
        data = eval(data)
        self.write({"result":data})

        '''
        typeName="DataTransfer"
        rep=RPCClient("Accounting/ReportGenerator")
        res=rep.listReports(typeName)
        self.log.always(res)
        if res["OK"]:
           self.write({"result":res['Value']})

    def web_getSelectData(self):
        '''
        '''
        typeName="DataTransfer"
        rep=RPCClient("Accounting/ReportGenerator")
        res=rep.listUniqueKeyValues(typeName)
        self.log.always(res)
        if res["OK"]:
            resd=res['Value'].keys()
        self.log.always('1111111111111111111111111111111111')
        S=res['Value']['Source']
        D=res['Value']['Destination']
        P=res['Value']['Protocol']
        F=res['Value']['FinalStatus']
        U=res['Value']['User']
        self.log.always(S)
        self.log.always('22222222222222222222222222222222')
        data=[]
        for i in resd:
            data.append(dict(value = i, text = i))
        self.finish({'success' : 'true', 'result' : data})

    def web_getSource(self):
        '''
        res['Value']={"Source": [], "Destination": [], "Protocol": [], "FinalStatus": [], "User": []}
        data[Source] data[Destination] data[Protocol] data[FinalStatus] data[User]
        list: s d p f u
        '''
        typeName="DataTransfer"
        rep=RPCClient("Accounting/ReportGenerator")
        res=rep.listUniqueKeyValues(typeName)
        self.log.always(res)
        if res["OK"]:
            resd=res['Value'].keys()
        S=res['Value']['Source']
        self.log.always(S)
        data=[]
        for x in S:
            data.append(dict(value = x, text = x))
        self.finish({'success' : 'true', 'result' : data})


    def web_getDestination(self):
        typeName="DataTransfer"
        rep=RPCClient("Accounting/ReportGenerator")
        res=rep.listUniqueKeyValues(typeName)
        self.log.always(res)
        if res["OK"]:
            resd=res['Value'].keys()
        S=res['Value']['Destination']
        self.log.always(S)
        data=[]
        for x in S:
            data.append(dict(value = x, text = x))
        self.finish({'success' : 'true', 'result' : data})



    def web_getProtocol(self):
        typeName="DataTransfer"
        rep=RPCClient("Accounting/ReportGenerator")
        res=rep.listUniqueKeyValues(typeName)
        self.log.always(res)
        if res["OK"]:
            resd=res['Value'].keys()
        S=res['Value']['Protocol']
        self.log.always(S)
        data=[]
        for x in S:
            data.append(dict(value = x, text = x))
        self.finish({'success' : 'true', 'result' : data})



    def web_getFinalStatus(self):
        typeName="DataTransfer"
        rep=RPCClient("Accounting/ReportGenerator")
        res=rep.listUniqueKeyValues(typeName)
        self.log.always(res)
        if res["OK"]:
            resd=res['Value'].keys()
        S=res['Value']['FinalStatus']
        self.log.always(S)
        data=[]
        for x in S:
            data.append(dict(value = x, text = x))
        self.finish({'success' : 'true', 'result' : data})



    def web_getUser(self):
        typeName="DataTransfer"
        rep=RPCClient("Accounting/ReportGenerator")
        res=rep.listUniqueKeyValues(typeName)
        self.log.always(res)
        if res["OK"]:
            resd=res['Value'].keys()
        S=res['Value']['User']
        self.log.always(S)
        data=[]
        for x in S:
            data.append(dict(value = x, text = x))
        self.finish({'success' : 'true', 'result' : data})


    def web_getPlotData(self):
        callback = {}
        retVal = self.__parseFormParams()
        if not retVal[ 'OK' ]:
            callback = {"success":"false", "error":retVal[ 'Message' ]}
            self.finish( callback )

        params = retVal[ 'Value' ]
        '''self.finish({'success' : 'true', 'result' : params})'''
        repClient = ReportsClient( rpcClient = RPCClient( "Accounting/ReportGenerator" ) )
        retVal = repClient.getReport(*params)
        if not retVal[ 'OK' ]:
            callback = {"success":"false", "error":retVal[ 'Message' ]}
            self.finish( callback )
        rawData = retVal[ 'Value' ]
        groupKeys = rawData[ 'data' ].keys()
        self.finish({'success' : 'true', 'result' : groupKeys})

    def web_generatePlot(self):
        callback = {}
        retVal = self.__parseFormParams()
        if not retVal[ 'OK' ]:
            callback = {"success":"false", "error":retVal[ 'Message' ]}
            self.finish( callback )

        params = retVal[ 'Value' ]
        repClient = ReportsClient( rpcClient = RPCClient( "Accounting/ReportGenerator" ) )
        retVal = repClient.generateDelayedPlot( *params )
        if not retVal[ 'OK' ]:
            callback = {"success":"false", "error":retVal[ 'Message' ]}
            self.finish( callback )
        rawData = retVal[ 'Value' ]
        '''groupKeys = rawData[ 'data' ].keys()'''
        self.log.always("11111111111111111111111111111111111111111111111111111111111")
        self.log.always(retVal[ 'Value' ][ 'plot' ])
        self.log.always("22222222222222222222222222222222222222222222222222222222222")
        self.finish({'success' : 'true', 'result' : rawData['plot']})




    def web_getPlotImg(self):
        """
        Get plot image
        """
        callback = {}
        if 'file' not in self.request.arguments:
            callback = {"success":"false", "error":"Maybe you forgot the file?"}
            self.finish( callback )
            return
        plotImageFile = str( self.request.arguments[ 'file' ][0] )

        if plotImageFile.find( ".png" ) < -1:
            callback = {"success":"false", "error":"Not a valid image!"}
            self.finish( callback )
            return

        transferClient = TransferClient( "Accounting/ReportGenerator" )
        tempFile = tempfile.TemporaryFile()
        retVal = transferClient.receiveFile( tempFile, plotImageFile )
        if not retVal[ 'OK' ]:
            callback = {"success":"false", "error":retVal[ 'Message' ]}
            self.finish( callback )
            return
        tempFile.seek( 0 )
        data = tempFile.read()
        self.set_header( 'Content-type', 'image/png' )
        self.set_header( 'Content-Disposition', 'attachment; filename="%s.png"' % md5( plotImageFile ).hexdigest() )
        self.set_header( 'Content-Length', len( data ) )
        self.set_header( 'Content-Transfer-Encoding', 'Binary' )
    #self.set_header( 'Cache-Control', "no-cache, no-store, must-revalidate, max-age=0" )
    #self.set_header( 'Pragma', "no-cache" )
    #self.set_header( 'Expires', ( datetime.datetime.utcnow() - datetime.timedelta( minutes = -10 ) ).strftime( "%d %b %Y %H:%M:%S GMT" ) )
        self.finish( data )



    def __parseFormParams(self):
        params = self.request.arguments

        self.log.always(params)
        pD = {}
        extraParams = {}
        for name in params:
            if name =='_Source':
                value = ",".join(params['_Source'])
                pD['Source']=str( value )
            if name =='_Destination':
                value = ",".join(params['_Destination'])
                pD['Destination']=str( value )
            if name =='_User':
                value = ",".join(params['_User'])
                pD['User']=str( value )
        if('_Source' in  params.keys()):
            del(params['_Source'])
        if('_Destination' in  params.keys()):
            del(params['_Destination'])
        if('_User' in  params.keys()):
            del(params['_User'])

        for name in params:
            if name.find( "_" ) != 0:
              continue
            value = params[ name ][0]
            name = name[1:]
            pD[ name ] = str( value )
        self.log.always(pD)

        # Get plotname
        if not 'grouping' in pD:
           return S_ERROR( "Missing grouping!" )
        grouping = pD[ 'grouping' ]
        # Get plotname
        if not 'typeName' in pD:
           return S_ERROR( "Missing type name!" )
        typeName = pD[ 'typeName' ]
        del( pD[ 'typeName' ] )
        # Get plotname
        if not 'plotName' in pD:
           return S_ERROR( "Missing plot name!" )
        reportName = pD[ 'plotName' ]
        del( pD[ 'plotName' ] )
        # Get times
        start =datetime.datetime.strptime(pD[ 'startTime' ],"%Y-%m-%d %H:%M")
        end = datetime.datetime.strptime(pD[ 'endTime' ],"%Y-%m-%d %H:%M")
        del( pD[ 'startTime' ] )
        del( pD[ 'endTime' ] )
        # Get extraParams

        # Listify the rest
        for selName in pD:
          pD[ selName ] = List.fromChar( pD[ selName ], "," )
          self.log.always("11111111111111111111111111111111111111111111111111111111111111111111111111111")
          self.log.always(pD[ selName ])
        return S_OK( ( typeName, reportName, start, end, pD, grouping, extraParams ) )
