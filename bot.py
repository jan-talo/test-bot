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

# config.jsonの設定を読み込み
config_data = json.load(open('config.json','r',encoding="utf-8_sig"))
TOKEN = config_data['TOKEN']
ID = config_data['ID']

# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)

# 起動時に動作する処理
@bot.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print(f'Logged on as {bot.user}!')
'''
async def on_ready(self):
    print(f'Logged on as {self.user}!')
'''
# メッセージ受信時に動作する処理
@bot.event
async def on_message(message):
 # async def on_message(self, message):
    # Userが発言したらターミナルに 名前(ID): 発言内容 が表示される
    print(f'Message from {message.author} ({message.author.id}): {message.content}')
    text = message.content

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    # 「/neko」と発言したら「にゃーん」が返る処理
    elif text == '/neko' \
      or text == '/ねこ':
        await message.channel.send('にゃーん')

    elif text == '!じゃんけん' \
      or text == '!ジャンケン' \
      or text == '!janken':
        listJanken = ["ぐー", "ちょき", "ぱー"]
        result = random.choice(listJanken)
        await message.channel.send(f'{message.author}さん：　{result}')

    elif message.author.id == ID:
        if text == '/おやすみ':
           await bot.close()
           print('botはコマンドによりログアウトしました')

#@bot.event
#async def on_disconnect():
#    await bot.logout()
#    raise SystemExit()
#    sys.exit()

"""
 @bot.command()
async def createChannel(ctx, name: str = None, category: str = None):
    if not name:
        await ctx.send('チャンネル名を指定してください。')
        return

    guild = ctx.guild

    if category:
        category_channel = discord.utils.get(guild.categories, name=category)
        if category_channel is None:
            await ctx.send(f'カテゴリー「{category}」が見つかりません。')
            return
    else:
        category_channel = None

    if category_channel:
        await guild.create_text_channel(name, category=category_channel)
    else:
        await guild.create_text_channel(name)

    await ctx.send(f'チャンネル「{name}」が作成されました。') 
"""

# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)