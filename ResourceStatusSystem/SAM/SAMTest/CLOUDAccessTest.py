''' CLOUDAccessTest

A test class to test the access to clouds.

'''

import subprocess, re
from datetime import datetime
from DIRAC import S_OK, S_ERROR, gConfig


class CLOUDAccessTest:
  ''' CLOUDAccessTest
  '''

  def _getAccessParams( self, element ):
    '''
      get the access host and port for the specified cloud.
    '''

    _basePath = 'Resources/Sites'
    _searchKey = ( 'ex_force_auth_url', 'EndpointUrl' )

    cloud = gConfig.getSections( '%s/CLOUD/%s/Cloud' % ( _basePath, element ) )
    if not cloud[ 'OK' ]:
      return cloud
    cloud = cloud[ 'Value' ][ 0 ]

    for key in _searchKey:
      url = gConfig.getValue( '%s/CLOUD/%s/Cloud/%s/%s' % ( _basePath, element, cloud, key ) )
      if url:
        return S_OK(re.match(r'https?://(.+):([0-9]+).*', url).groups())

    return S_ERROR('%s is not a vaild CLOUD.' % element)
