def test_class(settings_class):
    assert hasattr(settings_class, "APP_NAME")
    assert not hasattr(settings_class, "WEBSITE_HOST")


def test_load(settings_class):
    assert hasattr(settings_class(), "WEBSITE_HOST")


def test_reload(settings):
    app_name = settings.APP_NAME
    assert settings.WEBSITE_HOST != "changed"

    settings.reload(
        {
            "APP_NAME": "not_changed",
            "WEBSITE_HOST": "changed",
        }
    )

    assert settings.APP_NAME == app_name
    assert settings.WEBSITE_HOST == "changed"
