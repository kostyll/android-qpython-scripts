# import androidhelper
# droid = androidhelper.Android()
# droid.makeToast('Hello, Username!')

import mock       

import telnet_server_as_tcp_client as tstc


@mock.patch('io.BytesIO',side_effect=None)
def test_NetworkCommunicator_convert_data_to_uint(mock):
    network_communicator = tstc.NetworkCommuticator()
    assert 23 == network_communicator.convert_data_to_uint(chr(23))
    assert 2**32-1 == network_communicator.convert_data_to_uint('\xff\xff\xff\xff')

def test_NetworkCommuticator_convert_uint_to_data():
    network_communicator = tstc.NetworkCommuticator()
    assert '\xff\xff\xff\xff' == network_communicator.convert_uint_to_data(2**32-1)

    assert '\xff\xff\xff\xff' == network_communicator.convert_uint_to_data(2**32)
