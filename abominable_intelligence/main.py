import os
import hikari
import lightbulb

import miru
from data_manager import config, bot_dir

os.chdir(bot_dir)

bot_config = config()["bot"]

bot = hikari.GatewayBot(
    token=bot_config["token"],
    intents=hikari.Intents.ALL,
    logs={
        "version": 1,
        "incremental": True,
        "loggers": {
            "hikari": {"level": "INFO"},
            # "hikari.ratelimits": {"level": "TRACE_HIKARI"},
            "lightbulb": {"level": "INFO"},
        },
    },
)
client = lightbulb.client_from_app(bot)
miru_client = miru.Client(bot)


@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    client.di.registry_for(lightbulb.di.Contexts.DEFAULT).register_value(
        miru.Client, miru_client
    )
    await client.start()


if __name__ == "__main__":
    bot.run()
