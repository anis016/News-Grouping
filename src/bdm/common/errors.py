# Error is the parent class.
# Define all the other User Defined Error extending Error class
class Error(Exception):

    def __init__(self, message):
        self.message = message