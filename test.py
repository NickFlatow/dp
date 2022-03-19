class Member():
    '''some documentation'''

    # __slots__ =["member_id","name"]

    def __init__(self,member_id,name):
        self.member_id = member_id
        self.name = name

    def __someFunc__(self):
        print("someFunc")


# a = Member(1,"tseet")
# print(Member.__module__)
# # a.age = 15
# print(Member.__dict__)



processor_strategies = {
    "registrationRequest": {
        "request_map_key": 'generate_registration_request_map_key',
        "response_map_key": 'generate_simple_response_map_key',
        "process_responses": 'process_registration_responses',
    },
    "spectrumInquiryRequest": {
        "request_map_key": 'generate_simple_request_map_key',
        "response_map_key": 'generate_simple_response_map_key',
        "process_responses": 'process_spectrum_inquiry_responses',
    },
    "grantRequest": {
        "request_map_key": 'generate_simple_request_map_key',
        "response_map_key": 'generate_simple_response_map_key',
        "process_responses": 'process_grant_responses',
    },
    "heartbeatRequest": {
        "request_map_key": 'generate_compound_request_map_key',
        "response_map_key": 'generate_compound_response_map_key',
        "process_responses": 'process_heartbeat_responses',
    },
    "relinquishmentRequest": {
        "request_map_key": 'generate_compound_request_map_key',
        "response_map_key": 'generate_compound_response_map_key',
        "process_responses": 'process_relinquishment_responses',
    },
    "deregistrationRequest": {
        "request_map_key": 'generate_simple_request_map_key',
        "response_map_key": 'generate_simple_response_map_key',
        "process_responses": 'process_deregistration_responses',
    },
}





def registration(test):
    print(test)


funcDict = {"registartionResposne":registration}
reg = funcDict["registartionResposne"]
reg("myfuncTest")
# print(processor_strategies("registartionRequest"))