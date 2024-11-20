import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_CHAT_ID = "-1002461867830"  # Replace with your group chat ID

# Define conversation states
LANGUAGE, EXPO_CHOICE, FULL_NAME, PHONE_NUMBER, EMAIL, COMPANY_NAME = range(6)

# Language-specific messages
MESSAGES = {
    "welcome": {
        "uz": "Xush kelibsiz! Tilni tanlang.",
        "en": "Welcome! Please choose a language.",
        "ru": "Добро пожаловать! Выберите язык."
    },
    "invalid_choice": {
        "uz": "Iltimos, quyidagi variantlardan birini tanlang.",
        "en": "Please choose one of the given options.",
        "ru": "Пожалуйста, выберите один из предложенных вариантов."
    },
    "expo_choice": {
        "uz": "Qaysi ekspo-ga tashrif buyurasiz?",
        "en": "Which expo are you attending?",
        "ru": "На какую выставку вы планируете посетить?"
    },
    "full_name": {
        "uz": "Iltimos, to'liq ismingizni kiriting.",
        "en": "Please enter your full name.",
        "ru": "Пожалуйста, введите ваше полное имя."
    },
    "phone_number": {
        "uz": "Iltimos, telefon raqamingizni kiriting.",
        "en": "Please provide your phone number.",
        "ru": "Пожалуйста, укажите ваш номер телефона."
    },
    "email": {
        "uz": "Iltimos, elektron pochtangizni kiriting.",
        "en": "Please enter your email address.",
        "ru": "Пожалуйста, введите ваш адрес электронной почты."
    },
    "company_name": {
        "uz": "Iltimos, kompaniya nomini kiriting.",
        "en": "Please enter your company name.",
        "ru": "Пожалуйста, введите название вашей компании."
    },
    "confirmation": {
        "uz": "Rahmat! Siz expo uchun ro'yxatdan o'tdingiz. Bu yerda sizning kirish tasdig'ingiz.",
        "en": "Thank you! You are registered for the expo. Here’s your entry confirmation.",
        "ru": "Спасибо! Вы зарегистрированы на выставку. Вот ваше подтверждение."
    },
    "cancel": {
        "uz": "Ro'yxatdan o'tish bekor qilindi.",
        "en": "Registration canceled.",
        "ru": "Регистрация отменена."
    }
}

EXPO_OPTIONS = {
    "BUILD PRO EXPO": "build_pro_expo",
    "AGRO PRO EXPO": "agro_pro_expo",
    "WORLD EDU": "world_edu",
    "E-com": "e_com",
    "PRO MOTORS": "pro_motors",
    "SAMARKAND HOSPITALITY DAYS": "samarkand_hospitality_days"
}


async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [['Uzbek', 'English', 'Russian']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"{MESSAGES['welcome']['uz']}\n{MESSAGES['welcome']['en']}\n{MESSAGES['welcome']['ru']}",
        reply_markup=reply_markup
    )
    return LANGUAGE


async def choose_language(update: Update, context: CallbackContext) -> int:
    lang = update.message.text.lower()
    language_code = {'uzbek': 'uz', 'english': 'en', 'russian': 'ru'}.get(lang)

    if language_code:
        context.user_data['language'] = language_code
        keyboard = [[expo] for expo in EXPO_OPTIONS.keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(MESSAGES['expo_choice'][language_code], reply_markup=reply_markup)
        return EXPO_CHOICE
    else:
        await update.message.reply_text(MESSAGES['invalid_choice']['en'])  # Adjust language as needed
        return LANGUAGE


async def expo_choice(update: Update, context: CallbackContext) -> int:
    expo = update.message.text.strip().lower()  # Normalize user input to lowercase
    expo_key = next((key for key in EXPO_OPTIONS if key.lower() == expo), None)  # Case-insensitive match

    if expo_key:
        context.user_data['expo_choice'] = EXPO_OPTIONS[expo_key]
        language = context.user_data['language']
        await update.message.reply_text(MESSAGES['full_name'][language], reply_markup=ReplyKeyboardRemove())
        return FULL_NAME
    else:
        language = context.user_data['language']
        # Send the expo choice prompt again if input is invalid
        keyboard = [[expo] for expo in EXPO_OPTIONS.keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(MESSAGES['invalid_choice'][language], reply_markup=reply_markup)
        return EXPO_CHOICE


async def full_name(update: Update, context: CallbackContext) -> int:
    language = context.user_data['language']
    context.user_data['full_name'] = update.message.text

    button = [[KeyboardButton(MESSAGES['phone_number'][language], request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(button, resize_keyboard=True)
    await update.message.reply_text(MESSAGES['phone_number'][language], reply_markup=reply_markup)
    return PHONE_NUMBER


async def phone_number(update: Update, context: CallbackContext) -> int:
    if update.message.contact:
        language = context.user_data['language']
        context.user_data['phone_number'] = update.message.contact.phone_number
        await update.message.reply_text(MESSAGES['email'][language], reply_markup=ReplyKeyboardRemove())
        return EMAIL
    else:
        language = context.user_data['language']
        await update.message.reply_text(MESSAGES['invalid_choice'][language], reply_markup=ReplyKeyboardRemove())
        return PHONE_NUMBER

# Rest of the code remains unchanged
async def phone_number(update: Update, context: CallbackContext) -> int:
    language = context.user_data['language']
    context.user_data['phone_number'] = update.message.contact.phone_number

    # Remove phone number keyboard after contact is received
    await update.message.reply_text(MESSAGES['email'][language], reply_markup=ReplyKeyboardRemove())
    return EMAIL


async def email(update: Update, context: CallbackContext) -> int:
    language = context.user_data['language']
    context.user_data['email'] = update.message.text
    await update.message.reply_text(MESSAGES['company_name'][language])
    return COMPANY_NAME


async def company_name(update: Update, context: CallbackContext) -> int:
    language = context.user_data['language']
    context.user_data['company_name'] = update.message.text

    # Send a confirmation message to the user
    await update.message.reply_text(MESSAGES['confirmation'][language])
    await update.message.reply_photo(photo=open('expo_confirmation.jpg', 'rb'))

    # Format and send the user's data to the group
    user_data = context.user_data
    message_to_group = (
        f"#New expo registration:\n\n"
        f"Expo: #{user_data['expo_choice']}\n"
        f"Full Name: {user_data['full_name']}\n"
        f"Phone Number: {user_data['phone_number']}\n"
        f"Email: {user_data['email']}\n"
        f"Company Name: {user_data['company_name']}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=message_to_group)

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    language = context.user_data.get('language', 'en')
    await update.message.reply_text(MESSAGES['cancel'][language], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    # Initialize bot application
    application = Application.builder().token(TOKEN).build()

    # Define conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            EXPO_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, expo_choice)],
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
            PHONE_NUMBER: [MessageHandler(filters.CONTACT, phone_number)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            COMPANY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Add conversation handler to the bot application
    application.add_handler(conv_handler)

    # Run the bot
    application.run_polling()


if __name__ == "__main__":
    main()


