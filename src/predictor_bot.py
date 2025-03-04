# -*- coding: utf-8 -*-
"""
This bot is a wrapper for my League of Legends esports prediction model.
It is intended to allow users to call down predictions. 
"""

# Housekeeping
import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
import pandas as pd
from pathlib import Path
import src.match_predictor as mp
import nest_asyncio

nest_asyncio.apply()

# Variable Definitions
load_dotenv()
token = getenv("DISCORD_TOKEN")

client = discord.Client()
helper = """This is ProjektZero's bot. Ask him about it. Eventually I'll put a real readme here."""

bot = commands.Bot(command_prefix='!')


# Party Time
@bot.command(name='schedule')
async def schedule(ctx, league):
    try:
        output = pd.read_csv(Path.cwd().parent.joinpath('data', 'processed', 'schedule.csv'))
        output = output[output["league"] == league].drop(['league'], axis=1).reset_index(drop=True)
        output = f"Upcoming {league} Games (Next 10 Games Within 5 Days): \n \n" \
                 f"`{output.head(10).to_markdown()}` \n \n" \
                 "NOTE: Win percentages use the last fielded roster! Try predict_draft if you need substitutions."
    except Exception as e:
        output = f"Something went wrong, sorry about that. \n" \
                 "If this is still breaking, ping ProjektZero for support. \n" \
                 "Error: \n" \
                 f"```{e}```"

    await ctx.send(content=output)


@bot.command(name='profile')
async def profile(ctx, entity):
    try:
        players = pd.read_csv(Path.cwd().parent.joinpath('data', 'processed', 'flattened_players.csv'))
        teams = pd.read_csv(Path.cwd().parent.joinpath('data', 'processed', 'flattened_teams.csv'))

        players_list = [p.lower() if isinstance(p, str) else p for p in players.playername.unique()]
        teams_list = [t.lower() if isinstance(t, str) else t for t in teams.teamname.unique()]
        lower_entity = str(entity).lower()

        if lower_entity in players_list:
            data = players[players.playername.str.lower() == lower_entity].to_dict(orient="records")[0]
            output = f"{entity} Profile: \n \n" \
                     f"`Position: {data['position']} \n" \
                     f"Elo: {data['player_elo']:.2f} \n" \
                     f"TrueSkill Mu: {data['trueskill_mu']:.2f} \n" \
                     f"EGPM Dominance: {data['egpm_dominance_ema_after']:.2f} \n" \
                     f"K/D/A Ratio: {data['kda']:.2f} \n" \
                     f"Gold Diff At 15: {data['golddiffat15']:.2f} \n" \
                     f"CS Diff At 15: {data['csdiffat15']:.2f} \n" \
                     f"DK Points: {data['dkpoints']:.2f}`"
        elif lower_entity in teams_list:
            data = teams[teams.teamname.str.lower() == lower_entity].to_dict(orient="records")[0]
            output = f"{entity} Profile: \n \n" \
                     f"`Elo: {data['team_elo']:.2f} \n" \
                     f"TrueSkill Mu: {data['trueskill_sum_mu']:.2f} \n" \
                     f"EGPM Dominance: {data['egpm_dominance_ema_after']:.2f} \n" \
                     f"K/D/A Ratio: {data['kda']:.2f} \n" \
                     f"Gold Diff At 15: {data['golddiffat15']:.2f} \n" \
                     f"CS Diff At 15: {data['csdiffat15']:.2f} \n" \
                     f"DK Points: {data['dkpoints']:.2f}`"
        else:
            output = f"Data for {entity} not found in database. \n" \
                     "Make sure that your spelling perfectly matches the Oracle's Elixir data."
    except Exception as e:
        output = f"Something went wrong, sorry about that. \n" \
                 "If this is still breaking, ping ProjektZero for support. \n" \
                 "Error: \n" \
                 f"```{e}```"

    await ctx.send(content=output)


@bot.command(name='predict_draft')
async def predict_draft(ctx, blue_team, blue1, blue2, blue3, blue4, blue5, red_team, red1, red2, red3, red4, red5):
    prelim = "```Calculating...```"
    message = await ctx.send(content=prelim)

    try:
        output = mp.predict_draft(blue_team, blue1, blue2, blue3, blue4, blue5,
                                  red_team, red1, red2, red3, red4, red5)
    except Exception as e:
        output = f"Something went wrong, sorry about that. \n" \
                 "If this is still breaking, ping ProjektZero for support. \n" \
                 "Error: \n" \
                 f"```{e}```"
    await message.edit(content=output)


@bot.command(name='mock_draft')
async def mock_draft(ctx, blue1, blue2, blue3, blue4, blue5,
                     red1, red2, red3, red4, red5):
    prelim = "```Calculating...```"
    message = await ctx.send(content=prelim)

    try:
        output = mp.mock_draft(blue1, blue2, blue3, blue4, blue5, red1, red2, red3, red4, red5)
    except Exception as e:
        output = f"Something went wrong, sorry about that. \n" \
                 "If this is still breaking, ping ProjektZero for support. \n" \
                 "Error: \n" \
                 f"```{e}```"
    await message.edit(content=output)


bot.run(token)
