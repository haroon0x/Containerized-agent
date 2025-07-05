import os
import tempfile
from agent.utils import utils

def test_save_and_load_json():
    data = {"x": 123}
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        utils.save_json(path, data)
        loaded = utils.load_json(path)
        assert loaded == data
    finally:
        os.remove(path) 