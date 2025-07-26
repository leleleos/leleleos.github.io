"""Bot main module (patched).
This is a trimmed version of the original code that focuses on the bug-fix for the
`/creat_my_role` flow and introduces a phrase library so that all replies are
centralised in one place (`bot_phrases.py`).  The rest of the implementation is
identical to the original and has been omitted for brevity – replace the
`# ... existing code ...` blocks with the corresponding parts from your current
source file.
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp

from bot_phrases import t, PHRASES

# ... existing code ... (imports, Config class, Database class definitions)

class Database:
    # ... existing code ...
    def get_chat_context(self, user_id: int, conversation_id: int,
                         limit: Optional[int] = None,
                         ascending: bool = False) -> List[Dict]:
        """Fetch chat context.

        Parameters
        ----------
        user_id : int
            User id.
        conversation_id : int
            Conversation id.
        limit : Optional[int]
            Maximum number of rows to return.  If *None* all rows are returned.
        ascending : bool
            If *True* results are ordered ASC (oldest → newest), otherwise DESC.
        """
        cursor = self.conn.cursor()
        order = "ASC" if ascending else "DESC"
        sql = (
            "SELECT role, content FROM chat_context "
            "WHERE user_id = ? AND conversation_id = ? "
            f"ORDER BY timestamp {order}"
        )
        params: List = [int(user_id), int(conversation_id)]
        if limit is not None:
            sql += " LIMIT ?"
            params.append(int(limit))
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    # ... existing code ...

class MessageHandler:
    # ... existing code ...

    async def handle_start_command(self, sender_id: int, token: str) -> None:
        """处理 /start 命令 (now uses phrase library)."""
        self.db.set_chat_status(sender_id, menu="main")
        await self.send_message(sender_id, t("menu_main"), token)

    # ------------------------------------------------------------------
    # Bug-fix: role creation flow
    # ------------------------------------------------------------------
    async def handle_create_role_answer(self, sender_id: int, token: str, answer: str) -> None:
        """Patched version that no longer crashes when multiple users create roles
        concurrently.  We fetch the full context in ASC order so that the list
        of questions is always complete and in the original order regardless of
        how many answers have already been stored.
        """
        chat_status = self.db.get_chat_status(sender_id)
        if not chat_status["conversation_id"]:
            await self.send_message(sender_id, t("error_generic", msg="创建角色流程出错，请重新开始"), token)
            return

        # Fetch **all** question / answer messages for this conversation in the
        # order they were inserted so that indices line up correctly.
        context = self.db.get_chat_context(sender_id,
                                           chat_status["conversation_id"],
                                           limit=None,
                                           ascending=True)

        # Extract questions and answers preserving their numeric suffix.
        questions = {}
        for c in context:
            role = c["role"]
            if role.startswith("question_"):
                idx = int(role.split("_")[1])
                questions[idx] = c["content"]
        answers = [c["content"] for c in context if c["role"] == "answer"]

        current_step = len(answers)

        # Guard against out-of-sync indices.
        if current_step >= len(questions):
            await self.send_message(sender_id,
                                    t("error_generic", msg="问题索引溢出，请重新开始创建流程"),
                                    token)
            return

        # Save current answer.
        self.db.save_chat_context(sender_id,
                                  chat_status["conversation_id"],
                                  "answer", answer)

        # Ask next question.
        next_question = questions[current_step]
        await self.send_message(sender_id, next_question, token)

    # ------------------------------------------------------------------
    # Example of phrase usage in another command
    # ------------------------------------------------------------------
    async def handle_sign_command(self, sender_id: int, token: str) -> None:
        if self.db.can_sign_today(sender_id):
            self.db.update_user_tokens(sender_id, 8000)
            await self.send_message(sender_id, t("sign_success", reward=8000), token)
        else:
            await self.send_message(sender_id, t("sign_repeat"), token)

    # ... existing code ...

    async def handle_chat_message(self, msg_data: Dict, token: str) -> None:
        sender_id = int(msg_data['sendId'])
        content = msg_data['content']
        # ... existing code ...
        # When busy processing previous message
            if chat_status.get("is_processing", False):
                await self.send_message(sender_id, t("processing_wait"), token)
                return
        # ... existing code ...
        # Fallback auto reply
        else:
            await self.send_message(sender_id, PHRASES["auto_reply"], token)
            # ... existing code ...

    # ... existing code ...

# ----------------------------------------------------------------------
# Entry point (unchanged)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        handler = MessageHandler()
        asyncio.run(handler.run())
    except KeyboardInterrupt:
        logging.info("\n👋 程序已退出")
    except Exception as exc:
        logging.error(f"❌ 全局异常: {exc}")