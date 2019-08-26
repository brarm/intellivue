import string
import random

class SerialDevice():
    def write(self, message):
        print 'Writing serial message ', message, 'to device'

    def read(self):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(16))