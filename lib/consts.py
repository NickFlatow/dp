#program constants
REG = 'registration'
SPECTRUM = 'spectrumInquiry'
GRANT = 'grant'
HEART = 'heartbeat'
DEREG = 'deregistration'
REL = 'relinquishment'

#DATA MODEL PATHS
TXPOWER_PATH = 'Device.X_FOXCONN_FAP.CellConfig.SonMaxTxPower_Max' 
EARFCN_LIST = 'Device.X_FOXCONN_FAP.CellConfig.EUTRACarrierARFCNDL'
EARFCN_IN_USE = 'Device.X_FOXCONN_FAP.CellConfig.EUTRACarrierARFCNULInUse'


DB = 'ACS_V1_1'
FS = {
  "spectrumInquiryResponse": [
    {
      "cbsdId": "DCE994613163",
      "availableChannel": [
        {
          "frequencyRange": {
            "lowFrequency": 3620000000,
            "highFrequency": 3630000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3630000000,
            "highFrequency": 3640000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3640000000,
            "highFrequency": 3650000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3680000000,
            "highFrequency": 3690000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3690000000,
            "highFrequency": 3700000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3650000000,
            "highFrequency": 3660000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3660000000,
            "highFrequency": 3670000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3670000000,
            "highFrequency": 3680000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3590000000,
            "highFrequency": 3600000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3600000000,
            "highFrequency": 3610000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3610000000,
            "highFrequency": 3620000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3580000000,
            "highFrequency": 3590000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3550000000,
            "highFrequency": 3560000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3560000000,
            "highFrequency": 3570000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        },
        {
          "frequencyRange": {
            "lowFrequency": 3570000000,
            "highFrequency": 3580000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 30
        }
      ],
      "response": {
        "responseCode": 0
      }
    }
  ]
}
FS1 = {
  "spectrumInquiryResponse": [
    {
      "cbsdId": "DCE994613163",
      "availableChannel": [
        {
          "frequencyRange": {
            "lowFrequency": 3620000000,
            "highFrequency": 3630000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 20
        },
        {
          "frequencyRange": {
            "lowFrequency": 3630000000,
            "highFrequency": 3640000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 20
        },
        {
          "frequencyRange": {
            "lowFrequency": 3560000000,
            "highFrequency": 3610000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 20
        },
        {
          "frequencyRange": {
            "lowFrequency": 3610000000,
            "highFrequency": 3620000000
          },
          "channelType": "GAA",
          "ruleApplied": "FCC_PART_96",
          "maxEirp": 20
        }
      ],
      "response": {
        "responseCode": 0
      }
    }
  ]
}