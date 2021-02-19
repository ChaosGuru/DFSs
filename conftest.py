import pytest
import rpyc

@pytest.fixture(scope="session")
def sensei():
    conn = rpyc.connect("localhost", 33333).root
    yield conn
    conn.remove_namespaces('/')

    print("\n-----TEARDOWN-----")