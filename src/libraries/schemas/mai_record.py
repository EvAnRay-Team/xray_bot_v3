from typing import Dict, Annotated, Any
from pydantic import BaseModel, Field, BeforeValidator
from .mai import MaiBasicInfo, MaiCharts, MaiScoreInfo

class MaiRecord(BaseModel):
    basic_info: MaiBasicInfo
    charts: MaiCharts
    score_info: MaiScoreInfo


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
        # Map fields from DivingFish format to generic MaiRecord format
        return MaiRecord(
            basic_info=MaiBasicInfo(
                id=self.song_id,
                title=self.title,
                type=self.type
            ),
            charts=MaiCharts(
                difficulty=self.level_index,
                level=self.level,
                constant=self.ds
            ),
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

def transform_and_convert(data: Any) -> Any:
    if not isinstance(data, dict):
        return data
        
    transformed = {}
    for song_id, records in data.items():
        if isinstance(records, list):
            level_dict = {}
            for record_data in records:
                # Validate and parse using DivingFishMaiRecord
                df_record = DivingFishMaiRecord.model_validate(record_data)
                # Convert to generic MaiRecord
                level_dict[df_record.level_index] = df_record.to_mai_record()
            transformed[song_id] = level_dict
        else:
            transformed[song_id] = records
    return transformed

DivingFishPlayerRecordResponse = Annotated[Dict[str, Dict[int, MaiRecord]], BeforeValidator(transform_and_convert)]