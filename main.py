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

    review_channel = bot.get_channel(config.review_channel)

    if review_channel:
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

bot.run(
    os.getenv("TOKEN")
)