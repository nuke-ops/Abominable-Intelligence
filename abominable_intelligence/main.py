import logging
import os
import traceback

import hikari
import lightbulb
import miru
from data_manager import bot_dir, config

os.chdir(bot_dir)

bot_config = config()["bot"]

bot = hikari.GatewayBot(
    token=bot_config["token"],
    intents=hikari.Intents.ALL,
    cache_settings=hikari.impl.CacheSettings(
        components=hikari.api.CacheComponents.MEMBERS
    ),
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
    # save miru's client
    client.di.registry_for(lightbulb.di.Contexts.DEFAULT).register_value(
        miru.Client, miru_client
    )
    # core extensions
    await client.load_extensions(
        "extensions.core",
        "extensions.listeners",
        "extensions.git",
        "extensions.utility",
    )

    # general use extensions
    await client.load_extensions("extensions.tabletop", "extensions.ollama")

    # guild extensions
    await client.load_extensions("extensions.gw2.gw2")

    # external extensions
    if os.path.exists(bot_dir + "/extensions/test.py"):
        await client.load_extensions("extensions.test")

    try:
        print("Bot started, I think")
        logging.info("Abominable intelligence has started!")
        channel_id = os.environ.get("BOT_RESTARTED_CHANNEL")
        if channel_id:
            del os.environ["BOT_RESTARTED_CHANNEL"]
            await event.app.rest.create_message(
                channel=int(channel_id), content="Restart succeeded"
            )
    except Exception:
        traceback.print_exc()

    await client.start()


if __name__ == "__main__":
    bot.run()
