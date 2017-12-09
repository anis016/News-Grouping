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


# def flip(flag):
#     if flag is True:
#         return False
#     else:
#         return True
#
# groups = collections.defaultdict(set)
# group_value = 0
#
# def transitive_closure(v1, v2):
#     global group_value
#
#     if len(groups) == 0:
#         key = "group" + str(group_value)
#         groups[key].add(v1)
#         groups[key].add(v2)
#         group_value += 1
#     else:
#         flagv1 = False
#         flagv2 = False
#         which_group = ""
#         for key, value in groups.items():
#             if v1 in value and v2 in value:
#                 which_group = key
#                 flagv2 = False
#                 flagv1 = False
#                 break
#             elif v1 not in value and v2 in value:
#                 which_group = key
#                 flagv1 = True
#                 flagv2 = False
#                 break
#             elif v1 in value and v2 not in value:
#                 which_group = key
#                 flagv1 = False
#                 flagv2 = True
#                 break
#             elif v1 not in value and v2 not in value:
#                 flagv1 = True
#                 flagv2 = True
#
#         if flagv1 == True and flagv2 == True:
#             key = "group" + str(group_value)
#             groups[key].add(v1)
#             groups[key].add(v2)
#             group_value += 1
#         else:
#             groups[which_group].add(v1)
#             groups[which_group].add(v2)