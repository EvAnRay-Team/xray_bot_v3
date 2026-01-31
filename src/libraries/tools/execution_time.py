import time
from nonebot.log import logger
from contextlib import contextmanager

@contextmanager
def timing_block(description: str = "代码块"):
    """
    用于测量代码块执行时间的上下文管理器
    用法: 
    with timing_block("加载数据"):
        ... 你的代码 ...
    """
    start_time = time.time()
    try:
        yield  # 这里执行 with 语句块体内的内容
    finally:
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"代码块 {description} 的执行时间: {execution_time:.6f} 秒")

def timing_decorator(func):  
    def wrapper(*args, **kwargs):  
        start_time = time.time()  
        result = func(*args, **kwargs)  
        end_time = time.time()  
        execution_time = end_time - start_time  
        logger.info(f"方法 {func.__name__} 的执行时间: {execution_time:.6f} 秒")  
        return result  
    return wrapper

def timing_decorator_async(func):  
    async def wrapper(*args, **kwargs):  
        start_time = time.time()  
        result = await func(*args, **kwargs)  
        end_time = time.time()  
        execution_time = end_time - start_time  
        logger.info(f"异步方法 {func.__name__} 的执行时间: {execution_time:.6f} 秒")  
        return result  
    return wrapper
