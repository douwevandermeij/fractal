def test_is_healthy(service):
    assert service.is_healthy()


def test_install(empty_application_context):
    from fractal.core.services import Service

    assert next(Service.install(empty_application_context)).__class__ == Service
