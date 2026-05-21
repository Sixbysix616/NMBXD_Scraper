"""Filesystem paths and resume checkpoint handling."""
import os
import json


def get_downloads_dir():
    return os.path.join(os.path.expanduser("~"), "Downloads", "nmbxd")


def get_thread_dir(thread_id):
    return os.path.join(get_downloads_dir(), str(thread_id))


def get_images_dir(thread_id):
    return os.path.join(get_thread_dir(thread_id), "images")


def ensure_thread_dirs(thread_id):
    """Create the thread and images directories. Returns the images dir path."""
    images_dir = get_images_dir(thread_id)
    os.makedirs(images_dir, exist_ok=True)
    return images_dir


def _checkpoint_path(thread_id):
    return os.path.join(get_thread_dir(thread_id), ".checkpoint.json")


def save_checkpoint(thread_id, state):
    with open(_checkpoint_path(thread_id), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)


def load_checkpoint(thread_id):
    path = _checkpoint_path(thread_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def clear_checkpoint(thread_id):
    path = _checkpoint_path(thread_id)
    if os.path.exists(path):
        os.remove(path)
