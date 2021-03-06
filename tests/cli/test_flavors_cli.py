from mock import patch

from lavaclient.cli import main
from lavaclient.api.response import Flavor


@patch('sys.argv', ['lava', 'flavors', 'list'])
def test_list(print_table, mock_client, flavors_response):
    mock_client._request.return_value = flavors_response
    main()

    (data, header), kwargs = print_table.call_args
    assert list(data) == [['hadoop1-15', 'Medium Hadoop Instance', 15360, 4,
                           2500]]
    assert header == Flavor.table_header
    assert kwargs['title'] is None
