import base64
import re
import secrets
from datetime import datetime, timedelta
from uuid import uuid4

from nonebot import logger, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Depends
from nonebot.rule import to_me
from nonebot_plugin_orm import async_scoped_session
from sqlalchemy import exists, select, update
from sqlalchemy.exc import SQLAlchemyError

from src.libraries.models.enums import BindType
from src.libraries.models.bind import BindToken
from src.dependencies.deps import get_user
from src.libraries.models.user import User, UserAuth


from .rule import check_token_usage

BindUserRequestCommand = on_command("bind_user_request", rule=to_me(), block=True)
BindUserConfirmCommand = on_command("bind_user_confirm", rule=to_me(), block=True)
BindUserFinalizeCommand = on_command("bind_user_finalize", rule=to_me(), block=True)


def validate_handshake_token(token: str) -> bool:
    """
    验证握手令牌格式是否正确。

    :param token: 待验证的令牌
    :return: 如果令牌格式正确（10位大写字母和数字2-7），返回 True；否则返回 False
    """
    return bool(re.fullmatch(r"[A-Z2-7]{10}", token))


async def get_confirm_token(args: Message = CommandArg()) -> str | None:
    """
    获取并验证确认命令中的握手令牌参数。

    :param args: 命令参数
    :return: 有效的令牌字符串，如果无效直接结束当前事件处理
    """
    if (token := args.extract_plain_text().strip()) and validate_handshake_token(token):
        return token
    await BindUserConfirmCommand.finish(
        "请提供有效的握手令牌（10位大写字母和数字2-7组成）"
    )
    return None


async def get_finalize_token(args: Message = CommandArg()) -> str | None:
    """
    获取并验证完成绑定命令中的握手令牌参数。

    :param args: 命令参数
    :return: 有效的令牌字符串，如果无效直接结束当前事件处理
    """
    if (token := args.extract_plain_text().strip()) and validate_handshake_token(token):
        return token
    await BindUserFinalizeCommand.finish(
        "请提供有效的握手令牌（10位大写字母和数字2-7组成）"
    )
    return None


def generate_random_token() -> str:
    """
    生成一个随机的握手令牌，十位大写字母和数字2-7组成。

    :return: 生成的握手令牌
    :rtype: str
    """
    return base64.b32encode(secrets.token_bytes(7)).decode()[:10]


@BindUserRequestCommand.handle()
async def _(session: async_scoped_session, user: User = Depends(get_user)):
    """
    处理用户绑定请求指令（第一步）。

    主账号发起绑定请求，生成一个有效期的请求令牌。
    用户需将此令牌发送给希望绑定的子账号。

    :param session: 数据库会话
    :param user: 当前发送指令的用户（主账号）
    """
    # 用户的主账号发起绑定请求触发的指令
    if not await check_token_usage(session, user):
        await BindUserRequestCommand.finish("您在过去24小时内生成的绑定令牌数量已达到上限（8个）。")

    now = datetime.now()
    expires = now + timedelta(minutes=5)
    bind_token = None
    for _ in range(5):
        token_str = generate_random_token()
        existing_token = await session.scalar(
            select(BindToken)
            .where(BindToken.token == token_str)
            .where(BindToken.expires_at > now)
        )
        if existing_token:
            logger.warning(
                "生成绑定令牌时发生冲突，尝试重新生成。冲突令牌: %s", token_str
            )
            continue
        bind_token = BindToken(
            id=uuid4(),
            token=token_str,
            main_user_id=user.id,
            type=BindType.REQUEST,
            created_at=now,
            expires_at=expires,
            sub_user_id=None,
        )
        session.add(bind_token)
        break
    if bind_token:
        try:
            await session.commit()
            await session.refresh(bind_token)
            await BindUserRequestCommand.finish(
                f"已生成绑定令牌: {bind_token.token}\n请在5分钟内完成绑定。"
            )
        except SQLAlchemyError as e:
            import traceback
            logger.error(traceback.format_exc())
            logger.error("生成绑定令牌时发生数据库错误: %s", e)
            await BindUserRequestCommand.finish("生成绑定令牌失败，请稍后重试。")
    else:
        logger.error("生成绑定令牌失败，尝试多次后仍未成功。")
        await BindUserRequestCommand.finish("生成绑定令牌失败，请稍后重试。")


