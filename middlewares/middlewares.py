import datetime
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, CallbackQuery
from database import requests1 as db

class Changelogs(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any],
    ) -> Any:
        callback: Update = data.get('event_update')
        if callback.callback_query.data == 'Показать':
            filters = await db.select_filters(callback.callback_query.from_user.id)
            logs_count = await db.manage_filter_logs(callback.callback_query.from_user.id)
            if logs_count < 5:
                await db.add_filter_log(callback.callback_query.from_user.id, text = filters[0][0], salary=filters[0][1], city=filters[0][2],
                                        schedule=filters[0][3], experience=filters[0][4], prof_role=filters[0][5],
                                        test=bool(filters[0][6]), time=datetime.datetime.now())
                return await handler(event, data)
            else:
                await db.change_logs(callback.callback_query.from_user.id, text = filters[0][0], salary=filters[0][1], city=filters[0][2],
                                     schedule=filters[0][3], experience=filters[0][4], prof_role=filters[0][5],
                                     test=bool(filters[0][6]), time=datetime.datetime.now())
                return await handler(event, data)
        return await handler(event, data)



