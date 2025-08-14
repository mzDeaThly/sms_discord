import discord
from discord import app_commands
import requests
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("API_URL", "https://your-api.onrender.com/api/sms")

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

@client.tree.command(name="sms", description="ส่ง SMS spam ไปยังเบอร์ที่ระบุ")
@app_commands.describe(phone="เบอร์โทรศัพท์", count="จำนวนครั้งที่จะส่ง")
async def sms(interaction: discord.Interaction, phone: str, count: int):
    await interaction.response.defer(thinking=True)
    try:
        resp = requests.get(API_URL, params={"phone": phone, "count": count})
        data = resp.json()
        if resp.status_code == 200:
            await interaction.followup.send(f"✅ ส่ง SMS ไปที่ `{phone}` จำนวน `{count}` ครั้งแล้ว")
        else:
            await interaction.followup.send(f"❌ Error: {data.get('error', 'ไม่ทราบสาเหตุ')}")
    except Exception as e:
        await interaction.followup.send(f"⚠ ไม่สามารถเชื่อมต่อ API ได้: {e}")

client.run(TOKEN)
