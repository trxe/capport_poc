import logging
from pathlib import Path
from typing import Optional


class Logger:
    logger = None

    @classmethod
    def init(
        cls,
        name: str = __name__,
        level=logging.DEBUG,
        output_dir: Optional[str] = None,
        output_filename: str = "%H%M%S_out.log",
    ):
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        if output_dir:
            path = Path(output_dir)
            if not path.exists():
                path.mkdir(parents=True)
            path.joinpath(output_filename)
            with open(path, "+w") as logfile:
                cls.logfilepath = path
                cls.logfile = logfile
                handler.setStream(cls.logfile)

        cls.logger = logging.getLogger(name)
        cls.logger.setLevel(level)
        cls.logger.addHandler(handler)

    @classmethod
    def log(cls, msg, level=logging.INFO):
        if not cls.logger:
            cls.init()
        cls.logger.log(level, msg)

    @classmethod
    def info(cls, msg):
        cls.log(msg, level=logging.INFO)

    @classmethod
    def error(cls, msg):
        cls.log(msg, level=logging.ERROR)

    @classmethod
    def warn(cls, msg):
        cls.log(msg, level=logging.WARNING)

    @classmethod
    def debug(cls, msg):
        cls.log(msg, level=logging.DEBUG)
