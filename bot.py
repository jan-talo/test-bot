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
    
    # 「！ねこ」と発言したら「にゃーん」が返る処理
    elif command == '！ねこ':
        sendMessage = await message.channel.send('にゃーん')
        Emoji = "\N{Grinning Cat Face with Smiling Eyes}"
        await message.add_reaction(Emoji)
        await sendMessage.add_reaction(Emoji)
        await asyncio.sleep(10)
        # print(message.reactions)
        # sendMessage = await sendMessage.fetch()
        # print(sendMessage.reactions)
        await sendMessage.edit(content='にゃーん！')
    
    elif command == '！くじ':
        if not texts:
            await message.channel.send('！くじ タイトル (回数)で入力してください。\nタイトルは ！タイトル で確認できます。\n新しく作る場合は、以下の形で入力してください。\n！メモリー タイトル 内容1 内容2 内容3...')
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
            if count == 0:
                count = 1
        else:
            count = 1 

        choice = ''
        isLong = False
        for i in range(count):
            choice += f'{random.choice(kuji_list)}'
            if len(choice) >= 300:
                isLong = True
                break
            elif i == count:
                break
            choice += ' '
        if isLong:
            reply_text = f'{choice[:300]}...too long'
        else:
            reply_text = choice
        await message.channel.send(reply_text)

    elif command == '！メモリー':
        if not texts:
            await message.channel.send('以下の形で入力してください。\n！メモリー タイトル 内容1 内容2 内容3...')
            return
        title = texts.pop(0)
        if len(title) >= 16:
            await message.channel.send(f'タイトルは16文字以下にしてください。\n参考：{title[:16]}')
            return            
        elif not texts:
            await message.channel.send('以下の形で入力してください。\n！メモリー タイトル 内容1 内容2 内容3...')
            return
        kuji_list = texts
        kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))

        if title in kuji_data:
            reply_text = f'{title}は既にあります。内容を変更したい場合は、一度 ！デリート タイトル で削除してください。'
        else:
            kuji_data[title] = kuji_list
            writhing = open('kuji_data.json','w',encoding="utf-8_sig")
            json.dump(kuji_data, writhing, ensure_ascii=False, indent=4)
            reply_text = f'{title}を登録しました。'            
        await message.channel.send(reply_text)

    elif command == '！タイトル':
        kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
        if not texts:
            reply_text = '詳細は ！タイトル タイトル\n'
            titles = list(kuji_data.keys())
            while titles:
                title = random.choice(titles)
                reply_text += f'{title}, '
                titles.remove(title)
                if len(reply_text) >= 320:
                    reply_text = f'{reply_text[:320]}...'
                    break
            await message.channel.send(reply_text)
            return    
        title = texts.pop(0)
        if title in kuji_data:

            kuji_list = kuji_data[title]
            kuji_text = ' '.join(kuji_list)
            reply_text = f'{kuji_text}'
            if len(reply_text) >= 320:
                reply_text = f'{reply_text[:320]}...'
        else:
            reply_text = '指定されたタイトルは未登録です。'         
        await message.channel.send(reply_text)

    elif command == '！デリート':
        if not texts:
            await message.channel.send('以下の形で入力してください。\n！デリート タイトル')
            return
        title = texts.pop(0)
        kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
        if title in kuji_data:
            del kuji_data[title]
            writhing = open('kuji_data.json','w',encoding="utf-8_sig")
            json.dump(kuji_data, writhing, ensure_ascii=False, indent=4)
            reply_text = '指定されたタイトルを削除しました。'
        else:
            reply_text = '指定されたタイトルは未登録です。'    
        await message.channel.send(reply_text)
    
    elif command == '！ファイル':
        file_path = 'kuji_data.json'
        file = discord.File(file_path,filename='kuji_data.txt')
        await message.channel.send('ファイルを送ります。', file=file)

    elif await bot.is_owner(message.author):
        if command == '/おやすみ':
            await message.channel.send(f'{message.author}さん、おやすみなさい')
            print('botはコマンドによりログアウトしました')
            await bot.close()

        elif command == '/タイトル':
            kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
            if not texts:
                reply_text = ''
                titles = list(kuji_data.keys())
                while titles:
                    title = random.choice(titles)
                    reply_text += f'{title}, '
                    titles.remove(title)
                    #if len(reply_text) >= 320:
                    #    reply_text = f'{reply_text[:320]}...'
                    #    break
                await message.channel.send(reply_text[:2000])
                return    
            title = texts.pop(0)
            if title in kuji_data:

                kuji_list = kuji_data[title]
                kuji_text = ' '.join(kuji_list)
                reply_text = f'{kuji_text}'
                #if len(reply_text) >= 320:
                #    reply_text = f'{reply_text[:320]}...'
            else:
                reply_text = '指定されたタイトルは未登録です。'         
            await message.channel.send(reply_text[:2000])



# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)

