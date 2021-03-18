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
    
    assert sorted(sensei.get_namespaces("/getting")) == \
        sorted(["/getting/tes1", "/getting/more/tes3"])
    assert sorted(sensei.get_namespaces("/getting/more")) == \
        sorted(["/getting/more/tes3"])
    assert sorted(sensei.get_namespaces("/random_string")) == []


def test_remove_namespaces(sensei):
    sensei.create_directory("/test_remove/tes1")
    sensei.create_directory("/test_remove")
    sensei.create_directory("/test_not_remove")

    sensei.remove_namespaces("/test_remove")

    assert "/test_remove/tes1" not in sensei.get_namespaces("/")
    assert "/test_remove" not in sensei.get_namespaces("/")
    assert "/test_not_remove" in sensei.get_namespaces("/")


def test_put_filename(sensei):
    sensei.create_directory("/test_put")
    
    assert len(sensei.put_file("/test_put/my_file.txt", 1_000_000)) == 16
    assert "/test_put/my_file.txt" in sensei.get_namespaces("/test_put")


def test_make_chunkuuids(sensei):
    assert 0