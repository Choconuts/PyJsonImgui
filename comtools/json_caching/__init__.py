import json
import os
import shutil
from os import path
import logging


def save_json(obj, file):
    with open(file, 'w') as fp:
        json.dump(obj, fp)


def load_json(file):
    with open(file, 'r') as fp:
        return json.load(fp)


def is_child_of(obj, cls):
    try:
        for i in obj.__bases__:
            if i is cls or isinstance(i, cls):
                return True
        for i in obj.__bases__:
            if is_child_of(i, cls):
                return True
    except AttributeError:
        return is_child_of(obj.__class__, cls)
    return False


class JsonCache:

    WARN = False

    def __init__(self, tag):
        """
        default located in the work dir,
        if you want to change, use relocate.

        ** tag can not start with '_' !!! or you cannot

        :param tag: the name by which you find the cache
        """
        self._tag = tag
        self._folder = '.'
        self._expansion = '.txt'
        self._make_dir()

    def set_expansion(self, new_expansion:str):
        if not new_expansion.startswith('.'):
            new_expansion = '.' + new_expansion
        self._expansion = new_expansion
        return self

    def relocate(self, folder, retain=False):
        """
        move the cache to the destination dir, won't cover the destination caches, just relocating the readable source

        :param folder: the parent dir of the destination
        :param retain: retain the current cache folders, default False
        :return:
        """
        last_cd = self.cache_dir()

        if os.path.samefile(folder, self._folder):
            return self

        self._folder = os.path.normpath(folder)
        if not os.path.exists(self.cache_dir()):
            shutil.move(last_cd, self.cache_dir())
        else:
            if not retain:
                shutil.rmtree(last_cd)
            if self.WARN:
                logging.warning('Dir already exists!')
        return self

    def cache_dir(self):
        return self._tags_to_path(self._tag)

    def _make_dir(self):
        if not path.exists(self.cache_dir()):
            os.makedirs(self.cache_dir())

    def _tags_to_path(self, *tags):
        return path.join(self._folder, *['.' + t for t in tags])

    def __getitem__(self, item):
        if os.path.isdir(self._tags_to_path(self._tag, item)):
            return self.__class__(item).relocate(self.cache_dir())
        try:
            return load_json(self._tags_to_path(self._tag, item + self._expansion))
        except FileNotFoundError:
            return None
        except json.decoder.JSONDecodeError:
            return None

    def __getattr__(self, item):
        if item.startswith('_'):
            return super().__getattribute__(item)
        else:
            return self.__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(value, JsonCache):
            assert key == value._tag
            value.relocate(self.cache_dir())
        elif value == JsonCache or is_child_of(value, JsonCache):
            value(key).relocate(self.cache_dir())
        else:
            try:
                save_json(value, self._tags_to_path(self._tag, key + self._expansion))
            except TypeError as e:
                os.remove(self._tags_to_path(self._tag, key + self._expansion))
                raise e

    def __setattr__(self, key, value):
        if key.startswith('_'):
            return super().__setattr__(key, value)
        self.__setitem__(key, value)

    def clear(self):
        shutil.rmtree(self.cache_dir())
        self._make_dir()


if __name__ == '__main__':
    jc = JsonCache('tst').relocate('tmp')
    jc.b = JsonCache
    print(jc.c)
    jc.clear()
