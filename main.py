import requests
import nextcord
import logging
import coloredlogs
import json
import asyncio
import aiohttp
import time

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log)

storage = {}

with open('settings.json', 'r') as f:
    settings = json.load(f)

def cLog(message):
    log.debug(f"[+] APPLE AIO | {message}")
    return

def getAppleJobOpenings():
    resp = requests.get('https://jobs.apple.com/api/v1/jobDetails/PIPE-114438151/storeLocations?fieldValue=postLocation-SFMETRO')
    if resp.status_code != 200:
       cLog(f"Error: {resp.status_code}")
       return None
    return resp.json()

async def notifyUser(i):
    global settings
    webhook = settings['webhook']
    embed = nextcord.Embed(title="Apple Job Opening", description="Apple Job Opening", color=0xFFFFFF)
    embed.set_author(
        name='Apple Job Opening',
        icon_url='https://1000logos.net/wp-content/uploads/2016/10/apple-emblem.jpg'
    )
    embed.set_footer(
        text="Apple Job Opening",
        icon_url='https://1000logos.net/wp-content/uploads/2016/10/apple-emblem.jpg'
    )
    embed.add_field(name="**City**", value=f"{i['city']}", inline=True)
    embed.add_field(name="**Location**", value=f"{i['locationId']}", inline=True)
    embed.add_field(name="**Name**", value=f"{i['name']}", inline=True)
    async with aiohttp.ClientSession() as session:
        webhook = nextcord.Webhook.from_url(webhook,session = session)
        await webhook.send(embed=embed)

def start():
    global settings
    while True:
        openings = getAppleJobOpenings()
        for i in openings:
            if i['currentOpening'] and storage.get('postLocation-R824',{"beenOpen":False})['beenOpen'] == False:
                cLog(f"New Job Opening: {i['locationId']}")
                storage['postLocation-R824'] = {"beenOpen":True}
                if settings['webhook'].startswith("https://"):
                    asyncio.run(notifyUser(i))
                break
            elif i['currentOpening'] and storage.get('postLocation-R824',{"beenOpen":False})['beenOpen'] == True:
                break
        time.sleep(settings['delay'])

if __name__ == "__main__":
    start()

    
