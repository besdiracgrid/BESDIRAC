extra_dErrName = {
        'EAPPCOMMON'       : 1,
        'EAPPCMDNOTFOUND'  : 127,
        'EAPPSIGABRT'      : 134,
        'EAPPKILLED'       : 137,

        'EBOSSRANTRGERROR'     : 66,
        'EBOSSCVMFS'           : 70,
        'EBOSSTOOMANYRUNS'     : 71,
        'EBOSSUPLOAD'          : 72,

        'ECEPCCVMFS'           : 11,
        'ECEPCDOWNLOADINPUT'   : 12,
        'ECEPCSIM'             : 20,
        'ECEPCDATABASE'        : 21,
        'ECEPCTOOMANYSUBSTEPS' : 22,
        'ECEPCSIMNOEVENTS'     : 23,
        'ECEPCREC'             : 30,
        'ECEPCRECNOEVENTS'     : 31,
        'ECEPCUPLOAD'          : 51,
}

extra_dErrorCode = {
        1   : 'EAPPCOMMON',
        127 : 'EAPPCMDNOTFOUND',
        134 : 'EAPPSIGABRT',
        137 : 'EAPPKILLED',

        66 : 'EBOSSRANTRGERROR',
        70 : 'EBOSSCVMFS',
        71 : 'EBOSSTOOMANYRUNS',
        72 : 'EBOSSUPLOAD',

        11 : 'ECEPCCVMFS',
        12 : 'ECEPCDOWNLOADINPUT',
        20 : 'ECEPCSIM',
        21 : 'ECEPCDATABASE',
        22 : 'ECEPCTOOMANYSUBSTEPS',
        23 : 'ECEPCSIMNOEVENTS',
        30 : 'ECEPCREC',
        31 : 'ECEPCRECNOEVENTS',
        51 : 'ECEPCUPLOAD',
}

extra_dStrError = {
        1   : 'Common exit error',
        127 : 'Command or library not found',
        134 : 'Aborted with SIGABRT',
        137 : 'Killed by system',

        66 : 'BOSS random trigger download error',
        70 : 'BOSS CVMFS not found',
        71 : 'BOSS too many runs for reconstruction',
        72 : 'BOSS upload output data error',

        11 : 'CEPC CVMFS not found',
        12 : 'CEPC download input error',
        20 : 'CEPC simulation error',
        21 : 'CEPC database connection error',
        22 : 'CEPC too many substeps',
        23 : 'CEPC simulation insufficient events',
        30 : 'CEPC reconstruction error',
        31 : 'CEPC reconstruction insufficient events',
        51 : 'CEPC upload output data error',
}
