import demistomock as demisto
import json

INTEGRATION_CONNECTION = {
    'serverURL': 'http://example.com',
    'APIKey': 'This is the API',
    'proxy': True,
    'insecure': False,
    'isFetch': True
}


def get_fetch_data():
    with open('./test_data.json', 'r') as f:
        return json.loads(f.read())


def test_fetch(mocker, requests_mock):
    """
    Args:
        mocker:

    Returns:
        Validates that:
         * the first fetch works properly.
         * fetching one more incident fetches only that new one
    """
    mocker.patch.object(demisto, 'params', return_value=INTEGRATION_CONNECTION)
    mocker.patch.object(demisto, 'getLastRun', return_value={'last_fetch_time': '2019-10-21T15:00:00Z'})
    requests_mock.get('http://example.com/api/v3/alerts/alert/?ordering=created&limit=100', json=get_fetch_data())
    from Stealthwatch_Cloud import fetch_incidents
    mocker.patch.object(demisto, 'setLastRun')
    mocker.patch.object(demisto, 'incidents')
    fetch_incidents()
    # The fetch time was updated.
    assert demisto.setLastRun.call_args[0][0].get('last_fetch_time') == '2019-10-22T15:00:00Z'
    # Created 2 new incidents
    assert len(demisto.incidents.call_args[0][0]) == 2

    mocker.patch.object(demisto, 'getLastRun', return_value={'last_fetch_time': '2019-10-22T15:00:00Z'})
    fetch_incidents()
    # The fetch time was not updated this time.
    assert demisto.setLastRun.call_args[0][0].get('last_fetch_time') == '2019-10-22T15:00:00Z'
    # No new incidents were made
    assert len(demisto.incidents.call_args[0][0]) == 0
