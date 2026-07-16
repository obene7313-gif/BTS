import discord
from discord.ext import commands
import random
import asyncio
import os
from flask import Flask
from threading import Thread

# --- 🌐 RENDER PORT BAĞLANTISI (Flask) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Aktif!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 🤖 BOT AYARLARI ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

# --- 📁 DİĞER DOSYADAN VERİLERİ ÇEKME ---
# Senin o 300 iltifatlık ve 100 selamlık dev listen bu dosyadan otomatik çekiliyor aşkım!
from iltifatlar import iltifatlar, selam_cevaplari

sorular = [
    {"soru": "567 - 45 kaçtır?", "cevap": "522"},
    {"soru": "789 - 123 kaçtır?", "cevap": "666"},
    {"soru": "7 * 8 kaçtır?", "cevap": "56"},
    {"soru": "12^2 (12'nin karesi) kaçtır?", "cevap": "144"},
    {"soru": "15 + 28 kaçtır?", "cevap": "43"},
    {"soru": "9 * 6 kaçtır?", "cevap": "54"},
    {"soru": "150 / 5 kaçtır?", "cevap": "30"},
    {"soru": "85 - 19 kaçtır?", "cevap": "66"}
]

# --- ⚙️ FİLTRE DEĞİŞKENLERİ ---
kufur_filtresi = False
reklam_filtresi = False
spam_filtresi = False
son_mesajlar = {}

# --- 🛡️ OTOMATİK FİLTRE SİSTEMLERİ ---
@bot.event
async def on_message(message):
    global kufur_filtresi, reklam_filtresi, spam_filtresi, son_mesajlar
    if message.author.bot:
        return

    # Spam Filtresi
    if spam_filtresi:
        ust_id = message.author.id
        simdi = asyncio.get_event_loop().time()
        if ust_id not in son_mesajlar:
            son_mesajlar[ust_id] = []
        son_mesajlar[ust_id].append(simdi)
        son_mesajlar[ust_id] = [t for t in son_mesajlar[ust_id] if simdi - t < 3]
        if len(son_mesajlar[ust_id]) > 3:
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, lütfen spam yapma!", delete_after=3)
            return

    # Küfür Filtresi
    if kufur_filtresi:
        kufurler = ["küfür1", "küfür2", "piç", "sik", "orospu", "amk", "aq"] 
        if any(kelime in message.content.lower() for kelime in kufurler):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda küfür etmek yasaktır!", delete_after=3)
            return

    # Reklam Filtresi
    if reklam_filtresi:
        linkler = ["http://", "https://", "discord.gg/"]
        if any(link in message.content.lower() for link in linkler):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda link/reklam paylaşımı yasaktır!", delete_after=3)
            return

    await bot.process_commands(message)

# --- 👑 YETKİLİ KONTROLÜ ---
def yetkili_kontrol():
    async def predict(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predict)

# --- 🛠️ FİLTRE KOMUTLARI ---
@bot.command()
@yetkili_kontrol()
async def kufurengel(ctx):
    global kufur_filtresi
    kufur_filtresi = not kufur_filtresi
    durum = "Aktif 🟢" if kufur_filtresi else "Devre Dışı 🔴"
    await ctx.send(f"🤬 **Küfür Filtresi:** {durum}")

@bot.command()
@yetkili_kontrol()
async def reklamengel(ctx):
    global reklam_filtresi
    reklam_filtresi = not reklam_filtresi
    durum = "Aktif 🟢" if reklam_filtresi else "Devre Dışı 🔴"
    await ctx.send(f"🔗 **Reklam Filtresi:** {durum}")

@bot.command()
@yetkili_kontrol()
async def spamengel(ctx):
    global spam_filtresi
    spam_filtresi = not spam_filtresi
    durum = "Aktif 🟢" if spam_filtresi else "Devre Dışı 🔴"
    await ctx.send(f"⚡ **Spam Filtresi:** {durum}")

# --- 🧼 SUNUCU TEMİZLİK / YÖNETİM ---
@bot.command()
@yetkili_kontrol()
async def nuke(ctx):
    ch = await ctx.guild.create_text_channel(name=ctx.channel.name, category=ctx.channel.category, topic=ctx.channel.topic)
    await ctx.channel.delete()
    await ch.send("💥 🌋 **Kanal Sıfırlandı!** ✨")

# --- 🎮 EĞLENCE & ETKİLEŞİM KOMUTLARI ---
@bot.command()
async def slaps(ctx, member: discord.Member):
    await ctx.send(f"✋ {ctx.author.mention}, {member.mention} kullanıcısına sert bir tokat attı! Öfkesi dindi mi acaba? 🤫")

@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"💋 {ctx.author.mention}, {member.mention} kullanıcısını yanaktan kocaman öptü! Ortam ısındı sanki... 🥰")

@bot.command()
async def ship(ctx):
    uyeler = [m for m in ctx.guild.members if not m.bot]
    if len(uyeler) < 2:
        await ctx.send("Sunucuda ship yapacak yeterli üye yok canım! 😔")
        return
    u1, u2 = random.sample(uyeler, 2)
    oran = random.randint(0, 100)
    iltifat_mesaji = random.choice(iltifatlar)
    await ctx.send(f"💟 **Aşk Ölçer Rastgele Seçti!** 💟\n👥 **{u1.mention}**  x  **{u2.mention}**\n💘 **Aşk Oranı:** %{oran}\n✨ *{iltifat_mesaji}*")

