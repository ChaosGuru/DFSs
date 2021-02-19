import pytest
import rpyc

import sensei_dono


def test_empty_namespace(sensei):
    assert list(sensei.get_namespaces("/")) == []
    assert list(sensei.get_namespaces()) == []


def test_add_namespace(sensei):
    sensei.create_namespaces("/", "boom")
    assert sorted(sensei.get_namespaces("/")) == sorted(["/boom"])