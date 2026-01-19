from fastapi import HTTPException


class ListingGenieException(HTTPException):
    """Base exception for Listing Genie application"""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class ValidationError(ListingGenieException):
    """Raised when input validation fails"""
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class NotFoundError(ListingGenieException):
    """Raised when a resource is not found"""
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)


class GenerationError(ListingGenieException):
    """Raised when image generation fails"""
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)


class StorageError(ListingGenieException):
    """Raised when storage operations fail"""
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)
