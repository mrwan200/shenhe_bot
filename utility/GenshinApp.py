from datetime import datetime, timedelta
import genshin
import yaml
from utility.utils import errEmbed, defaultEmbed, log, getCharacterName, getWeekdayName


class GenshinApp:
    def __init__(self) -> None:
        try:
            with open('data/accounts.yaml', 'r', encoding="utf-8") as f:
                self.user_data = yaml.full_load(f)
        except:
            self.user_data = {}

    async def claimDailyReward(self, user_id:int):
        print(log(False, False, 'Claim', f'{user_id}'))
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        client, nickname = self.getUserCookie(user_id)
        try:
            reward = await client.claim_daily_reward()
        except genshin.errors.AlreadyClaimed:
            result = errEmbed(f'你已經領過今天的獎勵了!','')
        except genshin.errors.GenshinException as e:
            print(log(False, True, 'Claim', e))
            result = errEmbed('簽到失敗：{e.original}','')
        except Exception as e:
            print(log(False, True, 'Claim', e))
            result = errEmbed(f'簽到失敗：{e}','')
        else:
            result = defaultEmbed(f'{nickname}: 今日簽到成功',f'獲得 {reward.amount}x {reward.name}')
        return result
    
    async def getRealTimeNotes(self, user_id: int):
        print(log(False, False, 'Notes', user_id))
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        uid = self.user_data[user_id]['uid']
        client, nickname = self.getUserCookie(user_id)
        try:
            notes = await client.get_notes(uid)
        except genshin.errors.DataNotPublic as e:
            print(log(False, True, 'Notes', f'{user_id}: {e}'))
            result = errEmbed('你的資料並不是公開的!', '請輸入`!stuck`來取得更多資訊')
        except genshin.errors.GenshinException as e:
            print(log(False, True, 'Notes', f'{user_id}: {e}'))
            result = errEmbed('太快了!', '目前原神API請求次數過多, 請稍後再試')
        except Exception as e:
            print(log(False, True, 'Notes', e))
        else:
            if notes.current_resin == notes.max_resin:
                resin_recover_time = '已滿'
            else:
                day_msg = '今天' if notes.resin_recovery_time.day == datetime.now().day else '明天'
                resin_recover_time = f'{day_msg} {notes.resin_recovery_time.strftime("%H:%M")}'
            
            if notes.current_realm_currency == notes.max_realm_currency:
                realm_recover_time = '已滿'
            else:
                weekday_msg = getWeekdayName(notes.realm_currency_recovery_time.weekday())
                realm_recover_time = f'{weekday_msg} {notes.realm_currency_recovery_time.strftime("%H:%M")}'
            if notes.transformer_recovery_time != None:
                if notes.remaining_transformer_recovery_time < 10:
                    transformer_recover_time = '已可使用'
                else:
                    t = timedelta(seconds=notes.remaining_transformer_recovery_time+10)
                    if t.days > 0:
                        transformer_recover_time = f'{t.days} 天'
                    elif t.seconds > 3600:
                        transformer_recover_time = f'{round(t.seconds/3600)} 小時'
                    else:
                        transformer_recover_time = f'{round(t.seconds/60)} 分'
            result = defaultEmbed(
                f"{nickname}: 即時便籤",
                f"<:daily:956383830070140938> 已完成的每日數量: {notes.completed_commissions}/{notes.max_commissions}\n"
                f"<:transformer:966156330089971732> 質變儀剩餘時間: {transformer_recover_time}"
            )
            result.add_field(
                name='樹脂',
                value=
                f"<:resin:956377956115157022> 目前樹脂: {notes.current_resin}/{notes.max_resin}\n"
                f"樹脂回滿時間: {resin_recover_time}\n"
                f'週本樹脂減半：剩餘 {notes.remaining_resin_discounts}/3 次',
                inline=False
            )
            result.add_field(
                name='塵歌壺',
                value=
                f"<:realm:956384011750613112> 目前洞天寶錢數量: {notes.current_realm_currency}/{notes.max_realm_currency}\n"
                f'寶錢全部恢復時間: {realm_recover_time}',
                inline=False
            )
            exped_finished = 0
            exped_msg = ''
            for expedition in notes.expeditions:
                exped_msg += f'• {getCharacterName(expedition.character)}'
                if expedition.finished:
                    exped_finished += 1
                    exped_msg += ': 已完成\n'
                else:
                    day_msg = '今天' if expedition.completion_time.day == datetime.now().day else '明天'
                    exped_msg += f' 完成時間: {day_msg} {expedition.completion_time.strftime("%H:%M")}\n'
            result.add_field(
                name=f'探索派遣 ({exped_finished}/{len(notes.expeditions)})', 
                value=exped_msg,
                inline=False
            )
        return result

    async def getUserStats(self, user_id:int):
        print(log(False, False, 'Stats', user_id))
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        uid = self.user_data[user_id]['uid']
        client, nickname = self.getUserCookie(user_id)
        try:
            genshinUser = await client.get_partial_genshin_user(uid)
        except genshin.errors.GenshinException as e:
            print(log(False, True, 'Notes', f'{user_id}: {e}'))
            result = errEmbed('太多了!', '目前原神API請求次數過多, 請稍後再試')
        except Exception as e:
            print(log(False, True, 'Notes', e))
        else:
            result = defaultEmbed(f"{nickname}: 統計數據","")
            result.add_field(name='綜合',value=
                f"📅 活躍天數: {genshinUser.stats.days_active}\n"
                f"<:expedition:956385168757780631> 角色數量: {genshinUser.stats.characters}/50\n"
                f"📜 成就數量:{genshinUser.stats.achievements}/639\n"
                f"🌙 深淵已達: {genshinUser.stats.spiral_abyss}層"
            , inline = False)
            result.add_field(name='神瞳',value=
                f"<:anemo:956719995906322472> 風神瞳: {genshinUser.stats.anemoculi}/66\n"
                f"<:geo:956719995440730143> 岩神瞳: {genshinUser.stats.geoculi}/131\n"
                f"<:electro:956719996262821928> 雷神瞳: {genshinUser.stats.electroculi}/181"
            , inline = False)
            result.add_field(name='寶箱', value=
                f"一般寶箱: {genshinUser.stats.common_chests}\n"
                f"稀有寶箱: {genshinUser.stats.exquisite_chests}\n"
                f"珍貴寶箱: {genshinUser.stats.luxurious_chests}"
            , inline = False)
        return result

    async def getArea(self, user_id:int):
        print(log(False, False, 'Area', user_id))
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        uid = self.user_data[user_id]['uid']
        client, nickname = self.getUserCookie(user_id)
        try:
            genshinUser = await client.get_partial_genshin_user(uid)
        except genshin.errors.GenshinException as e:
            print(log(False, True, 'Area', f'{user_id}: {e}'))
            result = errEmbed('太多了!', '目前原神API請求次數過多, 請稍後再試')
        except Exception as e:
            print(log(False, True, 'Area', e))
        else:
            explorations = genshinUser.explorations
            exploreStr = ""
            for exploration in explorations:
                exploreStr += f"{exploration.name}: {exploration.explored}% • Lvl.{exploration.level}\n"
            result = defaultEmbed(
                f"{nickname}: 探索度",
                exploreStr
            )
        return result

    async def getDiary(self, user_id:int, month:int):
        print(log(False, False, 'Diary', user_id))
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        uid = self.user_data[user_id]['uid']
        client, nickname = self.getUserCookie(user_id)
        try:
            diary = await client.get_diary(month=month)
        except genshin.errors.GenshinException as e:
            print(log(False, True, 'Diary', f'{user_id}: {e}'))
            result = errEmbed('太多了!', '目前原神API請求次數過多, 請稍後再試')
        except Exception as e:
            print(log(False, True, 'Diary', e))
        else:
            d = diary.data 
            result = defaultEmbed(
                f'{nickname}: 旅行者日記  •  {month}月',
                f'<:primo:958555698596290570> 原石收入比上個月{"增加" if d.primogems_rate > 0 else "減少"}了{abs(d.primogems_rate)}%\n'
                f'<:mora:958577933650362468> 摩拉收入比上個月{"增加" if d.mora_rate > 0 else "減少"}了{abs(d.mora_rate)}%'
            )
            result.add_field(
                name='本月共獲得',
                value=
                f'<:primo:958555698596290570> : {d.current_primogems} • 上個月：{d.last_primogems}\n'
                f'<:mora:958577933650362468> : {d.current_mora} • 上個月：{d.last_mora}',
                inline=False
            )
            msg = ''
            for cat in d.categories:
                msg += f'{cat.name}: {cat.percentage}%\n'
            result.add_field(name=f'收入分類', value=msg, inline=False)

        return result

    def checkUserData(self, user_id: int):
        with open(f'data/accounts.yaml', encoding='utf-8') as file:
            users = yaml.full_load(file)
        if user_id not in users:
            return False, errEmbed('找不到原神帳號!', '請輸入`!reg`來查看註冊方式')
        else:
            return True, None

    def getUserCookie(self, user_id: int):
        with open(f'data/accounts.yaml', encoding='utf-8') as f:
            users = yaml.full_load(f)
        cookies = {"ltuid": users[user_id]['ltuid'],
                    "ltoken": users[user_id]['ltoken']}
        uid = users[user_id]['uid']
        nickname = users[user_id]['name']
        client = genshin.Client(cookies)
        client.lang = "zh-tw"
        client.default_game = genshin.Game.GENSHIN
        client.uids[genshin.Game.GENSHIN] = uid
        return client, nickname

    def saveUserData(self):
        with open('data/accounts.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(self.user_data, f)


genshin_app = GenshinApp()
