# import unittest
# mport Domain_Proxy.run as r


# def fun(x):
#     return x + 1

# def test():
#     unittest.TestCase.assertEqual(fun(3), 4)

# test()
# # def fun(x):
# #     return x + 1

# # class MyTest(unittest.TestCase):
# #     def test(self):
# #         self.assertEqual(fun(3), 4)
# error_resposne = {"registrationResponse": [{"response": {"responseCode": 200}},{"response": {"responseCode": 200}}]}
# error_response =  {"registrationResponse": [{"response": {"responseCode": 200,"responseMessage": "A Category B device must be installed by a CPI"}}]}
error_list = {
  "registrationResponse": [
    {
      "response": {
        "responseCode": 200,
        "responseMessage": "A Category B device must be installed by a CPI"
      }
    },
    {
      "response": {
        "responseCode": 200,
        "responseMessage": "A Category B device must be installed by a CPI"
      }
    },
    {
      "response": {
        "responseCode": 200,
        "responseMessage": "A Category B device must be installed by a CPI"
      }
    }
  ]
}
