"""Config module.
"""
import os


class Config:
    base_path = os.path.expanduser("~/.astrobucket")
    tmp_path = os.path.join(base_path, "tmp")
    cache_path = os.path.join(base_path, "cache")

    def setup_path(self):
        os.makedirs(self.base_path, exist_ok=True)
        for d in ["cache", "tmp"]:
            target_path = os.path.join(self.base_path, d)
            os.makedirs(target_path, exist_ok=True)


def setup_path():
    Config().setup_path()
