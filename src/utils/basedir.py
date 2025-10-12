from pathlib import Path


__BASEDIR__: Path = None

class Basedir:
    @staticmethod
    def init(basedir):
        global __BASEDIR__
        __BASEDIR__ = Path(basedir)

    @staticmethod
    def get() -> Path:
        global __BASEDIR__
        return __BASEDIR__

    @staticmethod
    def get_str() -> str:
        return Basedir.get().absolute().as_posix()
