# -*- coding: utf-8 -*-

import logging
from .core import Core


def start(settings)-> Core:
    """
    Стартует ядро. Вызывается из CoreLoader или юнит-тестов.
    :param settings: настройки, с которыми создавать ядро.
    """
    if Core.is_created():
        return Core.get_instance()

    init_logger()

    core = Core.create_instance(settings=settings)

    return core


_has_initialised_init_logger = False


def init_logger(level=logging.WARNING, quiet=False):
    """
    Создаёт и инициализирует логгер.
    """
    global _has_initialised_init_logger

    if _has_initialised_init_logger:
        # инициализировать один раз
        return

    logger = logging.getLogger()
    logger.setLevel(level)

    if level == logging.DEBUG:
        # для дебаг-уровня - побробный лог
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(levelname)3.3s] %(module)s.%(funcName)s: %(message)s', '%y%m%d %H:%M:%S')
    else:
        # для других уровней - просто сообщения
        formatter = logging.Formatter('%(message)s')

    if not quiet:
        # создадим хендлер и добавим его к логгеру питона
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    else:
        # млочаливый режим - логов нет
        logger.handlers = []
        logger.propagate = False
        logger.disabled = True

    _has_initialised_init_logger = True

