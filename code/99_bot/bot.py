# import jiakbot
import sys
sys.path.insert(0, 'D:/Workspace-Github/saproject/code/99_bot/jiakbot')

from jiakbot import JiakBot

jiakbot = JiakBot

# -------------------------------------------------------------------
# ID mapping: hardcode
# -------------------------------------------------------------------

uid = 81916899

# -------------------------------------------------------------------
# telegram codes
# -------------------------------------------------------------------
# telegram wrapper
from telegram.ext import Updater, CommandHandler,MessageHandler, Filters

# functions
def start(bot, update):
    update.message.reply_text('Hello World!')

def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

def reply(bot, update):
    response = jiakbot.respond(jiakbot, sentence=update.message['text'],uid=uid)
    bot.send_message(chat_id=update.message.chat_id, text=response)


updater = Updater('418463610:AAHh8CEVl4hu4J6D6_BnxhqT39TlPVfadmM')
message_handler = MessageHandler(Filters.text, reply)
start_handler = CommandHandler('start', start)
hello_handler = CommandHandler('hello', hello)

# adding handlers
updater.dispatcher.add_handler(message_handler)
updater.dispatcher.add_handler(start_handler)
updater.dispatcher.add_handler(hello_handler)

# listen to requests
updater.start_polling()

