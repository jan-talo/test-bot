# インストールした discord.py を読み込む
import discord
from discord.ext import commands
from discord import app_commands,Interaction
from discord.ui import Select, View

import sys
import json
import random
from pathlib import Path
import uuid
import requests
from craiyon import Craiyon, craiyon_utils
from io import BytesIO
import base64

import re
from unidecode import unidecode

import asyncio

# config.jsonの設定を読み込み
with open('config.json','r',encoding="utf-8_sig") as file:
    config_data = json.load(file)
TOKEN = config_data['TOKEN']

# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

generator = Craiyon() # Initialize Craiyon() class

#ドロップダウンチャレンジ
class SelectView_kujibun(View):
    @discord.ui.select(
        cls = Select,
        placeholder = '引くクジを選択してください。',
    )
    async def selectMenu(self, interaction: Interaction, select: Select):
        select.disabled = True
        await interaction.response.edit_message(view = self)
        values = select.values[0]
        values = values.split(' ')
        title = values.pop(0)
        values = ' '.join(values)
        values = values.split(',')
        prefix = values[0]
        suffix = values[1]
        with open('kuji_data.json','r',encoding="utf-8_sig") as file:
            kuji_data = json.load(file)
        if title in kuji_data:
            kuji_list = kuji_data[title]
        else:
            await interaction.followup.send('くじの名前が違うようです。', ephemeral=True)
            return
        choice = f'{random.choice(kuji_list)}'
        reply_text = f'{prefix} 【{choice}】 {suffix}'      
        await interaction.followup.send(f'{title}で作成しました。',ephemeral=True)
        await interaction.channel.send(reply_text[:600])


@tree.command(name='kujibun', description='クジと組み合わせた文章を作ります')
@app_commands.describe(prefix='クジの前につける文章', suffix='クジの後につける文章')
async def kujibun(interaction: Interaction, prefix: str='',suffix: str=''):
    view = SelectView_kujibun()
    with open('kuji_data.json','r',encoding="utf-8_sig") as file:
        kuji_data = json.load(file)
    titles = list(kuji_data.keys())
    while titles:
        title = random.choice(titles)
        detail = ' '.join(kuji_data[title])
        view.selectMenu.add_option(
            label=title,
            value=f'{title} {prefix},{suffix}',
            description=detail[:35],
        )
        titles.remove(title)
    await interaction.response.send_message(f'{prefix} 【クジの結果】 {suffix}', view=view, ephemeral=True)


#ドロップダウンチャレンジ
class SelectView_delete(View):
    @discord.ui.select(
        cls = Select,
        placeholder = '削除するクジを選択してください。',
    )
    async def selectMenu(self, interaction: Interaction, select: Select):
        select.disabled = True
        await interaction.response.edit_message(view = self)
        with open('kuji_data.json','r',encoding="utf-8_sig") as file:
            kuji_data = json.load(file)
        title = select.values[0]
        if title in kuji_data:
            del kuji_data[title]
            with open('kuji_data.json','w',encoding="utf-8_sig") as file:
                writing = json.load(file)
            json.dump(kuji_data, writing, ensure_ascii=False, indent=4)
            reply_text = f'{title}を削除しました。'
            await interaction.followup.send(reply_text)
        else:
            reply_text = '指定されたクジは未登録です。'  
            await interaction.followup.send(reply_text,ephemeral=True)  

@tree.command(name='delete', description='クジを削除します')
async def delete(interaction: Interaction):
    view = SelectView_delete()
    with open('kuji_data.json','r',encoding="utf-8_sig") as file:
        kuji_data = json.load(file)
    titles = list(kuji_data.keys())
    while titles:
        title = random.choice(titles)
        detail = ' '.join(kuji_data[title])
        view.selectMenu.add_option(
            label=title,
            value=title,
            description=detail[:35],
        )
        titles.remove(title)
    await interaction.response.send_message("", view=view, ephemeral=True)

#ドロップダウンチャレンジ
class SelectView_kuji(View):
    @discord.ui.select(
        cls = Select,
        placeholder = '引くクジを選択してください。',
    )
    async def selectMenu(self, interaction: Interaction, select: Select):
        select.disabled = True
        await interaction.response.edit_message(view = self)
        values = select.values[0]
        values = values.split(' ')
        title = values.pop(0)
        count = int(values[0])
        with open('kuji_data.json','r',encoding="utf-8_sig") as file:
            kuji_data = json.load(file)
        if title in kuji_data:
            kuji_list = kuji_data[title]
        else:
            await interaction.followup.send('くじの名前が違うようです。', ephemeral=True)
            return
        if count <= 0:
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
        # await interaction.followup.send(f'{reply_text}')
        await interaction.followup.send(f'{title}を{count}回引きました。',ephemeral=True)
        await interaction.channel.send(reply_text)

