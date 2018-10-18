from logging.config import dictConfig
from . import settings

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'console': {
            'format':   '[%(asctime)s][%(levelname)s] %(naem)s '
                        '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt':  '%H:%M:%S',
        },
    },

    'handlers': {
        'console': {
            'level':    settings.LOG_LEVEL,
            'class':    'logging.StreamHandler',
            'formatter':    'console'
        },
    },

    'loggers': {
        '': {
            'handlers': ['console'],
            'level': settings.LOG_LEVEL,
            'propogate': False,
        },
    }
}

dictConfig(logging_config)