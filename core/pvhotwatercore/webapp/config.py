""" This obtains the webapp runtime configuration from .env and environment variables.
"""

import os
from typing import Any, Dict
from dotenv import dotenv_values

__all__ = ['config']

basedir = os.path.abspath(os.path.dirname(__file__))

config: Dict[str, Any] = {
    **dotenv_values(".env"),
    **os.environ
}
