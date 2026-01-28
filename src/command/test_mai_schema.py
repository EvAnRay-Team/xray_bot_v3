from command.base import BaseCommand
from server.mai_music_server import total_music

class Command(BaseCommand):
    def handle(self, **options):
        try:
            self.run_test()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

    def run_test(self):
        music_result = total_music.find_by_title('海底譚')
        if len(music_result) >= 1:
            music = music_result[0]
            if music and music.charts:
                print(music.charts.master.notes)

        # """测试 MaiMusic 模型的实例化"""
        # print("=" * 60)
        # print("测试 MaiMusic 模型实例化")
        # print("=" * 60)
        
        # # 加载 music_data_temp.json
        # data_path = Path("data/music_data_temp.json")
        # if not data_path.exists():
        #     print(f"错误: 文件 {data_path} 不存在")
        #     return
        
        # print(f"\n加载数据文件: {data_path}")
        # with data_path.open("r", encoding="utf-8") as f:
        #     data = json.load(f)
        
        # print(f"总共 {len(data)} 首歌曲\n")
        
        # # 测试前几首普通歌曲
        # print("-" * 60)
        # print("测试普通歌曲实例化")
        # print("-" * 60)
        
        # normal_song_count = 0
        # for i, song_data in enumerate(data[:5]):
        #     try:
        #         music = MaiMusic.model_validate(song_data)
        #         normal_song_count += 1
                
        #         print(f"\n[{i+1}] 歌曲ID: {music.basic_info.id}")
        #         print(f"    标题: {music.basic_info.title}")
        #         print(f"    艺术家: {music.basic_info.artist}")
        #         print(f"    类型: {music.basic_info.type}")
        #         print(f"    流派: {music.basic_info.genre}")
        #         print(f"    BPM: {music.basic_info.bpm}")
        #         print(f"    版本: {music.basic_info.version.text} (ID: {music.basic_info.version.id})")
                
        #         if music.is_utage():
        #             print(f"    ⚠️  这是宴谱（不应该出现在前5首）")
        #         else:
        #             print(f"    ✅ 普通歌曲")
        #             if music.charts:
        #                 print(f"    谱面数量: {len(music.charts.keys())}")
        #                 # 测试属性访问
        #                 if "BASIC" in music.charts.keys():
        #                     basic = music.charts.BASIC
        #                     print(f"    BASIC: Lv.{basic.level} (定数: {basic.constant})")
        #                 if "EXPERT" in music.charts.keys():
        #                     expert = music.charts.EXPERT
        #                     print(f"    EXPERT: Lv.{expert.level} (定数: {expert.constant})")
        #                 if "MASTER" in music.charts.keys():
        #                     master = music.charts.MASTER
        #                     print(f"    MASTER: Lv.{master.level} (定数: {master.constant})")
        #                     print(f"    MASTER notes: tap={master.notes.tap}, hold={master.notes.hold}, slide={master.notes.slide}, touch={master.notes.touch}, break={master.notes.break_note}")
                
        #     except Exception as e:
        #         print(f"\n[{i+1}] ❌ 实例化失败: {e}")
        #         import traceback
        #         traceback.print_exc()
        
        # # 查找并测试宴谱
        # print("\n" + "-" * 60)
        # print("测试宴谱实例化")
        # print("-" * 60)
        
        # utage_song_count = 0
        # for i, song_data in enumerate(data):
        #     if "utage_info" in song_data:
        #         try:
        #             music = MaiMusic.model_validate(song_data)
        #             utage_song_count += 1
                    
        #             print(f"\n[{utage_song_count}] 宴谱ID: {music.basic_info.id}")
        #             print(f"    标题: {music.basic_info.title}")
        #             print(f"    艺术家: {music.basic_info.artist}")
        #             print(f"    流派: {music.basic_info.genre}")
        #             print(f"    BPM: {music.basic_info.bpm}")
        #             print(f"    版本: {music.basic_info.version.text} (ID: {music.basic_info.version.id})")
                    
        #             if music.is_utage():
        #                 print(f"    ✅ 宴谱")
        #                 if music.utage_info:
        #                     print(f"    宴等级: {music.utage_info.level}")
        #                     print(f"    类型: {music.utage_info.type}")
        #                     print(f"    谱师骚话: {music.utage_info.commit}")
        #                     print(f"    是否Buddy: {music.utage_info.is_buddy}")
        #                     print(f"    玩家数: {music.utage_info.player_count}")
                        
        #                 if music.utage_charts:
        #                     chart_keys = list(music.utage_charts.keys())
        #                     print(f"    谱面键: {chart_keys}")
                            
        #                     # 测试属性访问
        #                     if "left" in chart_keys:
        #                         left = music.utage_charts.left
        #                         print(f"    LEFT notes: total={left.total}, tap={left.tap}, hold={left.hold}, slide={left.slide}, touch={left.touch}, break={left.break_note}")
                            
        #                     if "right" in chart_keys:
        #                         right = music.utage_charts.right
        #                         print(f"    RIGHT notes: total={right.total}, tap={right.tap}, hold={right.hold}, slide={right.slide}, touch={right.touch}, break={right.break_note}")
                            
        #                     if "single" in chart_keys:
        #                         single = music.utage_charts.single
        #                         print(f"    SINGLE notes: total={single.total}, tap={single.tap}, hold={single.hold}, slide={single.slide}, touch={single.touch}, break={single.break_note}")
                        
        #                 # 只测试前3首宴谱
        #                 if utage_song_count >= 3:
        #                     break
        #             else:
        #                 print(f"    ⚠️  不是宴谱（数据异常）")
                
        #         except Exception as e:
        #             print(f"\n[{utage_song_count+1}] ❌ 宴谱实例化失败: {e}")
        #             import traceback
        #             traceback.print_exc()
        #             break
        
        # # 统计信息
        # print("\n" + "=" * 60)
        # print("测试总结")
        # print("=" * 60)
        # print(f"✅ 成功实例化普通歌曲: {normal_song_count}/5")
        # print(f"✅ 成功实例化宴谱: {utage_song_count}/3")
        # print(f"📊 总歌曲数: {len(data)}")
        
        # # 测试属性访问和字典访问的兼容性
        # print("\n" + "-" * 60)
        # print("测试属性访问和字典访问兼容性")
        # print("-" * 60)
        
        # # 找一个有 BASIC 的普通歌曲
        # for song_data in data:
        #     if "charts" in song_data and "BASIC" in song_data.get("charts", {}):
        #         music = MaiMusic.model_validate(song_data)
        #         print(f"\n测试歌曲: {music.basic_info.title}")
                
        #         if music.charts is None:
        #             print("  ⚠️  charts 为 None，跳过测试")
        #             break
                
        #         # 属性访问
        #         basic_attr = music.charts.BASIC
        #         print(f"  属性访问 music.charts.BASIC.level = {basic_attr.level}")
                
        #         # 字典访问
        #         basic_dict = music.charts["BASIC"]
        #         print(f"  字典访问 music.charts['BASIC'].level = {basic_dict.level}")
                
        #         # 验证两者相等
        #         assert basic_attr.level == basic_dict.level, "属性访问和字典访问结果不一致"
        #         print(f"  ✅ 属性访问和字典访问结果一致")
                
        #         break
        
        # # 找一个有 left/right 的宴谱
        # for song_data in data:
        #     if "utage_charts" in song_data:
        #         utage_charts = song_data.get("utage_charts", {})
        #         if "left" in utage_charts and "right" in utage_charts:
        #             music = MaiMusic.model_validate(song_data)
        #             print(f"\n测试宴谱: {music.basic_info.title}")
                    
        #             if music.utage_charts is None:
        #                 print("  ⚠️  utage_charts 为 None，跳过测试")
        #                 break
                    
        #             # 属性访问
        #             left_attr = music.utage_charts.left
        #             print(f"  属性访问 music.utage_charts.left.total = {left_attr.total}")
                    
        #             # 字典访问
        #             left_dict = music.utage_charts["left"]
        #             print(f"  字典访问 music.utage_charts['left'].total = {left_dict.total}")
                    
        #             # 验证两者相等
        #             assert left_attr.total == left_dict.total, "属性访问和字典访问结果不一致"
        #             print(f"  ✅ 属性访问和字典访问结果一致")
                    
        #             break
        
        # print("\n" + "=" * 60)
        # print("✅ 所有测试完成！")
        # print("=" * 60)

