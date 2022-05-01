from datetime import datetime
import re
import discord
from discord import Interaction, app_commands
from discord.ext import tasks, commands
from discord.app_commands import Choice
import yaml
from utility.utils import defaultEmbed, getWeekdayName, log
from discord import Member
from utility.GenshinApp import genshin_app
from typing import List, Optional
from utility.paginator import Paginator

class GenshinCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('data/accounts.yaml', 'r', encoding='utf-8') as f:
            self.user_dict: dict[str, dict[str, str]] = yaml.full_load(f)
        with open('data/builds/anemo.yaml', 'r', encoding='utf-8') as f:
            self.anemo_dict = yaml.full_load(f)
        with open('data/builds/cryo.yaml', 'r', encoding='utf-8') as f:
            self.cryo_dict = yaml.full_load(f)
        with open('data/builds/electro.yaml', 'r', encoding='utf-8') as f:
            self.electro_dict = yaml.full_load(f)
        with open('data/builds/geo.yaml', 'r', encoding='utf-8') as f:
            self.geo_dict = yaml.full_load(f)
        with open('data/builds/hydro.yaml', 'r', encoding='utf-8') as f:
            self.hydro_dict = yaml.full_load(f)
        with open('data/builds/pyro.yaml', 'r', encoding='utf-8') as f:
            self.pyro_dict = yaml.full_load(f)
        # self.schedule.start()

    class CookieModal(discord.ui.Modal, title='提交Cookie'):
        cookie = discord.ui.TextInput(
            label='Cookie',
            placeholder='請貼上從網頁上取得的Cookie, 取得方式請使用指令 "/cookie"',
            style=discord.TextStyle.long,
            required=True,
            min_length=100,
            max_length=1500
        )
        async def on_submit(self, interaction: discord.Interaction):
            result = await genshin_app.setCookie(interaction.user.id, self.cookie.value)
            await interaction.response.send_message(result, ephemeral=True)
        
        async def on_error(self, error: Exception, interaction: discord.Interaction):
            await interaction.response.send_message('發生未知錯誤', ephemeral=True)
            print(error)

    @app_commands.command(
        name='cookie',
        description='設定Cookie')
    @app_commands.rename(option='選項')
    @app_commands.choices(option=[
        Choice(name='1. 顯示說明如何取得Cookie', value=0),
        Choice(name='2. 提交已取得的Cookie', value=1)])
    async def slash_cookie(self, interaction: discord.Interaction, option: int):
        if option == 0:
            help_msg = (
            "1.先複製底下的整段程式碼\n"
            "2.PC或手機使用Chrome開啟Hoyolab登入帳號 <https://www.hoyolab.com>\n"
            "3.在網址列先輸入 `java`, 然後貼上程式碼, 確保網址開頭變成 `javascript:`\n"
            "4.按Enter, 網頁會變成顯示你的Cookie, 全選然後複製\n"
            "5.在這裡提交結果, 使用：`/cookie 提交已取得的Cookie`\n"
            "https://i.imgur.com/OQ8arx0.gif")
            code_msg = "```script:d=document.cookie; c=d.includes('account_id') || alert('過期或無效的Cookie,請先登出帳號再重新登入!'); c && document.write(d)```"
            await interaction.response.send_message(content=help_msg)
            await interaction.followup.send(content=code_msg)
        elif option == 1:
            await interaction.response.send_modal(self.CookieModal())

    @app_commands.command(
        name='setuid',
        description='設定原神UID')
    @app_commands.describe(uid='請輸入要保存的原神UID')
    async def slash_uid(self, interaction: discord.Interaction, uid: int):
        await interaction.response.defer(ephemeral=True)
        result = await genshin_app.setUID(interaction.user.id, int(uid))
        await interaction.edit_original_message(content=result)

    @app_commands.command(
        name='check',
        description='查看即時便籤, 例如樹脂、洞天寶錢、探索派遣'
    )
    @app_commands.rename(member='其他人')
    @app_commands.describe(member='查看其他群友的資料')
    async def check(self, interaction: discord.Interaction,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getRealTimeNotes(member.id, False)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @app_commands.command(
        name='stats',
        description='查看原神資料, 如活躍時間、神瞳數量、寶箱數量'
    )
    @app_commands.rename(member='其他人')
    @app_commands.describe(member='查看其他群友的資料')
    async def stats(self, interaction: discord.Interaction,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getUserStats(member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @app_commands.command(
        name='area',
        description='查看區域探索度'
    )
    @app_commands.rename(member='其他人')
    @app_commands.describe(member='查看其他群友的資料')
    async def area(self, interaction: discord.Interaction,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getArea(member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @app_commands.command(
        name='claim',
        description='領取hoyolab登入獎勵'
    )
    @app_commands.rename(member='其他人')
    @app_commands.describe(member='查看其他群友的資料')
    async def claim(self, interaction: discord.Interaction,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.claimDailyReward(member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @app_commands.command(
        name='diary',
        description='查看旅行者日記'
    )
    @app_commands.rename(month='月份',member='其他人')
    @app_commands.describe(month='要查詢的月份',member='查看其他群友的資料')
    @app_commands.choices(month=[
        app_commands.Choice(name='這個月', value=0),
        app_commands.Choice(name='上個月', value=-1),
        app_commands.Choice(name='上上個月', value=-2)]
    )
    async def diary(self, interaction: discord.Interaction,
        month: int, member: Optional[Member] = None
    ):
        member = member or interaction.user
        month = datetime.now().month + month
        month = month + 12 if month < 1 else month
        result = await genshin_app.getDiary(member.id, month)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @app_commands.command(
        name='log',
        description='查看最近25筆原石或摩拉收入紀錄'
    )
    @app_commands.choices(
        type=[app_commands.Choice(name='原石', value=0),
            app_commands.Choice(name='摩拉', value=1)]
    )
    @app_commands.rename(type='類別',member='其他人')
    @app_commands.describe(member='查看其他群友的資料')
    async def log(self, interaction:discord.Interaction, type:int,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getDiaryLog(member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result[type])

    @app_commands.command(
        name='users',
        description='查看所有已註冊原神帳號'
    )
    async def users(self, interaction: discord.Interaction):
        print(log(False, False, 'Users', interaction.user.id))
        user_dict = dict(self.user_dict)
        userStr = ""
        count = 0
        for user_id, value in user_dict.items():
            count += 1
            userStr = userStr + \
                f"{count}. {value['name']} - {value['uid']}\n"
        embed = defaultEmbed("所有帳號", userStr)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name='today',
        description='查看今日原石與摩拉收入'
    )
    @app_commands.rename(member='其他人')
    @app_commands.describe(member='查看其他群友的資料')
    async def today(self, interaction: discord.Interaction,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getToday(member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @app_commands.command(name='abyss', description='深淵資料查詢')
    @app_commands.rename(check_type='類別',season='期別',floor='層數',member='其他人')
    @app_commands.describe(check_type='想要查看的資料類別',
        season='這期還是上期?',floor='欲查閱的層數', member='查看其他群友的資料')
    @app_commands.choices(
        check_type=[Choice(name='總覽', value=0),
                Choice(name='詳細',value=1)],
        season=[Choice(name='上期紀錄', value=0),
                Choice(name='本期紀錄', value=1)],
        floor=[Choice(name='所有樓層', value=0),
                Choice(name='最後一層', value=1)]
    )
    async def abyss(self, interaction:discord.Interaction, check_type:int, season:int=1, floor:int=0, member: Optional[Member] = None):
        member = member or interaction.user
        previous = True if season == 0 else False
        result = await genshin_app.getAbyss(member.id, previous)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        if type(result) == discord.Embed:
            await interaction.response.send_message(embed=result)
            return 
        if check_type==0:
            await interaction.response.send_message(embed=result[0])
        else:
            if floor == 1:
                await interaction.response.send_message(embed=result[-1])
            else:
                await Paginator(interaction, result[1:]).start(embeded=True)

    @app_commands.command(
        name='stuck',
        description='找不到資料?'
    )
    async def stuck(self, interaction: discord.Interaction):
        embed = defaultEmbed(
            "已經註冊,但有些資料找不到?",
            "1. 至hoyolab網頁中\n"
            "2. 點擊頭像\n"
            "3. personal homepage\n"
            "4. 右邊會看到genshin impact\n"
            "5. 點擊之後看到設定按鈕\n"
            "6. 打開 Do you want to enable real time-notes")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name='farm',
        description='查看原神今日可刷素材'
    )
    async def farm(self, interaction: discord.Interaction):
        weekdayGet = datetime.today().weekday()
        embedFarm = defaultEmbed(f"今天({getWeekdayName(weekdayGet)})可以刷的副本材料", " ")
        if weekdayGet == 0 or weekdayGet == 3:
            embedFarm.set_image(
                url="https://media.discordapp.net/attachments/823440627127287839/958862746349346896/73268cfab4b4a112.png")
        elif weekdayGet == 1 or weekdayGet == 4:
            embedFarm.set_image(
                url="https://media.discordapp.net/attachments/823440627127287839/958862746127060992/5ac261bdfc846f45.png")
        elif weekdayGet == 2 or weekdayGet == 5:
            embedFarm.set_image(
                url="https://media.discordapp.net/attachments/823440627127287839/958862745871220796/0b16376c23bfa1ab.png")
        elif weekdayGet == 6:
            embedFarm = defaultEmbed(
                f"今天({getWeekdayName(weekdayGet)})可以刷的副本材料", "禮拜日可以刷所有素材 (❁´◡`❁)")
        await interaction.response.send_message(embed=embedFarm)


    build = app_commands.Group(name='build', description='查看角色推薦主詞條、畢業面板、不同配置等')

    async def anemo_autocomplete(self,
    interaction: discord.Interaction,
    current: str,) -> List[app_commands.Choice[str]]:
        anemo = dict(self.anemo_dict)
        return [
            app_commands.Choice(name=anemo, value=anemo)
            for anemo in anemo if current.lower() in anemo.lower()
        ]

    @build.command(name='風', description='查看風元素角色的配置、武器、畢業面板')
    @app_commands.rename(chara='角色')
    @app_commands.autocomplete(chara=anemo_autocomplete)
    async def anemo_build(self, interaction: discord.Interaction, chara: str):
        result = await genshin_app.getBuild(self.anemo_dict, str(chara))
        await interaction.response.send_message(embed=result)

    async def cryo_autocomplete(self,
    interaction: discord.Interaction,
    current: str,) -> List[app_commands.Choice[str]]:
        cryo = dict(self.cryo_dict)
        return [
            app_commands.Choice(name=cryo, value=cryo)
            for cryo in cryo if current.lower() in cryo.lower()
        ]

    @build.command(name='冰', description='查看冰元素角色的配置、武器、畢業面板')
    @app_commands.rename(chara='角色')
    @app_commands.autocomplete(chara=cryo_autocomplete)
    async def anemo_build(self, interaction: discord.Interaction, chara: str):
        result = await genshin_app.getBuild(self.cryo_dict, str(chara))
        await interaction.response.send_message(embed=result)

    async def electro_autocomplete(self,
    interaction: discord.Interaction,
    current: str,) -> List[app_commands.Choice[str]]:
        electro = dict(self.electro_dict)
        return [
            app_commands.Choice(name=electro, value=electro)
            for electro in electro if current.lower() in electro.lower()
        ]

    @build.command(name='雷', description='查看雷元素角色的配置、武器、畢業面板')
    @app_commands.rename(chara='角色')
    @app_commands.autocomplete(chara=electro_autocomplete)
    async def electro_build(self, interaction: discord.Interaction, chara: str):
        result = await genshin_app.getBuild(self.electro_dict, str(chara))
        await interaction.response.send_message(embed=result)

    async def geo_autocomplete(self,
    interaction: discord.Interaction,
    current: str,) -> List[app_commands.Choice[str]]:
        geo = dict(self.geo_dict)
        return [
            app_commands.Choice(name=geo, value=geo)
            for geo in geo if current.lower() in geo.lower()
        ]

    @build.command(name='岩', description='查看岩元素角色的配置、武器、畢業面板')
    @app_commands.rename(chara='角色')
    @app_commands.autocomplete(chara=geo_autocomplete)
    async def geo_build(self, interaction: discord.Interaction, chara: str):
        result = await genshin_app.getBuild(self.geo_dict, str(chara))
        await interaction.response.send_message(embed=result)

    async def hydro_autocomplete(self,
    interaction: discord.Interaction,
    current: str,) -> List[app_commands.Choice[str]]:
        hydro = dict(self.hydro_dict)
        return [
            app_commands.Choice(name=hydro, value=hydro)
            for hydro in hydro if current.lower() in hydro.lower()
        ]

    @build.command(name='水', description='查看水元素角色的配置、武器、畢業面板')
    @app_commands.rename(chara='角色')
    @app_commands.autocomplete(chara=hydro_autocomplete)
    async def anemo_build(self, interaction: discord.Interaction, chara: str):
        result = await genshin_app.getBuild(self.hydro_dict, str(chara))
        await interaction.response.send_message(embed=result)

    async def pyro_autocomplete(self,
    interaction: discord.Interaction,
    current: str,) -> List[app_commands.Choice[str]]:
        pyro = dict(self.pyro_dict)
        return [
            app_commands.Choice(name=pyro, value=pyro)
            for pyro in pyro if current.lower() in pyro.lower()
        ]

    @build.command(name='火', description='查看火元素角色的配置、武器、畢業面板')
    @app_commands.rename(chara='角色')
    @app_commands.autocomplete(chara=pyro_autocomplete)
    async def pyro_build(self, interaction: discord.Interaction, chara: str):
        result = await genshin_app.getBuild(self.pyro_dict, str(chara))
        await interaction.response.send_message(embed=result)

    char = app_commands.Group(name='char',description='查看已擁有角色資訊, 如命座、親密度、聖遺物')

    @char.command(name='風',description='查看已擁有風元素角色資訊, 如命座、親密度、聖遺物')
    @app_commands.rename(char='角色',member='其他人')
    @app_commands.describe(char='僅能查看自己擁有角色的資料',member='查看其他群友的資料')
    @app_commands.autocomplete(char=anemo_autocomplete)
    async def anemo_char(self, interaction:discord.Interaction,char:str,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getUserCharacters(char, member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @char.command(name='冰',description='查看已擁有冰元素角色資訊, 如命座、親密度、聖遺物')
    @app_commands.rename(char='角色',member='其他人')
    @app_commands.describe(char='僅能查看自己擁有角色的資料',member='查看其他群友的資料')
    @app_commands.autocomplete(char=cryo_autocomplete)
    async def cryo_char(self, interaction:discord.Interaction,char:str,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getUserCharacters(char, member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @char.command(name='雷',description='查看已擁有雷元素角色資訊, 如命座、親密度、聖遺物')
    @app_commands.rename(char='角色',member='其他人')
    @app_commands.describe(char='僅能查看自己擁有角色的資料',member='查看其他群友的資料')
    @app_commands.autocomplete(char=electro_autocomplete)
    async def electro_char(self, interaction:discord.Interaction,char:str,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getUserCharacters(char, member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @char.command(name='岩',description='查看已擁有岩元素角色資訊, 如命座、親密度、聖遺物')
    @app_commands.rename(char='角色',member='其他人')
    @app_commands.describe(char='僅能查看自己擁有角色的資料',member='查看其他群友的資料')
    @app_commands.autocomplete(char=geo_autocomplete)
    async def geo_char(self, interaction:discord.Interaction,char:str,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getUserCharacters(char, member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @char.command(name='水',description='查看已擁有水元素角色資訊, 如命座、親密度、聖遺物')
    @app_commands.rename(char='角色',member='其他人')
    @app_commands.describe(char='僅能查看自己擁有角色的資料',member='查看其他群友的資料')
    @app_commands.autocomplete(char=hydro_autocomplete)
    async def hydro_char(self, interaction:discord.Interaction,char:str,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getUserCharacters(char, member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @char.command(name='火',description='查看已擁有火元素角色資訊, 如命座、親密度、聖遺物')
    @app_commands.rename(char='角色',member='其他人')
    @app_commands.describe(char='僅能查看自己擁有角色的資料',member='查看其他群友的資料')
    @app_commands.autocomplete(char=pyro_autocomplete)
    async def pyro_char(self, interaction:discord.Interaction,char:str,
        member: Optional[Member] = None
    ):
        member = member or interaction.user
        result = await genshin_app.getUserCharacters(char, member.id)
        result.set_author(name=self.bot.get_user(member.id), icon_url=self.bot.get_user(member.id).avatar)
        await interaction.response.send_message(embed=result)

    @app_commands.command(name='rate', description='聖遺物評分計算(根據副詞條)')
    @app_commands.rename(type='聖遺物類型',crit_dmg='暴傷',crit_rate='暴擊率',atk='攻擊百分比')
    @app_commands.choices(type=[
        Choice(name='生之花', value=0),
        Choice(name='死之羽', value=1),
        # Choice(name='時之沙', value=2),
        Choice(name='空之杯', value=3)])
        # Choice(name='理之冠', value=4)])
    async def rate(self, interaction:discord.Interaction,type:int,crit_dmg:str,crit_rate:str,atk:str):
        crit_dmg = int(re.search(r'\d+', crit_dmg).group())
        crit_rate = int(re.search(r'\d+', crit_rate).group())
        atk = int(re.search(r'\d+', atk).group())
        score = crit_rate*2 + atk*1.3 + crit_dmg*1
        typeStr = ''
        if type==0:
            typeStr='生之花'
        elif type==1:
            typeStr='死之羽'
        elif type==2:
            typeStr='時之沙'
        elif type==3:
            typeStr='空之杯'
        else:
            typeStr='理之冠'
        if type==0 or type==1:
            if score >= 40:
                tier_url = 'https://www.expertwm.com/static/images/badges/badge-s.png'
                desc = '極品聖遺物, 足以用到關服'
            elif score >=30:
                tier_url = 'https://www.expertwm.com/static/images/badges/badge-a.png'
                desc = '良品, 追求強度的人的目標'
            elif score >= 20:
                tier_url = 'https://www.expertwm.com/static/images/badges/badge-b.png'
                desc = '及格, 可以用了'
            else:
                tier_url = 'https://www.expertwm.com/static/images/badges/badge-c.png'
                desc = '過渡用, 繼續刷'
        else:
            if score >= 50:
                tier_url = 'https://www.expertwm.com/static/images/badges/badge-s.png'
                desc = '極品聖遺物, 足以用到關服'
            elif score >=40:
                tier_url = 'https://www.expertwm.com/static/images/badges/badge-a.png'
                desc = '良品, 追求強度的人的目標'
            elif score >= 30:
                tier_url = 'https://www.expertwm.com/static/images/badges/badge-b.png'
                desc = '及格, 可以用了'
            else:
                tier_url = 'https://www.expertwm.com/static/images/badges/badge-c.png'
                desc = '過渡用, 繼續刷'
        result = defaultEmbed(
            '聖遺物評分結果',
            f'總分: {score}\n'
            f'「{desc}」'
        )
        result.add_field(
            name='詳情',
            value=
            f'類型: {typeStr}\n'
            f'暴傷: {crit_dmg}%\n'
            f'暴擊率: {crit_rate}%\n'
            f'攻擊百分比: {atk}%'
        )
        result.set_thumbnail(url=tier_url)
        result.set_footer(text='[來源](https://forum.gamer.com.tw/C.php?bsn=36730&snA=11316)')
        await interaction.response.send_message(embed=result)

    def saveUserData(self, data:dict):
        with open('data/accounts.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(data, f)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GenshinCog(bot))
