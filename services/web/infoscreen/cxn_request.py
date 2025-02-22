#!/usr/bin/env python3
import aiohttp
import asyncio


async def get_now_playing():

    async with aiohttp.ClientSession() as session:
        async with session.get("http://192.168.1.29/smoip/zone/play_state") as resp:
            now_playing = await resp.json()
            print(now_playing["data"]["metadata"]["title"])

    # return now_playing.data


if __name__ == "__main__":
    asyncio.run(get_now_playing())
# print(f"Play State: {test.metadata.station}")
