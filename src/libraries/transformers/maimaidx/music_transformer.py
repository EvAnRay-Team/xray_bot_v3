import json
import logging
from pathlib import Path
from typing import Any

from src.libraries.config.GLOBAL_CONSTANT import (
    MAIMAI_GENRE_MAP,
    MAIMAI_VERSION_CN_MAP,
    VERSION_EZ_MAP,
)
from src.libraries.config.GLOBAL_PATH import DATA_PATH


def transform_music_data() -> list[dict[str, Any]]:
    """
    Load music_data.json and transform it to standardized dictionary format.
    Excludes UTAGE data.
    """
    music_data_path = Path(f"{DATA_PATH}/maimai/music_data.json")

    try:
        with music_data_path.open(encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        logging.exception(f"Error: Music data file not found at {music_data_path}")
        return []

    transformed_list = []

    for item in raw_data:
        basic_info = item.get("basic_info", {})

        # 1. 版本映射 (和制 -> 中文)
        origin_ver = basic_info.get("from", "")
        cn_ver = MAIMAI_VERSION_CN_MAP.get(origin_ver, origin_ver)

        # 2. 简易版本映射 (中文 -> 简写)
        ez_ver = VERSION_EZ_MAP.get(cn_ver or "", cn_ver or "")

        # 3. 流派映射 (日文 -> 中文/梗)
        origin_genre = basic_info.get("genre", "")
        mapped_genre = MAIMAI_GENRE_MAP.get(origin_genre, origin_genre)

        # 注入标准键值 (为了方便在根层级调用，也为了兼容 v2 逻辑同步更新 basic_info)
        item["cn_version"] = cn_ver
        item["ez_version"] = ez_ver
        item["genre"] = mapped_genre

        item["basic_info"]["cn_from"] = cn_ver
        item["basic_info"]["ez_from"] = ez_ver
        item["basic_info"]["genre"] = mapped_genre

        transformed_list.append(item)

    return transformed_list
