from click.testing import CliRunner
import pytest
import rpyc

import client_kun


@pytest.fixture
def new_user_data():
    client_kun.new_user()
    yield client_kun.get_cache()
    client_kun.new_user()


def test_pwd(new_user_data):
    runner = CliRunner()
    result = runner.invoke(client_kun.dfs, ["pwd"])

    assert result.output == new_user_data["pwd"] + "\n"


def test_ls(sensei, new_user_data):
    runner = CliRunner()
    result = runner.invoke(client_kun.dfs, ["ls"])

    # temp
    assert result.output == ' '.join(sensei.get_namespaces(new_user_data["pwd"]))