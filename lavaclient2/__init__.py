# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

__version_info__ = (0, 1, '1a1')
__version__ = '.'.join(map(str, __version_info__))


import logging
from lavaclient2 import constants
from lavaclient2.client import Lava


# Attempt to import the NullHandler (not available in py2.6)
try:
    from logging import NullHandler
except ImportError:  # pragma: no cover
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


LOG = logging.getLogger(constants.LOGGER_NAME)
LOG.addHandler(NullHandler())


__all__ = ['Lava']
