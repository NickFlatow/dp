import enum

class cbsdAction(enum.Enum):
    STARTGRANT  = "startGrant"
    DEREGISTER  = "deregister"
    RELINQUISH  = "relinquish"


class MessageTypes(enum.Enum):
    REGISTRATION = "registration"
    SPECTRUM_INQUIRY = "spectrumInquiry"
    GRANT = "grant"
    HEARTBEAT = "heartbeat"
    RELINQUISHMENT = "relinquishment"
    DEREGISTRATION = "deregistration"


class GrantStates(enum.Enum):
    IDLE = "idle"
    GRANTED = "granted"
    AUTHORIZED = "authorized"

class ResponseCodes(enum.Enum):
    # Success
    SUCCESS = 0

    # 100 – 199: general errors related to the SAS-CBSD protocol
    VERSION = 100
    BLACKLISTED = 101
    MISSING_PARAM = 102
    INVALID_VALUE = 103
    CERT_ERROR = 104
    DEREGISTER = 105

    # 200 – 299: error events related to the CBSD Registration procedure
    REG_PENDING = 200
    GROUP_ERROR = 201

    # 300 – 399: error events related to the Spectrum Inquiry procedure
    UNSUPPORTED_SPECTRUM = 300

    # 400 – 499: error events related to the Grant procedure
    INTERFERENCE = 400
    GRANT_CONFLICT = 401

    # 500 – 599: error events related to the Heartbeat procedure
    TERMINATED_GRANT = 500
    SUSPENDED_GRANT = 501
    UNSYNC_OP_PARAM = 502
