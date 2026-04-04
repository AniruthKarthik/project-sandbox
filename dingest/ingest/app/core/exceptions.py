class BaseError(Exception):
    pass


class UnsupportedFormatError(BaseError):
    def __init__(self, extension: str):
        super().__init__(f"No parser registered for file ext: '{extension}'")
        self.extension = extension


class ParseFailureError(BaseError):
    def __init__(self, file_name: str, reason: str):
        super().__init__(f"Failed to parse '{file_name}': {reason}")
        self.file_name = file_name
        self.reason = reason


class FileTooLargeError(BaseError):
    def __init__(self, file_name: str, sizeMB: float, limitMB: float):
        super().__init__(
            f"File '{file_name}' is {sizeMB:.1f} MB, " f"exceeds limit of {limitMB} MB"
        )
        self.file_name = file_name
        self.sizeMB = sizeMB
        self.limitMB = limitMB
