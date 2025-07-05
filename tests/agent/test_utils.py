import os
import tempfile
from src.agent.utils import save_json, load_json

def test_save_and_load_json():
    data = {"x": 123}
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        save_json(path, data)
        loaded = load_json(path)
        assert loaded == data
    finally:
        os.remove(path) 