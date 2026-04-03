import json

import disnake
from disnake.ext import commands
from dotenv import load_dotenv
import os
import config
import datetime

load_dotenv()

intents = disnake.Intents.all()

bot = commands.Bot(
    intents=intents
)

@bot.slash_command(
    name="review",
    description="Submit a review for my services!"
)
async def review(interaction, service: str, message: str, rating: commands.Range[int, 1, 5]):
    await interaction.response.defer(ephemeral=True)

    client_role = interaction.guild.get_role(config.client_id)
    if client_role not in interaction.user.roles:
        await interaction.edit_original_response(content="You must be a client to submit a review.")
        return
    
    with open("allowance.json", "r") as f:
        allowance = json.load(f)
        user_points = allowance.get(str(interaction.user.id))

        if not user_points:
            allowance[str(interaction.user.id)] = 0

        if user_points == 0:
            await interaction.edit_original_response(content="Failed to give review, insufficient review points!")
            return

    review_channel = bot.get_channel(config.review_channel)

    if review_channel:

        with open("allowance.json", "r") as f:
            allowance = json.load(f)
            user_points = allowance.get(str(interaction.user.id))

            if not user_points:
                allowance[str(interaction.user.id)] = 0

            if user_points - 1 < 0:
                await interaction.edit_original_response(content="Failed to give review, insufficient review points!")
                return
            else:
                allowance[str(interaction.user.id)] = 0
        
        with open("allowance.json", "w") as f:
            json.dump(allowance, f)

        embed = disnake.Embed(
            title=service,
            description=message
        )

        embed.color = disnake.Color.gold()

        stars = ""

        for _ in range(rating):
            stars = stars + "⭐"
        
        for _ in range(5 - rating):
            stars = stars + "⚫"
        
        embed.add_field(name="Rating", value=f"{rating}/5 ({stars})")

        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        
        embed.set_footer(text="Powered by Atomic Services.")

        embed.timestamp = datetime.datetime.now()

        await review_channel.send(embed=embed)
    else:
        await interaction.edit_original_response(content="An error occurred while sending your review, please try again later.")
        return
    
    await interaction.edit_original_response(content="Thank you for the review, your review has been received!")

@bot.slash_command(
    name="give_review_allowance",
    description="Give a user the ability to submit reviews."
)
async def give_review_allowance(interaction, user: disnake.User):
    await interaction.response.defer(ephemeral=True)

    if not interaction.user.guild_permissions.administrator:
        await interaction.edit_original_response(content="You must be an administrator to give review allowance!")
        return
    
    client_role = interaction.guild.get_role(config.client_id)
    if client_role not in user.roles:
        await interaction.edit_original_response(content="User must be a client to submit a review.")
        return
    
    with open("allowance.json", "r") as f:
        allowance = json.load(f)

        if allowance.get(str(user.id)):
            allowance[str(user.id)] += 1
        else:
            allowance[str(user.id)] = 1

    with open("allowance.json", "w") as f:
        json.dump(allowance, f)

    await interaction.edit_original_response(content=f"Gave review allowance to {user.mention}. User currently has {allowance[str(user.id)]} points!")

@bot.slash_command(
    name="check_review_allowance",
    description="Checks a user the ability to submit reviews."
)
async def check_review_allowance(interaction, user: disnake.User):
    await interaction.response.defer(ephemeral=True)

    if not interaction.user.guild_permissions.administrator:
        await interaction.edit_original_response(content="You must be an administrator to give review allowance!")
        return
    
    client_role = interaction.guild.get_role(config.client_id)
    if client_role not in user.roles:
        await interaction.edit_original_response(content="User must be a client to submit a review.")
        return
    
    with open("allowance.json", "r") as f:
        allowance = json.load(f)
        if not allowance.get(str(user.id)):
            allowance[str(user.id)] = 0

            with open("allowance.json", "w") as f:
                json.dump(allowance, f)

            await interaction.edit_original_response(f"{user.mention} has 0 points!")
            return
        else:
            await interaction.edit_original_response(f"{user.mention} has {allowance[str(user.id)]} points!")
            return
    
    await interaction.edit_original_response(f"Unable to open file!")
        
bot.run(
    os.getenv("TOKEN")
)