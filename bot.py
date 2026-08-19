import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

API_URL = "https://open.er-api.com/v6/latest/"

TRANSLATIONS = {
    "am": {
        "select_curr": "Լեզուն ընտրված է։ Ընտրիր հիմնական արժույթը:",
        "rate_title": "փոխարժեքն աշխարհի արժույթների նկատմամբ (Օնլայն):",
        "other_title": "--- Աշխարհի երկրներ (այբենական) ---",
        "error_format": "⚠️ **Խնդրում եմ նշել թե՛ գումարը, թե՛ արժույթը:**\nՕրինակ՝ `1000 AMD` կամ `100 USD`",
        "api_error": "⚠️ Չհաջողվեց կապվել փոխարժեքների սերվերի հետ։ Փորձեք փոքր ուշ:",
        "currencies": {
            "USD": ("🇺🇸", "ԱՄՆ դոլար"), "EUR": ("🇪🇺", "Եվրո"),
            "RUB": ("🇷🇺", "Ռուսական ռուբլի"), "GEL": ("🇬🇪", "Վրացական լարի"),
            "CNY": ("🇨🇳", "Չինական յուան"), "AMD": ("🇦🇲", "Հայկական դրամ")
        },
        "world": [
            ("AED", "🇦🇪", "ԱՄԷ դիրհամ"), ("ARS", "🇦🇷", "Արգենտինական պեսո"), ("AUD", "🇦🇺", "Ավստրալական դոլար"),
            ("AZN", "🇦🇿", "Ադրբեջանական մանաթ"), ("BGN", "🇧🇬", "Բուլղարական լև"), ("BRL", "🇧🇷", "Բրազիլական ռեալ"),
            ("CAD", "🇨🇦", "Կանադական դոլար"), ("CHF", "🇨🇭", "Շվեյցարական ֆրանկ"), ("CLP", "🇨🇱", "Չիլիական պեսո"),
            ("COP", "🇨🇴", "Կոլումբիական պեսո"), ("CZK", "🇨🇿", "Չեխական կրոն"), ("DKK", "🇩🇰", "Դանիական կրոն"),
            ("EGP", "🇪🇬", "Եգիպտական ֆունտ"), ("GBP", "🇬🇧", "Բրիտանական ֆունտ"), ("GHS", "🇬🇭", "Գանական սեդի"),
            ("HKD", "🇭🇰", "Հոնկոնգյան դոլար"), ("HUF", "🇭🇺", "Հունգարական ֆորինտ"), ("IDR", "🇮🇩", "Ինդոնեզական ռուփի"),
            ("ILS", "🇮🇱", "Իսրայելական շեքել"), ("INR", "🇮🇳", "Հնդկական ռուփի"), ("IQD", "🇮🇶", "Իրաքյան դինար"),
            ("ISK", "🇮🇸", "Իսլանդական կրոն"), ("JPY", "🇯🇵", "Ճապոնական իեն"), ("KES", "🇰🇪", "Քենիական շիլլինգ"),
            ("KGS", "🇰🇬", "Ղրղզական սոմ"), ("KRW", "🇰🇷", "Հարավկորեական վոն"), ("KWD", "🇰🇼", "Քուվեյթյան դինար"),
            ("KZT", "🇰🇿", "Ղազախական տենգե"), ("LBP", "🇱🇧", "Լիբանանյան ֆունտ"), ("MAD", "🇲🇦", "Մարոկկական դիրհամ"),
            ("MDL", "🇲🇩", "Մոլդովական լեյ"), ("MXN", "🇲🇽", "Մեքսիկական պեսո"), ("MYR", "🇲🇾", "Մալայզիական ռինգիտ"),
            ("NOK", "🇳🇴", "Նորվեգական կրոն"), ("NZD", "🇳🇿", "Նորզելանդական դոլար"), ("OMR", "🇴🇲", "Օմանական ռիալ"),
            ("PEN", "🇵🇪", "Պերուական սոլ"), ("PHP", "🇵🇭", "Ֆիլիպինյան պեսո"), ("PKR", "🇵🇰", "Պակիստանյան ռուփի"),
            ("PLN", "🇵🇱", "Լեհական զլոտի"), ("QAR", "🇶🇦", "Կատարական ռիալ"), ("RON", "🇷🇴", "Ռումինական լեյ"),
            ("RSD", "🇷🇸", "Սերբական դինար"), ("SAR", "🇸🇦", "Սաուդյան Արաբիայի ռիալ"), ("SEK", "🇸🇪", "Շվեդական կրոն"),
            ("SGD", "🇸🇬", "Սինգապուրյան դոլար"), ("THB", "🇹🇭", "Թայական բատ"), ("TJS", "🇹🇯", "Տաջիկական սոմոնի"),
            ("TMT", "🇹🇲", "Թուրքմենական մանաթ"), ("TND", "🇹🇳", "Թունիսյան դինար"), ("TRY", "🇹🇷", "Թուրքական լիրա"),
            ("TWD", "🇹🇼", "Նոր թայվանական դոլար"), ("UAH", "🇺🇦", "Ուկրաինական գրիվնա"), ("UGX", "🇺🇬", "Ուգանդական շիլլինգ"),
            ("UYU", "🇺🇾", "Ուրուգվայական պեսո"), ("UZS", "🇺🇿", "Ուզբեկական սոմ"), ("VND", "🇻🇳", "Վիետնամական դոնգ"),
            ("ZAR", "🇿🇦", "Հարավաֆրիկյան ռանդ"), ("ZMW", "🇿🇲", "Զամբիական կվաչա")
        ]
    },
    "ru": {
        "select_curr": "Язык выбран. Выберите основную валюту:",
        "rate_title": "курс по отношению к мировым валютам (Онлайн):",
        "other_title": "--- Страны мира (по алфавиту) ---",
        "error_format": "⚠️ **Пожалуйста, укажите сумму и валюту:**\nПример: `1000 AMD` или `100 USD`",
        "api_error": "⚠️ Не удалось связаться с сервером валют. Попробуйте позже.",
        "currencies": {
            "USD": ("🇺🇸", "Доллар США"), "EUR": ("🇪🇺", "Евро"),
            "RUB": ("🇷🇺", "Российский рубль"), "GEL": ("🇬🇪", "Грузинский лари"),
            "CNY": ("🇨🇳", "Китайский юань"), "AMD": ("🇦🇲", "Армянский драм")
        },
        "world": [
            ("AED", "🇦🇪", "Дирхам ОАЭ"), ("ARS", "🇦🇷", "Аргентинский песо"), ("AUD", "🇦🇺", "Австралийский доллар"),
            ("AZN", "🇦🇿", "Азербайджанский манат"), ("BGN", "🇧🇬", "Болгарский лев"), ("BRL", "🇧🇷", "Бразильский реал"),
            ("CAD", "🇨🇦", "Канадский доллар"), ("CHF", "🇨🇭", "Швейцарский франк"), ("CLP", "🇨🇱", "Чилийский песо"),
            ("COP", "🇨🇴", "Колумбийский песо"), ("CZK", "🇨🇿", "Чешская крона"), ("DKK", "🇩🇰", "Датская крона"),
            ("EGP", "🇪🇬", "Египетский фунт"), ("GBP", "🇬🇧", "Британский фунт стерлингов"), ("GHS", "🇬🇭", "Ганский седи"),
            ("HKD", "🇭🇰", "Гонконгский доллар"), ("HUF", "🇭🇺", "Венгерский форинт"), ("IDR", "🇮🇩", "Индонезийская рупия"),
            ("ILS", "🇮🇱", "Израильский шекель"), ("INR", "🇮🇳", "Индийская рупия"), ("IQD", "🇮🇶", "Иракский динар"),
            ("ISK", "🇮🇸", "Исландская крона"), ("JPY", "🇯🇵", "Японская иена"), ("KES", "🇰🇪", "Кенийский шиллинг"),
            ("KGS", "🇰🇬", "Киргизский сом"), ("KRW", "🇰🇷", "Южнокорейская вона"), ("KWD", "🇰🇼", "Кувейтский динар"),
            ("KZT", "🇰🇿", "Казахстанский тенге"), ("LBP", "🇱🇧", "Ливанский фунт"), ("MAD", "🇲🇦", "Марокканский дирхам"),
            ("MDL", "🇲🇩", "Молдавский лей"), ("MXN", "🇲🇽", "Мексиканский песо"), ("MYR", "🇲🇾", "Малайзийский ринггит"),
            ("NOK", "🇳🇴", "Норвежская крона"), ("NZD", "🇳🇿", "Новозеландский доллар"), ("OMR", "🇴🇲", "Оманский риал"),
            ("PEN", "🇵🇪", "Перуанский соль"), ("PHP", "🇵🇭", "Филиппинский песо"), ("PKR", "🇵🇰", "Пакистанская рупия"),
            ("PLN", "🇵🇱", "Польский злотый"), ("QAR", "🇶🇦", "Катарский риал"), ("RON", "🇷🇴", "Румынский лей"),
            ("RSD", "🇷🇸", "Сербский динар"), ("SAR", "🇸🇦", "Саудовский риял"), ("SEK", "🇸🇪", "Шведская крона"),
            ("SGD", "🇸🇬", "Сингапурский доллар"), ("THB", "🇹🇭", "Тайский бат"), ("TJS", "🇹🇯", "Таджикский сомони"),
            ("TMT", "🇹🇲", "Туркменский манат"), ("TND", "🇹🇳", "Тунисский динар"), ("TRY", "🇹🇷", "Турецкая лира"),
            ("TWD", "🇹🇼", "Новый тайваньский доллар"), ("UAH", "🇺🇦", "Украинская гривна"), ("UGX", "🇺🇬", "Угандийский шиллинг"),
            ("UYU", "🇺🇾", "Уругвайский песо"), ("UZS", "🇺🇿", "Узбекский сум"), ("VND", "🇻🇳", "Вьетнамский донг"),
            ("ZAR", "🇿🇦", "Южноафриканский рэнд"), ("ZMW", "🇿🇲", "Замбийская квача")
        ]
    },
    "en": {
        "select_curr": "Language selected. Choose the base currency:",
        "rate_title": "exchange rate against world currencies (Online):",
        "other_title": "--- World Countries (Alphabetical) ---",
        "error_format": "⚠️ **Please specify both the amount and the currency:**\nExample: `1000 AMD` or `100 USD`",
        "api_error": "⚠️ Failed to connect to exchange rates server. Try again later.",
        "currencies": {
            "USD": ("🇺🇸", "US Dollar"), "EUR": ("🇪🇺", "Euro"),
            "RUB": ("🇷🇺", "Russian Ruble"), "GEL": ("🇬🇪", "Georgian Lari"),
            "CNY": ("🇨🇳", "Chinese Yuan"), "AMD": ("🇦🇲", "Armenian Dram")
        },
        "world": [
            ("AED", "🇦🇪", "UAE Dirham"), ("ARS", "🇦🇷", "Argentine Peso"), ("AUD", "🇦🇺", "Australian Dollar"),
            ("AZN", "🇦🇿", "Azerbaijani Manat"), ("BGN", "🇧🇬", "Bulgarian Lev"), ("BRL", "🇧🇷", "Brazilian Real"),
            ("CAD", "🇨🇦", "Canadian Dollar"), ("CHF", "🇨🇭", "Swiss Franc"), ("CLP", "🇨🇱", "Chilean Peso"),
            ("COP", "🇨🇴", "Colombian Peso"), ("CZK", "🇨🇿", "Czech Koruna"), ("DKK", "🇩🇰", "Danish Krone"),
            ("EGP", "🇪🇬", "Egyptian Pound"), ("GBP", "🇬🇧", "British Pound"), ("GHS", "🇬🇭", "Ghanaian Cedi"),
            ("HKD", "🇭🇰", "Hong Kong Dollar"), ("HUF", "🇭🇺", "Hungarian Forint"), ("IDR", "🇮🇩", "Indonesian Rupiah"),
            ("ILS", "🇮🇱", "Israeli New Shekel"), ("INR", "🇮🇳", "Indian Rupee"), ("IQD", "🇮🇶", "Iraqi Dinar"),
            ("ISK", "🇮🇸", "Icelandic Króna"), ("JPY", "🇯🇵", "Japanese Yen"), ("KES", "🇰🇪", "Kenyan Shilling"),
            ("KGS", "🇰🇬", "Kyrgystani Som"), ("KRW", "🇰🇷", "South Korean Won"), ("KWD", "🇰🇼", "Kuwaiti Dinar"),
            ("KZT", "🇰🇿", "Kazakhstani Tenge"), ("LBP", "🇱🇧", "Lebanese Pound"), ("MAD", "🇲🇦", "Moroccan Dirham"),
            ("MDL", "🇲🇩", "Moldovan Leu"), ("MXN", "🇲🇽", "Mexican Peso"), ("MYR", "🇲🇾", "Malaysian Ringgit"),
            ("NOK", "🇳🇴", "Norwegian Krone"), ("NZD", "🇳🇿", "New Zealand Dollar"), ("OMR", "🇴🇲", "Omani Rial"),
            ("PEN", "🇵🇪", "Peruvian Sol"), ("PHP", "🇵🇭", "Philippine Peso"), ("PKR", "🇵🇰", "Pakistani Rupee"),
            ("PLN", "🇵🇱", "Polish Zloty"), ("QAR", "🇶🇦", "Qatari Riyal"), ("RON", "🇷🇴", "Romanian Leu"),
            ("RSD", "🇷🇸", "Serbian Dinar"), ("SAR", "🇸🇦", "Saudi Riyal"), ("SEK", "🇸🇪", "Swedish Krona"),
            ("SGD", "🇸🇬", "Singapore Dollar"), ("THB", "🇹🇭", "Thai Baht"), ("TJS", "🇹🇯", "Tajikistani Somoni"),
            ("TMT", "🇹🇲", "Turkmenistani Manat"), ("TND", "🇹🇳", "Tunisian Dinar"), ("TRY", "🇹🇷", "Turkish Lira"),
            ("TWD", "🇹🇼", "New Taiwan Dollar"), ("UAH", "🇺🇦", "Ukrainian Hryvnia"), ("UGX", "🇺🇬", "Ugandan Shilling"),
            ("UYU", "🇺🇾", "Uruguayan Peso"), ("UZS", "🇺🇿", "Uzbekistani Som"), ("VND", "🇻🇳", "Vietnamese Đồng"),
            ("ZAR", "🇿🇦", "South African Rand"), ("ZMW", "🇿🇲", "Zambian Kwacha")
        ]
    },
    "zh": {
        "select_curr": "已选择语言。请选择基础货币：",
        "rate_title": "兑世界各主要货币汇率 (实时):",
        "other_title": "--- 世界各国 (按字母排序) ---",
        "error_format": "⚠️ **请指定金额和货币：**\n例如：`1000 AMD` 或 `100 USD`",
        "api_error": "⚠️ 无法连接到汇率服务器，请稍后重试。",
        "currencies": {
            "USD": ("🇺🇸", "美元"), "EUR": ("🇪🇺", "欧元"),
            "RUB": ("🇷🇺", "俄罗斯卢布"), "GEL": ("🇪🇺", "格鲁吉亚拉里"),
            "CNY": ("🇨🇳", "中国人民币"), "AMD": ("🇦🇲", "亚美尼亚德拉姆")
        },
        "world": [
            ("AED", "🇦🇪", "阿联酋迪拉姆"), ("ARS", "🇦🇷", "阿根廷比索"), ("AUD", "🇦🇺", "澳大利亚元"),
            ("AZN", "🇦🇿", "阿塞拜疆马纳特"), ("BGN", "🇧🇬", "保加利亚列弗"), ("BRL", "🇧🇷", "巴西雷亚尔"),
            ("CAD", "🇨🇦", "加拿大元"), ("CHF", "🇨🇭", "瑞士法郎"), ("CLP", "🇨🇱", "智利比索"),
            ("COP", "🇨🇴", "哥伦比亚比索"), ("CZK", "🇨🇿", "捷克克朗"), ("DKK", "🇩🇰", "丹麦克朗"),
            ("EGP", "🇪🇬", "埃及镑"), ("GBP", "🇬🇧", "英镑"), ("GHS", "🇬🇭", "加纳塞地"),
            ("HKD", "🇭🇰", "港元"), ("HUF", "🇭🇺", "匈牙利福林"), ("IDR", "🇮🇩", "印度尼西亚卢比"),
            ("ILS", "🇮🇱", "以色列新谢克尔"), ("INR", "🇮🇳", "印度卢比"), ("IQD", "🇮🇶", "伊拉克第纳尔"),
            ("ISK", "🇮🇸", "冰岛克朗"), ("JPY", "🇯🇵", "日元"), ("KES", "🇰🇪", "肯尼亚先令"),
            ("KGS", "🇰🇬", "吉尔吉斯斯坦索姆"), ("KRW", "🇰🇷", "韩元"), ("KWD", "🇰🇼", "科威特第纳尔"),
            ("KZT", "🇰🇿", "哈萨克斯坦坚戈"), ("LBP", "🇱🇧", "黎巴嫩镑"), ("MAD", "🇲🇦", "摩洛哥迪拉姆"),
            ("MDL", "🇲🇩", "摩尔多瓦列伊"), ("MXN", "🇲🇽", "墨西哥比索"), ("MYR", "🇲🇾", "马来西亚林吉特"),
            ("NOK", "🇳🇴", "挪威克朗"), ("NZD", "🇳🇿", "新西兰元"), ("OMR", "🇴🇲", "阿曼里亚尔"),
            ("PEN", "🇵🇪", "秘鲁索尔"), ("PHP", "🇵🇭", "菲律宾比索"), ("PKR", "🇵🇰", "巴基斯坦卢比"),
            ("PLN", "🇵🇱", "波兰兹罗提"), ("QAR", "🇶🇦", "卡塔尔里亚尔"), ("RON", "🇷🇴", "罗马尼亚列伊"),
            ("RSD", "🇷🇸", "塞尔维亚第纳尔"), ("SAR", "🇸🇦", "沙特里亚尔"), ("SEK", "🇸🇪", "瑞典克朗"),
            ("SGD", "🇸🇬", "新加坡元"), ("THB", "🇹🇭", "泰铢"), ("TJS", "🇹🇯", "塔吉克斯坦索莫尼"),
            ("TMT", "🇹🇲", "土库曼斯坦马纳特"), ("TND", "🇹🇳", "突尼斯第纳尔"), ("TRY", "🇹🇷", "土耳其里拉"),
            ("TWD", "🇹🇼", "新台币"), ("UAH", "🇦🇺", "乌克兰格里夫纳"), ("UGX", "🇺🇬", "乌干达先令"),
            ("UYU", "🇺🇾", "乌拉圭比索"), ("UZS", "🇺🇿", "乌兹别克斯坦苏姆"), ("VND", "🇻🇳", "越南盾"),
            ("ZAR", "🇿🇦", "南非兰特"), ("ZMW", "🇿🇲", "赞比亚克瓦查")
        ]
    }
}

