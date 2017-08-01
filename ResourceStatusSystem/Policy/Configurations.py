from DIRAC.ResourceStatusSystem.Policy.Configurations import POLICIESMETA as DIRACPOLICIESMETA

__RCSID__ = '$Id:  $'

POLICIESMETA = DIRACPOLICIESMETA

BESPOLICIESMETA = {
    'SiteSAM' : {
        'description' : 'Policy based on site SAM information',
        'module' : 'SiteSAMPolicy',
        'command' : ( 'SAMCommand', 'SAMCommand' ),
        'args' : None
    }
}

POLICIESMETA.update( BESPOLICIESMETA )
