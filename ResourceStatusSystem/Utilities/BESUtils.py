import os
from DIRAC import S_OK, S_ERROR, gConfig
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.FrameworkSystem.Client.ProxyManagerClient import gProxyManager
from DIRAC.ConfigurationSystem.Client.Helpers import Registry


def getProxyByVO( user, vo ):
  group = vo.lower() + '_user'

  userDN = Registry.getDNForUsername( user )
  if not userDN[ 'OK' ]:
    return S_ERROR( 'Cannot discover DN for user %s: %s' % ( user, userDN[ 'Message' ] ) )
  userDN = userDN[ 'Value' ][ 0 ]

  chain = gProxyManager.downloadVOMSProxy( userDN, group )
  if not chain[ 'OK' ]:
    return S_ERROR( 'Proxy file cannot be retrieved: %s' % chain[ 'Message' ] )
  chain = chain[ 'Value' ]

  proxyPath = "%s/proxy.%s.%s" % ( os.getcwd(), user, group )
  result = chain.dumpAllToFile( proxyPath )
  if not result[ 'OK' ]:
    return S_ERROR( 'Proxy file cannot be written to %s: %s' % ( proxyPath, result[ 'Message' ] ) )

  return S_OK( proxyPath )


def getSiteForCE( ce ):
  _basePath = 'Resources/Sites'

  domains = gConfig.getSections( _basePath )[ 'Value' ]
  for domain in domains:
    sites = gConfig.getSections( '%s/%s' % ( _basePath, domain ) )[ 'Value' ]
    for site in sites:
      ces = gConfig.getValue( '%s/%s/%s/CE' % ( _basePath, domain, site ) , '' ).split( ',' )
      ces = map(lambda str : str.strip(), ces);
      if ce in ces:
        return site


def getSitesForSE( se ):
  _basePath = 'Resources/Sites'

  seSites = []
  domains = gConfig.getSections( _basePath )[ 'Value' ]
  for domain in domains:
    sites = gConfig.getSections( '%s/%s' % ( _basePath, domain ) )[ 'Value' ]
    for site in sites:
      ses = gConfig.getValue( '%s/%s/%s/SE' % ( _basePath, domain, site ), '' ).split( ',' )
      ses = map(lambda str : str.strip(), ses);
      if se in ses:
        seSites.append(site)

  return seSites


def getSiteVO( siteName ):
  _basePath = 'Resources/Sites'

  res = Registry.getVOs()
  if res[ 'OK' ]:
    allVOs = res[ 'Value' ]
  else:
    allVOs = [ 'bes', 'cepc', 'juno' ]

  domain = siteName.split( '.' )[ 0 ]
  if domain == 'CLOUD':
    vos = []
    clouds = gConfig.getSections( '%s/CLOUD/%s/Cloud/' % ( _basePath, siteName ) )
    if clouds[ 'OK' ]:
      for cloud in clouds[ 'Value' ]:
        images = gConfig.getSections( '%s/CLOUD/%s/Cloud/%s/Images' % ( _basePath, siteName, cloud ) )
        if images[ 'OK' ]:
          for image in images[ 'Value' ]:
            vo = gConfig.getValue( '%s/CLOUD/%s/Cloud/%s/Images/%s/VO' % ( _basePath, siteName, cloud, image ) )
            if vo:
              vos.append( vo )
    if vos:
      return list( set( vos ) )

  else:
    vos = gConfig.getValue( '%s/%s/%s/VO' % ( _basePath, domain, siteName ) )
    if vos is None:
      ces = gConfig.getSections( '%s/%s/%s/CEs' % ( _basePath, domain, siteName ) )
      if ces[ 'OK' ]:
        ces = ces[ 'Value' ]
        vos = gConfig.getValue( '%s/%s/%s/CEs/%s/VO' % ( _basePath, domain, siteName, ces[ 0 ] ) )
        if vos is None:
          queues = gConfig.getSections( '%s/%s/%s/CEs/%s/Queues' % ( _basePath, domain, siteName, ces[ 0 ] ) )
          if queues[ 'OK' ]:
            queues = queues[ 'Value' ]
            vos = gConfig.getValue( '%s/%s/%s/CEs/%s/Queues/%s/VO' % ( _basePath, domain, siteName, ces[ 0 ], queues[ 0 ] ) )
    if vos:
      vos = [ vo.strip() for vo in vos.split( ',' ) ]
      return vos

  return allVOs
