from dataclasses import dataclass


@dataclass
class Command:
    pass
    # @property
    # def get_account_id(self):
    #     if hasattr(self, "auth_user"):
    #         auth_user = getattr(self, "auth_user")
    #         if auth_user:
    #             return auth_user.account_id
    #
    # @property
    # def user_id(self):
    #     if hasattr(self, "auth_user"):
    #         auth_user = getattr(self, "auth_user")
    #         if auth_user:
    #             return auth_user.id

    # @property
    # def get_account_id(self):
    #     if hasattr(self, "account_id"):
    #         return getattr(self, "account_id")
    #     if hasattr(self, "user"):
    #         if user := getattr(self, "user"):
    #             return user.account_id
    #
    # @property
    # def user_id(self):
    #     if hasattr(self, "user_id"):
    #         return getattr(self, "user_id")
    #     if hasattr(self, "user"):
    #         if user := getattr(self, "user"):
    #             return user.id
