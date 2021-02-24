from click.testing import CliRunner
import pytest
import rpyc

import client_kun


@pytest.fixture
def client():
    client_kun.new_user()
    yield client_kun
    client_kun.new_user()


def test_pwd(client):
    runner = CliRunner()
    result = runner.invoke(client_kun.dfs, ["pwd"])

    assert result.output.strip("\n") == client.get_cache()["pwd"]


def test_mkdir(sensei, client):
    runner = CliRunner()
    runner.invoke(client_kun.mkdir, ["mkdir_test"])

    assert "/mkdir_test" in sorted(sensei.get_namespaces("/"))


def test_cd(client):
    runner = CliRunner()
    runner.invoke(client_kun.mkdir, ["cd_test"])
    runner.invoke(client_kun.cd, ["cd_test"])

    assert client.get_cache()["pwd"] == "/cd_test"


def test_cd_root(client):
    runner = CliRunner()
    runner.invoke(client_kun.mkdir, ["cd_test_root"])
    runner.invoke(client_kun.cd, ["cd_test_root"])
    runner.invoke(client_kun.cd, ["/"])

    assert client.get_cache()["pwd"] == "/"


def test_cd_parent(client):
    runner = CliRunner()
    runner.invoke(client_kun.mkdir, ["cd_test_parent"])
    runner.invoke(client_kun.cd, ["cd_test_parent"])
    runner.invoke(client_kun.cd, [".."])

    assert client.get_cache()["pwd"] == "/"

    runner.invoke(client_kun.cd, ["/"])


def test_cd_fail(client):
    runner = CliRunner()
    runner.invoke(client_kun.cd, ["cd_test_fail"])

    assert client.get_cache()["pwd"] == "/"

    runner.invoke(client_kun.cd, ["/"])


def test_ls(client):
    runner = CliRunner()
    runner.invoke(client_kun.mkdir, ["ls_test"])
    runner.invoke(client_kun.cd, ["ls_test"])
    runner.invoke(client_kun.mkdir, ["ls_test2"])

    result = runner.invoke(client_kun.dfs, ["ls"])

    assert result.output.strip("\n") == "ls_test2"
        

def test_rm(client):
    runner = CliRunner()
    runner.invoke(client_kun.mkdir, ["rm_test"])
    runner.invoke(client_kun.cd, ["rm_test"])
    runner.invoke(client_kun.mkdir, ["rm_test2"])
    runner.invoke(client_kun.rm, ["rm_test2"])

    result = runner.invoke(client_kun.dfs, ["ls"])

    assert result.output.strip("\n") == ""