@tree.command(name='kuji', description='登録されたクジを引きます')
@app_commands.describe(count='クジを引く回数')
async def kuji(interaction: Interaction, count: int = 1):
    view = SelectView_kuji()
    with open('kuji_data.json','r',encoding="utf-8_sig") as file:
        kuji_data = json.load(file)
    titles = list(kuji_data.keys())
    while titles:
        title = random.choice(titles)
        detail = ' '.join(kuji_data[title])
        view.selectMenu.add_option(
            label=title,
            value=f'{title} {count}',
            description=detail[:35],
        )
        titles.remove(title)
    await interaction.response.send_message("", view=view, ephemeral=True)

@client.event
async def on_ready():
    print('slash command!')
    new_activity = f'クジを引こう！'
    await client.change_presence(activity=discord.Game(new_activity))    
    await tree.sync()

# @tree.command(name='kuji', description='登録されたクジを引きます')
# @app_commands.describe(title='クジの名前', count='クジを引く回数')
# async def kuji(interaction: discord.Interaction, title:str, count:int):
#     # await interaction.response.send_message('Hello, Workd!')
#     # await interaction.response.send_message(f'{title}, {count}')

#     kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
#     if title in kuji_data:
#         kuji_list = kuji_data[title]
#     else:
#         await interaction.response.send_message('くじの名前が違うようです。', ephemeral=True)
#         return
#     if count <= 0:
#         count = 1
#     choice = ''
#     isLong = False
#     for i in range(count):
#         choice += f'{random.choice(kuji_list)}'
#         if len(choice) >= 300:
#             isLong = True
#             break
#         elif i == count:
#             break
#         choice += ' '
#     if isLong:
#         reply_text = f'{choice[:300]}...too long'
#     else:
#         reply_text = choice
#     await interaction.response.send_message(reply_text)

#　以下のコードでは、Craiyonからのレスポンスを正しく処理できませんでした。Craiyonの最新の仕様に合わせて修正してください。
@tree.command(name='generate_image', description='英文から画像生成します')
@app_commands.describe(prompt='英字で生成したい画像を指定')
async def generate_image(interaction: discord.Interaction, prompt:str):
    reply_text='画像生成中...（あと5年待って）'
    await interaction.response.send_message(f'{reply_text}', ephemeral=True) 

@tree.command(name='kuji_list', description='登録されたクジの名前を一覧します')
async def kuji_list(interaction: discord.Interaction):
    with open('kuji_data.json','r',encoding="utf-8_sig") as file:
        kuji_data = json.load(file)
    titles = list(kuji_data.keys())
    reply_text=''
    while titles:
        title = random.choice(titles)
        reply_text += f'{title}, '
        titles.remove(title)
        if len(reply_text) >= 320:
            reply_text = f'{reply_text[:320]}...'
            break
    await interaction.response.send_message(f'クジ一覧：\n{reply_text}')  

@tree.command(name='kuji_detail', description='登録されたクジの中身を表示します')
async def kuji_detail(interaction: discord.Interaction, title:str):
    with open('kuji_data.json','r',encoding="utf-8_sig") as file:
        kuji_data = json.load(file)
    if title in kuji_data:

        kuji_list = kuji_data[title]
        kuji_text = ' '.join(kuji_list)
        reply_text = f'{kuji_text}'
        if len(reply_text) >= 320:
            reply_text = f'{reply_text[:320]}...'
    else:
        await interaction.response.send_message('クジの名前が違うようです。', ephemeral=True)       
    await interaction.response.send_message(f'{title}の中身：\n{reply_text}')

