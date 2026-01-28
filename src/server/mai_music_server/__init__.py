from src.libraries.providers.mai import DivingFishMaiApi,LxnsMaiApi
from src.libraries.schemas.mai import DIFFICULTY_KEY_MAP
from src.libraries.schemas.mai_music import MaiMusicList
from src.libraries.config.GLOBAL_PATH import MAI_MUSIC_DATA_PATH
from nonebot.log import logger
from pathlib import Path
import json
import asyncio

class MaiMusicMerge():
    def __init__(self) -> None:
        asyncio.run(self.run_async())

    def convert_notes_array_to_object(self, notes_array: list, song_type: str) -> dict:
        """
        将notes数组转换为notes对象
        SD类型: [tap, hold, slide, break] -> 4个元素
        DX类型: [tap, hold, slide, touch, break] -> 5个元素
        """
        if song_type == "DX" and len(notes_array) == 5:
            tap, hold, slide, touch, break_note = notes_array
            total = tap + hold + slide + touch + break_note
            return {
                "total": total,
                "tap": tap,
                "hold": hold,
                "slide": slide,
                "touch": touch,
                "break": break_note
            }
        elif song_type == "SD" and len(notes_array) == 4:
            tap, hold, slide, break_note = notes_array
            total = tap + hold + slide + break_note
            return {
                "total": total,
                "tap": tap,
                "hold": hold,
                "slide": slide,
                "touch": 0,  # SD类型没有touch
                "break": break_note
            }
        else:
            # 兼容处理：如果数组长度不符合预期，尝试推断
            logger.warning(f"Unexpected notes array length: {len(notes_array)} for type: {song_type}")
            if len(notes_array) == 5:
                tap, hold, slide, touch, break_note = notes_array
                total = tap + hold + slide + touch + break_note
                return {
                    "total": total,
                    "tap": tap,
                    "hold": hold,
                    "slide": slide,
                    "touch": touch,
                    "break": break_note
                }
            elif len(notes_array) == 4:
                tap, hold, slide, break_note = notes_array
                total = tap + hold + slide + break_note
                return {
                    "total": total,
                    "tap": tap,
                    "hold": hold,
                    "slide": slide,
                    "touch": 0,
                    "break": break_note
                }
            else:
                # 默认值
                return {
                    "total": sum(notes_array),
                    "tap": notes_array[0] if len(notes_array) > 0 else 0,
                    "hold": notes_array[1] if len(notes_array) > 1 else 0,
                    "slide": notes_array[2] if len(notes_array) > 2 else 0,
                    "touch": notes_array[3] if len(notes_array) > 3 else 0,
                    "break": notes_array[4] if len(notes_array) > 4 else (notes_array[3] if len(notes_array) > 3 else 0)
                }

    def _build_utage_song(self, df_song: dict, lxns_song: dict | None, basic_info: dict) -> dict:
        """
        构建宴谱的特殊格式
        """
        # 从lxns数据中获取utage信息
        utage_difficulties = []
        if lxns_song and "difficulties" in lxns_song:
            utage_difficulties = lxns_song["difficulties"].get("utage", [])
        
        # 获取第一个utage难度作为主要信息（通常只有一个）
        utage_info_data = utage_difficulties[0] if utage_difficulties else {}
        
        # 构建utage_info
        kanji = utage_info_data.get("kanji", "")
        utage_type = kanji if kanji else "宴"  # 默认使用"宴"
        
        # 获取commit字段，用于统计感叹号数量
        commit_text = utage_info_data.get("description", "")
        
        # 构建utage_charts（对象格式）
        utage_charts = {}
        df_charts = df_song.get("charts", [])
        
        # 统计commit中感叹号的数量
        exclamation_count = commit_text.count("!")
        
        # 如果lxns有utage数据，使用lxns的notes
        if utage_difficulties:
            # 通常只有一个utage难度
            lxns_utage = utage_difficulties[0]
            notes_obj = lxns_utage.get("notes", {})
            
            # 检查notes是否包含left/right（双人谱）
            if isinstance(notes_obj, dict) and ("left" in notes_obj or "right" in notes_obj):
                # 有left/right，直接使用
                utage_charts = notes_obj
            elif notes_obj and isinstance(notes_obj, dict) and "total" in notes_obj:
                # 单个谱面（notes_obj是单个notes对象）
                # 检查df_charts是否有多个，如果有多个可能需要构建left/right
                # 但通常lxns的notes如果是单个对象，就表示只有一个谱面
                # 单个谱面时，utage_charts应该是一个对象，但只有一个键值对
                # 键名可以是任意的，但为了保持一致性，使用第一个chart的索引或默认键名
                # 实际上，从用户提供的格式来看，单个谱面时utage_charts应该只有一个键
                # 但根据实际数据结构，如果只有一个谱面，可能需要一个默认键名
                # 暂时使用空字符串作为键名，或者根据实际情况调整
                # 但更合理的做法是：如果只有一个谱面，utage_charts直接就是notes对象
                # 不过用户要求utage_charts是对象格式，所以需要一个键名
                # 根据用户示例，单个谱面时可能不需要特定的键名，但需要保持对象格式
                # 让我使用一个默认键名，比如"0"或"main"
                utage_charts = {"single": notes_obj}
        else:
            # 回退到使用df_music的charts
            if len(df_charts) >= 2:
                # 有两个charts，构建left和right
                left_notes = self.convert_notes_array_to_object(df_charts[0].get("notes", []), "DX") if df_charts[0].get("notes") else {
                    "total": 0, "tap": 0, "hold": 0, "slide": 0, "touch": 0, "break": 0
                }
                right_notes = self.convert_notes_array_to_object(df_charts[1].get("notes", []), "DX") if len(df_charts) > 1 and df_charts[1].get("notes") else {
                    "total": 0, "tap": 0, "hold": 0, "slide": 0, "touch": 0, "break": 0
                }
                utage_charts = {
                    "left": left_notes,
                    "right": right_notes
                }
            elif len(df_charts) == 1:
                # 单个chart
                notes_array = df_charts[0].get("notes", [])
                notes_obj = self.convert_notes_array_to_object(notes_array, "DX") if notes_array else {
                    "total": 0, "tap": 0, "hold": 0, "slide": 0, "touch": 0, "break": 0
                }
                utage_charts = {"single": notes_obj}
            else:
                # 没有charts，使用空对象
                utage_charts = {}
        
        # 根据utage_charts的键数量和commit中感叹号数量确定player_count
        # x = commit中感叹号数量
        # 数量 = utage_charts的键数量（left+right 或 single）
        # player_count = [x] * 数量
        chart_keys = list(utage_charts.keys())
        chart_count = len(chart_keys)
        
        if chart_count == 0:
            player_count = []
        else:
            # 每个谱面的玩家数都是commit中感叹号的数量
            # 如果感叹号数量为0，默认为1
            x = exclamation_count if exclamation_count > 0 else 1
            player_count = [x] * chart_count
        
        utage_info = {
            "level": utage_info_data.get("level", ""),
            "type": utage_type,
            "commit": utage_info_data.get("description", ""),
            "skip_condition": "",  # 跳关条件，df_music中没有这个信息
            "is_buddy": utage_info_data.get("is_buddy", False),
            "player_count": player_count
        }
        
        # 确保genre是"宴会场"
        basic_info["genre"] = "宴会场"
        
        return {
            "basic_info": basic_info,
            "utage_info": utage_info,
            "utage_charts": utage_charts
        }

    def merge_music_data(self, df_music_data: list, lxns_music_data: dict) -> list:
        """
        合并两个数据源
        df_music_data: DivingFish API返回的数据（主数据源）
        lxns_music_data: Lxns API返回的数据（用于获取version信息）
        """
        logger.info("开始合并音乐数据...")
        
        # 创建lxns数据的索引，以id为key
        lxns_index = {}
        if "songs" in lxns_music_data:
            for song in lxns_music_data["songs"]:
                lxns_index[str(song["id"])] = song
        
        logger.info(f"已索引 {len(lxns_index)} 首 Lxns 歌曲数据")
        
        merged_data = []
        stats = {
            "total": 0,
            "st": 0,
            "dx": 0,
            "utage": 0,
            "missing_lxns": 0,
            "using_lxns_difficulties": 0,
            "using_df_difficulties": 0
        }
        
        for df_song in df_music_data:
            song_id = str(df_song["id"])
            song_id_int = int(df_song["id"])
            song_type = df_song.get("type", "SD")  # SD or DX
            
            # 检查是否是宴谱（id > 100000）
            is_utage = song_id_int > 100000
            
            # 获取lxns数据中的版本信息
            # 如果df_music的id大于10000（DX谱），需要减去10000来匹配lxns的id
            # 宴谱的id直接使用（因为lxns中宴谱的id就是100000+）
            lxns_lookup_id = song_id_int
            if 100000 > song_id_int > 10000:
                lxns_lookup_id = song_id_int - 10000
            
            lxns_song = lxns_index.get(str(lxns_lookup_id))
            version_id = lxns_song.get("version") if lxns_song else None
            version_text = df_song.get("basic_info", {}).get("from", "")
            
            # 如果没有找到lxns数据，记录警告
            if not lxns_song:
                stats["missing_lxns"] += 1
                logger.warning(f"Song {song_id} ({df_song.get('title', 'Unknown')}) not found in lxns data (looked up as {lxns_lookup_id})")
            
            # 构建basic_info
            basic_info = df_song.get("basic_info", {})
            merged_basic_info = {
                "id": int(df_song["id"]),
                "title": basic_info.get("title", df_song.get("title", "")),
                "artist": basic_info.get("artist", ""),
                "bpm": int(basic_info.get("bpm", 0)),
                "genre": basic_info.get("genre", ""),
                "version": {
                    "text": version_text,
                    "id": version_id if version_id is not None else 0
                }
            }
            
            # 如果是宴谱，使用特殊的格式（不包含type字段）
            if is_utage:
                stats["utage"] += 1
                merged_song = self._build_utage_song(df_song, lxns_song, merged_basic_info)
            else:
                # 普通歌曲需要type字段
                merged_basic_info["type"] = "ST" if song_type == "SD" else "DX"
                if song_type == "SD":
                    stats["st"] += 1
                else:
                    stats["dx"] += 1
                
                # 构建charts（普通歌曲）
                charts = {}
                df_charts = df_song.get("charts", [])
                ds_array = df_song.get("ds", [])
                level_array = df_song.get("level", [])
                
                # 确定使用哪个数据源的难度信息
                # 优先使用lxns的difficulties，因为它有更完整的difficulty映射
                if lxns_song and "difficulties" in lxns_song:
                    # 使用lxns的difficulties结构
                    stats["using_lxns_difficulties"] += 1
                    difficulties_key = "standard" if song_type == "SD" else "dx"
                    lxns_difficulties = lxns_song["difficulties"].get(difficulties_key, [])
                    
                    for lxns_diff in lxns_difficulties:
                        difficulty_index = lxns_diff.get("difficulty", 0)
                        if difficulty_index not in DIFFICULTY_KEY_MAP:
                            continue
                        
                        diff_name = DIFFICULTY_KEY_MAP[difficulty_index]
                        
                        # 从df_charts中获取notes和charter
                        df_chart = df_charts[difficulty_index] if difficulty_index < len(df_charts) else None
                        
                        notes_obj = {
                            "total": 0,
                            "tap": 0,
                            "hold": 0,
                            "slide": 0,
                            "touch": 0,
                            "break": 0
                        }
                        charter = "-"
                        if df_chart:
                            notes_array = df_chart.get("notes", [])
                            if notes_array:
                                notes_obj = self.convert_notes_array_to_object(notes_array, song_type)
                            charter = df_chart.get("charter", "-")
                        
                        charts[diff_name] = {
                            "difficulty": difficulty_index,
                            "level": lxns_diff.get("level", level_array[difficulty_index] if difficulty_index < len(level_array) else ""),
                            "level_lable": diff_name,  # 使用 DIFFICULTY_KEY_MAP 对应的值
                            "constant": float(lxns_diff.get("level_value", ds_array[difficulty_index] if difficulty_index < len(ds_array) else 0.0)),
                            "designer": lxns_diff.get("note_designer", charter),
                            "notes": notes_obj
                        }
                else:
                    # 回退到使用df_music的charts数组
                    stats["using_df_difficulties"] += 1
                    for idx, df_chart in enumerate(df_charts):
                        if idx not in DIFFICULTY_KEY_MAP:
                            continue
                        
                        diff_name = DIFFICULTY_KEY_MAP[idx]
                        notes_array = df_chart.get("notes", [])
                        
                        charts[diff_name] = {
                            "difficulty": idx,
                            "level": level_array[idx] if idx < len(level_array) else "",
                            "level_lable": diff_name,  # 使用 DIFFICULTY_KEY_MAP 对应的值
                            "constant": float(ds_array[idx] if idx < len(ds_array) else 0.0),
                            "designer": df_chart.get("charter", "-"),
                            "notes": self.convert_notes_array_to_object(notes_array, song_type)
                        }
                
                merged_song = {
                    "basic_info": merged_basic_info,
                    "charts": charts
                }
            
            merged_data.append(merged_song)
            stats["total"] += 1
        
        # 输出合并统计信息
        logger.info("合并完成，统计信息：")
        logger.info(f"  总歌曲数: {stats['total']}")
        logger.info(f"  ST歌曲: {stats['st']}")
        logger.info(f"  DX歌曲: {stats['dx']}")
        logger.info(f"  宴谱: {stats['utage']}")
        logger.info(f"  使用 Lxns 难度数据: {stats['using_lxns_difficulties']}")
        logger.info(f"  使用 DF 难度数据: {stats['using_df_difficulties']}")
        if stats["missing_lxns"] > 0:
            logger.warning(f"  未找到 Lxns 数据的歌曲: {stats['missing_lxns']}")
        
        return merged_data

    async def run_async(self):
        logger.info("开始获取音乐数据...")
        df_music_data = await DivingFishMaiApi().music_data()
        lxns_music_data = await LxnsMaiApi().song_list()
        
        logger.info(f"DivingFish API 返回 {len(df_music_data)} 首歌曲")
        logger.info(f"Lxns API 返回 {len(lxns_music_data.get('songs', []))} 首歌曲")
        
        merged_data = self.merge_music_data(df_music_data, lxns_music_data)
        
        logger.info(f"合并完成，共 {len(merged_data)} 首歌曲")
        
        # 保存到文件
        output_path = Path(MAI_MUSIC_DATA_PATH)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"正在保存合并数据到 {output_path}...")
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"音乐数据已成功保存到 {output_path}")

MaiMusicMerge()
total_music: MaiMusicList = MaiMusicList.from_json_file(Path(MAI_MUSIC_DATA_PATH))