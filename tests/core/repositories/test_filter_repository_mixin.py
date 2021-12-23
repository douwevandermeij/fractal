def test_filter(inmemory_filter_repository, an_object, another_object):
    inmemory_filter_repository.add(an_object)
    inmemory_filter_repository.add(another_object)

    assert len(list(inmemory_filter_repository.find_filter("", fields=["name"]))) == 2
    assert len(list(inmemory_filter_repository.find_filter("default_name", fields=["name"]))) == 1
    assert len(list(inmemory_filter_repository.find_filter("default", fields=["name"]))) == 1
    assert len(list(inmemory_filter_repository.find_filter("name", fields=["name"]))) == 2
    assert len(list(inmemory_filter_repository.find_filter("t_n", fields=["name"]))) == 1
    assert len(list(inmemory_filter_repository.find_filter("_", fields=["name"]))) == 2
    assert len(list(inmemory_filter_repository.find_filter("x", fields=["name"]))) == 0


def test_filter_specification(inmemory_filter_repository, an_object, another_object):
    inmemory_filter_repository.add(an_object)
    inmemory_filter_repository.add(another_object)

    from fractal.core.specifications.id_specification import IdSpecification

    specification = IdSpecification("1")

    assert len(list(inmemory_filter_repository.find_filter("_", fields=["name"], specification=specification))) == 1


def test_filter_pre_processor(inmemory_filter_repository, an_object):
    an_object.name = an_object.name.upper()

    inmemory_filter_repository.add(an_object)

    assert len(list(inmemory_filter_repository.find_filter("default_name", fields=["name"]))) == 0
    assert len(list(inmemory_filter_repository.find_filter("DEFAULT_NAME", fields=["name"]))) == 1
    assert len(list(inmemory_filter_repository.find_filter("default_name", fields=["name"], pre_processor=lambda i: i.lower()))) == 1
