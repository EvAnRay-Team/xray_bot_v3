from pathlib import Path
from typing import Optional
from src.libraries.tools.execution_time import timing_decorator

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
        self.bucket = bucket or getattr(config, 'tencent_cloud_cos_bucket', None)
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
    
    @timing_decorator
    def upload_file(self, local_path: Path, key: str) -> bool:
        """
        上传文件到 COS
        
        Args:
            local_path: 本地文件路径
            key: COS 对象键 (例如: maimaidx/abstract_cover/12/34/md5.png)
        
        Returns:
            bool: 是否上传成功
        """
        try:
            if not local_path.exists():
                logger.error(f"本地文件不存在: {local_path}")
                return False
            
            with open(local_path, 'rb') as f:
                response = self.client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=f
                )
            
            logger.info(f"上传文件成功: {local_path} -> {key}")
            return True
            
        except Exception as e:
            logger.error(f"上传文件失败: {local_path} -> {key}, 错误: {e}")
            return False
        
    @timing_decorator
    def download_file(self, key: str, local_path: Path) -> bool:
        """
        从 COS 下载文件到本地
        
        Args:
            key: COS 对象键 (例如: maimaidx/abstract_cover/12/34/md5.png)
            local_path: 本地保存路径
        
        Returns:
            bool: 是否下载成功
        """
        try:
            # 确保父目录存在
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 下载文件
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=key
            )
            
            response["Body"].get_stream_to_file(local_path)
            
            logger.info(f"下载文件成功: {key} -> {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"下载文件失败: {key}, 错误: {e}")
            return False
    
    @timing_decorator
    def file_exists(self, key: str) -> bool:
        """
        检查文件是否存在于 COS
        
        Args:
            key: COS 对象键
        
        Returns:
            bool: 文件是否存在
        """
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=key
            )
            return True
        except Exception:
            return False
    
    @timing_decorator
    def delete_file(self, key: str) -> bool:
        """
        从 COS 删除文件
        
        Args:
            key: COS 对象键
        
        Returns:
            bool: 是否删除成功
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            logger.info(f"删除文件成功: {key}")
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {key}, 错误: {e}")
            return False

assets_tencent_cos_client = TencentCOS()