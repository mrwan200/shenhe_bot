from yelan.draw import draw_domain_card
import config

__all__ = ["DomainPaginator"]


from io import BytesIO
from typing import List, Optional, Union

import aiosqlite
from apps.text_map.text_map_app import text_map
from apps.text_map.utils import get_user_locale
from discord import ButtonStyle, Embed, File, HTTPException, Interaction, NotFound, User
from discord.ui import Button, Select, View, button

from utility.utils import error_embed


class _view(View):
    def __init__(
        self,
        author: User,
        embeds: List[Embed],
        db: aiosqlite.Connection,
        check: bool = True,
        files: Optional[List[BytesIO]] = [],
    ):
        super().__init__(timeout=config.mid_timeout)
        self.author = author
        self.embeds = embeds
        self.check = check
        self.db = db
        self.files = files

        self.current_page = 0

    async def update_children(self, interaction: Interaction):
        self.next.disabled = self.current_page + 1 == len(self.embeds)
        self.previous.disabled = self.current_page <= 0

        user_locale = await get_user_locale(interaction.user.id, self.db)
        card = await draw_domain_card(
            self.files[self.current_page]["domain"],
            user_locale or interaction.locale,
            self.files[self.current_page]["items"],
        )

        kwargs = {"embed": self.embeds[self.current_page]}

        card.seek(0)
        file_name = "farm.jpeg"
        file = File(card, file_name)
        kwargs["attachments"] = [file]

        kwargs["view"] = self

        await interaction.response.edit_message(**kwargs)

    @button(
        emoji="<:double_left:982588991461281833>",
        style=ButtonStyle.gray,
        row=1,
        custom_id="paginator_double_left",
    )
    async def first(self, interaction: Interaction, button: Button):
        self.current_page = 0

        await self.update_children(interaction)

    @button(
        emoji="<:left:982588994778972171>",
        style=ButtonStyle.blurple,
        row=1,
        custom_id="paginator_left",
    )
    async def previous(self, interaction: Interaction, button: Button):
        self.current_page -= 1

        await self.update_children(interaction)

    @button(
        emoji="<:right:982588993122238524>",
        style=ButtonStyle.blurple,
        row=1,
        custom_id="paginator_right",
    )
    async def next(self, interaction: Interaction, button: Button):
        self.current_page += 1

        await self.update_children(interaction)

    @button(
        emoji="<:double_right:982588990223958047>",
        style=ButtonStyle.gray,
        row=1,
        custom_id="paginator_double_right",
    )
    async def last(self, interaction: Interaction, button: Button):
        self.current_page = len(self.embeds) - 1

        await self.update_children(interaction)


class DomainPaginator:
    def __init__(
        self,
        interaction: Interaction,
        embeds: List[Embed],
        db: aiosqlite.Connection,
        custom_children: Optional[List[Union[Button, Select]]] = [],
        files: Optional[List[BytesIO]] = [],
        domain: Optional[bool] = False,
    ):
        self.custom_children = custom_children
        self.interaction = interaction
        self.embeds = embeds
        self.db = db
        self.files = files
        self.domain = domain

    async def start(
        self,
        check: bool = True,
    ) -> None:
        if not (self.embeds):
            raise ValueError("Missing embeds")

        view = _view(self.interaction.user, self.embeds, self.db, check, self.files)
        view.previous.disabled = True if (view.current_page <= 0) else False
        view.next.disabled = (
            True if (view.current_page + 1 >= len(self.embeds)) else False
        )

        if len(self.custom_children) > 0:
            for child in self.custom_children:
                view.add_item(child)

        user_locale = await get_user_locale(self.interaction.user.id, self.db)
        card = await draw_domain_card(
            self.files[0]["domain"],
            user_locale or self.interaction.locale,
            self.files[0]["items"],
        )

        kwargs = {"embed": self.embeds[view.current_page]}

        card.seek(0)
        file_name = "farm.jpeg"
        file = File(card, file_name)
        kwargs["files"] = [file]

        kwargs["view"] = view

        await self.interaction.response.send_message(**kwargs)

        await view.wait()
        for item in view.children:
            item.disabled = True
        try:
            view.message = await self.interaction.original_response()
        except (NotFound, HTTPException):
            pass
