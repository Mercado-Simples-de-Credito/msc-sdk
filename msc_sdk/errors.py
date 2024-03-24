class Unauthorized(Exception):
    def __init__(self, message: str):
        self.message = message if message else "Unauthorized"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NotFound(Exception):
    def __init__(self, message: str):
        self.message = message if message else "Not found"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class BadRequest(Exception):
    def __init__(self, message: str):
        self.message = message if message else "Bad request"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class BillingError(Exception):
    def __init__(self, message: str):
        self.message = message if message else "Billing error"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ServerError(Exception):
    def __init__(self, message: str):
        self.message = message if message else "Server error"
        super().__init__(self.message)

    def __str__(self):
        return self.message
