import pytest
import rpyc

import sensei_dono


def test_add_single_directory(sensei):
    sensei.create_directory("/boom")
    assert "/boom" in sorted(sensei.get_namespaces("/"))


def test_create_duplicate(sensei):
    assert sensei.create_directory("/duplicate1") == "/duplicate1"
    assert sensei.create_directory("/duplicate1") == False


def test_add_directory_fail(sensei):
    assert sensei.create_directory("/test1") == "/test1"
    assert sensei.create_directory("/some/test") == "/some/test"
    assert sensei.create_directory("/some/more/test") == "/some/more/test"
    assert sensei.create_directory("/test2/") == "/test2"
    assert sensei.create_directory("/test3//") == False


def test_get_namespace(sensei):
    sensei.create_directory("/getting/tes1")
    sensei.create_directory("/getting/more/tes3")
    
    assert sorted(sensei.get_namespaces('/getting')) == \
        sorted(["/getting/tes1", "/getting/more/tes3"])
    assert sorted(sensei.get_namespaces('/getting/more')) == \
        sorted(["/getting/more/tes3"])
    assert sorted(sensei.get_namespaces('/random_string')) == []