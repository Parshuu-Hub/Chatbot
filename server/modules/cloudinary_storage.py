import cloudinary
import cloudinary.uploader
import os

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_SECRET_KEY"),
    secure=True
)

def upload_pdf_to_cloudinary(file_bytes: bytes, filename: str, content_type: str) -> str:
    """
    Uploads PDF to Cloudinary and returns the secure URL.
    """
    result = cloudinary.uploader.upload(
        file_bytes,
        resource_type="raw",
        public_id=f"pdf_uploads/{filename}",
        format="pdf"
    )
    return result["secure_url"]
