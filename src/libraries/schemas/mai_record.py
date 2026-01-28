from pydantic import BaseModel, Field
from .mai import MaiBasicInfo, MaiChart, MaiScoreInfo, DIFFICULTY_KEY_MAP
from src.server.mai_music_server import total_music



class MaiRecord(BaseModel):
    basic_info: MaiBasicInfo
    chart: MaiChart
    score_info: MaiScoreInfo

class MaiRecordList(BaseModel):
    records: list[MaiRecord]

    def __getitem__(self, index: int) -> MaiRecord:
        return self.records[index]
    
    def __len__(self) -> int:
        return len(self.records)
    
    def __iter__(self):
        return iter(self.records)

class DivingFishMaiRecord(BaseModel):
    song_id: int
    title: str
    achievements: float
    ds: float
    type: str
    dx_score: int = Field(alias="dxScore")
    fc: str
    fs: str
    level: str
    level_index: int
    level_label: str
    rate: str
    ra: int

    def to_mai_record(self) -> MaiRecord:
        """
        将 DivingFish 格式转换为 MaiRecord 格式
        通过 MaiMusicList 匹配并填充完整的 MaiBasicInfo 和 MaiChart
        """
        
        # 从 MaiMusicList 中查找对应的音乐
        music = total_music.find_by_id(self.song_id)
        difficulty = DIFFICULTY_KEY_MAP[self.level_index]
        # 构建 basic_info
        if music and music.charts:
            return MaiRecord(
                basic_info=music.basic_info,
                chart=music.charts[difficulty],
                score_info=MaiScoreInfo(
                    achievement=self.achievements,
                    rank=self.rate,
                    rating=self.ra,
                    dx_rate=self.ra,
                    dx_score=self.dx_score,
                    combo_status=self.fc,
                    sync_status=self.fs
                )
            )
        else:
            raise ValueError(f"music not found: {self.song_id}")

# def transform_and_convert(data: Any) -> Any:
#     if not isinstance(data, dict):
#         return data
        
#     transformed = {}
#     for song_id, records in data.items():
#         if isinstance(records, list):
#             level_dict = {}
#             for record_data in records:
#                 # Validate and parse using DivingFishMaiRecord
#                 df_record = DivingFishMaiRecord.model_validate(record_data)
#                 # Convert to generic MaiRecord
#                 level_dict[df_record.level_index] = df_record.to_mai_record()
#             transformed[song_id] = level_dict
#         else:
#             transformed[song_id] = records
#     return transformed

# DivingFishPlayerRecordResponse = Annotated[Dict[str, Dict[int, MaiRecord]], BeforeValidator(transform_and_convert)]