@tree.command(name='memory', description='クジを登録します')
@app_commands.describe(title='クジの名前', details='クジの中身：半角スペース区切りで入力してください')
async def memory(interaction: discord.Interaction, title:str, details:str):
    if len(title) >= 16:
        await interaction.response.send_message(f'名前は16文字以下にしてください。\n参考：{title[:16]}', ephemeral=True)
        return   
    elif ' ' in title:
        await interaction.response.send_message(f'名前には半角スペースを入れないでください。', ephemeral=True)
        return       
    kuji_list = details.split(' ')
    with open('kuji_data.json','r',encoding="utf-8_sig") as file:
        kuji_data = json.load(file)

    if title in kuji_data:
        reply_text = f'{title}は既にあります。内容を変更したい場合は、一度 /delete で削除してください。'
        await interaction.response.send_message(reply_text,ephemeral=True)
    else:
        kuji_data[title] = kuji_list
        with open('kuji_data.json','w',encoding="utf-8_sig") as file:
            writing = json.load(file)
        json.dump(kuji_data, writing, ensure_ascii=False, indent=4)
        reply_text = f'{title}を登録しました。'            
        await interaction.response.send_message(reply_text)

@tree.command(name='file', description='クジのリストをtextファイルで添付します')
async def file(interaction: discord.Interaction):
        file_path = 'kuji_data.json'
        file = discord.File(file_path,filename='kuji_data.txt')
        await interaction.response.send_message('ファイルを送ります。', file=file)


# @tree.command(name='delete', description='クジを削除します')
# @app_commands.describe(title='クジの名前')
# async def delete(interaction: discord.Interaction, title:str):
#     kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
#     if title in kuji_data:
#         del kuji_data[title]
#         writhing = open('kuji_data.json','w',encoding="utf-8_sig")
#         json.dump(kuji_data, writhing, ensure_ascii=False, indent=4)
#         reply_text = '指定されたクジを削除しました。'
#         await interaction.response.send_message(reply_text)
#     else:
#         reply_text = '指定されたクジは未登録です。'  
#         await interaction.response.send_message(reply_text,ephemeral=True)  

# Botの起動とDiscordサーバーへの接続
# bot.run(TOKEN)

client.run(TOKEN)









#　以下のコードを改良して


# #ドロップダウンチャレンジ
# class SelectView(View):
#     @discord.ui.select(
#         cls = Select,
#         placeholder = 'クジを選択してください。',
#     )
#     async def selectMenu(self, interaction: Interaction, select: Select):
#         select.disabled = True
#         await interaction.response.edit_message(view = self)
#         await interaction.followup.send(f'You selected {select.values}')

# @tree.command()
# async def somemenu(interaction: Interaction):
#     view = SelectView()
    
#     kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
#     titles = list(kuji_data.keys())
#     while titles:
#         title = random.choice(titles)
#         detail = ' '.join(kuji_data[title])
#         view.selectMenu.add_option(
#             label=title,
#             value=title,
#             description=detail[:35],
#         )
#         titles.remove(title)
#     await interaction.response.send_message("", view=view, ephemeral=True)












# intents.message_content = True  # Enable message content intent
# bot = commands.Bot(command_prefix='!', intents=intents)

# # 起動時に動作する処理
# @bot.event
# async def on_ready():
#     # 起動したらターミナルにログイン通知が表示される
#     print(f'Logged on as {bot.user}!')

# # メッセージ受信時に動作する処理
# @bot.event
# async def on_message(message):
#     # Userが発言したらターミナルに 名前(ID): 発言内容 が表示される
#     # print(f'Message from {message.author} ({message.author.id}): {message.content}')
#     texts = message.content.split(' ')
#     command = texts.pop(0)
#     # メッセージ送信者がBotだった場合は無視する
#     if message.author.bot:
#         return
    
#     # 「！ねこ」と発言したら「にゃーん」が返る処理
#     # elif command == '！ねこ':
#     #     sendMessage = await message.channel.send('にゃーん')
#     #     Emoji = "\N{Grinning Cat Face with Smiling Eyes}"
#     #     await message.add_reaction(Emoji)
#     #     await sendMessage.add_reaction(Emoji)
#     #     await asyncio.sleep(10)
#     #     # print(message.reactions)
#     #     # sendMessage = await sendMessage.fetch()
#     #     # print(sendMessage.reactions)
#     #     await sendMessage.edit(content='にゃーん！')
    


#     elif command == '！くじ':
#         if not texts:
#             await message.channel.send('！くじ タイトル (回数)で入力してください。\nタイトルは ！タイトル で確認できます。\n新しく作る場合は、以下の形で入力してください。\n！メモリー タイトル 内容1 内容2 内容3...')
#             return
#         title = texts.pop(0)
#         kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
#         if title in kuji_data:
#             kuji_list = kuji_data[title]
#         else:
#             await message.channel.send('くじのタイトルが違うようです。')
#             return
        
