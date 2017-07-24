import os,sys
#sys.path.insert(0, 'D:/Workspace-Github/saproject/code/99_bot/jiakbot')
sys.path.insert(0, '/Users/junquantham/Development/saproject/code/bot/jiakbot')


from telegram.ext import Updater, CommandHandler,MessageHandler, Filters # telegram wrapper
from jiakbot import JiakBot


jiakbot = JiakBot
jiak_sessions = {}
TOKEN = '418463610:AAHh8CEVl4hu4J6D6_BnxhqT39TlPVfadmM'

# specify uid mappings if any
uid = 81916899

# functions
def start(bot, update):
    jiakbot = JiakBot
    jiak_sessions[update.message.chat_id] = jiakbot
    update.message.reply_text('Hello' + update.message.from_user.first_name + '!')

def reply(bot, update):
    try:
        jiakbot = jiak_sessions[update.message.chat_id]
    except:
        jiakbot = JiakBot
        jiak_sessions[update.message.chat_id] = jiakbot

    response = jiakbot.respond(jiakbot, update.message['text'])
    bot.send_message(chat_id=update.message.chat_id, text=response)

# declaring handlers
updater = Updater(TOKEN)
message_handler = MessageHandler(Filters.text, reply)
start_handler = CommandHandler('start', start)

# adding handlers
updater.dispatcher.add_handler(message_handler)
updater.dispatcher.add_handler(start_handler)

# listen to requests
updater.start_polling()

