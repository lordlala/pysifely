#region Imports
from .version import version as __version__

import logging
import time
#endregion Imports

#region begin
_LOGGER = logging.getLogger(__name__)

__author__ = 'Jason Adams'
__license__ = 'MIT'
#endregion begin

class Pysifely:

    def __init__(self):
        self.email = None
        self.password = None