from src.libraries.tools.image import split_text_to_lines
from PIL import Image, ImageFont, ImageDraw
from src.server.mai_music_server import total_music
from .tools import get_cover_file_path
from src.libraries.config.GLOBAL_CONSTANT import VERSION_LOGO_MAP
from src.libraries.tools.execution_time import timing_decorator_async
from .tools import truncate_text, decimalPoints
from src.libraries.config.GLOBAL_PATH import MAI_MUSIC_INFO_ASSET_PATH, FONT_PATH
from src.libraries.schemas.mai import MaiCharts
class MaiMusicData():
    def __init__(self, music_id: int, is_abstract: bool) -> None:
        self.music_id = music_id 
        music_info = total_music.find_by_id(int(music_id))
        if not music_info:
            raise ValueError(f"音乐信息不存在: {music_id}")
        self.music_info = music_info
        self.is_abstract = is_abstract
        
        # 特殊背景配置字典 {音乐ID: (背景图片路径, 文字颜色)}
        self.special_backgrounds = {
            11663: ("系.png", (60, 60, 60)),
            834: ("潘.png", "white"),
        }
        
        self.use_special_bg = (music_id in self.special_backgrounds)
        
        # 获取当前音乐的背景配置
        if self.use_special_bg:
            self.bg_file, self.text_color = self.special_backgrounds[self.music_id]
        else:
            self.bg_file = "bg_circle.png"
            self.text_color = "black"
        
        self.baseImg = Image.new("RGBA", (1700, 2000), (0, 0, 0, 0))
        self.baseImgDraw = ImageDraw.Draw(self.baseImg)        
        

    def _create_composite_layer(self, image, position=None):
        """创建与baseImg相同尺寸的合成层"""
        if image.size != self.baseImg.size:
            # 创建与baseImg相同尺寸的透明层
            layer = Image.new("RGBA", self.baseImg.size, (0, 0, 0, 0))
            if position:
                # 如果指定了位置，将图片粘贴到指定位置
                layer.paste(image, position)
            else:
                # 如果不指定位置，居中放置
                x = (self.baseImg.width - image.width) // 2
                y = (self.baseImg.height - image.height) // 2
                layer.paste(image, (x, y))
            return layer
        else:
            return image

    @timing_decorator_async
    async def draw(self):
        # 第一步：加载歌曲封面（最底层）
        # 使用get_cover_path_and_nickname获取封面路径和作者信息
        chars: MaiCharts = self.music_info.charts # type: ignore
        
        cover_path, cover_artist = await get_cover_file_path(self.music_info.basic_info.id, self.is_abstract)
        if not cover_path:
            raise ValueError(f"封面路径不存在: {self.music_info.basic_info.id}")
        self.abstract_artist = cover_artist
        musicCoverImg = Image.open(cover_path).convert('RGBA')
        
        musicCoverImg = musicCoverImg.resize((494, 494))
        # 【alpha_composite合成】首先合成封面图片（最底层）
        cover_layer = self._create_composite_layer(musicCoverImg, (191, 172))
        self.baseImg = Image.alpha_composite(self.baseImg, cover_layer)

        # 第二步：加载背景
        backageImg = Image.open(f"{MAI_MUSIC_INFO_ASSET_PATH}/{self.bg_file}").convert('RGBA')
        
        # 【alpha_composite合成】合成背景（在封面之上）
        if backageImg.size != self.baseImg.size:
            backageImg = backageImg.resize(self.baseImg.size)
        self.baseImg = Image.alpha_composite(self.baseImg, backageImg)

        # 版本logo
        if self.music_info.basic_info.version.cn_ver in VERSION_LOGO_MAP:
            VersionLogoImg = Image.open(f"{MAI_MUSIC_INFO_ASSET_PATH}/版本牌/UI_CMN_TabTitle_MaimaiTitle_Ver{VERSION_LOGO_MAP.get(self.music_info.basic_info.version.cn_ver)}.png").convert('RGBA')
            # 【alpha_composite合成】合成版本logo
            text_width, text_height = VersionLogoImg.size
            version_layer = self._create_composite_layer(VersionLogoImg, (200 - text_width // 2, 150 - text_height // 2))
            self.baseImg = Image.alpha_composite(self.baseImg, version_layer)

        # 重新创建Draw对象，因为baseImg被重新赋值了
        self.baseImgDraw = ImageDraw.Draw(self.baseImg)

        # 第三步：绘制所有文字（在背景之上）
        # 添加曲师文字
        tempFont = ImageFont.truetype(f"{FONT_PATH}/FOT-NewRodinProN-EB.otf", 43, encoding='utf-8')
        artist = truncate_text(self.music_info.basic_info.artist, tempFont, 800)
        self.baseImgDraw.text((729, 182), artist, "white", tempFont)

        # 标题文字 - 修改后的代码
        tempFont_title = ImageFont.truetype(f'{FONT_PATH}/FOT-NewRodinProN-EB.otf', 55, encoding='utf-8')
        tempFont_basic = ImageFont.truetype(f'{FONT_PATH}/SourceHanSans_17.ttf', 55, encoding='utf-8')

        # 检查标题中是否包含特殊字符
        from src.libraries.config.GLOBAL_CONSTANT import SPECIAL_CHAR
        has_special_char = any(char in SPECIAL_CHAR for char in self.music_info.basic_info.title)
        
        if not has_special_char:
            # 情况一：没有特殊字符，使用原有换行逻辑
            title = split_text_to_lines(self.music_info.basic_info.title, 800, tempFont_title)
            
            if isinstance(title, str):
                lines = title.split('\n')
            else:
                lines = title

            # 普通情况的高度参数
            line_height = 56
            line_spacing = 18
            start_y = 272

            for i, line in enumerate(lines):
                y_position = start_y + i * (line_height + line_spacing)
                # 普通情况：直接绘制整行
                self.baseImgDraw.text((727, y_position), line, "white", tempFont_title)
                
        else:
            # 情况二：有特殊字符，使用混合字体处理
            # 需要手动处理换行
            title = self.music_info.basic_info.title
            
            # 缺字情况的特殊高度参数
            line_height = 56
            line_spacing = 18
            start_y = 290  # 缺字情况的起始高度可以不同
            
            # 手动换行逻辑（基于字符宽度）
            lines = []
            current_line = ""
            current_width = 0
            max_width = 800  # 最大宽度限制
            
            for char in title:
                if char in SPECIAL_CHAR:
                    try:
                        char_bbox = tempFont_basic.getbbox(char)
                        char_width = char_bbox[2] - char_bbox[0]
                    except:
                        char_width = 30
                else:
                    try:
                        char_bbox = tempFont_title.getbbox(char)
                        char_width = char_bbox[2] - char_bbox[0]
                    except:
                        char_width = 30
                
                if current_width + char_width > max_width and current_line:
                    lines.append(current_line)
                    current_line = char
                    current_width = char_width
                else:
                    current_line += char
                    current_width += char_width
            
            if current_line:
                lines.append(current_line)

            # 绘制缺字情况的文本
            for i, line in enumerate(lines):
                y_position = start_y + i * (line_height + line_spacing)
                
                # 计算当前行的总宽度
                try:
                    line_width = 0
                    for char in line:
                        if char in SPECIAL_CHAR:
                            char_bbox = tempFont_basic.getbbox(char)
                            line_width += char_bbox[2] - char_bbox[0]
                        else:
                            char_bbox = tempFont_title.getbbox(char)
                            line_width += char_bbox[2] - char_bbox[0]
                except:
                    line_width = len(line) * 30
                
                # 计算起始位置（左对齐，x=727）
                current_x = 727
                
                # 逐个字符绘制
                for char in line:
                    if char in SPECIAL_CHAR:
                        # 使用基础字体绘制特殊字符
                        char_bbox = tempFont_basic.getbbox(char)
                        char_width = char_bbox[2] - char_bbox[0]
                        self.baseImgDraw.text((current_x + char_width // 2, y_position), char, "white", tempFont_basic, anchor='mm')
                        current_x += char_width
                    else:
                        # 使用标题字体绘制普通字符
                        char_bbox = tempFont_title.getbbox(char)
                        char_width = char_bbox[2] - char_bbox[0]
                        self.baseImgDraw.text((current_x + char_width // 2, y_position), char, "white", tempFont_title, anchor='mm')
                        current_x += char_width
            

        # 歌曲ID、BPM、分类、版本信息
        tempFont = ImageFont.truetype(f"{FONT_PATH}/GlowSansSC-Normal-Heavy.otf", 42, encoding='utf-8')

        text_width, text_height = tempFont.getsize(str(self.music_info.basic_info.id))
        self.baseImgDraw.text(((820 - text_width / 2), (621 - text_height / 2)), str(self.music_info.basic_info.id), "white", tempFont)

        text_width, text_height = tempFont.getsize(str(self.music_info.basic_info.bpm))
        self.baseImgDraw.text(((979 - text_width / 2), (621 - text_height / 2)), str(self.music_info.basic_info.bpm), "white", tempFont)

        if self.music_info.basic_info.genre in ["niconico & VOCALOID", "niconicoボーカロイド", "ゲームバラエティ"]:
            tempFont = ImageFont.truetype(f"{FONT_PATH}/GlowSansSC-Normal-Heavy.otf", 29, encoding='utf-8')
            text_width, text_height = tempFont.getsize(self.music_info.basic_info.genre)
            self.baseImgDraw.text(((1210 - text_width / 2), (624 - text_height / 2)), self.music_info.basic_info.genre, "white", tempFont)
        else:
            text_width, text_height = tempFont.getsize(self.music_info.basic_info.genre)
            self.baseImgDraw.text(((1210 - text_width / 2), (624 - text_height / 2)), self.music_info.basic_info.genre, "white", tempFont)

        # 第四步：合成其他装饰元素（在文字之上）
        # 类型图标
        TypeIconImg = Image.open(f"{MAI_MUSIC_INFO_ASSET_PATH}/类型/{self.music_info.basic_info.type}.png").convert('RGBA')
        # 【alpha_composite合成】合成类型图标
        type_layer = self._create_composite_layer(TypeIconImg, (1397, 606))
        self.baseImg = Image.alpha_composite(self.baseImg, type_layer)

        # 版本logo
        if self.music_info.basic_info.version.id in VERSION_LOGO_MAP:
            VersionLogoImg = Image.open(f"{MAI_MUSIC_INFO_ASSET_PATH}/版本牌/UI_CMN_TabTitle_MaimaiTitle_Ver{VERSION_LOGO_MAP.get(self.music_info.basic_info.version.id)}.png").convert('RGBA')
            # 【alpha_composite合成】合成版本logo
            text_width, text_height = VersionLogoImg.size
            version_layer = self._create_composite_layer(VersionLogoImg, (200 - text_width // 2, 150 - text_height // 2))
            self.baseImg = Image.alpha_composite(self.baseImg, version_layer)

        # 先统一把需要加载的图片处理完
        if not self.use_special_bg:
            if self.music_info.is_re_master():
                charter_bg = Image.open(f"{MAI_MUSIC_INFO_ASSET_PATH}/cr_circle_2.png").convert('RGBA')
            else:
                charter_bg = Image.open(f"{MAI_MUSIC_INFO_ASSET_PATH}/cr_circle_1.png").convert('RGBA')
            
            # 确保作者信息背景尺寸正确
            if charter_bg.size != self.baseImg.size:
                charter_bg = charter_bg.resize(self.baseImg.size)

            # 【alpha_composite合成】合成作者信息背景
            self.baseImg = Image.alpha_composite(self.baseImg, charter_bg)
 
        if self.music_info.is_re_master():
            charter_map = [(), (), (428, 1456), (428, 1536), (428, 1616)]
        else:
            charter_map = [(), (), (431, 1474), (431, 1594)]

        # 重新创建Draw对象，因为baseImg被重新赋值了
        self.baseImgDraw = ImageDraw.Draw(self.baseImg)
        tempFont = ImageFont.truetype(f"{FONT_PATH}/GlowSansSC-Normal-ExtraBold.otf", 40, encoding='utf-8')
    
        if chars:
            for index, chart in enumerate(chars.get_chart_list()):
                if index < len(charter_map) and charter_map[index]:
                    chart_charter = str(chart.designer)
                    x, base_y = charter_map[index]
                    
                    # 检查文本宽度，决定是否需要换行
                    text_width = tempFont.getsize(chart_charter)[0]
                    max_width = 550
                    
                    if text_width <= max_width:
                        # 单行显示
                        self.baseImgDraw.text((x, base_y), chart_charter, self.text_color, tempFont)
                    else:
                        # 需要换行，将文本分成两行
                        lines = []
                        current_line = ""
                        
                        for char in chart_charter:
                            test_line = current_line + char
                            if tempFont.getsize(test_line)[0] <= max_width:
                                current_line = test_line
                            else:
                                if current_line:
                                    lines.append(current_line)
                                current_line = char
                        
                        if current_line:
                            lines.append(current_line)
                        
                        # 如果超过2行，后续行截断
                        if len(lines) > 2:
                            lines = lines[:2]
                            lines[1] = truncate_text(lines[1], tempFont, max_width)
                        
                        # 计算行高和总高度
                        line_height = tempFont.getsize("测试")[1]
                        line_spacing = 5
                        total_height = len(lines) * line_height + (len(lines) - 1) * line_spacing
                        
                        # 调整起始Y坐标，使多行文本整体居中
                        start_y = base_y - (total_height - line_height) // 2
                        
                        # 绘制每一行
                        for i, line in enumerate(lines):
                            y_position = start_y + i * (line_height + line_spacing)
                            self.baseImgDraw.text((x, y_position), line, self.text_color, tempFont)

        # 版本&抽象画作者文字
        tempFont = ImageFont.truetype(f"{FONT_PATH}/GlowSansSC-Normal-Bold.otf", 40, encoding='utf-8')

        version = truncate_text(self.music_info.basic_info.version.text, tempFont, 420)
        fontSizeX, fontSizeY = tempFont.getsize(version)
        self.baseImgDraw.text((1262 - int(fontSizeX / 2), 1499), version, self.text_color, tempFont)

        abstract_artist = truncate_text(self.abstract_artist, tempFont, 420)
        fontSizeX, fontSizeY = tempFont.getsize(abstract_artist)
        self.baseImgDraw.text((1262 - int(fontSizeX / 2), 1618), abstract_artist, self.text_color, tempFont)
        

        # 先统一把需要加载的图片处理完
        if not self.use_special_bg:
            if self.music_info.is_re_master():
                tap_data_bg = Image.open(f"{MAI_MUSIC_INFO_ASSET_PATH}/im_circle_2.png").convert('RGBA')
            else:
                tap_data_bg = Image.open(f"{MAI_MUSIC_INFO_ASSET_PATH}/im_circle_1.png").convert('RGBA')
            
            # 确保作者信息背景尺寸正确
            if tap_data_bg.size != self.baseImg.size:
                tap_data_bg = tap_data_bg.resize(self.baseImg.size)

            # 【alpha_composite合成】合成作者信息背景
            self.baseImg = Image.alpha_composite(self.baseImg, tap_data_bg)
            self.baseImgDraw = ImageDraw.Draw(self.baseImg)

        for index, chart in enumerate(chars.get_chart_list()):
            constant = chart.constant
            tempFont = ImageFont.truetype(f"{FONT_PATH}/RoGSanSrfStd-Bd.otf", 50, encoding='utf-8')
            constant = decimalPoints(constant, 1)
            fontSizeX, fontSizeY = tempFont.getsize(constant)

            constant_start_x = 556 if self.music_info.is_re_master() else 656

            self.baseImgDraw.text((constant_start_x + (202 * index) - int(fontSizeX / 2), 829 - int(fontSizeY / 2)), constant, "white", tempFont)
            chart_notes = chart.notes

            if self.music_info.is_re_master():
                notes = [chart_notes.total, chart_notes.tap, chart_notes.hold, chart_notes.slide, chart_notes.touch, chart_notes.break_note]
            else:
                notes = [chart_notes.total, chart_notes.tap, chart_notes.hold, chart_notes.slide, '-', chart_notes.break_note]

            for note_index, note_count in enumerate(notes):
                tempFont = ImageFont.truetype(f"{FONT_PATH}/RoGSanSrfStd-Bd.otf", 48, encoding='utf-8')
                note_count = str(note_count)
                fontSizeX, fontSizeY = tempFont.getsize(note_count)
                self.baseImgDraw.text((constant_start_x + (202 * index) - int(fontSizeX / 2), 891 + (88 * note_index)), note_count, self.text_color, tempFont)
        return self.baseImg