import asyncio
import random

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from proxy_bot.constants.load_constants import Constant
from proxy_bot.imports import bot
from proxy_bot.settings import settings


async def check_member_user(user_id: int):
    status = await bot.get_chat_member(chat_id=settings.CHAT_SUB_ID, user_id=user_id)
    if status.status == 'left':
        return False
    return True


def countries_dict(code: str):
    countries = {'ru': '🇷🇺 Россия',
                 'ca': '🇨🇦 Канада',
                 'us': '🇺🇸 США',
                 'de': '🇩🇪 Германия',
                 'gb': '🇬🇧 Великобритания',
                 'nl': '🇳🇱 Нидерланды',
                 'es': '🇪🇸 Испания',
                 'it': '🇮🇹 Италия',
                 'id': '🇮🇩 Индонезия',
                 'fr': '🇫🇷 Франция',
                 'ch': '🇨🇭 Швейцария',
                 'pt': '🇵🇹 Португалия',
                 'ua': '🇺🇦 Украина',
                 'kz': '🇰🇿 Казахстан',
                 'cn': '🇨🇳 Китай',
                 'pl': '🇵🇱 Польша',
                 'in': '🇮🇳 Индия',
                 'jp': '🇯🇵 Япония',
                 'ab': 'Абхазия',
                 'ad': '🇦🇩 Андорра',
                 'au': '🇦🇺 Австралия',
                 'at': '🇦🇹 Австрия',
                 'az': '🇦🇿 Азербайджан',
                 'al': '🇦🇱 Албания',
                 'dz': '🇩🇿 Алжир',
                 'ar': '🇦🇷 Аргентина',
                 'am': '🇦🇲 Армения',
                 'bd': '🇧🇩 Бангладеш',
                 'by': '🇧🇾 Беларусь',
                 'be': '🇧🇪 Бельгия',
                 'bg': '🇧🇬 Болгария',
                 'bo': '🇧🇴 Боливия',
                 'ba': '🇧🇦 Босния и Герцеговина',
                 'br': '🇧🇷 Бразилия',
                 'bs': '🇧🇸 Багамские острова',
                 'bh': '🇧🇭 Бахрейн',
                 'mg': '🇲🇬 Мадагаскар',
                 'hu': '🇭🇺 Венгрия',
                 've': '🇻🇪 Венесуэла',
                 'vn': '🇻🇳 Вьетнам',
                 'hk': '🇭🇰 Гонконг',
                 'gr': '🇬🇷 Греция',
                 'ge': '🇬🇪 Грузия',
                 'dk': '🇩🇰 Дания',
                 'eg': '🇪🇬 Египет',
                 'zm': '🇿🇲 Замбия',
                 'il': '🇮🇱 Израиль',
                 'jo': '🇯🇴 Иордания',
                 'iq': '🇮🇶 Ирак',
                 'ir': '🇮🇷 Иран',
                 'ie': '🇮🇪 Ирландия',
                 'is': '🇮🇸 Исландия',
                 'kh': '🇰🇭 Камбоджа',
                 'cm': '🇨🇲 Камерун',
                 'gt': 'Гватемала',
                 'qa': '🇶🇦 Катар',
                 'ke': '🇰🇪 Кения',
                 'cy': '🇨🇾 Кипр',
                 'co': '🇨🇴 Колумбия',
                 'kr': '🇰🇷 Корея',
                 'cr': '🇨🇷 Коста-Рика',
                 'ci': "🇨🇮 Кот-д'Ивуар",
                 'cu': '🇨🇺 Куба',
                 'kg': '🇰🇬 Кыргызстан',
                 'lv': '🇱🇻 Латвия',
                 'lr': '🇱🇷 Либерия',
                 'lb': '🇱🇧 Ливан',
                 'ly': '🇱🇾 Ливия',
                 'lt': '🇱🇹 Литва',
                 'lu': '🇱🇺 Люксембург',
                 'my': '🇲🇾 Малайзия',
                 'mv': '🇲🇻 Мальдивы',
                 'mt': '🇲🇹 Мальта',
                 'ma': '🇲🇦 Марокко',
                 'mx': '🇲🇽 Мексика',
                 'md': '🇲🇩 Молдова',
                 'mc': '🇲🇨 Монако',
                 'mn': '🇲🇳 Монголия',
                 'mk': '🇲🇰 Македония',
                 'np': '🇳🇵 Непал',
                 'nz': '🇳🇿 Новая Зеландия',
                 'no': '🇳🇴 Норвегия',
                 'ae': '🇦🇪 Объединённые Арабские Эмираты',
                 'pk': '🇵🇰 Пакистан',
                 'py': '🇵🇾 Парагвай',
                 'pe': '🇵🇪 Перу',
                 'ro': '🇷🇴 Румыния',
                 'sa': '🇸🇦 Саудовская Аравия',
                 'sc': '🇸🇨 Сейшелы',
                 'rs': '🇷🇸 Сербия',
                 'sg': '🇸🇬 Сингапур',
                 'sk': '🇸🇰 Словакия',
                 'si': '🇸🇮 Словения',
                 'tj': '🇹🇯 Таджикистан',
                 'tw': '🇹🇼 Тайвань',
                 'th': '🇹🇭 Тайланд',
                 'tz': '🇹🇿 Танзания',
                 'tn': '🇹🇳 Тунис',
                 'tm': '🇹🇲 Туркменистан',
                 'tr': '🇹🇷 Турция',
                 'uz': '🇺🇿 Узбекистан',
                 'uy': '🇺🇾 Уругвай',
                 'ph': '🇵🇭 Филиппины',
                 'fi': '🇫🇮 Финляндия',
                 'hr': '🇭🇷 Хорватия',
                 'me': '🇲🇪 Черногория',
                 'cz': '🇨🇿 Чехия',
                 'cl': '🇨🇱 Чили',
                 'se': '🇸🇪 Швеция',
                 'lk': '🇱🇰 Шри-Ланка',
                 'ee': '🇪🇪 Эстония',
                 'et': '🇪🇹 Эфиопия',
                 'za': '🇿🇦 Южная Африка',
                 'sd': '🇸🇩 Южного Судана',
                 'jm': '🇯🇲 Ямайка'}
    name = countries.get(code, None)
    if name is not None:
        return name


