from pathlib import Path
from typing import Optional
import time
from src.libraries.tools.execution_time import timing_decorator
from src.libraries.tools.image import image_to_bytesio
import nonebot
from nonebot.log import logger
from qcloud_cos import CosConfig, CosS3Client

class TencentCOS:
    """腾讯云 COS 对象存储客户端"""
    
    def __init__(
        self,
        secret_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        初始化 COS 客户端
        
        Args:
            secret_id: 腾讯云 SecretId (默认从环境变量读取)
            secret_key: 腾讯云 SecretKey (默认从环境变量读取)
            bucket: COS Bucket 名称 (默认从环境变量读取)
            region: COS 地域 (默认从环境变量读取,默认值: ap-guangzhou)
        """
        config = nonebot.get_driver().config
        
        self.secret_id = secret_id or getattr(config, 'tencent_cloud_secret_id', None)
        self.secret_key = secret_key or getattr(config, 'tencent_cloud_secret_key', None)
        self.bucket = bucket or getattr(config, 'message_image_tencent_cos_bucket', None)
        self.region = region or getattr(config, 'tencent_cloud_cos_region', None)
        
        if not self.bucket:
            raise ValueError("COS Bucket 未配置,请在环境变量中设置 TENCENT_CLOUD_COS_BUCKET")
        
        # 初始化 COS 客户端
        cos_config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Scheme='https'
        )
        self.client = CosS3Client(cos_config)
        
        logger.info(f"COS 客户端初始化成功: Bucket={self.bucket}, Region={self.region}")
    
    def upload_file(self, image):
        cos_key = f'temp/images/{int(time.time() * 1000)}.jpg'
        response = self.client.put_object(
            Bucket=self.bucket,
            Body=image_to_bytesio(image.convert('RGB')),
            Key= cos_key,
            EnableMD5=False
        )
        return cos_key

    def get_presigned_url(self, cos_key):
        signed_url = self.client.get_presigned_url(
            Method='GET',
            Bucket=self.bucket,
            Key=cos_key,
            Expired=120)
        return signed_url

message_image_tencent_cos_client = TencentCOS()