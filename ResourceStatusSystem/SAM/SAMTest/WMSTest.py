""" WMSTest

  A simplest test to test job submission function.

"""

from BESDIRAC.ResourceStatusSystem.SAM.SAMTest.CEBaseTest import CEBaseTest


__RCSID__ = '$Id: $'


class WMSTest( CEBaseTest ):
  """
    WMSTest is used to test whether jobs can be submitted to the specified
    ce or cloud.
  """

  def __init__( self, args = None, apis = None ):
    super( WMSTest, self ).__init__( args, apis )


  @staticmethod
  def _judge( log ):
    """
      judge the WMS test status.
    """

    if log.find( 'hello' ) != -1:
      return 'OK'
    else:
      return 'Bad'
