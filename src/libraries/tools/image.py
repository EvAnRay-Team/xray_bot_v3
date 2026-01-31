import base64
from io import BytesIO
from PIL import Image
from src.libraries.config.GLOBAL_PATH import FONT_PATH
from PIL import ImageFont, ImageDraw
# 辅助函数：分割文本以适应最大宽度  
def split_text_to_lines(text, max_width, font):  
    lines = []  
    current_line = ""  
    for char in text:  
        # 检查当前行的宽度加上新字符的宽度是否超过最大宽度  
        text_width, text_height = font.getsize(current_line + char)
        if text_width <= max_width:  
            current_line += char  
        else:  
            # 如果超过最大宽度，则将当前行添加到列表中，并开始新行  
            lines.append(current_line)  
            current_line = char  
    # 添加最后一行（如果有的话）  
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)

def text_to_image(text: str) -> Image.Image:
    font = ImageFont.truetype(f"{FONT_PATH}/FOT-NewRodinProN-EB.otf", 24, encoding='utf-8')
    padding = 10
    margin = 4
    lines = text.strip().split('\n')
    max_width = 0
    b = 0
    for line in lines:
        l, t, r, b = font.getbbox(line)
        max_width = max(max_width, r)
    wa = max_width + padding * 2
    ha = b * len(lines) + margin * (len(lines) - 1) + padding * 2
    im = Image.new('RGB', (wa, ha), color=(255, 255, 255))
    draw = ImageDraw.Draw(im)
    for index, line in enumerate(lines):
        draw.text((padding, padding + index * (margin + b)), line, font=font, fill=(0, 0, 0))
    return im

def text_to_bytes_io(text: str) -> BytesIO:
    bio = BytesIO()
    text_to_image(text).save(bio, format='PNG')
    bio.seek(0)
    return bio

def base64_to_bytesio(base64_str: str) -> BytesIO:
    if base64_str.startswith('base64://'):
        base64_str = base64_str[len('base64://'):]
    byte_data = base64.b64decode(base64_str)
    return BytesIO(byte_data)


def image_to_bytesio(img, format_='PNG') -> BytesIO:
    bio = BytesIO()
    img.save(bio, format_)
    bio.seek(0)
    return bio

def image_to_bytes(img: Image.Image, format='PNG') -> bytes:
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    return output_buffer.getvalue()

def image_to_base64(img, format='PNG'):
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str