import sys
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# try:
from src.libraries.database.models import (
    Abstract,
    Alias,
    AliasApply,
    AliasVote,
    UserConfig,
)
from src.libraries.enums import AliasStatus

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

async def main():
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    database = client.xray_mai_bot_v3_tests
    # Initialize Beanie with the Document classes
    await init_beanie(database=database, document_models=[  # type: ignore
        Abstract,
        Alias,
        AliasApply,
        AliasVote,
        UserConfig,
    ])
    print("Success: Database initialized.")

    # Test instantiation
    # Create
    # a = Abstract(
    #     music_id=1,
    #     user_id=100,
    #     nickname="Test",
    #     file_key="key",
    # )
    # await a.insert()
    # print(f"Create: {a}")

    # Read
    fetched = await Abstract.find_one(Abstract.music_id == 1)
    print(f"Read: {fetched}")

    # # Update
    # if fetched:
    #     fetched.nickname = "Updated Nickname"
    #     await fetched.save()
    #     print(f"Update: {fetched}")

    # # Delete
    # if fetched:
    #     await fetched.delete()
    #     print("Delete: Success")

    # al = Alias(
    #     music_id=1,
    #     alias="Song",
    #     title="Title",
    #     status=1,
    # )
    # print("Success: Alias instantiated.")

    # aa = AliasApply(
    #     id=1,
    #     music_id=1,
    #     alias="Song",
    #     user_id=100,
    #     group_id=200,
    #     status=AliasStatus.SCORING,
    # )
    # print("Success: AliasApply instantiated.")

    # av = AliasVote(
    #     id=1,
    #     user_id=100,
    #     group_id=200,
    #     score=1,
    # )
    # print("Success: AliasVote instantiated.")

    # uc = UserConfig(
    #     user_id=100,
    #     is_abstract=True,
    #     maimai_best_50_style="style1",
    #     chu_prober_mode="mode1",
    # )
    # print("Success: UserConfig instantiated.")

if __name__ == "__main__":
    asyncio.run(main())
