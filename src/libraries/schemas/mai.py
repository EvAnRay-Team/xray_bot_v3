from pydantic import BaseModel, Field
from typing import Optional, Any



class MaiVersionInfo(BaseModel):
    text: str
    id: int

class MaiBasicInfo(BaseModel):
    id: int
    title: str
    artist: str
    bpm: int
    genre: str
    version: MaiVersionInfo
    type: Optional[str] = None  # 宴谱没有type字段

class MaiNotes(BaseModel):
    total: int
    tap: int
    hold: int
    slide: int
    touch: int
    break_note: int = Field(alias="break")

    class Config:
        populate_by_name = True

class MaiChart(BaseModel):
    difficulty: int
    level: str
    constant: float
    designer: str
    notes: MaiNotes

class MaiCharts(BaseModel):
    """动态键名的charts，如 BASIC, ADVANCED, EXPERT, MASTER, Re:MASTER"""
    # 使用 model_config 和 extra = "allow" 来允许动态键名
    model_config = {"extra": "allow"}
    
    def __getattr__(self, name: str) -> MaiChart:
        """支持属性访问，如 charts.BASIC"""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # 尝试从 model_extra 获取（Pydantic v2 存储额外字段的地方）
        if hasattr(self, 'model_extra') and self.model_extra and name in self.model_extra:
            return self.model_extra[name]
        
        # 尝试从 __dict__ 获取
        if hasattr(self, '__dict__') and name in self.__dict__:
            return self.__dict__[name]
        
        # 尝试使用 getattr 获取（Pydantic 可能已经将其作为属性）
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __getitem__(self, key: str) -> MaiChart:
        """支持字典式访问，如 charts['BASIC']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: MaiChart) -> None:
        """支持字典式设置"""
        setattr(self, key, value)
    
    def keys(self):
        """返回所有键"""
        keys_list = []
        # 从 model_extra 获取
        if hasattr(self, 'model_extra') and self.model_extra:
            keys_list.extend(self.model_extra.keys())
        # 从 __dict__ 获取（排除私有属性）
        if hasattr(self, '__dict__'):
            keys_list.extend([k for k in self.__dict__.keys() if not k.startswith('_') and k != 'model_extra'])
        return list(set(keys_list))  # 去重
    
    def values(self):
        """返回所有值"""
        return [getattr(self, k) for k in self.keys()]
    
    def items(self):
        """返回所有键值对"""
        return [(k, getattr(self, k)) for k in self.keys()]

class MaiUtageInfo(BaseModel):
    level: str
    type: str
    commit: str
    skip_condition: str
    is_buddy: bool
    player_count: list[int]

class MaiUtageChart(BaseModel):
    total: int
    tap: int
    hold: int
    slide: int
    touch: int
    break_note: int = Field(alias="break")

    class Config:
        populate_by_name = True

class MaiUtageCharts(BaseModel):
    """动态键名的utage charts，如 left, right, single"""
    # 使用 model_config 和 extra = "allow" 来允许动态键名
    model_config = {"extra": "allow"}
    
    def __getattr__(self, name: str) -> MaiUtageChart:
        """支持属性访问，如 utage_charts.left"""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # 尝试从 model_extra 获取（Pydantic v2 存储额外字段的地方）
        if hasattr(self, 'model_extra') and self.model_extra and name in self.model_extra:
            return self.model_extra[name]
        
        # 尝试从 __dict__ 获取
        if hasattr(self, '__dict__') and name in self.__dict__:
            return self.__dict__[name]
        
        # 尝试使用 getattr 获取（Pydantic 可能已经将其作为属性）
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __getitem__(self, key: str) -> MaiUtageChart:
        """支持字典式访问，如 utage_charts['left']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: MaiUtageChart) -> None:
        """支持字典式设置"""
        setattr(self, key, value)
    
    def keys(self):
        """返回所有键"""
        keys_list = []
        # 从 model_extra 获取
        if hasattr(self, 'model_extra') and self.model_extra:
            keys_list.extend(self.model_extra.keys())
        # 从 __dict__ 获取（排除私有属性）
        if hasattr(self, '__dict__'):
            keys_list.extend([k for k in self.__dict__.keys() if not k.startswith('_') and k != 'model_extra'])
        return list(set(keys_list))  # 去重
    
    def values(self):
        """返回所有值"""
        return [getattr(self, k) for k in self.keys()]
    
    def items(self):
        """返回所有键值对"""
        return [(k, getattr(self, k)) for k in self.keys()]

class MaiMusic(BaseModel):
    """音乐数据模型，可以是普通歌曲或宴谱"""
    basic_info: MaiBasicInfo
    charts: Optional[MaiCharts] = None  # 普通歌曲的charts
    utage_info: Optional[MaiUtageInfo] = None  # 宴谱的info
    utage_charts: Optional[MaiUtageCharts] = None  # 宴谱的charts
    
    @classmethod
    def model_validate(cls, obj: Any):
        """重写 model_validate 以处理动态键名的 charts"""
        if isinstance(obj, dict):
            # 创建副本以避免修改原始数据
            obj = obj.copy()
            
            # 处理 charts
            if 'charts' in obj and obj['charts'] is not None:
                charts_dict = obj['charts']
                if isinstance(charts_dict, dict):
                    # 将每个 chart 转换为 MaiChart 对象
                    charts_data = {}
                    for key, chart_data in charts_dict.items():
                        if isinstance(chart_data, dict):
                            charts_data[key] = MaiChart(**chart_data)
                        else:
                            charts_data[key] = chart_data
                    # 使用 **charts_data 展开字典，这样 Pydantic 会将它们作为额外字段
                    obj['charts'] = MaiCharts(**charts_data)
            
            # 处理 utage_charts
            if 'utage_charts' in obj and obj['utage_charts'] is not None:
                charts_dict = obj['utage_charts']
                if isinstance(charts_dict, dict):
                    # 将每个 chart 转换为 MaiUtageChart 对象
                    charts_data = {}
                    for key, chart_data in charts_dict.items():
                        if isinstance(chart_data, dict):
                            charts_data[key] = MaiUtageChart(**chart_data)
                        else:
                            charts_data[key] = chart_data
                    # 使用 **charts_data 展开字典，这样 Pydantic 会将它们作为额外字段
                    obj['utage_charts'] = MaiUtageCharts(**charts_data)
        
        return super().model_validate(obj)
    
    def is_utage(self) -> bool:
        """判断是否是宴谱"""
        return self.utage_info is not None and self.utage_charts is not None

class MaiScoreInfo(BaseModel):
    achievement: float
    rank: str
    rating: int
    dx_score: int
    dx_rate: float
    combo_status: str
    sync_status: str

# class MaiMusicList(BaseModel):
#     musics: list[MaiMusic]

#     class Config:
#         populate_by_name = True
