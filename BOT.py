import os
import random
import urllib.parse
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

# ==================== FLASK SERVER (MỞ CỔNG CHỜ 24/7) ====================
app = Flask("")


@app.route("/")
def home():
  return "Bot is alive and running!"


def run_flask():
  app.run(host="0.0.0.0", port=8080)


def keep_alive():
  t = Thread(target=run_flask)
  t.start()


# ==================== CẤU HÌNH BOT ====================
# Bật các Intents cần thiết
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Khởi tạo bot với tiền tố lệnh là "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# FIX LỖI TRÙNG LỆNH: Xóa lệnh help mặc định đi để nhường chỗ cho lệnh custom
bot.remove_command("help")

# ID Role xác thực (đã cấu hình từ trước)
VERIFIED_ROLE_ID = 1502170743235149864


# ==================== VIEW NÚT XÁC THỰC (VERIFY) ====================
class VerifyView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)  # Vĩnh viễn không hết hạn nút

  @discord.ui.button(
      label="Xác thực ngay",
      style=discord.ButtonStyle.green,
      custom_id="verify_button",
      emoji="✅",
  )
  async def verify_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    # Tránh lỗi 3 giây timeout của Discord
    await interaction.response.defer(ephemeral=True)

    role = interaction.guild.get_role(VERIFIED_ROLE_ID)
    if not role:
      await interaction.followup.send(
          "⚠️ Lỗi hệ thống: Không tìm thấy Role xác thực trong Server!",
          ephemeral=True,
      )
      return

    if role in interaction.user.roles:
      await interaction.followup.send(
          "✨ Bạn đã được xác thực từ trước rồi mà!", ephemeral=True
      )
    else:
      await interaction.user.add_roles(role)
      await interaction.followup.send(
          "🎉 Xác thực thành công! Toàn bộ kênh chat đã được mở khóa.",
          ephemeral=True,
      )


# ==================== SỰ KIỆN KHI BOT SẴN SÀNG ====================
@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
  print("Bot is ready and connected to Discord!")


# ==================== CÁC LỆNH MỚI BỔ SUNG ====================


# 1. Lệnh !coin (Tung đồng xu)
@bot.command(name="coin")
async def coin_flip(ctx):
  result = random.choice(["Mặt Ngửa (Heads) 🪙", "Mặt Sấp (Tails) 🪙"])
  await ctx.send(f"Kết quả tung đồng xu cho {ctx.author.mention}: **{result}**")


# 2. Lệnh !snipe (Xem tin nhắn bị xóa gần đây)
snipe_cache = {}


@bot.event
async def on_message_delete(message):
  if message.author.bot:
    return
  snipe_cache[message.channel.id] = {
      "content": message.content,
      "author": message.author,
  }


@bot.command(name="snipe")
async def snipe(ctx):
  deleted = snipe_cache.get(ctx.channel.id)
  if not deleted:
    await ctx.send("Làm gì có ai xóa tin nhắn nào gần đây đâu mà hớt hải! 👀")
    return

  embed = discord.Embed(
      title="🎯 Bắt được quả tang tin nhắn vừa bay màu:",
      description=deleted["content"],
      color=discord.Color.red(),
  )
  embed.set_author(
      name=str(deleted["author"]),
      icon_url=deleted["author"].avatar.url
      if deleted["author"].avatar
      else None,
  )
  await ctx.send(embed=embed)


# 3. Lệnh !help (Hiện list lệnh đã custom)
@bot.command(name="help")
async def custom_help(ctx):
  embed = discord.Embed(
      title="📜 Danh sách lệnh hệ thống", color=discord.Color.blue()
  )
  embed.add_field(
      name="!coin", value="Tung đồng xu sấp/ngửa may rủi.", inline=False
  )
  embed.add_field(
      name="!snipe",
      value="Xem lại tin nhắn vừa bị xóa gần đây trong kênh.",
      inline=False,
  )
  embed.add_field(
      name="!search youtube <từ khóa>",
      value="Tìm kiếm nhanh video trên YouTube.",
      inline=False,
  )
  embed.add_field(
      name="!search google <từ khóa>",
      value="Tra cứu thông tin trên Google.",
      inline=False,
  )
  await ctx.send(embed=embed)


# 4 & 5. Lệnh !search youtube và google
@bot.command(name="search")
async def search_query(ctx, platform: str, *, query: str):
  query_encoded = urllib.parse.quote(query)
  platform = platform.lower()

  if platform == "youtube":
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    await ctx.send(f"📺 Kết quả tìm kiếm YouTube cho **'{query}'**: {url}")
  elif platform == "google":
    url = f"https://www.google.com/search?q={query_encoded}"
    await ctx.send(f"🔍 Kết quả tra cứu Google cho **'{query}'**: {url}")
  else:
    await ctx.send(
        "⚠️ Nền tảng không hợp lệ! Cú pháp đúng: `!search youtube <từ"
        " khóa>` hoặc `!search google <từ khóa>`."
    )


# ==================== KHỞI ĐỘNG BOT ====================
if __name__ == "__main__":
  # Chạy Flask server để qua mặt cổng port của Render
  keep_alive()

  # Token bảo mật (đã được bọc ngoặc kép an toàn)
  BOT_TOKEN = (
      "MTQ2MTM3MDE0MDEzMzE2MzMwNg.GzjDyn.F1OQe7L24zGqox1Q-BwfD5OYGeKY-F7uMdZwYs"
  )
  bot.run(BOT_TOKEN)
