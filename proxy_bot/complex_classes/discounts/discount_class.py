from aiogram.types import Message

from proxy_bot.complex_classes.discounts.exceptions import (NotDiscountTextError,
                                                            DiscountNotInBaseError,
                                                            UserHaveDiscountError,
                                                            DiscountWasActivatedError,
                                                            NotActivatesError)
from proxy_bot.db.requests_db import DiscountORM, UserORM


class ActivateDiscount:
    def __init__(self, event: Message):
        self.discount_name = event.text if event.text else NotDiscountTextError()
        self.discount_for_user = None
        self._discounts = DiscountORM()
        self._user_orm = UserORM(event)

    async def _check_discount_in_base(self):
        discount_in_base = await self._discounts.get_discounts(self.discount_name)
        if discount_in_base is None:
            raise DiscountNotInBaseError()
        if discount_in_base.activates == 0:
            raise NotActivatesError()
        await self._discounts.change_discount_count(self.discount_name)
        self.discount_for_user = discount_in_base.discount

    async def _check_discount_from_user(self):
        async with self._user_orm.session() as session:
            user = await self._user_orm.is_exist_user(session)
            if user.discount is not None:
                raise UserHaveDiscountError(user.discount)
            if user.activated_list is not None:
                if self.discount_name in user.activated_list:
                    raise DiscountWasActivatedError()

    async def activate(self):
        await self._check_discount_in_base()
        await self._check_discount_from_user()
        await self._user_orm.save_discount(self.discount_for_user, self.discount_name)
        return self.discount_for_user
