from fractal import Settings


class SettingsMixin(object):
    def __init__(self, settings: Settings, *args, **kwargs):
        super(SettingsMixin, self).__init__(*args, **kwargs)

        self.settings = settings
