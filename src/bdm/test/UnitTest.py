import unittest

def multiply(a, b):
    """
    >>> multiply(4, 3)
    12
    >>> multiply('a', 3)
    'aaa'
    """
    return a * b

# The standard workflow is:
# 1. Define your own class derived from unittest.TestCase.
# 2. Then fill it with functions that start with ‘test_’.
# 3. Run the tests by placing unittest.main() in __main__ method.

# Example
class UnitTestBDM(unittest.TestCase):

    def setUp(self):
        pass

    def test_numbers_3_4(self):
        self.assertEqual(multiply(3, 4), 12)

    # this will fail
    def test_numbers_a_3(self):
        self.assertEqual(multiply('a', 3), 'aa')

    # add more tests

if __name__ == '__main__':
    unittest.main()