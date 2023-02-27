"""Xselect test.
"""

import unittest

from xselect import XselectCommander


class TestXselectCommander(unittest.TestCase):
    def setUp(self):
        self.commander = XselectCommander()

    def test_create_generage_curve_command(self):
        fits_path = "/home/omama/Data/MAXI_J1820p070/nicer_data/DataSet/" \
                    "MainSet/1200120102/xti/" \
                    "event_cl/bc1200120102_0mpu7_cl.evt"
        inputs = [fits_path, "curve", "MAXI J1820+070", "NICER",
                  "1200120102", 0.1, (0.5, 10.0)]
        self.commander.create_curve(*inputs)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
