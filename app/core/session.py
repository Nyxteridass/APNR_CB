class SessionManager:
    _user = None
    _role = None

    @classmethod
    def set_user(cls, username, role):
        cls._user = username
        cls._role = role

    @classmethod
    def get_current_user(cls):
        return cls._user

    @classmethod
    def get_role(cls):
        return cls._role

    @classmethod
    def clear(cls):
        cls._user = None
        cls._role = None


        