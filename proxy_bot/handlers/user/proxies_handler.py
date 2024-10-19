from typing import Union

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from proxy_bot.cache_class.wrapper_to_user import user_information
from proxy_bot.complex_classes.buy_proxy.exceptions import UserNotMoneyError, ProxyDeathError, NotEnoughProxyError, \
    NotProxyInBaseError, NoMoneySiteError, UserNotMoneyProxyLineError, NoPlanError
from proxy_bot.complex_classes.buy_proxy.proxyline import CreateOrder, CreatePurchase
from proxy_bot.complex_classes.buy_proxy.service import SortedProxy, ProxyShop, WorkedProxy
from proxy_bot.constants.load_constants import Constant
from proxy_bot.constants.msg_constants import MenuButton, MainProxyPage, ChooseWorkProxy, NotProxyMessage, \
    ChooseSortProxy, ChooseLenSortProxy, CheckingProxyText, ShortButton, ProxyLineNoPlan, MainPageProxyLine, \
    ChooseTypeProxy, ChoiceCountry, PreviewMessage, ProxyLineWork
from proxy_bot.custom_sender.send_class import SendUser, SendAdmins
from proxy_bot.db.requests_db import Proxies
from proxy_bot.imports import bot
from proxy_bot.settings import settings

proxy_router = Router()


