import requests
import json

api_account = "https://api.guildwars2.com/v2/account/"
api_guild = "https://api.guildwars2.com/v2/guild/"
api_worlds = "https://api.guildwars2.com/v2/worlds"


def _convert_age(age_seconds: int) -> str:
    return f"{age_seconds}s / {round(age_seconds/3600, 2)}h"


def _created(date: str) -> str:
    return date.replace("T", " ").replace("Z", "")


def _convert_world(world_id: int) -> str:
    world_data = requests.get(f"{api_worlds}?ids={world_id}").json()[0]
    region = (
        "EU" if str(world_id)[0] == "2" else ("NA" if str(world_id)[0] == "1" else None)
    )
    return f"{world_data.get('name', 'unknown')} ({region})"


def _convert_value(key, value):
    if key == "age":
        return _convert_age(value)
    elif key == "created":
        return _created(value)
    elif key == "world":
        return _convert_world(value)
    else:
        return value


class Gw2API:
    def list_guilds(api_key) -> list:
        headers = {"Authorization": "Bearer " + api_key}
        response = requests.get(api_account, headers=headers)
        return json.loads(response.text)["guilds"]

    def get_guild_tag(guild_id) -> str:
        response = requests.get(api_guild + guild_id)
        return json.loads(response.text)["tag"]

    def account_exists(api_key) -> bool:
        headers = {"Authorization": "Bearer " + api_key}
        response = requests.get(api_account, headers=headers)
        return True if response.status_code == 200 else False

    def user_lookup(api_key) -> str:
        headers = {"Authorization": "Bearer " + api_key}
        account_info_json = requests.get(api_account, headers=headers).json()

        exclude = ["guilds", "guild_leader", "commander", "daily_ap", "monthly_ap"]
        account_info = "\n".join(
            [
                f"[2;31m{key}[0m: {_convert_value(key, value)}"
                for key, value in account_info_json.items()
                if key not in exclude
            ]
        )
        return f"```ansi\n{account_info}```"