#         if not texts:
#             count = 1
#         elif texts[0].isdigit():
#             count = int(texts[0])
#             if count == 0:
#                 count = 1
#         else:
#             count = 1 

#         choice = ''
#         isLong = False
#         for i in range(count):
#             choice += f'{random.choice(kuji_list)}'
#             if len(choice) >= 300:
#                 isLong = True
#                 break
#             elif i == count:
#                 break
#             choice += ' '
#         if isLong:
#             reply_text = f'{choice[:300]}...too long'
#         else:
#             reply_text = choice
#         await message.channel.send(reply_text)

#     elif command == '！メモリー':
#         if not texts:
#             await message.channel.send('以下の形で入力してください。\n！メモリー タイトル 内容1 内容2 内容3...')
#             return
#         title = texts.pop(0)
#         if len(title) >= 16:
#             await message.channel.send(f'タイトルは16文字以下にしてください。\n参考：{title[:16]}')
#             return            
#         elif not texts:
#             await message.channel.send('以下の形で入力してください。\n！メモリー タイトル 内容1 内容2 内容3...')
#             return
#         kuji_list = texts
#         kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))

#         if title in kuji_data:
#             reply_text = f'{title}は既にあります。内容を変更したい場合は、一度 ！デリート タイトル で削除してください。'
#         else:
#             kuji_data[title] = kuji_list
#             writhing = open('kuji_data.json','w',encoding="utf-8_sig")
#             json.dump(kuji_data, writhing, ensure_ascii=False, indent=4)
#             reply_text = f'{title}を登録しました。'            
#         await message.channel.send(reply_text)

#     elif command == '！タイトル':
#         kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
#         if not texts:
#             reply_text = '詳細は ！タイトル タイトル\n'
#             titles = list(kuji_data.keys())
#             while titles:
#                 title = random.choice(titles)
#                 reply_text += f'{title}, '
#                 titles.remove(title)
#                 if len(reply_text) >= 320:
#                     reply_text = f'{reply_text[:320]}...'
#                     break
#             await message.channel.send(reply_text)
#             return    
#         title = texts.pop(0)
#         if title in kuji_data:

#             kuji_list = kuji_data[title]
#             kuji_text = ' '.join(kuji_list)
#             reply_text = f'{kuji_text}'
#             if len(reply_text) >= 320:
#                 reply_text = f'{reply_text[:320]}...'
#         else:
#             reply_text = '指定されたタイトルは未登録です。'         
#         await message.channel.send(reply_text)

#     elif command == '！デリート':
#         if not texts:
#             await message.channel.send('以下の形で入力してください。\n！デリート タイトル')
#             return
#         title = texts.pop(0)
#         kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
#         if title in kuji_data:
#             del kuji_data[title]
#             writhing = open('kuji_data.json','w',encoding="utf-8_sig")
#             json.dump(kuji_data, writhing, ensure_ascii=False, indent=4)
#             reply_text = '指定されたタイトルを削除しました。'
#         else:
#             reply_text = '指定されたタイトルは未登録です。'    
#         await message.channel.send(reply_text)
    
#     elif command == '！ファイル':
#         file_path = 'kuji_data.json'
#         file = discord.File(file_path,filename='kuji_data.txt')
#         await message.channel.send('ファイルを送ります。', file=file)

#     elif await bot.is_owner(message.author):
#         if command == '/おやすみ':
#             await message.channel.send(f'{message.author}さん、おやすみなさい')
#             print('botはコマンドによりログアウトしました')
#             await bot.close()

#         elif command == '/タイトル':
#             kuji_data = json.load(open('kuji_data.json','r',encoding="utf-8_sig"))
#             if not texts:
#                 reply_text = ''
#                 titles = list(kuji_data.keys())
#                 while titles:
#                     title = random.choice(titles)
#                     reply_text += f'{title}, '
#                     titles.remove(title)
#                     #if len(reply_text) >= 320:
#                     #    reply_text = f'{reply_text[:320]}...'
#                     #    break
#                 await message.channel.send(reply_text[:2000])
#                 return    
#             title = texts.pop(0)
#             if title in kuji_data:

#                 kuji_list = kuji_data[title]
#                 kuji_text = ' '.join(kuji_list)
#                 reply_text = f'{kuji_text}'
#                 #if len(reply_text) >= 320:
#                 #    reply_text = f'{reply_text[:320]}...'
#             else:
#                 reply_text = '指定されたタイトルは未登録です。'         
#             await message.channel.send(reply_text[:2000])
