#program constants

#CBSD SAS states
PROV_REG = 'provision_registration'
REG = 'registration'
SPECTRUM = 'spectrumInquiry'
GRANT = 'grant'
HEART = 'heartbeat'
SUB_HEART = 'authorized_heartbeat'
DEREG = 'deregistration'
REL = 'relinquishment'
REPROV = 'provisioning'


#LICENSE FILE CONSTS
FUNC_MODE_ALL = 0
FUNC_MODE_DOMAIN_PROXY = 5

#DATA MODEL PATHS
TXPOWER_PATH  = 'Device.X_FOXCONN_FAP.CellConfig.SonMaxTxPower_Max'  
EARFCN_LIST   = 'Device.X_FOXCONN_FAP.CellConfig.EUTRACarrierARFCNDL'
EARFCN_IN_USE = 'Device.X_FOXCONN_FAP.CellConfig.EUTRACarrierARFCNULInUse'
ADMIN_STATE   = 'Device.Services.FAPService.1.FAPControl.LTE.AdminState'
PERIODIC      = 'Device.ManagementServer.PeriodicInformInterval' 

PERIODIC_ONE    = {'data_path':PERIODIC,'data_type':'unsignedInt','data_value':1}
ADMIN_POWER_OFF = {'data_path':ADMIN_STATE,'data_type':'boolean','data_value':'false'}
ADMIN_POWER_ON  = {'data_path':ADMIN_STATE,'data_type':'boolean','data_value':'true'}

#FREQUENCY CONTS
HIGH_FREQUENCY = 3700000000
LOW_FREQUENCY = 3550000000

Hz = 1000000
TEN_MHz = 10000000




DB = 'ACS_V1_1'

#TEST CONSTS
# TEST_CBSD_SN = '900F0C732A02'
TEST_CBSD_SN = 'DCE994613163'





#SAS HANDLER CONSTS
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
        # {
        #   "frequencyRange": {
        #     "lowFrequency": 3600000000,
        #     "highFrequency": 3610000000
        #   },
        #   "channelType": "GAA",
        #   "ruleApplied": "FCC_PART_96",
        #   "maxEirp": 30
        # },
        # {
        #   "frequencyRange": {
        #     "lowFrequency": 3610000000,
        #     "highFrequency": 3620000000
        #   },
        #   "channelType": "GAA",
        #   "ruleApplied": "FCC_PART_96",
        #   "maxEirp": 30
        # },
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
        ,
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
FS_MISING_55590 = {
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
        # {
        #   "frequencyRange": {
        #     "lowFrequency": 3580000000,
        #     "highFrequency": 3590000000
        #   },
        #   "channelType": "GAA",
        #   "ruleApplied": "FCC_PART_96",
        #   "maxEirp": 30
        # },
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
FSCB = {
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
        ,
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

# HB500 = {  
#    "heartbeatResponse":[  
#       {  
#          "cbsdId":"2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982",
#          "grantId":"2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982/1750595678109855402",
#          "transmitExpireTime":str(datetime.now()),
#          "operationParam":{
#             "maxEirp":25,
#             "operationFrequencyRange":{
#                "lowFrequency":3660000000,
#                "highFrequency":3680000000
#             }
#          },
#          "response":{  
#             "responseCode":500,
#             "responseMessage":"TERMINATED_GRANT"
#          }
#       }
#    ]
# }

GR = {    
  "grantResponse": [
        {
            "cbsdId": "2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982",
            "channelType": "GAA",
            "grantExpireTime": "2022-07-07T20:15:30Z",
            "grantId": "2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982/4386536123950778856",
            "heartbeatInterval": 60,
            "response": {
                "responseCode": 0
            }
        }
      ]
    }

HB500 = {  
    "heartbeatResponse": [
        {
            "cbsdId": "2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982",
            "grantId": "2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982/14299188259055949944",
            "heartbeatInterval": 60,
            "operationParam": {
                "maxEirp": 19,
                "operationFrequencyRange": {
                    "highFrequency": 3655000000,
                    "lowFrequency": 3635000000
                }
            },
            "response": {
                "responseCode": 500,
                "responseMessage": "TERMINATED_GRANT"
            },
            # "transmitExpireTime": "2021-07-07T20:15:00Z"
        }
    ]
}


ERR106 = {
    "grantResponse": [
        {
            "response": {
                "responseCode": 106,
                "responseMessage": "NOT_PROCESSED"
            }
        }
    ]
}

ERR501 = {
    "heartbeatResponse": [
        {
            "cbsdId": "2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982",
            "grantId": "2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982/1750595678109855402",
            "heartbeatInterval": 60,
            "response": {
                "responseCode": 501,
                "responseData": [
                    "The grant is suspended because it is in the move list of a DPA that has been activated"
                ],
                "responseMessage": "SUSPENDED_GRANT: The grant is suspended because it is in the move list of a DPA that has been activated"
            },
            "transmitExpireTime": "2021-06-21T22:35:35Z"
        },
        {
            "cbsdId": "2AQ68T99B226/87b4920114c1b81d92a3342a68fa0d86d2c71f37",
            "grantId": "2AQ68T99B226/87b4920114c1b81d92a3342a68fa0d86d2c71f37/11876706669600188705",
            "heartbeatInterval": 60,
            "response": {
                "responseCode": 501,
                "responseData": [
                    "The grant is suspended because it is in the move list of a DPA that has been activated"
                ],
                "responseMessage": "SUSPENDED_GRANT: The grant is suspended because it is in the move list of a DPA that has been activated"
            },
            "transmitExpireTime": "2021-06-21T22:35:35Z"
        }
    ]
}

# ERR400 = {
#     {  
#     "grantResponse":[  
#         {  
#           "cbsdId":"2AQ68T99B226/4943375cc665c2bc8f72536524cbb2ff3b4e7982",
#           "response":{  
#               "responseCode":400,
#               "responseMessage":"Inside GWPZ"
#           }
#         }
#     ]
#   }
# }