class Replacer:
    replacements = {
        'а': 'a', 'б': 'б', 'в': 'в', 'г': 'г', 'д': 'д',
        'е': 'e', 'ё': 'ё', 'ж': 'ж', 'з': 'з', 'и': 'и',
        'й': 'й', 'к': 'k', 'л': 'л', 'м': 'м', 'н': 'н',
        'о': 'o', 'п': 'n', 'р': 'p', 'с': 'c', 'т': 'т',
        'у': 'y', 'ф': 'ɸ', 'х': 'x', 'ц': 'ц', 'ч': 'ч',
        'ш': 'ш', 'щ': 'щ', 'ы': 'ы', 'э': 'э', 'ю': 'ю',
        'я': 'я',
        'А': 'A', 'Б': 'Б', 'В': 'B', 'Г': 'Г',
        'Д': 'Д', 'Е': 'E', 'Ё': 'Ë', 'Ж': 'Ж', 'З': '3',
        'И': 'И', 'Й': 'Й', 'К': 'K', 'Л': 'Λ', 'М': 'M',
        'Н': 'H', 'О': 'O', 'П': 'Π', 'Р': 'P', 'С': 'C',
        'Т': 'T', 'У': 'Y', 'Ф': 'Ф', 'Х': 'X', 'Ц': 'Ц',
        'Ч': 'Ч', 'Ш': 'Ш', 'Щ': 'Щ', 'Ы': 'Ꙑ', 'Э': 'Э',
        'Ю': 'Ю', 'Я': 'Я',
        'a': 'а', 'b': 'b', 'c': 'с', 'd': 'd', 'e': 'е',
        'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j',
        'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'о',
        'p': 'р', 'q': 'q', 'r': 'r', 's': 's', 't': 't',
        'u': 'u', 'v': 'v', 'w': 'w', 'x': 'х', 'y': 'у',
        'z': 'z',
        'A': 'А', 'B': 'В', 'C': 'С', 'D': 'D', 'E': 'Е',
        'F': 'F', 'G': 'G', 'H': 'Н', 'I': 'I', 'J': 'J',
        'K': 'К', 'L': 'L', 'M': 'М', 'N': 'N', 'O': 'О',
        'P': 'Р', 'Q': 'Ǫ', 'R': 'R', 'S': 'S', 'T': 'Т',
        'U': 'U', 'V': 'V', 'W': 'W', 'X': 'Х', 'Y': 'У',
        'Z': 'Z'
    }

    @staticmethod
    def replace_similar_letters_randomly(text, replacement_probability=0.5):
        if text is None:
            return "Введите текст!!!"
        text_list = list(text)
        for i, char in enumerate(text_list):
            if char in Replacer.replacements and random.random() < replacement_probability:
                text_list[i] = Replacer.replacements[char]

        return ''.join(text_list)


def pagination(callback_data: str, back_page: str):
    from proxy_bot.constants.msg_constants import ShortButton

    if ':' in callback_data:
        page = int(callback_data.split(':')[1])
        clean_callback_data = callback_data.split(':')[0]
    else:
        page = 0
        clean_callback_data = callback_data
    keyboard = InlineKeyboardBuilder()
    default_button = InlineKeyboardButton(text='...', callback_data='None')
    pages = len(Constant.COUNTRIES_CODES) // 15
    if page < 0:
        page = pages
    if page == pages + 1:
        page = 0
    if page <= pages:
        for code in Constant.COUNTRIES_CODES[15 * page: 15 * page + 15]:
            button = InlineKeyboardButton(text=f'{countries_dict(code)}', callback_data=f'country:{code}')
            keyboard.add(button)
        if not len(Constant.COUNTRIES_CODES[15 * page: 15 * page + 15]) // 15:
            keyboard.add(default_button)
    previous = InlineKeyboardButton(text='<<', callback_data=f'{clean_callback_data}:{page - 1}')
    counter = InlineKeyboardButton(text=f'{page + 1}/{pages + 1}', callback_data='None')
    next_b = InlineKeyboardButton(text='>>', callback_data=f'{clean_callback_data}:{page + 1}')
    back_button = InlineKeyboardButton(text=ShortButton.BACK, callback_data=f'{back_page}')
    keyboard.add(previous, counter, next_b)
    keyboard.add(back_button)
    return keyboard.adjust(3).as_markup()




if __name__ == '__main__':
    asyncio.run(check_member_user(123))
