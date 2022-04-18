from discord.ext.forms import Form
from discord.ext import commands
import yaml
import global_vars
import sys
import getpass
import uuid

owner = getpass.getuser()

sys.path.append(f'C:/Users/{owner}/shenhe_bot/asset')

global_vars.Global()

with open(f'C:/Users/{owner}/shenhe_bot/asset/flow.yaml', encoding='utf-8') as file:
    users = yaml.full_load(file)
with open(f'C:/Users/{owner}/shenhe_bot/asset/bank.yaml', encoding='utf-8') as file:
    bank = yaml.full_load(file)
with open(f'C:/Users/{owner}/shenhe_bot/asset/giveaways.yaml', encoding='utf-8') as file:
    giveaways = yaml.full_load(file)


class FlowGiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reactor = self.bot.get_user(payload.user_id)
        if payload.message_id == 965143582178705459 or payload.message_id == 963972447600771092:
            return
        if payload.emoji.name == "🎉" and payload.user_id != self.bot.user.id:
            for giveaway in giveaways:
                if giveaway['msgID'] == payload.message_id:
                    for user in users:
                        if user['flow'] < giveaway['ticket']:
                            await channel.send(f"{reactor.mention} 你的flow幣數量不足以參加這項抽獎", delete_after=5)
                            return
                        if user['discordID'] == payload.user_id:
                            user['flow'] -= giveaway['ticket']
                            bank['flow'] += giveaway['ticket']
                            giveaway['current'] += giveaway['ticket']
                            with open(f'C:/Users/{owner}/shenhe_bot/asset/flow.yaml', 'w', encoding='utf-8') as file:
                                yaml.dump(users, file)
                            with open(f'C:/Users/{owner}/shenhe_bot/asset/bank.yaml', 'w', encoding='utf-8') as file:
                                yaml.dump(bank, file)
                            with open(f'C:/Users/{owner}/shenhe_bot/asset/giveaways.yaml', 'w', encoding='utf-8') as file:
                                yaml.dump(giveaways, file)
                            giveawayMsg = await channel.fetch_message(giveaway['msgID'])
                            newEmbed = global_vars.defaultEmbed(":tada: 抽獎啦!!!",
                                                                f"獎品: {giveaway['prize']}\n目前flow幣: {giveaway['current']}/{giveaway['goal']}\n參加抽獎要付的flow幣: {giveaway['ticket']}\n\n註: 按🎉來支付flow幣並參加抽獎\n抽獎將會在目標達到後開始")
                            await giveawayMsg.edit(embed=newEmbed)
                            await channel.send(f"{reactor.mention} 花了 {giveaway['ticket']} flow幣參加 {giveaway['prize']} 抽獎", delete_after=5)
                            break
                    break

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reactor = self.bot.get_user(payload.user_id)
        if payload.message_id == 965143582178705459 or payload.message_id == 963972447600771092:
            return
        if payload.emoji.name == "🎉" and payload.user_id != self.bot.user.id:
            for giveaway in giveaways:
                if giveaway['msgID'] == payload.message_id:
                    for user in users:
                        if user['discordID'] == payload.user_id:
                            user['flow'] += giveaway['ticket']
                            bank['flow'] -= giveaway['ticket']
                            giveaway['current'] -= giveaway['ticket']
                            with open(f'C:/Users/{owner}/shenhe_bot/asset/flow.yaml', 'w', encoding='utf-8') as file:
                                yaml.dump(users, file)
                            with open(f'C:/Users/{owner}/shenhe_bot/asset/bank.yaml', 'w', encoding='utf-8') as file:
                                yaml.dump(bank, file)
                            with open(f'C:/Users/{owner}/shenhe_bot/asset/giveaways.yaml', 'w', encoding='utf-8') as file:
                                yaml.dump(giveaways, file)
                            giveawayMsg = await channel.fetch_message(giveaway['msgID'])
                            newEmbed = global_vars.defaultEmbed(":tada: 抽獎啦!!!",
                                                                f"獎品: {giveaway['prize']}\n目前flow幣: {giveaway['current']}/{giveaway['goal']}\n參加抽獎要付的flow幣: {giveaway['ticket']}\n\n註: 按🎉來支付flow幣並參加抽獎\n抽獎將會在目標達到後開始")
                            await giveawayMsg.edit(embed=newEmbed)
                            await channel.send(f"{reactor.mention} 收回了 {giveaway['ticket']} flow幣來取消參加 {giveaway['prize']} 抽獎", delete_after=5)
                            break
                    break

    @commands.command(aliases=['gv'])
    @commands.has_role("小雪團隊")
    async def giveaway(self, ctx):
        form = Form(ctx, '抽獎設置流程', cleanup=True)
        form.add_question('獎品是什麼?', 'prize')
        form.add_question('獎品價值多少flow幣?', 'goal')
        form.add_question('參與者得花多少flow幣參與抽獎?', 'ticket')
        form.edit_and_delete(True)
        form.set_timeout(60)
        await form.set_color("0xa68bd3")
        result = await form.start()
        id = uuid.uuid1()
        embedGiveaway = global_vars.defaultEmbed(
            ":tada: 抽獎啦!!!",
            f"獎品: {result.prize}\n目前flow幣: 0/{result.goal}\n參加抽獎要付的flow幣: {result.ticket}\n\n註: 按🎉來支付flow幣並參加抽獎\n抽獎將會在目標達到後開始")
        global_vars.setFooter(embedGiveaway)
        await ctx.send("✅ 抽獎設置完成", delete_after=5)
        gvChannel = self.bot.get_channel(957268464928718918)
        giveawayMsg = await gvChannel.send(embed=embedGiveaway)
        await giveawayMsg.add_reaction('🎉')
        newGiveaway = {
            'giveawayID': str(id),
            'authorID': ctx.author.id,
            'msgID': giveawayMsg.id,
            'prize': result.prize,
            'goal': int(result.goal),
            'ticket': int(result.ticket),
            'current': 0
        }
        giveaways.append(newGiveaway)
        with open(f'C:/Users/{owner}/shenhe_bot/asset/giveaways.yaml', 'w', encoding='utf-8') as file:
            yaml.dump(giveaways, file)


def setup(bot):
    bot.add_cog(FlowGiveawayCog(bot))
