from django.apps import apps
from service.settings import Settings

from fractal.core.repositories.external_data_inmemory_repository_mixin import (
    ExternalDataInMemoryRepositoryMixin,
)


class SessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.tickets_fractal = apps.get_app_config(Settings.APP_NAME).tickets_fractal

    def __call__(self, request):
        if fractal := request.session.get("fractal", None):
            for repository in self.tickets_fractal.context.repositories:
                if issubclass(type(repository), ExternalDataInMemoryRepositoryMixin):
                    repository.load_data(fractal)

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        for repository in self.tickets_fractal.context.repositories:
            if issubclass(type(repository), ExternalDataInMemoryRepositoryMixin):
                if "fractal" not in request.session:
                    request.session["fractal"] = {}
                key, data = repository.dump_data()
                request.session["fractal"][key] = data
                request.session.modified = True

        return response
