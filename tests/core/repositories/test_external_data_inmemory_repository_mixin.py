def test_load_data_dict(external_data_inmemory_repository, an_object):
    data = {an_object.__class__.__name__.lower(): [an_object.__dict__]}

    external_data_inmemory_repository.load_data_dict(data)

    assert list(external_data_inmemory_repository.find()) == [an_object]


def test_dump_data_dict(external_data_inmemory_repository, an_object):
    external_data_inmemory_repository.add(an_object)

    data = (an_object.__class__.__name__.lower(), [an_object.__dict__])

    assert external_data_inmemory_repository.dump_data_dict() == data


def test_load_data_json(external_data_inmemory_repository, an_object):
    import json

    data = {an_object.__class__.__name__.lower(): json.dumps([an_object.__dict__])}

    external_data_inmemory_repository.load_data_json(data)

    assert list(external_data_inmemory_repository.find()) == [an_object]


def test_dump_data_json(external_data_inmemory_repository, an_object):
    external_data_inmemory_repository.add(an_object)

    import json

    data = (an_object.__class__.__name__.lower(), json.dumps([an_object.__dict__]))

    assert external_data_inmemory_repository.dump_data_json() == data
