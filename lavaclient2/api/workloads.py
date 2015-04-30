#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import six
import textwrap
import logging
from figgis import Config, Field, ListField

from lavaclient2.api import resource
from lavaclient2.util import (display, display_table, CommandLine, command,
                              argument, print_table, prettify)
from lavaclient2.log import NullHandler
from itertools import repeat, chain


LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


LIST_DESCRIPTION = """\
Get a list of possible workloads that Lava clusters can handle. Returned
workload ID's may be fed to the recommendations command for more information.
"""

RECOMMENDATIONS_EPILOG = """\
PERSISTENCE

For a particular workflow, you may need a persistent disk storage to access
your results, or you might need your cluster to have persistent nodes that you
can always log in to. Or, you might need neither (or both). You can tell the
recommendations API what you'll need using the 'persistence' paramter. Here
are the possible values:

    data - Require persistent on-disk data storage
    all  - Persist your data and cluster nodes
    none - You require neither persistent disk storage or cluster nodes
"""


######################################################################
# API Responses
######################################################################

class Workload(Config):

    table_columns = ('id', 'name', 'caption', '_description')
    table_header = ('ID', 'Name', 'Caption', 'Description')

    id = Field(six.text_type, required=True)
    name = Field(six.text_type, required=True)
    caption = Field(six.text_type, required=True)
    description = Field(six.text_type, required=True)

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 30))


class WorkloadsResponse(Config):

    """Response from /workloads"""

    workloads = ListField(Workload, required=True)


class Size(Config):

    table_columns = ('flavor', 'minutes', 'nodecount', 'recommended')
    table_header = ('Flavor', 'Minutes', 'Nodes', 'Recommended')

    flavor = Field(six.text_type, required=True)
    minutes = Field(float, required=True)
    nodecount = Field(int, required=True)
    recommended = Field(bool, default=False)


@prettify('requires')
class Recommendations(Config):

    """Recommendations on how to use the Lava API for a given workload"""

    name = Field(six.text_type, required=True)
    description = Field(six.text_type, required=True)
    requires = ListField(six.text_type, required=True)
    sizes = ListField(Size, required=True)

    @property
    def _description(self):
        return '\n'.join(textwrap.wrap(self.description, 30))


class RecommendationsResponse(Config):

    recommendations = ListField(Recommendations)


######################################################################
# API Request data
######################################################################

class RecommendationParams(Config):

    storagesize = Field(float, required=True)
    persistent = Field(six.text_type, choices=('all', 'none', 'data'))


######################################################################
# API Resource
######################################################################

def display_recommendations(data):
    rows = []
    for rec in data:
        items = six.moves.zip(
            chain([rec.name], repeat('')),
            chain(textwrap.wrap(rec._requires, 30), repeat('')),
            chain(textwrap.wrap(rec.description, 30), repeat('')),
            rec.sizes)

        rows.extend((name, requires, desc, size.flavor, size.minutes,
                     size.nodecount, size.recommended)
                    for name, requires, desc, size in items)

    header = ('Name', 'Requires', 'Description', 'Flavor', 'Minutes', 'Nodes',
              'Recommended')
    print_table(rows, header)


@six.add_metaclass(CommandLine)
class Resource(resource.Resource):

    """Workloads API methods"""

    @command(parser_options=dict(
        description=LIST_DESCRIPTION)
    )
    @display_table(Workload)
    def list(self):
        """
        Get list of Lava workloads

        :returns: List of Workload objects
        """
        return self._parse_response(
            self._client._get('/workloads'),
            WorkloadsResponse,
            wrapper='workloads')

    @command(
        parser_options=dict(
            description='Get recommendations for a certain workload',
            epilog=RECOMMENDATIONS_EPILOG,
        ),
        storage_size=argument(type=int, help='Required disk space (in GB)'),
        persistence=argument(choices=['all', 'data', 'none'],
                             help='See PERSISTENCE')
    )
    @display(display_recommendations)
    def recommendations(self, workload_id, storage_size, persistence):
        """
        Get recommendations for the given workload.

        :param workload_id: Workload ID (see the :func:`get` method)
        :param storage_size: The desired amount of disk space (in GB)
        :param persistence: One of the following values:
            - 'data': persistent (large) data storage is required
            - 'all': persist data and your cluster servers
            - 'none': your data and clusters are ephemeral
        :returns: List of Recommendation objects
        """
        params = self._marshal_request({'storagesize': storage_size,
                                        'persistent': persistence},
                                       RecommendationParams)
        return self._parse_response(
            self._client._get('/workloads/{0}/recommendations'.format(
                workload_id), params=params),
            RecommendationsResponse,
            wrapper='recommendations')
