import discord
from discord.ext import commands

# Cấu hình Intents (Bắt buộc phải bật intents.members)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === ĐIỀN THÔNG TIN CỦA BẠN VÀO ĐÂY ===
VERIFIED_ROLE_ID = 1502170743235149864  # Thay bằng ID của Role "Thành viên" sau khi verify
BOT_TOKEN = "MTQ2MTM3MDE0MDEzMzE2MzMwNg.G90Gar.hAQnKjyNGDHd3hZbMswXoQqyt0Lz_oZGR40DF4"  # Thay bằng Token Bot Discord của bạn
# ======================================


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


# Chạy bot
bot.run(BOT_TOKEN)