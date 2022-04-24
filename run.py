# shenhe-bot by seria

import discord
from discord.ext import commands
from utility.config import config
from utility.utils import log
from pathlib import Path

print("main or dev?")
user = input()
if user == "main":
    token = config.main
    prefix = ['!', '！']
else:
    token = config.dev
    prefix = ['%']

# 前綴, token, intents
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix=prefix, help_command=None,
                   intents=intents, case_insensitive=True)


for filepath in Path('./cogs').glob('**/*.py'):
    cog_name = Path(filepath).stem
    bot.load_extension(f'cogs.{cog_name}')
    print(log(True, False,'Cog', f'Loaded {cog_name}'))


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online, activity=discord.Game(name=f'輸入!help來查看幫助'))
    print(log(True, False, 'Bot', 'Logged in as {0.user}'.format(bot)))


@bot.event
async def on_message(message):
    await bot.process_commands(message)


bot.run(token, bot=True, reconnect=True)
