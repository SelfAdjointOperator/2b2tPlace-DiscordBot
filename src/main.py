import os
import json
import time
import random
import aiohttp
import discord
import datetime
# from discord.ext import commands

client = discord.Client()

GLOBAL_BOTCONFIG_PRIVATE = None # loaded in if __name__
GLOBAL_BOTCONFIG_PUBLIC  = None # loaded in if __name__

################################################################################

class ManualLogging():
    """For logging 401 and 403 errors etc"""

    filepathBase_error = "./logs/errors/error_{}.json"

    @staticmethod
    def saveJSON(filepath, pythonJSONObject):
        filepath = os.path.normpath(filepath)
        os.makedirs(os.path.split(filepath)[0], exist_ok = True)
        with open(filepath, "w+") as file:
            file.write(json.dumps(pythonJSONObject, indent = 4))

    @staticmethod
    def logErrorJSON(pythonJSONObject, addTimestampIfNotPresent = True):
        timestamp = int(time.time())
        if addTimestampIfNotPresent and not "timestamp" in pythonJSONObject:
            pythonJSONObject["timestamp"] = timestamp
        randomSuffix = "_%08x" % random.randrange(16 ** 8) # incase several errors happen at once
        filepath = ManualLogging.filepathBase_error.format(str(timestamp) + randomSuffix)
        ManualLogging.saveJSON(filepath, pythonJSONObject)

################################################################################

@client.event
async def on_ready():
    timestamp = int(time.time())
    print("Logged in as {} at {}".format(client.user, str(timestamp)))

@client.event
async def on_message(message):
    message_author = message.author
    if  message_author == client.user or \
        message.channel.id != GLOBAL_BOTCONFIG_PUBLIC["channelId"]["getToken"] or \
        not message.content.startswith("!token"):
            return
    try:
        await message_author.send("Getting token... 🤖🗺️🎟️")
    except discord.Forbidden:
        await message.channel.send("{} please allow DMs from me, the bot! 🥺".format(message_author.mention))
        return
    try:
        headers = {
            "authKey": GLOBAL_BOTCONFIG_PRIVATE["websiteAPIAuthKey"],
            "discordUUID": (discordUUID := str(message_author.id)),
            "discordTag": (discordTag := "{}#{}".format(message_author.name, message_author.discriminator))
        }
        async with aiohttp.ClientSession(headers = headers) as session:
            async with session.get(GLOBAL_BOTCONFIG_PUBLIC["APIEndpoint"]["tokenJSON"]) as r:
                if (statusCode := r.status) != 200:
                    errorDict = {
                        "statusCode":  statusCode,
                        "discordUUID": discordUUID,
                        "discordTag":  discordTag
                    }
                    ManualLogging.logErrorJSON(errorDict)
                    await message_author.send("Bot incurred status code {} while trying to connect to 2b2t.Place!\nError has been logged and will be fixed soon, apologies! 😵".format(str(statusCode)))
                else:
                    r_json = json.loads(await r.text())
                    if "nextTimeAllowed" in r_json:
                        await message_author.send("You may only choose a pixel once every 5 minutes! 😏\nNext token available at {} UTC".format(datetime.datetime.utcfromtimestamp(int(r_json["nextTimeAllowed"])).strftime("%Y-%m-%d %H:%M:%S")))
                    elif "token" in r_json:
                        await message_author.send("Your token is: '{}' 🎟️".format(r_json["token"]))
                    else:
                        errorDict = {
                            "statusCode":  "BAD_API_RESPONSE",
                            "discordUUID": discordUUID,
                            "discordTag":  discordTag,
                            "APIResponse": r_json
                        }
                        ManualLogging.logErrorJSON(errorDict)
                        await message_author.send("Bot received unexpected API response from 2b2t.Place!\nError has been logged and will be fixed soon, apologies! 😵")
    except aiohttp.client_exceptions.ClientConnectorError:
        errorDict = {
            "statusCode":  "FAILED_TO_CONNECT",
            "discordUUID": discordUUID,
            "discordTag":  discordTag
        }
        ManualLogging.logErrorJSON(errorDict)
        await message_author.send("Bot failed to connect to 2b2t.Place!\nError has been logged and will be fixed soon, apologies! 😵")

################################################################################

if __name__ == "__main__":
    try:
        with open("./botConfig_private.json") as botConfig_private_file:
            GLOBAL_BOTCONFIG_PRIVATE = json.load(botConfig_private_file)
    except FileNotFoundError:
        print("Error: File './botConfig_private.json' not found")
        raise SystemExit
    try:
        with open("./botConfig_public.json") as botConfig_public_file:
            GLOBAL_BOTCONFIG_PUBLIC = json.load(botConfig_public_file)
    except FileNotFoundError:
        print("Error: File './botConfig_public.json' not found")
        raise SystemExit

    client.run(GLOBAL_BOTCONFIG_PRIVATE["discordBotToken"])
