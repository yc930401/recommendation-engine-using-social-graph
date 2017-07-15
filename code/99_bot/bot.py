# import jiakbot
import sys
sys.path.insert(0, '/Users/junquantham/Development/saproject/code/99_bot/jiakbot')

from jiakbot import JiakBot

# main
jiakbot = JiakBot()

# telegram wrapper
from telegram.ext import Updater, CommandHandler,MessageHandler, Filters

# functions
def start(bot, update):
    update.message.reply_text('Hello World!')

def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

def echo(bot, update):
    response = jiakbot.respond(update.message['text'])
    bot.send_message(chat_id=update.message.chat_id, text=response)


updater = Updater('418463610:AAHh8CEVl4hu4J6D6_BnxhqT39TlPVfadmM')
echo_handler = MessageHandler(Filters.text, echo)

# adding handlers
updater.dispatcher.add_handler(echo_handler)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('hello', hello))

# listen to requests
updater.start_polling()

