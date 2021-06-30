from fractal.core.models import EnumModel


class Role(EnumModel):
    OWNER = "role.owner"
    ADMIN = "role.admin"
