PHRASES = {
    # General
    "auto_reply": "😊 小简不知道哟~要不你试试命令吧！输入 /start 查看可用命令~",
    "processing_wait": "⏰ 小简正在处理你的上一条消息呢~请稍等片刻",
    # Start menu
    "menu_main": (
        "👋 欢迎使用机器人服务！请选择功能：\n"
        "ℹ️ /info - 查看你的信息(包括身份)\n"
        "💰 /sign - 签到领积分(8000token)\n"
        "🤖 /chat - 开始AI智能聊天\n"
        "✨ /role - 获取角色扮演脚本\n"
        "🔥 /creat_my_role - 创建自己的角色\n"
        "🌈 /setu - 获取随机图片\n"
        "🎉 /rank - 查看角色排行榜\n"
        "👑 /my_role - 管理你的角色\n"
        "🤔 /chat_to_admin - 联系管理员\n\n"
        "直接输入命令即可使用功能"),
    # Info command
    "info_reply": (
        "ℹ️ 你的信息:\n"
        "⭐ 昵称: [nickname]\n"
        "💳︎ ID: [user_id]\n"
        "👑 身份: [role]\n"
        "✉️ 邮箱: [email]\n"
        "🧬 签名: [signature]\n"
        "💰 剩余token: [tokens]"),
    # Sign
    "sign_success": "💰 签到成功！获得[reward]token",
    "sign_repeat": "⚠️ 你今天已经签到过了哦~明天再来吧",
    # Error generic
    "error_generic": "❌ [msg]",
}

def t(key: str, **kwargs) -> str:
    """Return phrase by key and replace placeholder with kwargs."""
    phrase = PHRASES.get(key, "")
    for k, v in kwargs.items():
        phrase = phrase.replace(f"[{k}]", str(v))
    return phrase