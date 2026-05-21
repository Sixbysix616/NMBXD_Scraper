"""Filesystem paths and resume checkpoint handling."""
import os
import json


def get_default_output_dir():
    """Default parent folder for archives when the user doesn't pick one."""
    return os.path.join(os.path.expanduser("~"), "Downloads", "nmbxd")


def get_thread_dir(output_dir, thread_id):
    return os.path.join(output_dir, str(thread_id))


def get_images_dir(thread_dir):
    return os.path.join(thread_dir, "images")


def ensure_thread_dirs(thread_dir):
    """Create the thread and images directories. Returns the images dir path."""
    images_dir = get_images_dir(thread_dir)
    os.makedirs(images_dir, exist_ok=True)
    return images_dir


def _checkpoint_path(thread_dir):
    return os.path.join(thread_dir, ".checkpoint.json")


def save_checkpoint(thread_dir, state):
    with open(_checkpoint_path(thread_dir), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)


def load_checkpoint(thread_dir):
    path = _checkpoint_path(thread_dir)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def clear_checkpoint(thread_dir):
    path = _checkpoint_path(thread_dir)
    if os.path.exists(path):
        os.remove(path)
