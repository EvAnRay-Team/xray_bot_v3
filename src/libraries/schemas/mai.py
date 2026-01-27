from pydantic import BaseModel

class MaiBasicInfo(BaseModel):
    id: int
    title: str
    type: str

class MaiCharts(BaseModel):
    difficulty: int
    level: str
    constant: float

class MaiScoreInfo(BaseModel):
    achievement: float
    rank: str
    rating: int
    dx_score: int
    dx_rate: float
    combo_status: str
    sync_status: str
