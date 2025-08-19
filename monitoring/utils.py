import qrcode
import cloudinary
import cloudinary.uploader
from django.conf import settings
from io import BytesIO
import base64
import logging

logger = logging.getLogger(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CONFIG['cloud_name'],
    api_key=settings.CLOUDINARY_CONFIG['api_key'],
    api_secret=settings.CLOUDINARY_CONFIG['api_secret']
)

def generate_qr_code(data, size=10, border=4):
    """
    Generate QR code for given data

    Args:
        data (str): Data to encode in QR code
        size (int): Size of QR code
        border (int): Border size

    Returns:
        PIL.Image: QR code image
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        logger.info(f"QR code generated for data: {data[:50]}...")
        return img
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return None

def upload_to_cloudinary(image, public_id=None, folder="qr_codes"):
    """
    Upload image to Cloudinary

    Args:
        image (PIL.Image): Image to upload
        public_id (str): Public ID for the image
        folder (str): Folder to store the image

    Returns:
        dict: Upload result with URL
    """
    try:
        # Convert PIL image to bytes
        img_buffer = BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Upload to Cloudinary
        upload_params = {
            'folder': folder,
            'resource_type': 'image',
            'format': 'png'
        }

        if public_id:
            upload_params['public_id'] = public_id

        result = cloudinary.uploader.upload(img_buffer, **upload_params)
        logger.info(f"Image uploaded to Cloudinary: {result.get('public_id')}")
        return result
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {e}")
        return None

def generate_and_upload_qr(terminal_id, terminal_name):
    """
    Generate QR code for terminal and upload to Cloudinary

    Args:
        terminal_id (str): Terminal ID
        terminal_name (str): Terminal name

    Returns:
        str: Cloudinary URL of uploaded QR code
    """
    try:
        # Generate QR code data (you can customize this format)
        qr_data = f"terminal_id:{terminal_id}"

        # Generate QR code
        qr_image = generate_qr_code(qr_data)
        if not qr_image:
            return None

        # Upload to Cloudinary
        public_id = f"terminal_{terminal_id}_{terminal_name.lower().replace(' ', '_')}"
        upload_result = upload_to_cloudinary(qr_image, public_id=public_id)

        if upload_result:
            return upload_result.get('secure_url')
        return None
    except Exception as e:
        logger.error(f"Error generating and uploading QR code: {e}")
        return None

def get_qr_code_base64(data):
    """
    Generate QR code and return as base64 string for display

    Args:
        data (str): Data to encode

    Returns:
        str: Base64 encoded QR code image
    """
    try:
        qr_image = generate_qr_code(data)
        if not qr_image:
            return None

        img_buffer = BytesIO()
        qr_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        logger.error(f"Error generating base64 QR code: {e}")
        return None