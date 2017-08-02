''' SEAccessTest

A test class to test the access to ses.

'''

import subprocess, re
from datetime import datetime
from DIRAC import S_OK, S_ERROR, gConfig


class SEAccessTest:
  ''' SEAccessTest
  '''

  def _getAccessParams( self, element ):
    '''
      get the access host and port for the specified se.
    '''

    _basePath = 'Resources/StorageElements'

    host = gConfig.getValue( '%s/%s/AccessProtocol.1/Host' % ( _basePath, element ), '' )
    port = gConfig.getValue( '%s/%s/AccessProtocol.1/Port' % ( _basePath, element ), '' )

    return S_OK( ( host, port ) )
