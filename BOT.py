import os


# TOKEN GET BOT
BOT_TOKEN = (
  "MTQ2MTM3MDE0MDEzMzE2MzMwNg.GzjDyn.F1OQe7L24zGqox1Q-BwfD5OYGeKY-F7uMdZwYs"
)
from threading import Thread
import discord
from discord.ext import commands
from flask import Flask

# ================= CẤU HÌNH TOKEN & ROLE =================
VERIFIED_ROLE_ID = 1502170743235149864


# ================= FLASK SERVER (MỞ CỔNG CHO RENDER) =================
app = Flask("")


@app.route("/")
def home():
  return "Bot is running 24/7!"


def run():
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)


def keep_alive():
  t = Thread(target=run)
  t.start()


# ================= KHỞI TẠO BOT & GIAO DIỆN =================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
class VerifyView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)  # Giữ nút tồn tại vĩnh viễn không hết hạn

  @discord.ui.button(
      label="Xác thực ngay",
      style=discord.ButtonStyle.green,
      custom_id="verify_button_click",
      emoji="✅",
  )
  async def verify_callback(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    # Lấy role từ ID server
    role = interaction.guild.get_role(VERIFIED_ROLE_ID)

    if not role:
      await interaction.response.send_message(
          "⚠️ Lỗi: Không tìm thấy Role xác thực trong cài đặt bot!",
          ephemeral=True,
      )
      return

    # Kiểm tra xem user đã có role đó chưa
    if role in interaction.user.roles:
      await interaction.response.send_message(
          "😄 Bạn đã xác thực từ trước rồi mà!", ephemeral=True
      )
    else:
      # Thêm role cho thành viên
      await interaction.user.add_roles(role)
      await interaction.response.send_message(
          "🎉 **Xác thực thành công!** Chào mừng bạn đã đến với server.",
          ephemeral=True,
      )


@bot.event
async def on_ready():
  print(f"Bot {bot.user} đã sẵn sàng hoạt động!")


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_verify(ctx):
  """Lệnh gửi khung Embed xác thực ra kênh hiện tại (Chỉ Admin dùng được)"""
  embed = discord.Embed(
      title="🛡️ XÁC THỰC TÀI KHOẢN (VERIFICATION)",
      description=(
          "Chào mừng bạn đến với server!\n\n"
          "Để mở khóa toàn bộ kênh chat và tham gia trò chuyện cùng mọi người,"
          " vui lòng nhấn nút **Xác thực ngay** bên dưới."
          "Kênh chỉ hiển thị với member chưa xác minh"
      ),
      color=discord.Color.brand_green(),
  )
  embed.set_footer(text="Hệ thống bảo mật tự động của server.")

  # Gửi tin nhắn kèm theo nút bấm (View)
  await ctx.send(embed=embed, view=VerifyView())
  await ctx.message.delete()  # Xóa tin nhắn lệnh !setup_verify cho sạch kênh

import discord
from discord.ext import commands

# Giả sử bot đã được khởi tạo bằng: bot = commands.Bot(command_prefix="!", ...)


# 1. Lệnh !coin (Tung đồng xu)
@bot.command(name="coin")
async def coin_flip(ctx):
  import random

  result = random.choice(["Mặt Ngửa (Heads) 🪙", "Mặt Sấp (Tails) 🪙"])
  await ctx.send(f"Kết quả tung đồng xu cho {ctx.author.mention}: **{result}**")


# 2. Lệnh !snipe (Xem tin nhắn bị xóa gần đây)
# Cần bật Message Content Intent ở Discord Developer Portal nhé
snipe_cache = {}


@bot.event
async def on_message_delete(message):
  if message.author.bot:
    return
  snipe_cache[message.channel.id] = {
      "content": message.content,
      "author": message.author,
      "time": message.created_at,
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
  embed.set_author(name=str(deleted["author"]), icon_url=deleted["author"].avatar.url if deleted["author"].avatar else None)
  await ctx.send(embed=embed)


# 3. Lệnh !help (Hiện list lệnh - custom lại cho gọn)
@bot.command(name="help")
async def custom_help(ctx):
  embed = discord.Embed(
      title="📜 Danh sách lệnh của hệ thống",
      color=discord.Color.blue(),
  )
  embed.add_field(name="!coin", value="Tung đồng xu sấp/ngửa may rủi.", inline=False)
  embed.add_field(name="!snipe", value="Xem lại tin nhắn vừa bị xóa trong kênh.", inline=False)
  embed.add_field(name="!search youtube <từ khóa>", value="Tìm kiếm nhanh trên YouTube.", inline=False)
  embed.add_field(name="!search google <từ khóa>", value="Tra cứu thông tin trên Google.", inline=False)
  await ctx.send(embed=embed)


# 4 & 5. Lệnh !search youtube và google
@bot.command(name="search")
async def search_query(ctx, platform: str, *, query: str):
  import urllib.parse

  query_encoded = urllib.parse.quote(query)
  platform = platform.lower()

  if platform == "youtube":
    url = f"https://www.youtube.com/results?search_query={query_encoded}"
    await ctx.send(f"📺 Kết quả tìm kiếm YouTube cho **'{query}'**: {url}")
  elif platform == "google":
    url = f"https://www.google.com/search?q={query_encoded}"
    await ctx.send(f"🔍 Kết quả tra cứu Google cho **'{query}'**: {url}")
  else:
    await ctx.send("⚠️ Nền tảng không hợp lệ! Cú pháp đúng: `!search youtube <từ khóa>` hoặc `!search google <từ khóa>`.")
# Chạy bot
if __name__ == "__main__":
  keep_alive()  # Kích hoạt web server ngầm
  bot.run(BOT_TOKEN)  # Chạy bot
