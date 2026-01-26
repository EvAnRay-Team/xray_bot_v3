#!/usr/bin/env python
import sys
import os
import importlib
import nonebot

# 1. 在初始化前屏蔽 localstore 的检测报错
# 这样它会直接使用当前目录下的 data 文件夹，而不会去溯源调用者
# os.environ["LOCALSTORE_DATA_DIR"] = os.path.join(os.getcwd(), "data")

# 2. 初始化 NoneBot
nonebot.init()

def main():
    # 将 src 加入路径，确保 command.xxx 导入正常
    sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
    
    # 3. 显式加载插件
    # 必须加载 ORM 插件和你的业务插件，否则 SQLAlchemy 找不到模型映射
    nonebot.load_plugin("nonebot_plugin_orm")

    if len(sys.argv) < 2:
        print("Usage: python manage.py <command> [options]")
        sys.exit(1)

    command_name = sys.argv[1]
    command_args = sys.argv[2:]

    try:
        module_path = f"command.{command_name}"
        module = importlib.import_module(module_path)
    except ImportError as e:
        print(f"Unknown command: '{command_name}'")
        print(f"Error: {e}")
        # ... 保持原有的可用命令打印逻辑 ...
        sys.exit(1)

    # ... 保持原有的 Command 类查找逻辑 ...
    command_class = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        try:
             from command.base import BaseCommand
             if (isinstance(attr, type) and 
                 issubclass(attr, BaseCommand) and 
                 attr is not BaseCommand):
                 command_class = attr
                 break
        except ImportError:
            pass
    
    if command_class is None:
        print(f"Module 'src/command/{command_name}.py' does not define a 'Command' class.")
        sys.exit(1)

    # 4. 执行命令
    command = command_class()
    command.run(command_args)

if __name__ == "__main__":
    main()