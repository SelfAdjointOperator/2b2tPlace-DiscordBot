# 2b2tPlace-DiscordBot

This repo contains the source code of the Discord bot I use for [2b2t.Place](https://2b2t.Place)

The bot will respond to messages in the channel with id specified in `bot/botConfig_public.json` beginning with `'!token'`. The bot will then try to DM the message author either their token for the website, or will inform them that they can only choose a pixel once per day. Errors are handled and logged in the `bot/logs/errors` folder.

## Setup
Virtual environment uses:

- `pip install requests`
- `pip install discord.py`

## Config

The two config files `bot/botConfig_public.json` and `bot/botConfig_private.json` are loaded. The latter contains sensitive / private information that should only be available to the web admin. The file structures are as follows:

```
botConfig_public.json
{
    "channelId": {
        "getToken": id of Discord channel that the bot should respond to messages in
    },
    "APIEndpoint": {
        "tokenJSON": url to 2b2t.place token api
    }
}
```

```
botConfig_private.json
{
    "discordBotToken": token given by Discord to log into the bot,
    "websiteAPIAuthKey": private authKey that is kept a secret between the website API and Discord bot
}
```
