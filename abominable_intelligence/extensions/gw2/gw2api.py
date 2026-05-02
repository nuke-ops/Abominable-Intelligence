import requests
import json

API_ACCOUNT = "https://api.guildwars2.com/v2/account/"
API_GUILD = "https://api.guildwars2.com/v2/guild/"
API_WORLDS = "https://api.guildwars2.com/v2/worlds"


def _convert_age(age_seconds: int) -> str:
    return f"{age_seconds}s / {round(age_seconds/3600, 2)}h"


def _created(date: str) -> str:
    return date.replace("T", " ").replace("Z", "")


def _convert_world(world_id: int) -> str:
    world_data = requests.get(f"{API_WORLDS}?ids={world_id}", timeout=10).json()[0]
    region = (
        "EU" if str(world_id)[0] == "2" else ("NA" if str(world_id)[0] == "1" else None)
    )
    return f"{world_data.get('name', 'unknown')} ({region})"


def _convert_value(key, value):
    print(key)
    print(value)
    if key == "age":
        return _convert_age(value)
    elif key == "created":
        return _created(value)
    elif key == "world":
        return _convert_world(value)
    else:
        return value


class Gw2API:
    def list_guilds(self, api_key: str) -> list[str]:
        headers = {"Authorization": "Bearer " + api_key}
        response = requests.get(API_ACCOUNT, headers=headers, timeout=10)
        return json.loads(response.text)["guilds"]

    def get_guild_tag(self, guild_id: str) -> str:
        response = requests.get(API_GUILD + guild_id, timeout=10)
        return json.loads(response.text)["tag"]

    def account_exists(self, api_key: str) -> bool:
        headers = {"Authorization": "Bearer " + api_key}
        response = requests.get(API_ACCOUNT, headers=headers, timeout=10)
        return True if response.status_code == 200 else False

    def user_lookup(self, api_key: str) -> str:
        headers = {"Authorization": "Bearer " + api_key}
        account_info_json = requests.get(
            API_ACCOUNT, headers=headers, timeout=10
        ).json()

        exclude = ["guilds", "guild_leader", "commander", "daily_ap", "monthly_ap"]
        account_info = "\n".join(
            [
                f"[2;31m{key}[0m: {_convert_value(key, value)}"
                for key, value in account_info_json.items()
                if key not in exclude
            ]
        )
        return f"```ansi\n{account_info}```"