@BindUserConfirmCommand.handle()
async def _(
    session: async_scoped_session,
    user: User = Depends(get_user),
    token: str = Depends(get_confirm_token),
):
    """
    处理用户绑定确认指令（第二步）。

    子账号使用主账号生成的请求令牌进行确认。
    验证成功后，生成一个确认令牌，子账号需将此令牌发回给主账号进行最终确认。

    :param session: 数据库会话
    :param user: 当前发送指令的用户（子账号）
    :param token: 从命令参数解析的请求令牌
    """
    # 用户的子账号响应绑定请求触发的指令
    bind_token = await session.scalar(
        select(BindToken)
        .where(BindToken.token == token)
        .where(BindToken.type == BindType.REQUEST)
        .where(BindToken.expires_at > datetime.now())
    )
    if bind_token is None:
        await BindUserConfirmCommand.finish("无效或已过期的绑定令牌。")
    now = datetime.now()
    expires = now + timedelta(minutes=5)
    confirm_bind_token = None
    for _ in range(5):
        confirm_token = generate_random_token()
        existing_token = await session.scalar(
            select(BindToken)
            .where(BindToken.token == confirm_token)
            .where(BindToken.expires_at > now)
        )
        if existing_token:
            logger.warning(
                "生成确认令牌时发生冲突，尝试重新生成。冲突令牌: %s", confirm_token
            )
            continue
        confirm_bind_token = BindToken(
            id=uuid4(),
            token=confirm_token,
            main_user_id=bind_token.main_user_id,
            type=BindType.CONFIRM,
            created_at=now,
            expires_at=expires,
            sub_user_id=user.id,
        )
        session.add(confirm_bind_token)
        break
    if confirm_bind_token:
        try:
            await session.commit()
            await session.refresh(confirm_bind_token)
            await BindUserConfirmCommand.finish(
                f"绑定请求已确认。请将以下握手令牌提供给主账号以完成绑定: {confirm_bind_token.token}"
            )
        except SQLAlchemyError as e:
            logger.error("生成确认令牌时发生数据库错误: %s", e)
            await BindUserConfirmCommand.finish("生成确认令牌失败，请稍后重试。")

    else:
        logger.error("生成确认令牌失败，尝试多次后仍未成功。")
        await BindUserConfirmCommand.finish("生成确认令牌失败，请稍后重试。")


@BindUserFinalizeCommand.handle()
async def _(
    session: async_scoped_session,
    user: User = Depends(get_user),
    token: str = Depends(get_finalize_token),
):
    """
    处理用户绑定最终确认指令（第三步）。

    主账号使用子账号生成的确认令牌完成绑定。
    验证成功后，将子账号的所有认证信息（UserAuth）迁移至主账号下。

    :param session: 数据库会话
    :param user: 当前发送指令的用户（主账号）
    :param token: 从命令参数解析的确认令牌
    """
    # 1. 查找确认token
    bind_token = await session.scalar(
        select(BindToken)
        .where(BindToken.token == token)
        .where(BindToken.type == BindType.CONFIRM)
        .where(BindToken.main_user_id == user.id)
        .where(BindToken.expires_at > datetime.now())
    )
    if not bind_token:
        logger.warning(
            "尝试使用无效或过期的确认令牌完成绑定，用户ID: %s, 令牌: %s",
            user.id,
            token,
        )
        await BindUserFinalizeCommand.finish("无效或已过期的确认令牌。")
    # 2. 迁移sub_user_id下所有UserAuth到main_user_id
    sub_user_id = bind_token.sub_user_id
    if not sub_user_id:
        logger.error(
            "绑定信息不完整，无法完成绑定。主账号ID: %s, 确认令牌: %s", user.id, token
        )
        await BindUserFinalizeCommand.finish("绑定信息不完整，无法完成绑定。")
    # 使用数据库批量迁移，避免全部加载到内存
    # 这里的逻辑是将子账号关联的 UserAuth 记录的 user_id 更新为主账号的 ID
    # 但需要避免主账号下已经存在相同的认证信息（type, external_id 相同），否则会违反唯一约束

    # 1. 先查出子账号拥有的所有认证记录
    sub_auths = await session.scalars(
        select(UserAuth).where(UserAuth.user_id == sub_user_id)
    )
    
    for auth in sub_auths:
        # 2. 检查主账号是否已经有同类型的认证
        exists_stmt = select(UserAuth).where(
            UserAuth.user_id == user.id,
            UserAuth.type == auth.type,
            UserAuth.external_id == auth.external_id
        )
        already_has = await session.scalar(exists_stmt)
        
        if not already_has:
            # 3. 只有不存在时才转移归属权
            auth.ext = {"original_id": str(auth.user_id)}
            auth.user_id = user.id
        else:
            # 4. 如果主账号已经有了，说明子账号的这条记录是冗余的，直接删除
            await session.delete(auth)
    
    await session.commit()
    await BindUserFinalizeCommand.finish("绑定完成，所有认证信息已合并到主账号。")
