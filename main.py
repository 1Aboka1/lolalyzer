import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from riotwatcher import LolWatcher, ApiError
import pandas as pd

regions = {
    'Russia': 'ru',
    'Europe West': 'euw',
    'Europe Nordic and East': 'eune',
    'North America': 'na',
    'Republic of Korea': 'kr',
    'Canada': 'cn',
    'South East Asia': 'sea',
    'Brazil': 'br',
    'Latin America North': 'lan',
    'Latin America South': 'las',
    'Oceania': 'oce',
    'Russia': 'ru',
    'Turkey': 'tr',
    'Japan': 'jp',
    'People\'s Republic of China': 'cn',
}

# Needs to be regenerated every 24 hours
riot_TOKEN = "RGAPI-f885ae8c-080f-4dc0-b4d1-bfa54b5a446d"
watcher = LolWatcher(riot_TOKEN)
region = 'ru'

bot_TOKEN = "5847363406:AAHY3CnYL2Pmwbl7qWZ2hybz-JmV0sa6ocI"
bot = telebot.TeleBot(bot_TOKEN, parse_mode=None)

def gen_regions():
    regions_markup = []
    for key in regions.keys():
        regions_markup.append([InlineKeyboardButton(key, callback_data=regions[key])])

    return regions_markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = [[InlineKeyboardButton('Get Summoner\'s Info', callback_data='summoner_data_request'),
                InlineKeyboardButton('Restart', callback_data='restart_request')]]
    markup = InlineKeyboardMarkup(keyboard)
    markup.row_width = 2

    bot.send_message(message.chat.id, "Welcome to LoLaLyze🔥")

    keyboard = gen_regions()
    markup = InlineKeyboardMarkup(keyboard)
    markup.row_width = 1 

    sent_msg = bot.send_message(message.chat.id, "Enter the Summoner's Region: 🏴", reply_markup=markup)
    bot.register_callback_query_handler(sent_msg, summoner_region_handler)

def summoner_region_handler(callback):
    region = callback.data

    sent_msg = bot.send_message(callback.from_user.id, "Enter the Summoner's Name: 🧙🏽‍♂️", parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, summoner_search_handler)

def summoner_search_handler(message):
    summoner_name = message.text 
    summoner = watcher.summoner.by_name(region, summoner_name)
    sent_msg = bot.send_message(message.chat.id, gen_summoner_summary(summoner))

    gen_more_options(message)

def gen_more_options(message):
    keyboard = [[InlineKeyboardButton('Summoner\'s Rank', callback_data='summoner_ranking_request'),
                InlineKeyboardButton('Last Game Info', callback_data='last_game_info_request')]]
    markup = InlineKeyboardMarkup(keyboard)
    markup.row_width = 2

    sent_msg = bot.send_message(message.chat.id, "What would you want to know about the Summoner❓", reply_markup=markup)
    bot.register_callback_query_handler(sent_msg, process_more_request)
    
def process_more_request(callback):
    if callback.data == 'summoner_ranking_request':
        print(summoner)

    elif callback.data == 'last_game_info_request':

def gen_summoner_summary(summoner):
    text = ''
    if summoner:
        text += '🧙🏻‍♂️ Summoner\'s name: ' + str(summoner['name']) + '\n'
        text += '🌡️Summoner\'s level: ' + str(summoner['summonerLevel']) + '\n'
    return text         

bot.infinity_polling(interval=0, timeout=20)
