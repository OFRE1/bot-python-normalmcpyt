import os
import asyncio
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# ================= 1. CẤU HÌNH WEB SERVER GIỮ SỐNG (RENDER/RAILWAY) =================
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is alive and running!", 200


def run_web():
  # Lấy cổng port do Cloud tự cấp, mặc định chạy port 8080
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)


def keep_alive():
  t = Thread(target=run_web)
  t.daemon = True
  t.start()


# ================= 2. CẤU HÌNH DISCORD BOT =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Khởi tạo bot với prefix là dấu chấm than '!'
bot = commands.Bot(command_prefix="!", intents=intents)

# Thay ID Role xác thực của server cậu vào đây
VERIFIED_ROLE_ID = 123456789012345678  # <-- ĐIỀN ID ROLE CỦA CẬU VÀO ĐÂY

# Biến lưu trữ tạm cho tính năng Snipe theo từng Channel
snipe_cache = {}


# ================= 3. HỆ THỐNG NÚT BẤM XÁC THỰC (PERSISTENT VIEW) =================
class VerifyView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)  # Vĩnh viễn không hết hạn nút

  @discord.ui.button(
      label="Xác thực ngay",
      style=discord.ButtonStyle.green,
      custom_id="verify_button_fixed_01",
      emoji="✅",
  )
  async def verify_button(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    # Tránh lỗi 3 giây timeout của Discord API
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


# ================= 4. SỰ KIỆN KHI BOT SẴN SÀNG =================
@bot.event
async def on_ready():
  # Đăng ký View vĩnh viễn để nút bấm không bị "chết" khi restart bot
  bot.add_view(VerifyView())
  print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
  print("Bot đã sẵn sàng và kích hoạt View thành công!")


# ================= 5. LỆNH TẠO BẢNG XÁC THỰC (ADMIN/MOD ONLY) =================
@bot.command(name="verify")
@commands.has_permissions(manage_guild=True)
async def send_verify_panel(ctx):
  # Cố gắng xóa tin nhắn gọi lệnh của mod, nếu thiếu quyền thì bỏ qua an toàn
  try:
    await ctx.message.delete()
  except Exception:
    pass

  embed = discord.Embed(
      title="🛡️ XÁC THỰC THÀNH VIÊN",
      description="DEV ĐANG THỬ NGHIỆM. CLICK ✅ ĐỂ TEST",
      color=discord.Color.green(),
  )

  await ctx.send(embed=embed, view=VerifyView())


# Bắt lỗi khi thành viên thường táy máy gõ lệnh verify
@send_verify_panel.error
async def send_verify_panel_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send(
        "❌ Whoops, bạn không phải quản lý. Lệnh này không hoạt động",
        delete_after=5,
    )


# ================= 6. TÍNH NĂNG SNIPE (ĐÃ VÁ LỖI GHI ĐÈ CACHE) =================
@bot.event
async def on_message_delete(message):
  # Bỏ qua tin nhắn của bot hoặc lệnh snipe để tránh ghi đè rác
  if message.author.bot or message.content.startswith("!snipe"):
    return

  snipe_cache[message.channel.id] = {
      "content": message.content,
      "author": message.author,
  }


@bot.command(name="snipe")
async def snipe(ctx):
  data = snipe_cache.get(ctx.channel.id)
  if not data:
    await ctx.send("Làm gì có ai xóa tin nhắn nào gần đây đâu mà hớt hải! 👀")
    return

  await ctx.send(
      f"🎯 Bắt được quả tang tin nhắn vừa bay màu của **{data['author']}**:\n> "
      f"{data['content']}"
  )


# ================= 7. KHỞI CHẠY CHƯƠNG TRÌNH =================
if __name__ == "__main__":
  # Kích hoạt Flask server chạy ngầm phục vụ UptimeRobot ping chống ngủ đông
  keep_alive()

  # Lấy Token từ biến môi trường của hệ thống (Railway / Render)
  TOKEN = os.getenv("DISCORD_TOKEN")
  if not TOKEN:
    print(
        "❌ LỖI NGHIÊM TRỌNG: Chưa thiết lập biến môi trường DISCORD_TOKEN trên"
        " Cloud!"
    )
  else:
    bot.run(TOKEN)
