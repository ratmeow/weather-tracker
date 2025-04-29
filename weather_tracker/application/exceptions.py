class ApplicationError(Exception):
    def __init__(self, message: str = ""):
        self.message = message


class UserAlreadyExistsError(ApplicationError):
    def __init__(self):
        super().__init__(message="User with this login already exists")


class LoginRequirementError(ApplicationError):
    def __init__(self):
        super().__init__(
            message="Login must be at least 3 characters long, "
            "with only Latin letters, digits and special character(!@#$%^&*)."
        )


class PasswordRequirementError(ApplicationError):
    def __init__(self):
        super().__init__(
            message="Password must be at least 8 characters long, "
            "with only Latin letters and at least one digit or special character(!@#$%^&*)."
        )


class UserNotFoundError(ApplicationError):
    def __init__(self, **kwargs):
        super().__init__(message=f"User with {kwargs} not found")


class WrongPasswordError(ApplicationError):
    def __init__(self):
        super().__init__(message="Wrong password")


class UserLocationError(ApplicationError):
    pass


class LocationNotFoundError(ApplicationError):
    def __init__(self, **kwargs):
        super().__init__(message=f"Location with {kwargs} not found")
