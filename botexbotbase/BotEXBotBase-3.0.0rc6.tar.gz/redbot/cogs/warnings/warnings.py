from collections import namedtuple

import discord
import datetime
import asyncio
import fuzzywuzzy

from .helpers import (
    warning_points_add_check,
    get_command_for_exceeded_points,
    get_command_for_dropping_points,
    warning_points_remove_check,
    EmbedPaginateWarnsList
)
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.utils.mod import is_admin_or_superior
from redbot.core.utils.chat_formatting import warning, pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.predicates import MessagePredicate

from typing import Union

_ = Translator("Warnings", __file__)


@cog_i18n(_)
class Warnings(commands.Cog):
    """Warn misbehaving users and take automated actions."""

    default_guild = {"actions": [], "reasons": {}, "allow_custom_reasons": False, 'compact_list': False, 'vips':[]}

    default_member = {"total_points": 0, "status": "", "warnings": []}

    def __init__(self, bot: Red):
        super().__init__()
        self.config = Config.get_conf(self, identifier=5757575755)
        self.config.register_guild(**self.default_guild)
        self.config.register_member(**self.default_member)
        self.bot = bot

    # We're not utilising modlog yet - no need to register a casetype
    # @staticmethod
    # async def register_warningtype():
    #     try:
    #         await modlog.register_casetype("warning", True, "\N{WARNING SIGN}", "Warning", None)
    #     except RuntimeError:
    #         pass

    @commands.group()
    @commands.guild_only()
    @checks.guildowner_or_permissions(administrator=True)
    async def warningset(self, ctx: commands.Context):
        """Manage settings for Warnings."""
        pass

    @warningset.command()
    @commands.guild_only()
    async def allowcustomreasons(self, ctx: commands.Context, allowed: bool):
        """Enable or disable custom reasons for a warning."""
        guild = ctx.guild
        await self.config.guild(guild).allow_custom_reasons.set(allowed)
        if allowed:
            await ctx.send(_("Custom reasons have been enabled."))
        else:
            await ctx.send(_("Custom reasons have been disabled."))

    @warningset.command()
    @commands.guild_only()
    async def vip(self, ctx: commands.Context, *vips: discord.Member):
        """Add remove vip(s), that causes 079 to warn users that ping a vip."""
        guild = ctx.guild
        VipList = await self.config.guild(guild).vips()

        if not vips:
            msg = f"```{guild.name}'s VIP List:\n\n"
            for user in VipList:
                user = self.bot.get_user(user)
                msg += f"{user}\n"
            msg += "```"

        else:
            msg = f"```diff\nMade the following changes to {guild.name}'s VIP List:\n\n"
            for user in vips:
                if user.id in VipList:
                    VipList.remove(user.id)
                    msg += f"- Removed VIP User {user} ({user.id})\n"
                else:
                    VipList.append(user.id)
                    msg += f"+ Added VIP User {user} ({user.id})\n"
            msg += "```"
            await self.config.guild(guild).vips.set(VipList)
        await ctx.send(msg)

    @warningset.command()
    @commands.is_owner()
    @commands.guildowner()
    async def reset(self, ctx : commands.Context):
        """Reset all Warning Data. Clears all saved warns, reasons, actions, and settings. Cannot be undone."""
        await self.config.clear_all()
        await ctx.send('Warnings Data Cleared. Change is permanent.')

    @warningset.command()
    @commands.guild_only()
    async def compact(self, ctx : commands.Context, option : bool):
        """Set compact view of listed warnings True / False."""
        await self.config.guild(ctx.guild).compact_list.set(allowed)
        if option:
            await ctx.send('Compact listed warns enabled.')
        else:
            await ctx.send('Compact listed warns disabled.')

    @commands.group()
    @commands.guild_only()
    @checks.guildowner_or_permissions(administrator=True)
    async def warnaction(self, ctx: commands.Context):
        """Manage automated actions for Warnings.

        Actions are essentially command macros. Any command can be run
        when the action is initially triggered, and/or when the action
        is lifted.

        Actions must be given a name and a points threshold. When a
        user is warned enough so that their points go over this
        threshold, the action will be executed.
        """
        pass

    @warnaction.command(name="add")
    @commands.guild_only()
    async def action_add(self, ctx: commands.Context, name: str, points: int):
        """Create an automated action.

        Duplicate action names are not allowed.
        """
        guild = ctx.guild

        exceed_command = await get_command_for_exceeded_points(ctx)
        drop_command = await get_command_for_dropping_points(ctx)

        to_add = {
            "action_name": name,
            "points": points,
            "exceed_command": exceed_command,
            "drop_command": drop_command,
        }

        # Have all details for the action, now save the action
        guild_settings = self.config.guild(guild)
        async with guild_settings.actions() as registered_actions:
            for act in registered_actions:
                if act["action_name"] == to_add["action_name"]:
                    await ctx.send(_("Duplicate action name found!"))
                    break
            else:
                registered_actions.append(to_add)
                # Sort in descending order by point count for ease in
                # finding the highest possible action to take
                registered_actions.sort(key=lambda a: a["points"], reverse=True)
                await ctx.send(_("Action {name} has been added.").format(name=name))

    @warnaction.command(name="del")
    @commands.guild_only()
    async def action_del(self, ctx: commands.Context, action_name: str):
        """Delete the action with the specified name."""
        guild = ctx.guild
        guild_settings = self.config.guild(guild)
        async with guild_settings.actions() as registered_actions:
            to_remove = None
            for act in registered_actions:
                if act["action_name"] == action_name:
                    to_remove = act
                    break
            if to_remove:
                registered_actions.remove(to_remove)
                await ctx.tick()
            else:
                await ctx.send(_("No action named {name} exists!").format(name=action_name))

    @commands.group()
    @commands.guild_only()
    @checks.guildowner_or_permissions(administrator=True)
    async def warnreason(self, ctx: commands.Context):
        """Manage warning reasons.

        Reasons must be given a name, description and points value. The
        name of the reason must be given when a user is warned.
        """
        pass

    @warnreason.command(name="create", aliases=["add"])
    @commands.guild_only()
    async def reason_create(
        self, ctx: commands.Context, name: str, points: int, *, description: str
    ):
        """Create a warning reason."""
        guild = ctx.guild

        if name.lower() == "custom":
            await ctx.send(_("*Custom* cannot be used as a reason name!"))
            return
        to_add = {"points": points, "description": description}
        completed = {name.lower(): to_add}

        guild_settings = self.config.guild(guild)

        async with guild_settings.reasons() as registered_reasons:
            registered_reasons.update(completed)

        await ctx.send(_("The new reason has been registered."))

    @warnreason.command(name="del", aliases=["remove"])
    @commands.guild_only()
    async def reason_del(self, ctx: commands.Context, reason_name: str):
        """Delete a warning reason."""
        guild = ctx.guild
        guild_settings = self.config.guild(guild)
        async with guild_settings.reasons() as registered_reasons:
            if registered_reasons.pop(reason_name.lower(), None):
                await ctx.tick()
            else:
                await ctx.send(_("That is not a registered reason name."))

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(ban_members=True)
    async def reasonlist(self, ctx: commands.Context):
        """List all configured reasons for Warnings."""
        guild = ctx.guild
        guild_settings = self.config.guild(guild)
        msg_list = []
        async with guild_settings.reasons() as registered_reasons:
            for r, v in registered_reasons.items():
                if ctx.embed_requested():
                    em = discord.Embed(
                        title=_("Reason: {name}").format(name=r), description=v["description"]
                    )
                    em.add_field(name=_("Points"), value=str(v["points"]))
                    msg_list.append(em)
                else:
                    msg_list.append(
                        _(
                            "Name: {reason_name}\nPoints: {points}\nDescription: {description}"
                        ).format(reason_name=r, **v)
                    )
        if msg_list:
            await menu(ctx, msg_list, DEFAULT_CONTROLS)
        else:
            await ctx.send(_("There are no reasons configured!"))

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(ban_members=True)
    async def actionlist(self, ctx: commands.Context):
        """List all configured automated actions for Warnings."""
        guild = ctx.guild
        guild_settings = self.config.guild(guild)
        msg_list = []
        async with guild_settings.actions() as registered_actions:
            for r in registered_actions:
                if await ctx.embed_requested():
                    em = discord.Embed(title=_("Action: {name}").format(name=r["action_name"]))
                    em.add_field(name=_("Points"), value="{}".format(r["points"]), inline=False)
                    em.add_field(name=_("Exceed command"), value=r["exceed_command"], inline=False)
                    em.add_field(name=_("Drop command"), value=r["drop_command"], inline=False)
                    msg_list.append(em)
                else:
                    msg_list.append(
                        _(
                            "Name: {action_name}\nPoints: {points}\n"
                            "Exceed command: {exceed_command}\nDrop command: {drop_command}"
                        ).format(**r)
                    )
        if msg_list:
            await menu(ctx, msg_list, DEFAULT_CONTROLS)
        else:
            await ctx.send(_("There are no actions configured!"))

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(ban_members=True)
    async def warn(self, ctx: commands.Context, user: Union[discord.Member, str], reason: str):
        """Warn the user for the specified reason.

        `<reason>` must be a registered reason name, or *custom* if
        custom reasons are enabled.
        """
        if user == ctx.author:
            await ctx.send(_("You cannot warn yourself."))
            return

        IsMemberTuple = False
        if self.isStrUserID(user): #User is int ID as str
                    searcheduser = ctx.guild.get_member(user)
                    if searcheduser is None:  # user not in guild
                        searcheduser = await self.bot.get_user_info(user)
                        user = (namedtuple('Member', 'id guild display_name')(searcheduser.id, ctx.guild, searcheduser.display_name) 
                                if searcheduser != None 
                                else namedtuple("Member", "id guild")(user, ctx.guild))
                        IsMemberTuple = True
                    else:
                        user = searcheduser
        elif type(user) == str:
            user = await self.GetMemberFromString(user, ctx.guild)
            if user is None: # user not in guild and no ID given
                await ctx.send("User not found in guild. Try mentioning them or using their UserID for an accurate search.")
                return

        custom_allowed = await self.config.guild(ctx.guild).allow_custom_reasons()
        if reason.lower() == "custom":
            if not custom_allowed:
                await ctx.send(
                    _(
                        "Custom reasons are not allowed! Please see `{prefix}reasonlist` for "
                        "a complete list of valid reasons."
                    ).format(prefix=ctx.prefix)
                )
                return
            reason_type = await self.custom_warning_reason(ctx)
        else:
            guild_settings = self.config.guild(ctx.guild)
            async with guild_settings.reasons() as registered_reasons:
                if reason.lower() not in registered_reasons:
                    msg = _("That is not a registered reason!")
                    if custom_allowed:
                        msg += " " + _(
                            "Do `{prefix}warn {user} custom` to specify a custom reason."
                        ).format(prefix=ctx.prefix, user=ctx.author)
                    elif (
                        ctx.guild.owner == ctx.author
                        or ctx.channel.permissions_for(ctx.author).administrator
                        or await ctx.bot.is_owner(ctx.author)
                    ):
                        msg += " " + _(
                            "Do `{prefix}warningset allowcustomreasons true` to enable custom "
                            "reasons."
                        ).format(prefix=ctx.prefix)
                    await ctx.send(msg)
                    return
                else:
                    reason_type = registered_reasons[reason.lower()]

        member_settings = self.config.member(user)
        current_point_count = await member_settings.total_points()
        warning_to_add = {
                "points": reason_type["points"],
                "description": reason_type["description"],
                "mod": ctx.author.id,
                "time": datetime.datetime.utcnow().timestamp()
                }

        async with member_settings.warnings() as user_warnings:
            #user_warnings.update(warning_to_add)
            user_warnings.append(warning_to_add)
        current_point_count += reason_type["points"]
        await member_settings.total_points.set(current_point_count)

        await warning_points_add_check(self.config, ctx, user, current_point_count)
        try:
            em = discord.Embed(
                title=_("Warning from {user}").format(user=ctx.author),
                description=reason_type["description"],
            )
            em.add_field(name=_("Points"), value=str(reason_type["points"]))
            if IsMemberTuple:
                user = searcheduser
            await user.send(
                _("You have received a warning in {guild_name}.").format(
                    guild_name=ctx.guild.name
                ),
                embed=em,
            )
        except discord.HTTPException:
            #await ctx.send("Failed to send user warning notification.")
            pass
        await ctx.send(_("User __**{user}**__ has been warned.").format(user=user))

    @commands.command()
    @commands.guild_only()
    async def warnings(self, ctx: commands.Context, user: Union[discord.Member, str] = None):
        """List the warnings for the specified user.

        Emit `<userid>` to see your own warnings.

        Note that showing warnings for users other than yourself requires
        appropriate permissions.
        """
        if user is None:
            user = ctx.author
        else:
            if self.isStrUserID(user): #User is int ID as str
                searcheduser = ctx.guild.get_member(user)
                if searcheduser is None:  # user not in guild
                    searcheduser = await self.bot.get_user_info(user)
                    user = (namedtuple('Member', 'id guild display_name')(searcheduser.id, ctx.guild, searcheduser.display_name) 
                            if searcheduser != None 
                            else namedtuple("Member", "id guild")(user, ctx.guild))
                else:
                    user = searcheduser
            elif type(user) == str:
                user = await self.GetMemberFromString(user, ctx.guild)
                if user is None: # user not in guild and no ID given
                    await ctx.send("User not found in guild. Try mentioning them or using their UserID for an accurate search.")
                    return

        member_settings = self.config.member(user)
        total_points = await member_settings.total_points()
        async with member_settings.warnings() as user_warnings:
            if not user_warnings:  # no warnings for the user
                await ctx.send(_(f"__**{user.display_name}**__ has no warnings!"))
            else:
                if not await self.config.guild(ctx.guild).compact_list():

                    return await EmbedPaginateWarnsList(self, ctx, user_warnings, author=f"Warnings for {user} | {total_points}", author_icon_url=user.avatar_url, thumbnail=user.avatar_url)
                else:
                    msg = ""
                    for warning in user_warnings:
                        mod = ctx.guild.get_member(warning["mod"])
                        if mod is None:
                            mod = discord.utils.get(
                                self.bot.get_all_members(), id = warning["mod"]
                            )
                            if mod is None:
                                mod = await self.bot.get_user_info(warning["mod"])
                        msg += _(
                            "{warn_num} | {num_points} point warning issued by {user} on {time} for "
                            "{description}\n"
                        ).format(
                            warn_num = f"{user_warnings.index(warning) + 1} of {len(user_warnings)}",
                            num_points = warning["points"],
                            user = mod,
                            time = datetime.datetime.fromtimestamp(warning['time']).strftime('%m/%d/%y @ %I:%M %p UTC'),
                            description = warning["description"],
                        )
                    await ctx.send_interactive(
                        pagify(msg, shorten_by=58), box_lang=_("Warnings for {user} | Total Points {total_points}").format(user=user, total_points=total_points)
                    )

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(ban_members=True)
    async def unwarn(self, ctx: commands.Context, user: Union[discord.Member, str], warn_num: str = None):
        """Remove a warning from a user. User must be in guild."""
        if user == ctx.author:
            await ctx.send(_("You cannot remove warnings from yourself."))
            return
        if type(user) == str:
            user = await self.GetMemberFromString(user, ctx.guild)
            if user is None: # user not in guild and no ID given
                await ctx.send("User not found in guild. Try mentioning them or using their UserID for an accurate search.")
                return

        member_settings = self.config.member(user)
        current_point_count = await member_settings.total_points()
        await warning_points_remove_check(self.config, ctx, user, current_point_count)
        async with member_settings.warnings() as user_warnings:
            if warn_num is not None and warn_num <= len(user_warnings) + 1: 
                await ctx.send(_("That warning doesn't exist!"))
                return
            else:
                try:
                    warning = (user_warnings.pop(warn_num) if warn_num != None else user_warnings.pop())
                    mod = discord.utils.get(
                            self.bot.get_all_members(), id = warning["mod"]
                        )
                    if mod is None:
                        mod = self.bot.get_user_info(warning["mod"])
                    current_point_count -= warning["points"]
                    await member_settings.total_points.set(current_point_count)
                except IndexError:
                    await ctx.send(f'Failed to unwarn {user}')
        await ctx.send("Removed Warning #{warn_num} | {points} point warning issued by {mod} for {description}".format(
                warn_num = user_warnings.index(warning),
                points = warning["points"],
                mod = mod,
                description = warning["description"]
            ))

    @staticmethod
    async def custom_warning_reason(ctx: commands.Context):
        """Handles getting description and points for custom reasons"""
        to_add = {"points": 0, "description": ""}

        await ctx.send(_("How many points should be given for this reason?"))
        try:
            msg = await ctx.bot.wait_for(
                "message", check=MessagePredicate.same_context(ctx), timeout=30
            )
        except asyncio.TimeoutError:
            await ctx.send(_("Ok then."))
            return
        try:
            int(msg.content)
        except ValueError:
            await ctx.send(_("That isn't a number!"))
            return
        else:
            if int(msg.content) <= 0:
                await ctx.send(_("The point value needs to be greater than 0!"))
                return
            to_add["points"] = int(msg.content)

        await ctx.send(_("Enter a description for this reason."))
        try:
            msg = await ctx.bot.wait_for(
                "message", check=MessagePredicate.same_context(ctx), timeout=30
            )
        except asyncio.TimeoutError:
            await ctx.send(_("Ok then."))
            return
        to_add["description"] = msg.content
        return to_add

    @staticmethod
    def isStrUserID(user : str):
        return type(user) == str and user.isdigit()

    @staticmethod
    async def GetMemberFromString(member : str, guild : discord.Guild):
        return discord.utils.find(lambda m: m.name[:len(member)].lower() == member.lower(), guild.members)

    async def on_message(self, message):
        if message.guild:  #Guild only

            if not message.author.bot:  #Ignores messages from bots

                if not message.content.startswith(('!', ';;', 't@', 't!', '!!', '-')): #Ignore messages that start with common bot prefixes

                    VipList = await self.config.guild(message.guild).vips()

                    for user in message.mentions:

                        if not message.author.id in VipList:  #Other VIPs excluded from warn for pinging VIPs

                            if user.id in VipList: #If message mentions a VIP, warn them
                                vip = user

                                ctx = await self.bot.get_context(message)
                                user = message.author

                                member_settings = self.config.member(user)
                                current_point_count = await member_settings.total_points()
                                warning_to_add = {
                                        "points": 50,
                                        "description": f"Pinging VIP {vip}",
                                        "mod": message.guild.me.id,
                                        "time": datetime.datetime.utcnow().timestamp()
                                        }

                                async with member_settings.warnings() as user_warnings:
                                    user_warnings.append(warning_to_add)
                                current_point_count += warning_to_add['points']
                                await member_settings.total_points.set(current_point_count)

                                await warning_points_add_check(self.config, ctx, user, current_point_count)
                                try:
                                    em = discord.Embed(
                                        title=_("Warning from {user}").format(user=message.guild.me),
                                        description=warning_to_add['description'],
                                    )
                                    em.add_field(name=_("Points"), value=str(warning_to_add['points']))
                                    await user.send(
                                        _("You have received a warning in {guild_name}.").format(
                                            guild_name=message.guild.name
                                        ),
                                        embed=em,
                                    )
                                except discord.HTTPException:
                                    #await ctx.send("Failed to send user warning notification.")
                                    pass
                                await message.channel.send(_("User __**{user}**__ has been warned for {description}.").format(user=user, description=warning_to_add['description']))
                                
