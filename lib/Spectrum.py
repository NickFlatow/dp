from lib.messagePrimitive import MessagePrimitive
from lib.types import cbsdAction
import time 

class Spectrum(MessagePrimitive):


  def Run(self) -> cbsdAction:
      while True:
        print("SIQ")
        time.sleep(3)