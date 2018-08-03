extra_dErrName = {
        'EBOSSCOMMON'          : 10001,
        'EBOSSRANTRGNOTFOUND'  : 10066,
        'EBOSSCVMFS'           : 10070,
        'EBOSSTOOMANYRUNS'     : 10071,
        'EBOSSUPLOAD'          : 10072,
        'EBOSSCMDNOTFOUND'     : 10127,
        'EBOSSSIGABRT'         : 10134,
        'EBOSSKILLED'          : 10137,

        'ECEPCCOMMON'          : 30001,
        'ECEPCCVMFS'           : 30011,
        'ECEPCDOWNLOADINPUT'   : 30012,
        'ECEPCSIM'             : 30020,
        'ECEPCDATABASE'        : 30021,
        'ECEPCTOOMANYSUBSTEPS' : 30022,
        'ECEPCSIMNOEVENTS'     : 30023,
        'ECEPCREC'             : 30030,
        'ECEPCRECNOEVENTS'     : 30031,
        'ECEPCUPLOAD'          : 30051,
}

extra_dErrorCode = {
        10001 : 'EBOSSCOMMON',
        10066 : 'EBOSSRANTRGNOTFOUND',
        10070 : 'EBOSSCVMFS',
        10071 : 'EBOSSTOOMANYRUNS',
        10072 : 'EBOSSUPLOAD',
        10127 : 'EBOSSCMDNOTFOUND',
        10134 : 'EBOSSSIGABRT',
        10137 : 'EBOSSKILLED',

        30001 : 'ECEPCCOMMON',
        30011 : 'ECEPCCVMFS',
        30012 : 'ECEPCDOWNLOADINPUT',
        30020 : 'ECEPCSIM'
        30021 : 'ECEPCDATABASE',
        30022 : 'ECEPCTOOMANYSUBSTEPS',
        30023 : 'ECEPCSIMNOEVENTS',
        30030 : 'ECEPCREC',
        30031 : 'ECEPCRECNOEVENTS',
        30051 : 'ECEPCUPLOAD',
}

extra_dStrError = {
        10001 : 'BOSS exit with error',
        10066 : 'BOSS andom trigger file not found',
        10070 : 'BOSS CVMFS not found',
        10071 : 'BOSS too many runs to do reconstruction',
        10072 : 'BOSS upload output data error',
        10127 : 'BOSS command or library not found',
        10134 : 'BOSS aborted with SIGABRT',
        10137 : 'BOSS killed by system',

        30001 : 'CEPC exit with error',
        30011 : 'CEPC CVMFS not found',
        30012 : 'CEPC download input error',
        30020 : 'CEPC simulation error'
        30021 : 'CEPC database connection error',
        30022 : 'CEPC too many substeps',
        30023 : 'CEPC simulation insufficient events',
        30030 : 'CEPC reconstruction error',
        30031 : 'CEPC reconstruction insufficient events',
        30051 : 'CEPC upload output data error',
}
