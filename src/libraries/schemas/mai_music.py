from .mai import *
from pathlib import Path

class MaiMusicList(BaseModel):
    """音乐数据列表，用于加载整个 music_data.json"""
    musics: list[MaiMusic]
    
    @classmethod
    def from_json_file(cls, file_path: str | Path) -> "MaiMusicList":
        """从 JSON 文件加载音乐数据列表"""
        import json
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 如果 data 是列表，直接使用
        if isinstance(data, list):
            musics = [MaiMusic.model_validate(song) for song in data]
            return cls(musics=musics)
        # 如果 data 是字典且包含 musics 键
        elif isinstance(data, dict) and "musics" in data:
            return cls.model_validate(data)
        else:
            raise ValueError(f"Invalid JSON format: expected list or dict with 'musics' key")
    
    @classmethod
    def from_json_data(cls, data: list[dict] | dict) -> "MaiMusicList":
        """从 JSON 数据（列表或字典）加载音乐数据列表"""
        if isinstance(data, list):
            musics = [MaiMusic.model_validate(song) for song in data]
            return cls(musics=musics)
        elif isinstance(data, dict) and "musics" in data:
            return cls.model_validate(data)
        else:
            raise ValueError(f"Invalid data format: expected list or dict with 'musics' key")
    
    def __getitem__(self, index: int) -> MaiMusic:
        """支持索引访问，如 music_list[0]"""
        return self.musics[index]
    
    def __len__(self) -> int:
        """返回音乐数量"""
        return len(self.musics)
    
    def __iter__(self):
        """支持迭代，如 for music in music_list"""
        return iter(self.musics)
    
    def find_by_id(self, music_id: int) -> MaiMusic | None:
        """根据 ID 查找音乐"""
        for music in self.musics:
            if music.basic_info.id == music_id:
                return music
        return None
    
    def find_by_title(self, title: str, is_utage: bool = False) -> list[MaiMusic]:
        """根据标题查找音乐（支持部分匹配）"""
        return [music for music in self.musics if (title.lower() in music.basic_info.title.lower() and music.is_utage() == is_utage)]
    
    def get_utage_musics(self) -> list[MaiMusic]:
        """获取所有宴谱"""
        return [music for music in self.musics if music.is_utage()]
    
    def get_normal_musics(self) -> list[MaiMusic]:
        """获取所有普通歌曲"""
        return [music for music in self.musics if not music.is_utage()]

    class Config:
        populate_by_name = True


