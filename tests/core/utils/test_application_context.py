def test_load(fake_application_context_class, fake_service_class):
    assert not fake_application_context_class.instance
    assert not hasattr(
        fake_application_context_class.instance, fake_service_class.__class__.__name__
    )

    context = fake_application_context_class()
    assert context == fake_application_context_class.instance

    assert len(context.repositories) == 1
    assert len(context.services) == 2

    from fractal.core.utils.string import camel_to_snake

    assert hasattr(context, camel_to_snake(fake_service_class.__name__))


def test_reload(
    fake_application_context_class,
    fake_service_class,
    another_fake_service_class,
    settings,
):
    context = fake_application_context_class()

    assert type(context.fake_service) == fake_service_class

    settings.reload(
        {
            "FAKE_SERVICE": "another",
        }
    )
    context.reload()
    assert context == fake_application_context_class.instance

    assert len(context.repositories) == 1
    assert len(context.services) == 2

    from fractal.core.utils.string import camel_to_snake

    assert hasattr(context, camel_to_snake(fake_service_class.__name__))
    assert type(context.fake_service) == another_fake_service_class


def test_adapters(
    fake_application_context_class, inmemory_repository, fake_service_class, settings
):
    settings.reload(
        {
            "FAKE_SERVICE": "",
        }
    )
    context = fake_application_context_class()

    assert len(list(context.adapters())) == 3

    from fractal.contrib.tokens.services import StaticTokenService

    assert {type(a) for a in context.adapters()} == {inmemory_repository.__class__, fake_service_class, StaticTokenService}
