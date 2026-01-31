import hashlib
import shutil
from command.base import BaseCommand
import nonebot
from nonebot.log import logger
import pymongo
from pathlib import Path
import puremagic
from src.libraries.models import Abstract
from nonebot_plugin_orm import get_session
from src.server.mai_music_server import total_music
import asyncio
from sqlalchemy import select


class Command(BaseCommand):
    def handle(self, **options):
        asyncio.run(self.demo())

    async def demo(self):
        async with get_session() as session:
            stmt = select(Abstract.music_id).group_by(Abstract.music_id)
            result = await session.execute(stmt)
            users = result.scalars().all()
            music_id_list = [item for item in users]
            for m in total_music.get_normal_musics():
                if m.basic_info.id not in music_id_list:
                    print(m.basic_info)

    async def run_async(self):
        # 定义 MIME 类型到后缀的映射，涵盖更多真实类型
        MIME_TO_EXT = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/bmp": ".bmp",
        }


        cover_base_path = '/Users/Ekzykes/Project/xray_mai_bot_v2/src/static/maimaidx/abstract_cover/'
        client = pymongo.MongoClient(nonebot.get_driver().config.mongodb_conn_url)
        db = client['xray-mai-bot']
        abstract_collection = db['abstract']
        docs = abstract_collection.find()

        async with get_session() as session:
            for item in docs:
                music_id = item['music_id']
                for abs in item['abstract_data']:
                    user_id = abs['user_id']
                    nickname = abs['nickname']
                    file_name = abs['file_name']
                    cover_file = Path(cover_base_path + f"{file_name}.png")
                    bak_cover_file = Path('/Users/Ekzykes/Project/xray_mai_bot_v2/src/static/maimaidx/abstract_cover_bak/' + f"{file_name}.png")
                    if cover_file.exists():
                        try:
                            with open(cover_file, 'rb') as f:
                                content = f.read()
                            md5 = hashlib.md5(content).hexdigest()
                            # ./data/abstract_cover/12/34/md5.png
                            save_dir = Path(f"./data/")
                            save_dir.mkdir(parents=True, exist_ok=True)

                            exts = puremagic.magic_string(content[:2048])
                            real_ext = exts if isinstance(exts, str) else exts[0].mime_type
                            real_ext = MIME_TO_EXT.get(real_ext, real_ext)
                            # print(real_ext)

                            key = f"maimaidx/abstract_cover/{md5[:2]}/{md5[2:4]}/{md5}{real_ext}"
                            save_path = save_dir / key
                            save_path.parent.mkdir(exist_ok=True,parents=True)
                            # if not save_path.exists():
                            # shutil.copy(cover_file, save_path)
                            shutil.move(cover_file,bak_cover_file)
                            logger.info(f"已保存 {file_name} 到 {save_path}")

                            # ab = Abstract(
                            #     music_id=int(music_id),
                            #     user_id=str(user_id),
                            #     nickname=nickname,
                            #     file_key=str(key)
                            # )
                            # session.add(ab)

                        except Exception as e:
                            logger.error(f"处理 {file_name} 时出错: {e}")
                    else:
                        logger.info(f'歌曲ID：【{music_id}】-昵称：【{nickname}】-ID：【{user_id}】，文件名：【{file_name}】')
            # await session.commit()
