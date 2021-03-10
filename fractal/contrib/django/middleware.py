from fractal.core.repositories.external_data_inmemory_repository_mixin import (
    ExternalDataInMemoryRepositoryMixin,
)


def before_view(request, fractal):
    if session := request.session.get("fractal", None):
        for repository in fractal.context.repositories:
            if issubclass(type(repository), ExternalDataInMemoryRepositoryMixin):
                repository.load_data_json(session)


def after_view(request, fractal):
    for repository in fractal.context.repositories:
        if issubclass(type(repository), ExternalDataInMemoryRepositoryMixin):
            if "clear_fractal" in request.session:
                if "fractal" in request.session:
                    del request.session["fractal"]
                return
            if "fractal" not in request.session:
                request.session["fractal"] = {}
            key, data = repository.dump_data_json()
            request.session["fractal"][key] = data
            request.session.modified = True


class SessionMiddlewareMixin:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.fractals = []  # SET THIS

    def __call__(self, request):
        for fractal in self.fractals:
            before_view(request, fractal)

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        for fractal in self.fractals:
            after_view(request, fractal)

        return response
