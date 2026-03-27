class BaseError(Exception):
    pass


class UnsupportedFormatError(BaseError):
    def __init__(self, extension: str):
        super().__init__(f"No parser registered for file ext: '{extension}'")
        self.extension = extension


class ParseFailureError(BaseError):
    def __init__(self, fileName: str, reason: str):
        super.__init__(f"Failed to parse '{fileName}': {reason}")
        self.fileName = fileName
        self.reason = reason


class FileTooLargeError(BaseError):
    def __init__(self, fileName: str, sizeMB: float, limitMB: float):
        def __init__(self, fileName: str, sizeMB: float, limitMB: float):
            super.__init__(
                f"File '{fileName}' is {sizeMB:.1f} MB,"
                f"exceeds limit of {limitMB} MB"
            )
            self.fileName = fileName
            self.sizeMB = sizeMB
            self.limitMB = limitMB
