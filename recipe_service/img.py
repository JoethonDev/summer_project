from PIL import Image
from io import BytesIO
from fastapi import HTTPException, UploadFile

async def resize_image(image: UploadFile, size: tuple = (128, 128)) -> BytesIO:
    try:
        img = Image.open(image.file)
        img = img.resize(size)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return img_byte_arr
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resizing image: {str(e)}")
