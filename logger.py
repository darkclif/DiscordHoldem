import time


class Logger:
    def __init__(self, *, prefix="", show=False):
        self.prefix = prefix
        self.show = show

        self.logs = []

    def log(self, msg):
        self.logs.append({"msg": msg, "time": time.time()})

        if self.show:
            pref = "" if self.prefix == "" else "[{}]".format(self.prefix)
            print(pref, msg)


def global_log(channel, msg):
    _loggers[channel].log(msg)


_loggers = {
    "warning": Logger(prefix="WARNING", show=True),
    "error": Logger(prefix="ERROR", show=True),
    "info": Logger(prefix="INFO", show=True),

    "dbg": Logger(prefix="DBG", show=True)
}
