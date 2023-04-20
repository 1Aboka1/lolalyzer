import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from riotwatcher import LolWatcher, ApiError
import pandas as pd

regions = {
    'Russia': 'ru',
    'Europe West': 'euw1',
    'Europe Nordic and East': 'eune1',
    'North America': 'na1',
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
    'People\'s Republic of China': 'cn1',
}

# Needs to be regenerated every 24 hours
riot_TOKEN = "RGAPI-b8ce27f6-9806-4897-9fe9-4eca8f0b2d05"
watcher = LolWatcher(riot_TOKEN)

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

    summoner = Summoner()
    summoner.name_is_known = False

    sent_msg = bot.send_message(message.chat.id, "Enter the Summoner's Region: 🏴", reply_markup=markup)
    bot.register_callback_query_handler(sent_msg, summoner.summoner_region_handler)

class Summoner:
    def __init__(self):
        self.region = ''
        self.summoner_data = {}
        self.ranked_stats = {}
        self.name_is_known = False

    def summoner_region_handler(self, callback):
        if self.name_is_known:
            return
        self.region = callback.data

        sent_msg = bot.send_message(callback.from_user.id, "Enter the Summoner's Name:  🧙🏽‍♂️", parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, self.summoner_search_handler)

    def summoner_search_handler(self, message):
        self.name_is_known = True
        summoner_name = message.text 
        self.safe_region = self.region
        self.summoner_data = watcher.summoner.by_name(self.safe_region, summoner_name)
        sent_msg = bot.send_message(message.chat.id, self.gen_summoner_summary())

        self.gen_more_options(message)

    def gen_more_options(self, message):
        keyboard = [[InlineKeyboardButton('Summoner\'s Rank', callback_data='summoner_ranking_request'),
                    InlineKeyboardButton('Last Game Info', callback_data='last_game_info_request')]]
        markup = InlineKeyboardMarkup(keyboard)
        markup.row_width = 2

        sent_msg = bot.send_message(message.chat.id, "What would you want to know about the Summoner❓", reply_markup=markup)
        bot.register_callback_query_handler(sent_msg, self.process_more_request)
        
    def gen_summoner_summary(self):
        text = ''
        text += '🧙🏻‍♂️    Summoner\'s name: ' + str(self.summoner_data['name']) + '\n'
        text += '🌡️   Summoner\'s level: ' + str(self.summoner_data['summonerLevel']) + '\n'
        return text

    def process_more_request(self, callback):
        if callback.data == 'summoner_ranking_request':
            self.ranked_stats = watcher.league.by_summoner(self.safe_region, self.summoner_data['id'])

        elif callback.data == 'last_game_info_request':
            my_matches = watcher.match.matchlist_by_puuid(self.safe_region, self.summoner_data['puuid'])
            last_match = my_matches[0]
            self.match_detail = watcher.match.by_id(self.safe_region, last_match)

            match_detail_text = ''

            if self.match_detail['info']['participants'][0]['win']:
                match_detail_text += "🏆   WIN  -  GG WP" +  '\n\n'
            else:
                match_detail_text += "❌  LOSS  -  FF" +  '\n\n'

            match_detail_text += "⌚   Duration of the Game: " + str(round(self.match_detail['info']['gameDuration'] / 60)) + ' minutes\n\n'
            self.summoner_detail_in_match = None
            for i in self.match_detail['info']['participants']:
                if i['puuid'] == self.summoner_data['puuid']:
                    self.summoner_detail_in_match = i 

            match_detail_text += "🌙   Game Mode: " + self.match_detail['info']['gameMode'].casefold().capitalize() + '\n\n'
            match_detail_text += "⚟    Role: " + str(self.summoner_detail_in_match['teamPosition']).casefold().capitalize() + '\n\n'
            match_detail_text += "🧠   Champion: " + str(self.summoner_detail_in_match['championName']) + '\n\n'
            match_detail_text += "‼️   KDA: \n\t    🗡️ " + str(self.summoner_detail_in_match['kills']) + ' kills\n'
            match_detail_text += "\t    💀 " + str(self.summoner_detail_in_match['deaths']) + ' deaths\n'
            match_detail_text += "\t    ℹ️ " + str(self.summoner_detail_in_match['assists']) + ' assists\n\n'
            match_detail_text += "🔥   Damage Dealt To Champions: " + str(self.summoner_detail_in_match['totalDamageDealtToChampions']) + '\n\n'

            bot.send_message(callback.from_user.id, match_detail_text)

bot.infinity_polling(interval=0, timeout=20)
