from logging import Logger

import pytest

from pyleecan.Classes_new._class_info import ClassInfo

# Class information rebuilt from the dataclasses themselves
class_list = list(ClassInfo().get_dict().values())


@pytest.mark.parametrize("class_dict", class_list, ids=lambda c: c["name"])
def test_loggers(class_dict):
    test_obj = class_dict["class"]()
    logger = test_obj.get_logger()
    logger.info("test")
    assert isinstance(logger, Logger)
