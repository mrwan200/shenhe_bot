import discord
import sentry_sdk

from apps.text_map.text_map_app import text_map
from apps.text_map.utils import get_user_locale
from utility.utils import error_embed, log


async def global_error_handler(
    i: discord.Interaction, e: Exception | discord.app_commands.AppCommandError
):
    if isinstance(e, discord.app_commands.errors.CheckFailure):
        return
    log.warning(f"[{i.user.id}]{type(e)}: {e}")
    sentry_sdk.capture_exception(e)
    user_locale = await get_user_locale(i.user.id, i.client.db)
    if isinstance(e, discord.errors.NotFound):
        if e.code in [10062, 10008]:
            embed = error_embed(message=text_map.get(624, i.locale, user_locale))
            embed.set_author(name=text_map.get(623, i.locale, user_locale))
    else:
        embed = error_embed(message=text_map.get(513, i.locale, user_locale))
        embed.set_author(
            name=text_map.get(135, i.locale, user_locale),
            icon_url=i.user.display_avatar.url,
        )
        embed.set_thumbnail(url="https://i.imgur.com/Xi51hSe.gif")

    try:
        await i.response.send_message(
            embed=embed,
            ephemeral=True,
        )
    except discord.errors.InteractionResponded:
        await i.followup.send(
            embed=embed,
            ephemeral=True,
        )
    except discord.errors.NotFound:
        pass


class BaseView(discord.ui.View):
    async def interaction_check(self, i: discord.Interaction) -> bool:
        if not hasattr(self, "author"):
            return True
        user_locale = await get_user_locale(i.user.id, i.client.db)
        if self.author.id != i.user.id:
            await i.response.send_message(
                embed=error_embed().set_author(
                    name=text_map.get(143, i.locale, user_locale),
                    icon_url=i.user.display_avatar.url,
                ),
                ephemeral=True,
            )
        return self.author.id == i.user.id

    async def on_error(self, i: discord.Interaction, e: Exception, item) -> None:
        await global_error_handler(i, e)

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

        try:
            await self.message.edit(view=self)
        except AttributeError:
            log.warning(
                f"[Edit View] Attribute Error: [children]{self.children} [view]{self}"
            )
        except discord.HTTPException:
            log.warning(
                f"[Edit View] HTTPException: [children]{self.children} [view]{self}"
            )
        except Exception as e:
            log.warning(f"[Edit View] Failed{e}")
            sentry_sdk.capture_event(e)


class BaseModal(discord.ui.Modal):
    async def on_error(self, i: discord.Interaction, e: Exception) -> None:
        await global_error_handler(i, e)