@proxy_router.message(F.text == MenuButton.PROXIES, F.chat.type == 'private')
@proxy_router.callback_query(F.data == 'shop')
@user_information
async def proxy_page_1(event: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    await SendUser(MainProxyPage())(event)


@proxy_router.callback_query(F.data == 'working')
async def proxy_page_2(call: CallbackQuery):
    if len(Constant.PROXIES_WORK) == 0:
        await bot.answer_callback_query(callback_query_id=call.id, text=NotProxyMessage.text, show_alert=True)
        if not Constant.NO_PROXY_WORK:
            await SendAdmins().to_all_admins(NotProxyMessage.text_no_work_proxy)
            Constant.NO_PROXY_WORK = True
    else:
        await SendUser(ChooseWorkProxy())(call)


@proxy_router.callback_query(F.data == 'sorted_work')
async def proxy_page_3(call: CallbackQuery):
    if len(await Proxies("ProxySort").get_proxies()) == 0:
        await bot.answer_callback_query(callback_query_id=call.id, text=NotProxyMessage.text, show_alert=True)
        if not Constant.NO_PROXY_SORT:
            await SendAdmins().to_all_admins(NotProxyMessage.text_no_sort_proxy)
            Constant.NO_PROXY_SORT = True
    else:
        await SendUser(ChooseSortProxy())(call)


@proxy_router.callback_query(F.data.startswith("sort_country"))
async def proxy_page_3_1(call: CallbackQuery, state: FSMContext):
    country_code = call.data.split(":")[1]
    await state.update_data(country_code=country_code)
    await SendUser(ChooseLenSortProxy(country_code=country_code))(call)


@proxy_router.callback_query(F.data.startswith("sort_proxy"))
async def proxy_page_3_2(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    proxy_data = SortedProxy(int(call.data.split(":")[1]), data.get("country_code"))
    shop = ProxyShop(proxy_data, call.from_user.id)
    try:
        await SendUser(text=CheckingProxyText.text, buttons=ShortButton.BACK_SORT)(call)
        await shop.buy_proxy()
        await SendUser(text=shop.message)(call)
        await bot.send_document(chat_id=call.from_user.id, document=shop.file)
    except (UserNotMoneyError, ProxyDeathError, NotEnoughProxyError, NotProxyInBaseError) as e:
        await bot.answer_callback_query(text=e.text, callback_query_id=call.id, show_alert=True)
        if isinstance(e, ProxyDeathError) and not Constant.PROXY_WORK_DEATH:
            await SendUser(text=CheckingProxyText.broken)(call)
            await SendAdmins().to_all_admins(NotProxyMessage.sort_proxy_death)
            Constant.PROXY_SORT_DEATH = True


@proxy_router.callback_query(F.data.startswith("work_proxy"))
async def proxy_page_2_1(call: CallbackQuery):
    proxy_data = WorkedProxy(int(call.data.split(":")[1]))
    shop = ProxyShop(proxy_data, call.from_user.id)
    try:
        await SendUser(text=CheckingProxyText.text)(call)
        await shop.buy_proxy()
        await SendUser(text=shop.message)(call)
        await bot.send_document(chat_id=call.from_user.id, document=shop.file)
    except (UserNotMoneyError, ProxyDeathError, NotEnoughProxyError, NotProxyInBaseError) as e:
        await bot.answer_callback_query(text=e.text, callback_query_id=call.id, show_alert=True)
        if isinstance(e, ProxyDeathError) and not Constant.PROXY_WORK_DEATH:
            await SendUser(text=CheckingProxyText.broken)(call)
            await SendAdmins().to_all_admins(NotProxyMessage.work_proxy_death)
            Constant.PROXY_WORK_DEATH = True


@proxy_router.callback_query(F.data == 'scrolling')
async def shop_3(call: CallbackQuery, state: FSMContext):
    if not Constant.NO_PROXY_PROXYLINE:
        await state.clear()
        new_order = CreateOrder()
        await state.update_data(new_order=new_order)
        await SendUser(ChooseTypeProxy())(call)
    else:
        await bot.answer_callback_query(callback_query_id=call.id, text=ProxyLineNoPlan.for_not_proxy,
                                        show_alert=True)


@proxy_router.callback_query(F.data.startswith('ipv'))
async def chop_3_1(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_order: CreateOrder = data.get('new_order')
    if "ipv4" in call.data:
        ip_version = 4
        new_order.ip_version = ip_version
        message = MainPageProxyLine(callback_data=call.data, back_page="scrolling", ip_version=ip_version)
        text = message.text
        reply_markup = message.buttons
        try:
            await call.message.edit_text(text=text, reply_markup=reply_markup)
        except TelegramBadRequest:
            await call.message.edit_caption(caption=text, reply_markup=reply_markup)
    else:
        ip_version = 6
        new_order.ip_version = ip_version
        await SendUser(MainPageProxyLine(ip_version=ip_version))(call)
    await state.update_data(new_order=new_order)


@proxy_router.callback_query(F.data.startswith("country"))
async def get_country(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_order: CreateOrder = data.get('new_order')
    country = call.data.split(":")[1]
    new_order.country = country
    await state.update_data(new_order=new_order)
    await SendUser(ChoiceCountry(new_order=new_order))(call)


@proxy_router.callback_query(F.data.startswith("period"))
async def get_period(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_order: CreateOrder = data.get('new_order')
    period = call.data.split(":")[1]
    new_order.period = period
    shop = CreatePurchase(user_id=call.from_user.id, order=new_order)
    await state.update_data(shop=shop)
    try:
        await shop.show_preview()
        await SendUser(PreviewMessage(new_order=new_order,
                                      price=shop.price_with_comision,
                                      discount=shop.user_discount))(call)
    except NoMoneySiteError as e:
        await SendUser(text=e.text_user)(call)
        if not Constant.NO_PROXY_PROXYLINE:
            await SendAdmins().send_one_admin(admin_id=settings.ADMIN, text=e.text_admin, buttons=e.buttons)
            Constant.NO_PROXY_PROXYLINE = True

    except (UserNotMoneyProxyLineError, NoPlanError) as e:
        await SendUser(text=e.text)(call)


@proxy_router.callback_query(F.data == "buy_with_discount")
async def use_discount(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    shop: CreatePurchase = data.get("shop")
    shop.price_with_comision = shop.price_with_comision - shop.price_with_comision * shop.user_discount
    try:
        message_to_admins = await shop.create_order()
        await SendUser(text=shop.message)(call)
        await SendAdmins().to_all_admins(text=message_to_admins)
    except NoMoneySiteError as e:
        await SendUser(text=e.text_user)(call)
        if not Constant.NO_PROXY_PROXYLINE:
            await SendAdmins().send_one_admin(admin_id=settings.ADMIN, text=e.text_admin, buttons=e.buttons)
            Constant.NO_PROXY_PROXYLINE = True


@proxy_router.callback_query(F.data == "proxyline_work")
async def proxy_ok(call: CallbackQuery):
    Constant.NO_PROXY_PROXYLINE = False
    await SendUser(ProxyLineWork())(call)
