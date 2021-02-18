from click.testing import CliRunner

from client_kun import dfs


def test_pwd():
    runner = CliRunner()
    result = runner.invoke(dfs, ["pwd"])

    assert result.output == "/\n"


def test_ls():
    pass