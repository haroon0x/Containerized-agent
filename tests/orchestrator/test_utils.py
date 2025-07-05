import os
import tempfile
from orchestrator.utils import utils

def test_save_and_load_json():
    data = {"a": 1, "b": 2}
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        utils.save_json(data, path)
        loaded = utils.load_json(path)
        assert loaded == data
    finally:
        os.remove(path) 