def get_exchange_rates(base_currency):
    try:
        response = requests.get(f"{API_URL}{base_currency}")
        data = response.json()
        if data.get("result") == "success":
            return data.get("rates", {})
    except Exception as e:
        print(f"API Error: {e}")
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_keyboard = [
        [InlineKeyboardButton("🇦🇲 Հայերեն", callback_data="lang_am"), InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"), InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    await update.message.reply_text(
        "Ընտրիր լեզուն / Please choose a language / Выберите язык / 请选择语言:", 
        reply_markup=inline_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        
        t_data = TRANSLATIONS.get(lang, TRANSLATIONS["am"])

        keyboard = [
            [InlineKeyboardButton("🇺🇸 USD", callback_data="curr_USD"), InlineKeyboardButton("🇪🇺 EUR", callback_data="curr_EUR")],
            [InlineKeyboardButton("🇷🇺 RUB", callback_data="curr_RUB"), InlineKeyboardButton("🇬🇪 GEL", callback_data="curr_GEL")],
            [InlineKeyboardButton("🇨🇳 CNY", callback_data="curr_CNY"), InlineKeyboardButton("🇦🇲 AMD", callback_data="curr_AMD")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = t_data["select_curr"]
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        
    elif data.startswith("curr_"):
        curr = data.split("_")[1]
        lang = context.user_data.get("lang", "am")
        t_data = TRANSLATIONS.get(lang, TRANSLATIONS["am"])
        
        rates = get_exchange_rates(curr)
        if not rates:
            await query.edit_message_text(text=t_data["api_error"])
            return

        curr_dict = t_data["currencies"]
        other_title = t_data["other_title"]
        world_list = t_data["world"]
        
        flag, name = curr_dict.get(curr, ("🌐", curr))
        response_text = f"💱 1.0 {flag} {curr} ({name}) {t_data['rate_title']}\n\n"
        
        for c_code, (c_flag, c_name) in curr_dict.items():
            rate = rates.get(c_code, 0.0)
            response_text += f"• {c_flag} {rate:.2f} {c_code} ({c_name})\n"
        response_text += "\n"
        
        response_text += f"{other_title}\n"
        for code, flag_w, name_w in world_list:
            rate = rates.get(code, 0.0)
            response_text += f"• {flag_w} {rate:.2f} {code} ({name_w})\n"

        await query.edit_message_text(text=response_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lang = context.user_data.get("lang", "am")
    t_data = TRANSLATIONS.get(lang, TRANSLATIONS["am"])
    
    parts = text.split()
    
    if len(parts) == 2 and parts[0].replace('.', '', 1).isdigit():
        amount = float(parts[0])
        curr = parts[1].upper()
    else:
        await update.message.reply_text(t_data["error_format"], parse_mode="Markdown")
        return

    rates = get_exchange_rates(curr)
    if not rates:
        await update.message.reply_text(t_data["api_error"])
        return

    curr_dict = t_data["currencies"]
    world_list = t_data["world"]
    flag, name = curr_dict.get(curr, ("🌐", curr))
    
    response_text = f"💱 {amount} {flag} {curr} ({name}) {t_data['rate_title']}\n\n"
    
    for c_code, (c_flag, c_name) in curr_dict.items():
        rate = rates.get(c_code, 0.0) * amount
        response_text += f"• {c_flag} {rate:.2f} {c_code} ({c_name})\n"
    
    response_text += f"\n{t_data['other_title']}\n"
    for code, flag_w, name_w in world_list:
        rate = rates.get(code, 0.0) * amount
        response_text += f"• {flag_w} {rate:.2f} {code} ({name_w})\n"

    await update.message.reply_text(response_text)

def main():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    TOKEN = "8989820281:AAGePam2vWb67_TXGjcAvips8y1MhgfeNnE"
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🚀 Բոտը աշխատում է մաքուր տեսքով...")
    app.run_polling()

if __name__ == "__main__":
    main()
