from flask import Blueprint, render_template

# import aiohttp

bp = Blueprint("cambridge", __name__)


@bp.route("/cambridge")
def departure():
    return render_template("nowplaying.html")


# @bp.route("/cxn", methods=("GET", "POST"))
# async def get_now_playing():
#     now_playing = list()
#     async with aiohttp.ClientSession() as session:
#         async with session.get("http://192.168.1.29/smoip/zone/play_state") as resp:
#             now_playing = await resp.json()
#             print(now_playing["data"]["metadata"]["title"])

#     return render_template("departure_tables.html")
