import os
import json

bot_dir = os.path.dirname(os.path.abspath(__file__))


def config() -> dict:
    try:
        config_file = os.path.join(bot_dir + "/data", "config.json")
        with open(config_file) as conf:
            return json.loads(conf.read())
    except FileNotFoundError:
        print("config file not found")
        return {
            "bot_token": os.environ.get("DISCORD_BOT_TOKEN"),
            "owner_id": (),
            "prefix": (),
            "guild_id": (),
        }


def data() -> dict:
    try:
        config_file = os.path.join(bot_dir + "/data", "data.json")
        with open(config_file) as conf:
            return json.loads(conf.read())
    except FileNotFoundError:
        print("data file not found")


def config_sql() -> dict:
    try:
        config_file = os.path.join(bot_dir + "/data", "sql.json")
        with open(config_file) as conf:
            return json.loads(conf.read())
    except FileNotFoundError:
        print("config_sql file not found")
        return {"encrypt_key": None}
