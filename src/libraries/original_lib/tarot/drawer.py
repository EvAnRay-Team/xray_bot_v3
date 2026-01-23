            
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any
from src.libraries.config.GLOBAL_PATH import FONT_PATH, TAROT_PATH

class TarotDrawer:
    def __init__(self, tarot_data: Dict[str, Any], is_abstract: bool = False):
        """
        :param tarot_data: 字典，包含 tarot_name, tarot_upright, title, artist, tarot_meaning, cover_abstract, cover_normal
        :param is_abstract: 是否使用抽象画封面
        """
        self.data = tarot_data
        self.is_abstract = is_abstract
        
        self.base_img = Image.new("RGBA", (1000, 1559), (0, 0, 0, 0))
        self.title_font_path = f'{FONT_PATH}/HYChangMeiHeiJ.ttf'
        self.song_font_path = f'{FONT_PATH}/叛逆明朝.ttf' # 需确保此字体存在或使用替代

    def draw(self) -> Image.Image:
        card_name = self.data.get('tarot_name', 'Unknown')
        tarot_upright = self.data.get('tarot_upright', '正位')
        song_title = self.data.get('title', '')
        song_artist = self.data.get('artist', '')
        card_info = self.data.get('tarot_meaning', '')
        cover_abstract = self.data.get('cover_abstract')
        cover_normal = self.data.get('cover_normal')

        # 1. 绘制封面
        try:
            target_path = cover_abstract if self.is_abstract else cover_normal
            cover_image = Image.open(target_path)
        except Exception:
            # Fallback trying normal if abstract failed or vice versa, or default
            try:
                cover_image = Image.open(cover_normal)
            except Exception:
                cover_image = Image.new("RGBA", (800, 800), (200, 200, 200))
        
        # 逆位旋转
        if tarot_upright == "逆位":
            cover_image = cover_image.rotate(180)
            
        cover_resized = cover_image.resize((800, 800))
        self.base_img.paste(cover_resized, (94, 102))

        # 2. 绘制背景 (前景遮罩)
        try:
            tarot_bg = Image.open(f'{TAROT_PATH}/tarot.png')
            self.base_img.paste(tarot_bg, (0, 0), tarot_bg.split()[3])
        except Exception as e:
            print(f"Warning: Failed to load tarot.png: {e}")

        # 3. 加载装饰素材
        try:
            left_img = Image.open(f'{TAROT_PATH}/left.png')
            middle_img = Image.open(f'{TAROT_PATH}/middle.png')
            right_img = Image.open(f'{TAROT_PATH}/right.png')
        except Exception:
            left_img = Image.new("RGBA", (1, 1), (0,0,0,0))
            middle_img = Image.new("RGBA", (1, 1), (0,0,0,0))
            right_img = Image.new("RGBA", (1, 1), (0,0,0,0))

        draw = ImageDraw.Draw(self.base_img)
        
        # 4. 绘制标题 (牌名 + 正逆位)
        try:
            title_font = ImageFont.truetype(self.title_font_path, 92, encoding='utf-8')
        except:
            title_font = ImageFont.load_default()
            
        title_text = f"{card_name}-{tarot_upright}"
        text_pos = (500, 1022)
        
        # 计算文字宽度以放置装饰线
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        text_width = bbox[2] - bbox[0]
        half_width = text_width / 2
        
        left_x = 500 - half_width
        right_x = 500 + half_width
        
        # 绘制底部装饰线
        if hasattr(left_img, 'width') and left_img.width > 1:
            # 简单计算，确保 middle 拉伸填补空隙
            # v2 逻辑: gap_width = right_x - (left_x - left.width) - left.width ?? 
            # 实际上应该是 Text 左边放 left, 右边放 right, 中间填? 
            # 原逻辑看起来是: left 图片在文字左侧, right 在右侧, middle 填充?
            # 还是说 left/right/middle 组成了下划线?
            # 让我们复刻 v2 逻辑:
            # left_x 是文字左边界。
            # paste left 在 (left_x - left.width, y)
            # paste right 在 (right_x, y)
            # middle 填充中间? 也就是 text 覆盖的区域?
            
            # v2: gap_width = right_x - (left_x - left.width) - left.width 
            #     middle_target_width = gap_width
            #     paste left at (left_x - left.width)
            #     paste middle at (left_x) ?? No, (left_x - left.width + left.width) = left_x 
            #     paste right at (right_x)
            
            # 所以 middle 的宽度就是 text_width + 2*left.width ?? 不对， gap_width = right_x - left_x = text_width.
            # v2的计算有点绕，但意图似乎是 下划线 = [LeftHead] + [MiddleBody(Resized)] + [RightTail]
            # 覆盖范围是从 (left_x - left.width) 到 (right_x + right.width) 
            
            middle_width = int(right_x - left_x)
            if middle_width < 1: middle_width = 1
            middle_resized = middle_img.resize((middle_width, middle_img.height))
            
            img_y = 1022
            self.base_img.paste(left_img, (int(left_x - left_img.width), img_y), left_img.split()[3])
            self.base_img.paste(middle_resized, (int(left_x), img_y), middle_resized.split()[3])
            self.base_img.paste(right_img, (int(right_x), img_y), right_img.split()[3])

        draw.text(text_pos, title_text, font=title_font, fill="white", anchor="mm")

        # 5. 绘制歌曲信息
        song_display = f"——  {song_title}  ——"
        artist_display = f"——  {song_artist}  ——"
        try:
            song_font = ImageFont.truetype(self.song_font_path, 60, encoding='utf-8')
        except:
             song_font = ImageFont.load_default()
             
        draw.text((500, 1175), song_display, font=song_font, fill="white", anchor="mm")
        draw.text((500, 1254), artist_display, font=song_font, fill="white", anchor="mm")

        # 6. 绘制卡面简介 (自动换行)
        try:
            info_font = ImageFont.truetype(self.title_font_path, 66, encoding='utf-8')
        except:
             info_font = ImageFont.load_default()
             
        max_w = 870
        lines = []
        for segment in card_info.split('、'): # v2 特定标点分割逻辑
             if not lines:
                 lines.append(segment)
             else:
                 test_str = lines[-1] + '、' + segment
                 if draw.textbbox((0,0), test_str, font=info_font)[2] > max_w:
                      lines.append(segment)
                 else:
                      lines[-1] = test_str
        
        y = 1330
        for line in lines:
            draw.text((500, y), line, font=info_font, fill="white", anchor="mt")
            y += 80

        return self.base_img
