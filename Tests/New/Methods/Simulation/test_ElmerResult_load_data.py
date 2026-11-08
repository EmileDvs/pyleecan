# -*- coding: utf-8 -*-

import pytest

from os.path import join
from Tests import TEST_DATA_DIR
from Tests.New._test_paths import save_path
from pyleecan.Classes_new.elmer_results import ElmerResults


@pytest.mark.StructElmer
class Test_ElmerResults(object):
    def test_ElmerResults(self):
        """Test that load_data method is working"""
        # TODO improve by different settings and compare values
        res = ElmerResults()
        res.file = join(TEST_DATA_DIR, "StructElmer/LineValues.dat")

        res.columns = [
            "Iteration step"
            "Boundary condition"
            "Node index"
            "coordinate 1"
            "coordinate 2"
            "coordinate 3"
            "displacement 1"
            "displacement 2"
            "principal stress 1"
            "principal stress 2"
            "vonmises"
        ]

        res.load_data()


# To run it without pytest
if __name__ == "__main__":
    # create test object and test to load result file
    obj = Test_ElmerResults()
    obj.test_ElmerResults()