@bot.command()
async def ship2(ctx, member: discord.Member):
    await ctx.send(f"💟 **Özel Aşk Ölçer** 💟\n👥 {ctx.author.mention} x {member.mention}\n💘 **Aşk Oranı:** %99999% \n👑 **Bu aşk ölçülemez!** 👑")

@bot.command()
async def askolcer(ctx, member: discord.Member):
    oran = random.randint(0, 100)
    await ctx.send(f"💓 {ctx.author.mention} ile {member.mention} arasındaki aşk oranı: **%{oran}** 💓")

# --- 💰 BASİT EKONOMİ SİSTEMİ ---
ekonomi_cuzdan = {}

@bot.command()
async def para(ctx, member: discord.Member = None):
    h = member or ctx.author
    await ctx.send(f"💰 {h.mention}: **{ekonomi_cuzdan.get(h.id, 100)}** BTS Parası**")

@bot.command()
async def slots(ctx, miktar: int):
    c = ekonomi_cuzdan.get(ctx.author.id, 100)
    if miktar <= 0 or miktar > c: 
        return await ctx.send("❌ Bakiye yetersiz veya geçersiz miktar!")
    res = [random.choice(["🍒", "🍇", "🍋", "🍊", "🍉"]) for _ in range(3)]
    if res[0] == res[1] == res[2]:
        ekonomi_cuzdan[ctx.author.id] = c + (miktar * 3)
        await ctx.send(f"🎰 | {res[0]} | {res[1]} | {res[2]} | \n🥳 **3'te 3! Kazandın!**")
    else:
        ekonomi_cuzdan[ctx.author.id] = c - miktar
        await ctx.send(f"🎰 | {res[0]} | {res[1]} | {res[2]} | \n😭 **Kaybettin...**")

# --- ℹ️ BİLGİ KOMUTLARI ---
@bot.command()
async def spty(ctx, member: discord.Member = None):
    h = member or ctx.author
    sp = next((a for a in h.activities if isinstance(a, discord.Spotify)), None)
    if not sp: 
        return await ctx.send("🎧 Spotify dinlenmiyor.")
    embed = discord.Embed(title=f"🎧 {h.name} Spotify", color=discord.Color.green())
    embed.add_field(name="🎵 Şarkı", value=sp.title)
    embed.add_field(name="🎤 Sanatçı", value=", ".join(sp.artists))
    embed.set_thumbnail(url=sp.album_cover_url)
    await ctx.send(embed=embed)

@bot.command()
async def kullanici(ctx, member: discord.Member = None):
    h = member or ctx.author
    embed = discord.Embed(title="👤 Kullanıcı Bilgisi", color=discord.Color.blue())
    embed.add_field(name="İsim", value=h.name)
    embed.add_field(name="ID", value=h.id)
    embed.add_field(name="Katılma Tarihi", value=h.joined_at.strftime("%d/%m/%Y"))
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    embed = discord.Embed(title="🏰 Sunucu Bilgisi", color=discord.Color.purple())
    embed.add_field(name="Sunucu Adı", value=ctx.guild.name)
    embed.add_field(name="Üye Sayısı", value=ctx.guild.member_count)
    await ctx.send(embed=embed)

# --- 🧠 SORU CEVAP OYUNU ---
@bot.command()
async def sorusor(ctx):
    soru_sec = random.choice(sorular)
    await ctx.send(f"🧠 **Soru Geldi:** {soru_sec['soru']}\n⏱️ *Cevap vermek için 15 saniyen var!*")
    
    def check(m):
        return m.channel == ctx.channel and not m.author.bot
        
    try:
        msg = await bot.wait_for('message', check=check, timeout=15.0)
        if msg.content.strip() == soru_sec['cevap']:
            await ctx.send(f"🎉 Tebrikler {msg.author.mention}! Doğru cevap verdi: **{soru_sec['cevap']}**")
        else:
            await ctx.send(f"❌ Yanlış cevap! Doğru cevap **{soru_sec['cevap']}** olacaktı.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏱️ Süre bitti! Kimse cevap veremedi. Doğru cevap: **{soru_sec['cevap']}**")

# --- 🌸 YARDIM MENÜSÜ KOMUTU ---
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🌸 Bot Menüsü 🌸", description=f"Merhaba {ctx.author.mention}! İşte tüm komutlarım:", color=discord.Color.gold())
    embed.add_field(name="🛡️ Filtreler (Yönetici)", value="`!kufurengel`, `!reklamengel`, `!spamengel`", inline=False)
    embed.add_field(name="🧼 Sunucu Yönetimi", value="`!nuke`", inline=False)
    embed.add_field(name="🎮 Eğlence & Etkileşim", value="`!slaps @üye`, `!kiss @üye`, `!ship`, `!ship2 @üye`, `!askolcer @üye`", inline=False)
    embed.add_field(name="🧠 Oyunlar", value="`!sorusor`", inline=False)
    embed.add_field(name="💰 Ekonomi", value="`!para`, `!slots <miktar>`", inline=False)
    embed.add_field(name="ℹ️ Bilgi Sistemleri", value="`!spty`, `!kullanici`, `!sunucu`", inline=False)
    await ctx.send(embed=embed)

# --- 🚀 BOTU BAŞLATMA ---
@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} olarak başarıyla giriş yaptı!")

keep_alive()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
    
