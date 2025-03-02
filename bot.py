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
    # print(f'Message from {message.author} ({message.author.id}): {message.content}')
    texts = message.content.split(' ')
    command = texts.pop(0)
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    
    # 「!neko」と発言したら「にゃーん」が返る処理
    elif command == '!ねこ':
        sendMessage = await message.channel.send('にゃーん')
        Emoji = "\N{Grinning Cat Face with Smiling Eyes}"
        await message.add_reaction(Emoji)
        await sendMessage.add_reaction(Emoji)
        await asyncio.sleep(10)
        # print(message.reactions)
        # sendMessage = await sendMessage.fetch()
        # print(sendMessage.reactions)
        await sendMessage.edit(content='にゃーん！')
    
    elif command == '!くじ':
        if not texts:
            await message.channel.send('コマンドの後に半角スペースに続けて、くじのタイトルを入れてください。登録されているタイトルは !タイトル で確認できます。')
            return
        title = texts.pop(0)
        kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
        if title in kuji_data:
            kuji_list = kuji_data[title]
        else:
            await message.channel.send('くじのタイトルが違うようです。')
            return
        
        if not texts:
            count = 1
        elif texts[0].isdigit():
            count = int(texts[0])
        else:
            count = 1 

        choice = ''
        isLong = False
        for i in range(count):
            choice += f'{random.choice(kuji_list)}'
            if len(choice) >= 250:
                isLong = True
                break
            elif i == count:
                break
            choice += ', '
        if isLong:
            reply_text = f'{choice[:250]}...too long'
        else:
            reply_text = choice
        await message.channel.send(reply_text)

    elif command == '!メモリー':
        title = texts.pop(0)
        kuji_list = texts
        kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
        kuji_data[title] = kuji_list
        writhing = open('kuji_data.json','w',encoding="utf-8_sig")
        json.dump(kuji_data, writhing, indent=4)
        if title in kuji_data:
            reply_text = f'{title}を記録しました。'
        else:
            reply_text = f'{title}を上書きしました。'            
        await message.channel.send(reply_text)

    elif command == '!タイトル':
        kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
        reply_text = ''
        for title, kuji_list in kuji_data.items():
            temp = ', '.join(kuji_list)
            reply_text += f'{title}: {temp[:20]}...\n'            
        await message.channel.send(reply_text)
    

    elif await bot.is_owner(message.author):
        if command == '/おやすみ':
            await message.channel.send(f'{message.author}さん、おやすみなさい')
            print('botはコマンドによりログアウトしました')
            await bot.close()

# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)

