
import sys
import os
import asyncio
from PIL import ImageFont, ImageDraw

# 兼容性补丁 (from v2 dev_best_50.py)
def _getsize_compat(self: ImageFont.FreeTypeFont, text: str) -> tuple[int, int]:
    """Pillow 10+ 用 getbbox 模拟旧 getsize"""
    bbox = self.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1] + 6

def _textsize_compat(self: ImageDraw.ImageDraw, txt, font=None, spacing=4, direction=None, features=None, language=None):
    bbox = self.textbbox((0, 0), txt, font=font, spacing=spacing, direction=direction, features=features, language=language)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

# 仅当不存在 getsize 时才打补丁
if not hasattr(ImageFont.FreeTypeFont, 'getsize'):
    ImageFont.FreeTypeFont.getsize = _getsize_compat

if not hasattr(ImageDraw.ImageDraw, 'textsize'):
    ImageDraw.ImageDraw.textsize = _textsize_compat

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

# 导入业务逻辑
from src.libraries.original_lib.tarot import tarot_divination
from src.libraries.original_lib.tarot.drawer import TarotDrawer

async def main():
    print("Step 1: 正在进行塔罗牌占卜...")
    divination_result = tarot_divination() 
    
    print("\n=== 占卜结果 ===")
    print(f"牌名: {divination_result['tarot_name']}")
    print(f"正逆: {divination_result['tarot_upright']}")
    print(f"含义: {divination_result['tarot_meaning']}")
    print(f"关联歌曲: {divination_result['title']} ({divination_result['artist']})")
    
    print("\nStep 2: 正在生成塔罗牌图片...")
    drawer = TarotDrawer(divination_result)
    img = drawer.draw()
        
    print("Step 3: 打开图片预览...")
    img.show()
    
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
