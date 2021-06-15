from datetime import datetime

#program constants
REG = 'registration'
SPECTRUM = 'spectrumInquiry'
GRANT = 'grant'
HEART = 'heartbeat'
DEREG = 'deregistration'
REL = 'relinquishment'

#DATA MODEL PATHS
TXPOWER_PATH  = 'Device.X_FOXCONN_FAP.CellConfig.SonMaxTxPower_Max'  
EARFCN_LIST   = 'Device.X_FOXCONN_FAP.CellConfig.EUTRACarrierARFCNDL'
EARFCN_IN_USE = 'Device.X_FOXCONN_FAP.CellConfig.EUTRACarrierARFCNULInUse'
ADMIN_STATE   = 'Device.Services.FAPService.1.FAPControl.LTE.AdminState'
PERIODIC      = 'Device.ManagementServer.PeriodicInformInterval' 

PERIODIC_ONE    = {'data_path':PERIODIC,'data_type':'unsignedInt','data_value':1}
ADMIN_POWER_OFF = {'data_path':ADMIN_STATE,'data_type':'boolean','data_value':'false'}
ADMIN_POWER_ON  = {'data_path':ADMIN_STATE,'data_type':'boolean','data_value':'true'}


HIGH_FREQUENCY = 3700000000
LOW_FREQUENCY = 3550000000

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
          "maxEirp": 0
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
          "maxEirp": 1
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
        }
        # ,
        # {
        #   "frequencyRange": {
        #     "lowFrequency": 3570000000,
        #     "highFrequency": 3580000000
        #   },
        #   "channelType": "GAA",
        #   "ruleApplied": "FCC_PART_96",
        #   "maxEirp": 30
        # }
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
HBE = {
    "heartbeatResponse": [
        {
            "cbsdId": "FoxconnMock-SASDCE994613163",
            "grantId": "438285164",
            "response": {
                "responseCode": 501
            },
            "transmitExpireTime": "2021-05-28T19:18:33Z"
        }
    ]
}

HBE2 =  hbresponse = {'heartbeatResponse': [{'grantId': '578807884', 'cbsdId': 'FoxconnMock-SASDCE994613163', 'transmitExpireTime': '2021-04-9T18:01:48Z', 'response': {'responseCode': 0}}, {'grantId': '32288332', 'cbsdId': 'FoxconMock-SAS1111', 'transmitExpireTime': '2021-03-26T21:30:48Z', 'response': {'responseCode': 0}}]}

HBGR = {
    "heartbeatResponse": [
        {
            "cbsdId": "FoxconnMock-SASDCE994613163",
            "grantExpireTime": "2021-06-03T18:54:05Z",
            "grantId": "296455749",
            "response": {
                "responseCode": 0
            },
            "transmitExpireTime": "2021-06-03T18:51:25Z"
        }
    ]
}

SPEC_EIRP = {
    "spectrumInquiryResponse": [
        {
            "availableChannel": [
                {
                    "channelType": "GAA",
                    "frequencyRange": {
                        "highFrequency": 3630000000,
                        "lowFrequency": 3620000000
                    },
                    "maxEirp": 13,
                    "ruleApplied": "FCC_PART_96"
                },
                {
                    "channelType": "GAA",
                    "frequencyRange": {
                        "highFrequency": 3640000000,
                        "lowFrequency": 3630000000
                    },
                    "maxEirp": 13,
                    "ruleApplied": "FCC_PART_96"
                }
            ],
            "cbsdId": "2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982",
            "response": {
                "responseCode": 0
            }
        }
    ]
}
GRANT_EIRP = {
    "grantRequest": [
        {
            "cbsdId": "2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982",
            "operationParam": {
                "maxEirp": 25,
                "operationFrequencyRange": {
                    "highFrequency": 3640000000,
                    "lowFrequency": 3620000000
                }
            }
        }
    ]
}

HB501 = {  
   "heartbeatResponse":[  
      {  
         "cbsdId":"<SAS-assigned device ID>",
         "grantId":"<SAS-assigned grant ID>",
         "transmitExpireTime":str(datetime.now()),
         "operationParam":{
            "maxEirp":11,
            "operationFrequencyRange":{
               "lowFrequency":3660000000,
               "highFrequency":3680000000
            }
         },
         "response":{  
            "responseCode":500,
            "responseMessage":"TERMINATED_GRANT"
         }
      }
   ]
}