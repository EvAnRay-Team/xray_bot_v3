"""
根据适配器名称生成对应的 MessageSegment
"""
from typing import Union
from PIL import Image
from nonebot.adapters import MessageSegment as BaseMessageSegment
from src.libraries.tools.image import image_to_bytes, image_to_base64
from src.dependencies.exceptions import UnsupportedAdapterError

# 延迟导入，避免循环依赖
_qq_cos_client = None

def _get_qq_cos_client():
    """延迟获取 QQ COS 客户端"""
    global _qq_cos_client
    if _qq_cos_client is None:
        try:
            from src.libraries.providers.message_image_tencent_cos import message_image_tencent_cos_client
            _qq_cos_client = message_image_tencent_cos_client
        except Exception:
            pass
    return _qq_cos_client


class MessageSegmentFactory:
    """根据适配器名称生成对应的 MessageSegment"""
    
    @staticmethod
    def get_message_segment_class(adapter_name: str):
        """根据适配器名称获取对应的 MessageSegment 类"""
        match adapter_name:
            case "OneBot V11":
                from nonebot.adapters.onebot.v11 import MessageSegment
                return MessageSegment
            case "QQ":
                from nonebot.adapters.qq import MessageSegment
                return MessageSegment
            case "Discord":
                from nonebot.adapters.discord import MessageSegment
                return MessageSegment
            case _:
                raise UnsupportedAdapterError(adapter_name)
    
    @classmethod
    def image(
        cls,
        adapter_name: str,
        image: Union[Image.Image, bytes],
        filename: str = "image.png",
        format: str = "PNG"
    ) -> BaseMessageSegment:
        """
        根据适配器名称生成图片 MessageSegment
        
        Args:
            adapter_name: 适配器名称，如 "OneBot V11", "QQ", "Discord"
            image: PIL Image 对象或 bytes 数据
            filename: 文件名（Discord 需要）
            format: 图片格式，默认为 PNG
            
        Returns:
            对应适配器的 MessageSegment
        """
        MessageSegment = cls.get_message_segment_class(adapter_name)
        
        # 保存原始 image 对象（如果是 Image.Image）
        original_image = image if isinstance(image, Image.Image) else None
        
        # 统一转换为 bytes
        if isinstance(image, Image.Image):
            image_bytes = image_to_bytes(image, format=format)
        elif isinstance(image, bytes):
            image_bytes = image
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")
        
        # 根据适配器生成不同的 MessageSegment
        match adapter_name:
            case "OneBot V11":
                # OneBot V11 使用 base64:// 协议
                # image_to_base64 需要 Image 对象
                if original_image:
                    base64_str = image_to_base64(original_image, format=format)
                else:
                    # 如果是 bytes，需要先转换为 Image 再转 base64
                    from io import BytesIO
                    img = Image.open(BytesIO(image_bytes))
                    base64_str = image_to_base64(img, format=format)
                if isinstance(base64_str, bytes):
                    base64_str = base64_str.decode('utf-8')
                return MessageSegment.image(f"base64://{base64_str}")  # type: ignore
            
            case "Discord":
                # Discord 使用 attachment
                return MessageSegment.attachment(file=filename, content=image_bytes)  # type: ignore
            
            case "QQ":
                # QQ 适配器需要上传到 COS 并获取预签名 URL
                cos_client = _get_qq_cos_client()
                if cos_client is None:
                    raise ValueError("QQ 适配器需要配置 message_image_tencent_cos_client，请检查环境变量配置")

                # 上传图片并获取 URL
                cos_key = cos_client.upload_file(image)
                url = cos_client.get_presigned_url(cos_key)
                return MessageSegment.image(url)  # type: ignore
            
            case _:
                raise UnsupportedAdapterError(adapter_name)
    
    @classmethod
    def text(cls, adapter_name: str, text: str) -> BaseMessageSegment:
        """
        根据适配器名称生成文本 MessageSegment
        
        Args:
            adapter_name: 适配器名称
            text: 文本内容
            
        Returns:
            对应适配器的 MessageSegment
        """
        MessageSegment = cls.get_message_segment_class(adapter_name)
        return MessageSegment.text(text)
