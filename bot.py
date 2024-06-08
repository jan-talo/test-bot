# インストールした discord.py を読み込む
import discord
from discord.ext import commands

import sys
import json
import random
from pathlib import Path
import uuid

import re
from unidecode import unidecode

import asyncio

# config.jsonの設定を読み込み
config_data = json.load(open('config.json','r',encoding="utf-8_sig"))
TOKEN = config_data['TOKEN']

# じゃんけんスタンプ定義
list_janken = ["guu","choki","paa"]
list_stump = {
    'guu': {
        'stumps': [":right_facing_fist:", ":punch:", ":fist:", ":left_facing_fist:", ":boxing_glove:", ":rock:", ":gem:", ":bricks:", ":curling_stone:", ":moyai:", ":ice_cube:", ":guitar:", ":zero:", ":o2:", ":u7121:"],
        'weights': [6,6,6,6,5,4,4,4,4,3,2,2,1,1,1]
    },
    'choki': {
        'stumps': [":v:" ,":scissors:" ,":crossed_swords:" ,":white_check_mark:" ,":heavy_check_mark:" ,":ballot_box_with_check:" ,":crab:" ,":lobster:" ,":fingers_crossed:" ,":person_getting_haircut:" ,":woman_getting_haircut:" ,":man_getting_haircut:" ,":clapper:" ,":carpentry_saw:" ,":axe:" ,":knife:" ,":dagger:" ,":aries:" ,":heavy_division_sign:" ,":u5272:" ,":two:"],
        'weights': [5,5,3,3,2,3,4,4,3,2,2,2,1,1,1,2,2,2,1,1,1]
    },
    'paa': {
        'stumps': [":rightwards_hand:", ":leftwards_hand:", ":wave:", ":hand_splayed:", ":raised_back_of_hand:", ":raised_hand:", ":scroll:", ":page_facing_up:", ":newspaper2:", ":newspaper:", ":hugging:", ":gloves:", ":vulcan:", ":raised_hands:", ":palms_up_together:", ":open_hands:", ":roll_of_paper:", ":dollar:", ":yen:", ":map:", ":page_with_curl:", ":bookmark_tabs:", ":parking:", ":five:", ":hamsa:", ":euro:", ":pound:"],
        'weights': [3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1]
    },
    'victory': {
        'stumps': [":trophy:", ":medal:", ":military_medal:", ":partying_face:", ":yum:", ":zany_face:", ":innocent:", ":smirk_cat:", ":crown:", ":cherry_blossom:", ":star:", ":sparkles:", ":rosette:", ":first_place:", ":confetti_ball:", ":tada:", ":sparkling_heart:", ":congratulations:", ":white_flower:", ":100:"],
        'weights': [2,2,2,2,2,1,2,1,2,2,2,2,2,2,2,2,2,2,2,2]
    }
}

def getText(name):
    result_text = ""
    if name in list_janken:
        index = list_janken.index(name)
        result_text = ["ぐー ","ちょき ","ぱー "][index]
    return result_text

def getStump(name):
    result_stump = ":green_heart:"
    if name =="vs":
        result_stump = ":vs:"
    elif name in list_stump:
        temp = list_stump[name]
        result_stump = random.choices(temp['stumps'],weights=temp['weights'])[0]   
    return result_stump

# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)

# 起動時に動作する処理
@bot.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print(f'Logged on as {bot.user}!')

# メッセージ受信時に動作する処理
@bot.event
async def on_message(message):
    # Userが発言したらターミナルに 名前(ID): 発言内容 が表示される
    print(f'Message from {message.author} ({message.author.id}): {message.content}')
    text = message.content

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    # 「/neko」と発言したら「にゃーん」が返る処理
    elif text == '/neko' \
      or text == '/ねこ':
        sendMessage = await message.channel.send('にゃーん')
        Emoji = "\N{Grinning Cat Face with Smiling Eyes}"
        await message.add_reaction(Emoji)
        await sendMessage.add_reaction(Emoji)
        await asyncio.sleep(10)
        await sendMessage.edit(content='にゃーん！')
          
    elif text == '!じゃんけん' \
      or text == '!ジャンケン' \
      or text == '!janken':
        choice = random.choice(list_janken)
        reply_text = f'{message.author}さん： {getText(choice)}'
        reply_text += getStump(choice)
        await message.channel.send(reply_text)

    elif await bot.is_owner(message.author):
        if text == '!jankenpon':
            sendMessage = await message.channel.send('じゃんけんに参加する方は、')
            # message.reactions[0]
        elif text == '/おやすみ':
            await message.channel.send(f'{message.author}さん、おやすみなさい')
            print('botはコマンドによりログアウトしました')
            await bot.close()

# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)
