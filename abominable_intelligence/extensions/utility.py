import lightbulb
from data_manager import config
from hooks import administration_only

bot_config = config()["bot"]

loader = lightbulb.Loader()


@loader.command
class NameFetch(
    lightbulb.SlashCommand,
    name="fetch_names",
    description="prints all users",
    hooks=[administration_only],
):
    mode = lightbulb.string(
        "mode",
        "method of name fetch",
        choices=[
            lightbulb.Choice("id_ping", "id_ping"),
            lightbulb.Choice("id_list", "id_list"),
            lightbulb.Choice("username_list", "username"),
            lightbulb.Choice("cache_list", "cache"),
        ],
    )

    @lightbulb.invoke
    async def name_fetch(self, ctx: lightbulb.Context) -> None:
        if self.mode == "id_ping":  # ping everyone
            members = await ctx.client.rest.fetch_members(ctx.guild_id)
            names: list[str] = [f"<@{x.id}>" for x in members]
            await ctx.respond(" ".join(names), user_mentions=members)
            return
        elif self.mode == "id_list":  # ping with no mention
            members = await ctx.client.rest.fetch_members(ctx.guild_id)
            names: list[str] = [f"<@{x.id}>" for x in members]
        elif self.mode == "username":  # list of usernames with no ping
            members = await ctx.client.rest.fetch_members(ctx.guild_id)
            names: list[str] = [f"@{x.username}" for x in members]
        elif self.mode == "cache":  # raw list of IDs
            members = ctx.client.app.cache.get_members_view_for_guild(ctx.guild_id)
            names: list[str] = [f"#{x}!" for x in members]

        await ctx.respond(" ".join(names))
