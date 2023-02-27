"""Test for core module.
"""

import unittest

from astropy.table import Table
import numpy as np

from core import Namer
from core import Client


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client_args_list = []

    def test_request_curve_cache(self):

        obsid = "1200120102"
        fits_path = "/home/omama/Data/MAXI_J1820p070/nicer_data/DataSet/" \
                    f"MainSet/{obsid}/xti/" \
                    f"event_cl/bc{obsid}_0mpu7_cl.evt"

        curve_args = [0.1, (0.5, 10.0)]
        client1 = Client(fits_path, "MAXI J1820+070", "NICER", obsid)
        table1 = client1.request_curve(*curve_args)

        client2 = Client(fits_path, "MAXI J1820+070", "NICER", obsid)
        table2 = client2.request_curve(*curve_args)

        self.assertTrue(np.array_equal(table1, table2))

        self.client_args_list.append([client1, "curve", curve_args])
        self.client_args_list.append([client2, "curve", curve_args])

    def test_request_curve_type(self):
        obsid = "1200120102"
        fits_path = "/home/omama/Data/MAXI_J1820p070/nicer_data/DataSet/" \
                    f"MainSet/{obsid}/xti/" \
                    f"event_cl/bc{obsid}_0mpu7_cl.evt"

        curve_args = [0.1, (0.5, 10.0)]
        client = Client(fits_path, "MAXI J1820+070", "NICER", obsid)
        table = client.request_curve(*curve_args)
        self.assertTrue(isinstance(table, Table))

        self.client_args_list.append([client, "curve", curve_args])

    def tearDown(self):
        for (client, mode, args) in self.client_args_list:
            client.clear_cache(mode, *args)


class NamerTest(unittest.TestCase):
    def test_get_name_01(self):
        inputs = ["curve", "MAXI J1820+070", "NICER", "1200120106", 0.1]
        fullname = Namer().get_name(*inputs)
        expected = "curve_maxij1820+070_nicer_1200120106_00000000p1"
        self.assertEqual(fullname, expected)

    def test_get_name_02(self):
        inputs = ["curve", "MAXI J1820+070", "NICER", "1200120106", 1.0]
        fullname = Namer().get_name(*inputs)
        expected = "curve_maxij1820+070_nicer_1200120106_0000000001"
        self.assertEqual(fullname, expected)

    def test_get_name_03(self):
        inputs = ["spectrum", "MAXI J1820+070", "NICER", "1200120106",
                  0.5, [0.7, 10.0]]
        fullname = Namer().get_name(*inputs)
        expected = "spectrum_maxij1820+070_nicer_1200120106_" \
                   "00000000p5_00000000p7-0000000010"
        self.assertEqual(fullname, expected)


if __name__ == "__main__":
    unittest.main()
