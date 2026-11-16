"""Saving of the user config file (Functions/init_environment.save_config_dict).

get_config_dict saves the config at each import of pyleecan.definitions: the
file is written only when its content changes, atomically, with the same
content as before (json.dump, sort_keys, indent 4).
"""

import json
import threading
from os import listdir
from os.path import getmtime

import pytest

import pyleecan.definitions
from pyleecan.Functions.init_environment import save_config_dict


@pytest.fixture
def conf_path(tmp_path, monkeypatch):
    path = tmp_path / "main_config_dict.json"
    monkeypatch.setattr(pyleecan.definitions, "CONF_PATH", str(path))
    return path


def test_same_content_as_json_dump(conf_path, tmp_path):
    config = {"b": {"y": [1, 2]}, "a": "text", "version": "1.5.2"}
    save_config_dict(config)
    expected = tmp_path / "expected.json"
    with open(expected, "w") as expected_file:  # Legacy writing
        json.dump(config, expected_file, sort_keys=True, indent=4, separators=(",", ": "))
    assert conf_path.read_bytes() == expected.read_bytes()
    assert sorted(listdir(tmp_path)) == ["expected.json", "main_config_dict.json"]


def test_unchanged_config_is_not_written(conf_path):
    save_config_dict({"a": 1})
    mtime = getmtime(conf_path)
    save_config_dict({"a": 1})
    assert getmtime(conf_path) == mtime
    save_config_dict({"a": 2})
    assert json.loads(conf_path.read_text()) == {"a": 2}


def test_readers_never_see_a_partial_file(conf_path):
    configs = [{"key": "x" * 5000}, {"key": "y" * 10, "other": list(range(500))}]
    save_config_dict(configs[0])
    errors = []

    def write():
        for index in range(100):
            save_config_dict(configs[index % 2])

    writer = threading.Thread(target=write)
    writer.start()
    while writer.is_alive():
        try:
            with open(conf_path) as config_file:
                assert json.load(config_file) in configs
        except PermissionError:
            pass  # Windows: the file is being replaced
        except json.JSONDecodeError as error:
            errors.append(error)
    writer.join()
    assert not errors
