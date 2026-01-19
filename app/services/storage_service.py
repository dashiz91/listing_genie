import uuid
import shutil
from pathlib import Path
from PIL import Image
from io import BytesIO
from typing import Tuple


class StorageService:
    """Local file storage for uploaded and generated images"""

    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.uploads_path = self.storage_path / "uploads"
        self.generated_path = self.storage_path / "generated"

        # Ensure directories exist
        self.uploads_path.mkdir(parents=True, exist_ok=True)
        self.generated_path.mkdir(parents=True, exist_ok=True)

    def save_upload(self, content: bytes, original_filename: str) -> Tuple[str, str]:
        """
        Save uploaded file securely.

        Args:
            content: Raw file bytes
            original_filename: Original filename (for extension only)

        Returns:
            Tuple of (upload_id, file_path)
        """
        # Generate safe filename
        file_id = str(uuid.uuid4())
        extension = self._get_safe_extension(original_filename)
        safe_filename = f"{file_id}.{extension}"

        # Re-encode image to strip metadata and validate
        image = Image.open(BytesIO(content))
        image = image.convert('RGB')  # Remove alpha channel if present

        output_path = self.uploads_path / safe_filename
        image.save(output_path, format='PNG', optimize=True)

        return file_id, str(output_path)

    def save_generated_image(
        self,
        session_id: str,
        image_type: str,
        image: Image.Image
    ) -> str:
        """
        Save generated image organized by session.

        Args:
            session_id: Generation session ID
            image_type: Type of image (main, infographic_1, etc.)
            image: PIL Image object

        Returns:
            Full path to saved file
        """
        # Create session directory
        session_dir = self.generated_path / session_id
        session_dir.mkdir(exist_ok=True)

        # Save image
        filename = f"{image_type}.png"
        output_path = session_dir / filename
        image.save(output_path, format='PNG', optimize=True)

        return str(output_path)

    def get_upload_path(self, upload_id: str) -> Path:
        """
        Get path to uploaded file with validation.

        Args:
            upload_id: Upload file ID (UUID)

        Returns:
            Path object to file

        Raises:
            ValueError: If path traversal attempted
            FileNotFoundError: If file doesn't exist
        """
        safe_path = self.uploads_path / f"{upload_id}.png"

        # Ensure path is within uploads directory (prevent traversal)
        if not safe_path.resolve().is_relative_to(self.uploads_path.resolve()):
            raise ValueError("Invalid upload ID")

        if not safe_path.exists():
            raise FileNotFoundError("Upload not found")

        return safe_path

    def get_generated_path(self, session_id: str, image_type: str) -> Path:
        """
        Get path to generated image.

        Args:
            session_id: Generation session ID
            image_type: Type of image

        Returns:
            Path object to file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.generated_path / session_id / f"{image_type}.png"

        if not file_path.exists():
            raise FileNotFoundError(f"Generated image not found: {image_type}")

        return file_path

    def delete_upload(self, upload_id: str) -> None:
        """Delete uploaded file"""
        try:
            path = self.get_upload_path(upload_id)
            path.unlink()
        except FileNotFoundError:
            pass  # Already deleted

    def delete_session_images(self, session_id: str) -> None:
        """Delete all generated images for a session"""
        session_dir = self.generated_path / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir)

    def get_session_image_count(self, session_id: str) -> int:
        """Count how many images exist for a session"""
        session_dir = self.generated_path / session_id
        if not session_dir.exists():
            return 0
        return len(list(session_dir.glob("*.png")))

    def _get_safe_extension(self, filename: str) -> str:
        """Extract and validate file extension"""
        extension = Path(filename).suffix.lower().lstrip('.')
        if extension in ('jpg', 'jpeg'):
            return 'png'  # Normalize to PNG
        if extension == 'png':
            return 'png'
        return 'png'  # Default to PNG

    def health_check(self) -> dict:
        """Check storage health"""
        try:
            # Check directories exist and are writable
            uploads_ok = self.uploads_path.exists() and self.uploads_path.is_dir()
            generated_ok = self.generated_path.exists() and self.generated_path.is_dir()

            # Try writing a test file
            test_file = self.storage_path / ".health_check"
            test_file.write_text("ok")
            test_file.unlink()

            if uploads_ok and generated_ok:
                return {"status": "accessible", "writable": True}
            else:
                return {"status": "error", "writable": False}

        except Exception as e:
            return {"status": "error", "error": str(e)}
