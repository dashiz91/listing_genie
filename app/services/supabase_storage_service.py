"""
Supabase Storage Service

Implements the same interface as StorageService but uses Supabase Storage.
"""
import uuid
import logging
from io import BytesIO
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image

from supabase import create_client, Client

from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """Supabase cloud storage for uploaded and generated images"""

    def __init__(self):
        if not settings.supabase_url:
            raise ValueError("Supabase URL must be configured")

        # Use service role key for storage operations (has full access)
        # Fall back to anon key if service role not available
        key = settings.supabase_service_role_key or settings.supabase_anon_key
        if not key:
            raise ValueError("Supabase key must be configured")

        self.client: Client = create_client(
            settings.supabase_url,
            key
        )
        self.uploads_bucket = settings.supabase_uploads_bucket
        self.generated_bucket = settings.supabase_generated_bucket

        logger.info(f"Supabase storage initialized with buckets: {self.uploads_bucket}, {self.generated_bucket}")

    def save_upload(self, content: bytes, original_filename: str) -> Tuple[str, str]:
        """
        Save uploaded file to Supabase Storage.

        Args:
            content: Raw file bytes
            original_filename: Original filename (for extension only)

        Returns:
            Tuple of (upload_id, storage_path)
        """
        # Generate safe filename
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}.png"

        # Re-encode image to strip metadata and validate
        image_buffer = BytesIO(content)
        image_buffer.seek(0)
        try:
            image = Image.open(image_buffer)
            image.load()  # Force full read to catch truncated/corrupt data
        except Exception as e:
            logger.error(f"PIL cannot identify image ({len(content)} bytes, first 16: {content[:16].hex() if content else 'empty'}): {e}")
            raise
        image = image.convert('RGB')  # Remove alpha channel if present

        # Convert to bytes
        output_buffer = BytesIO()
        image.save(output_buffer, format='PNG', optimize=True)
        output_buffer.seek(0)

        # Upload to Supabase
        try:
            self.client.storage.from_(self.uploads_bucket).upload(
                path=safe_filename,
                file=output_buffer.getvalue(),
                file_options={"content-type": "image/png"}
            )
            logger.info(f"Uploaded file to Supabase: {safe_filename}")
        except Exception as e:
            logger.error(f"Failed to upload to Supabase: {e}")
            raise

        # Return the storage path in a format that can be used later
        storage_path = f"supabase://{self.uploads_bucket}/{safe_filename}"
        return file_id, storage_path

    def save_generated_image(
        self,
        session_id: str,
        image_type: str,
        image: Image.Image
    ) -> str:
        """
        Save generated image to Supabase Storage.

        Args:
            session_id: Generation session ID
            image_type: Type of image (main, infographic_1, etc.)
            image: PIL Image object

        Returns:
            Storage path (supabase://bucket/path format)
        """
        # Create path: session_id/image_type.png
        filename = f"{session_id}/{image_type}.png"

        # Convert to bytes
        output_buffer = BytesIO()
        image.save(output_buffer, format='PNG', optimize=True)
        output_buffer.seek(0)

        # Upload to Supabase
        try:
            self.client.storage.from_(self.generated_bucket).upload(
                path=filename,
                file=output_buffer.getvalue(),
                file_options={"content-type": "image/png"}
            )
            logger.info(f"Saved generated image to Supabase: {filename}")
        except Exception as e:
            # If file exists, try to update it
            if "Duplicate" in str(e) or "already exists" in str(e).lower():
                logger.info(f"File exists, updating: {filename}")
                self.client.storage.from_(self.generated_bucket).update(
                    path=filename,
                    file=output_buffer.getvalue(),
                    file_options={"content-type": "image/png"}
                )
            else:
                logger.error(f"Failed to save generated image to Supabase: {e}")
                raise

        storage_path = f"supabase://{self.generated_bucket}/{filename}"
        return storage_path

    def save_generated_image_versioned(
        self,
        session_id: str,
        image_type: str,
        image: Image.Image,
        version: int,
    ) -> str:
        """
        Save a versioned copy of a generated image alongside the latest copy.

        Saves to:
          - {session_id}/{image_type}_v{version}.png  (permanent versioned copy)
          - {session_id}/{image_type}.png              (latest, backward compat)

        Returns:
            Storage path for the latest copy (supabase://bucket/path format)
        """
        output_buffer = BytesIO()
        image.save(output_buffer, format='PNG', optimize=True)
        png_bytes = output_buffer.getvalue()

        # Save versioned copy (permanent)
        versioned_filename = f"{session_id}/{image_type}_v{version}.png"
        try:
            self.client.storage.from_(self.generated_bucket).upload(
                path=versioned_filename,
                file=png_bytes,
                file_options={"content-type": "image/png"}
            )
            logger.info(f"Saved versioned image: {versioned_filename}")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e).lower():
                logger.info(f"Versioned file exists, updating: {versioned_filename}")
                self.client.storage.from_(self.generated_bucket).update(
                    path=versioned_filename,
                    file=png_bytes,
                    file_options={"content-type": "image/png"}
                )
            else:
                logger.error(f"Failed to save versioned image: {e}")
                raise

        # Save/update latest copy (overwrites)
        latest_path = self.save_generated_image(session_id, image_type, image)
        return latest_path

    def copy_upload_to_generated_versioned(
        self,
        upload_path: str,
        session_id: str,
        image_type: str,
        version: int,
    ) -> str:
        """
        Copy an uploaded file to the generated bucket with versioning.
        Used for style references that need to be versioned like generated images.

        Args:
            upload_path: Source path (supabase://uploads/xxx.png)
            session_id: Target session ID
            image_type: Target image type (e.g., 'style_reference')
            version: Version number

        Returns:
            Storage path for the latest copy (supabase://generated/session/type.png)
        """
        # Extract filename from upload path
        if upload_path.startswith("supabase://"):
            parts = upload_path.replace("supabase://", "").split("/", 1)
            if len(parts) == 2:
                source_bucket, source_filename = parts
            else:
                raise ValueError(f"Invalid upload path: {upload_path}")
        else:
            raise ValueError(f"Invalid upload path format: {upload_path}")

        # Download from uploads bucket
        try:
            response = self.client.storage.from_(source_bucket).download(source_filename)
            image = Image.open(BytesIO(response))
        except Exception as e:
            logger.error(f"Failed to download source image: {e}")
            raise

        # Save versioned copy to generated bucket
        return self.save_generated_image_versioned(session_id, image_type, image, version)

    def get_upload_url(self, upload_id: str, expires_in: int = 3600) -> str:
        """
        Get a signed URL for an uploaded file.

        Args:
            upload_id: Upload file ID (UUID)
            expires_in: URL expiration in seconds (default 1 hour)

        Returns:
            Signed URL for the file
        """
        filename = f"{upload_id}.png"
        try:
            response = self.client.storage.from_(self.uploads_bucket).create_signed_url(
                path=filename,
                expires_in=expires_in
            )
            return response.get('signedURL', '')
        except Exception as e:
            logger.error(f"Failed to get signed URL for upload: {e}")
            raise FileNotFoundError(f"Upload not found: {upload_id}")

    def get_generated_url(self, session_id: str, image_type: str, expires_in: int = 3600) -> str:
        """
        Get a signed URL for a generated image.

        Args:
            session_id: Generation session ID
            image_type: Type of image
            expires_in: URL expiration in seconds (default 1 hour)

        Returns:
            Signed URL for the file
        """
        filename = f"{session_id}/{image_type}.png"
        try:
            response = self.client.storage.from_(self.generated_bucket).create_signed_url(
                path=filename,
                expires_in=expires_in
            )
            return response.get('signedURL', '')
        except Exception as e:
            logger.error(f"Failed to get signed URL for generated image: {e}")
            raise FileNotFoundError(f"Generated image not found: {image_type}")

    def get_public_url(self, bucket: str, path: str) -> str:
        """
        Get public URL for a file (if bucket is public).

        Args:
            bucket: Bucket name
            path: File path within bucket

        Returns:
            Public URL
        """
        return self.client.storage.from_(bucket).get_public_url(path)

    def get_upload_path(self, upload_id: str) -> Path:
        """
        For compatibility with local storage interface.
        Returns a pseudo-path that can be used with get_file_bytes.
        """
        # Return a Path-like object for compatibility
        return Path(f"supabase://{self.uploads_bucket}/{upload_id}.png")

    def get_generated_path(self, session_id: str, image_type: str) -> Path:
        """
        For compatibility with local storage interface.
        Returns a pseudo-path that can be used with get_file_bytes.
        """
        return Path(f"supabase://{self.generated_bucket}/{session_id}/{image_type}.png")

    def get_file_bytes(self, storage_path: str) -> bytes:
        """
        Download file bytes from Supabase.

        Args:
            storage_path: Storage path (supabase://bucket/path format or just path)

        Returns:
            File bytes
        """
        # Parse the storage path
        if storage_path.startswith("supabase://"):
            # Format: supabase://bucket/path
            parts = storage_path[len("supabase://"):].split("/", 1)
            bucket = parts[0]
            path = parts[1] if len(parts) > 1 else ""
        else:
            # Assume it's a generated path
            bucket = self.generated_bucket
            path = storage_path

        try:
            response = self.client.storage.from_(bucket).download(path)
            return response
        except Exception as e:
            logger.error(f"Failed to download from Supabase: {e}")
            raise FileNotFoundError(f"File not found: {storage_path}")

    def delete_upload(self, upload_id: str) -> None:
        """Delete uploaded file from Supabase"""
        filename = f"{upload_id}.png"
        try:
            self.client.storage.from_(self.uploads_bucket).remove([filename])
            logger.info(f"Deleted upload from Supabase: {filename}")
        except Exception as e:
            logger.warning(f"Failed to delete upload from Supabase: {e}")

    def delete_session_images(self, session_id: str) -> None:
        """Delete all generated images for a session"""
        try:
            # List all files in the session folder
            files = self.client.storage.from_(self.generated_bucket).list(session_id)
            if files:
                paths = [f"{session_id}/{f['name']}" for f in files]
                self.client.storage.from_(self.generated_bucket).remove(paths)
                logger.info(f"Deleted session images from Supabase: {session_id}")
        except Exception as e:
            logger.warning(f"Failed to delete session images from Supabase: {e}")

    def get_session_image_count(self, session_id: str) -> int:
        """Count how many images exist for a session"""
        try:
            files = self.client.storage.from_(self.generated_bucket).list(session_id)
            return len([f for f in files if f['name'].endswith('.png')])
        except Exception:
            return 0

    def load_image(self, storage_path: str) -> Image.Image:
        """
        Load an image from Supabase storage as a PIL Image.

        Args:
            storage_path: Storage path (supabase://bucket/path format)

        Returns:
            PIL Image object
        """
        image_bytes = self.get_file_bytes(storage_path)
        return Image.open(BytesIO(image_bytes))

    def health_check(self) -> dict:
        """Check storage health"""
        try:
            # Try to list buckets
            buckets = self.client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]

            uploads_ok = self.uploads_bucket in bucket_names
            generated_ok = self.generated_bucket in bucket_names

            if uploads_ok and generated_ok:
                return {"status": "accessible", "provider": "supabase", "buckets": bucket_names}
            else:
                missing = []
                if not uploads_ok:
                    missing.append(self.uploads_bucket)
                if not generated_ok:
                    missing.append(self.generated_bucket)
                return {
                    "status": "error",
                    "error": f"Missing buckets: {missing}",
                    "available_buckets": bucket_names
                }

        except Exception as e:
            return {"status": "error", "provider": "supabase", "error": str(e)}
