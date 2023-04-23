import logging
from math import exp


_log = logging.getLogger('logs')


def log(msg: str, log_type: str = 'UNKNOWN', log_as: str = 'info'):
    log_type = f'{log_type:<8}'
    if log_as == 'info':
        msg = log_type + ' - ' + str(msg)
        _log.info(msg)
    elif log_as == 'error':
        _log.error(msg, exc_info=True)
    elif log_as == 'warn':
        msg = log_type + ' - ' + str(msg)
        _log.warning(msg),
    elif log_as == 'debug':
        msg = log_type + ' - ' + str(msg)
        _log.debug(msg)


def normed_exponential(z: list):
    k = 10 ** len(str(max(z)))
    x = list(map(lambda n: n / k, z))
    x_exps = list(map(lambda y: y if y != 1 else 0, list(map(lambda n: exp(n), x))))
    sum_x_exps = sum(x_exps)
    return [y / sum_x_exps for y in x_exps]


class ProgressBar:
    def __init__(self, max_size: int, current: int = 0, size: int = 10, advanced: bool = False):
        self.max_size = max_size
        self.current = current
        self.size = size
        self.advanced = advanced

        self.border = '│'
        self.sym = '█'
        self.space = '─'

    def __str__(self):
        if self.current > self.max_size:
            raise KeyError(f'ProgressBar current > max ({self.current} > {self.max_size})')

        step = self.max_size / self.size

        bar = self.border + self.sym * int(self.current / step) + int(
            (self.max_size - self.current) / step) * self.space + self.border
        if self.advanced:
            proc = round(self.current / self.max_size * 100, 2)
            bar = f'{bar} [{self.current}/{self.max_size}] {proc}%'
        return bar
