import unittest
from hand_namer import *


class TestHandNamer(unittest.TestCase):

    def test_every(self):
        for i in range(9):
            self.assertTrue(HandNamer.name_hand((i, 1, 2, 3)) != "")

    def test_empty(self):
        self.assertEqual(HandNamer.name_hand(()), "Unknown")


if __name__ == '__main__':
    unittest.main()
