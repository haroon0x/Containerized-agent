import os
import tempfile
from src.orchestrator.utils import save_json, load_json

def test_save_and_load_json():
    data = {"a": 1, "b": 2}
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        path = tf.name
    try:
        save_json(data, path)
        loaded = load_json(path)
        assert loaded == data
    finally:
        os.remove(path) 