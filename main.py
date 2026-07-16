import discord
from discord.ext import commands
import random
import asyncio
from datetime import timedelta, datetime
import os
from threading import Thread
from flask import Flask

# Yan taraftaki iltifatlar.py dosyasından çekiyoruz
from iltifatlar import iltifatlar, selam_cevaplari

# --- 🌐 Render Web Service Kapanma Önleyici (Flask) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot aktif ve 7/24 çalışıyor! 🌸"

def run_web():
    # Render'ın dinamik olarak atadığı portu yakalıyoruz (Hata almamak için çok önemli!)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Sunucuyu bot başlamadan hemen önce hayata geçiriyoruz
keep_alive()
# -----------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

sunucu_ayarlari = {
    "kufur_filtresi": False,
    "reklam_filtresi": False,
    "spam_filtresi": False,
    "log_kanali": None,
    "giris_cikis_kanali": None
}

yasakli_kelimeler = ["küfür1", "küfür2", "argo1"]
ekonomi_cuzdan = {}
spam_takip = {}

def matematik_sorusu_uret():
    tipler = ['toplama', 'cikarma', 'carpma', 'us']
    secilen = random.choice(tipler)
    if secilen == 'toplama':
        a, b = random.randint(100, 999), random.randint(100, 999)
        return f"{a}+{b}", str(a + b)
    elif secilen == 'cikarma':
        a, b = random.randint(100, 999), random.randint(10, 99)
        return f"{a}-{b}", str(a - b)
    elif secilen == 'carpma':
        a, b = random.randint(5, 15), random.randint(6, 9)
        return f"{a}*{b}", str(a * b)
    elif secilen == 'us':
        a = random.choice([11, 12, 13, 14, 15, 20, 25])
        return f"{a}^2", str(a ** 2)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower() == "sa":
        await message.channel.send(f"Aleyküm Selam {message.author.mention}, hoş geldin! 🌸✨")
        return

    if sunucu_ayarlari["kufur_filtresi"]:
        for kelime in yasakli_kelimeler:
            if kelime in message.content.lower():
                try:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, lütfen kelimelerimize dikkat edelim!", delete_after=5)
                    if sunucu_ayarlari["log_kanali"]:
                        log_ch = bot.get_channel(sunucu_ayarlari["log_kanali"])
                        if log_ch: await log_ch.send(f"🛡️ **Küfür Engellendi:** {message.author.name} -> `{message.content}`")
                except: pass
                return

    if sunucu_ayarlari["reklam_filtresi"]:
        if "http://" in message.content.lower() or "https://" in message.content.lower() or "discord.gg" in message.content.lower():
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda reklam yapmak yasaktır!", delete_after=5)
                if sunucu_ayarlari["log_kanali"]:
                    log_ch = bot.get_channel(sunucu_ayarlari["log_kanali"])
                    if log_ch: await log_ch.send(f"🛡️ **Reklam Engellendi:** {message.author.name} -> `{message.content}`")
            except: pass
            return

    if sunucu_ayarlari["spam_filtresi"]:
        now = datetime.utcnow()
        user_id = message.author.id
        if user_id not in spam_takip: spam_takip[user_id] = []
        spam_takip[user_id].append(now)
        spam_takip[user_id] = [t for t in spam_takip[user_id] if (now - t).total_seconds() <= 3]
        if len(spam_takip[user_id]) > 4:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, lütfen spam yapma.", delete_after=5)
                return
            except: pass

    zar = random.randint(1, 100)
    if zar <= 2:
        await message.channel.send(f"{message.author.mention} {random.choice(iltifatlar)}")
    elif zar > 2 and zar <= 10:
        soru, cevap = matematik_sorusu_uret()
        await message.channel.send(f"🧠 **Hızlı Soru!** {message.author.mention}, cevap nedir?\n👉 `{soru}` (15 saniyen var!)")
        def check(m): return m.author == message.author and m.channel == message.channel
        try:
            cevap_mesaj = await bot.wait_for('message', check=check, timeout=15.0)
            if cevap_mesaj.content.strip() == cevap:
                ekonomi_cuzdan[message.author.id] = ekonomi_cuzdan.get(message.author.id, 100) + 50
                await message.channel.send(f"🎉 Doğru! **50 BTS Parası** kazandın! 💰")
            else: await message.channel.send(f"❌ Yanlış! Cevap `{cevap}` olmalıydı.")
        except asyncio.TimeoutError: await message.channel.send(f"⏰ Süre doldu! Cevap `{cevap}` olmalıydı.")

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    if sunucu_ayarlari["giris_cikis_kanali"]:
        ch = bot.get_channel(sunucu_ayarlari["giris_cikis_kanali"])
        if ch: await ch.send(f"{random.choice(selam_cevaplari)} {member.mention}! 🥳")

@bot.event
async def on_member_remove(member):
    if sunucu_ayarlari["giris_cikis_kanali"]:
        ch = bot.get_channel(sunucu_ayarlari["giris_cikis_kanali"])
        if ch: await ch.send(f"👋 `{member.name}` sunucudan ayrıldı. 😔")

def yetkili_kontrol():
    async def predicate(ctx): return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

@bot.command()
@yetkili_kontrol()
async def ayarlar(ctx):
    embed = discord.Embed(title="🛡️ Sunucu Ayarları", color=discord.Color.blue())
    embed.add_field(name="🤬 Küfür Filtresi", value="🟢 AÇIK" if sunucu_ayarlari["kufur_filtresi"] else "🔴 KAPALI", inline=True)
    embed.add_field(name="🔗 Reklam Filtresi", value="🟢 AÇIK" if sunucu_ayarlari["reklam_filtresi"] else "🔴 KAPALI", inline=True)
    embed.add_field(name="⚡ Spam Filtresi", value="🟢 AÇIK" if sunucu_ayarlari["spam_filtresi"] else "🔴 KAPALI", inline=True)
    await ctx.send(embed=embed)

@bot.command()
@yetkili_kontrol()
async def kufurengel(ctx):
    sunucu_ayarlari["kufur_filtresi"] = not sunucu_ayarlari["kufur_filtresi"]
    await ctx.send(f"🤬 Küfür: {'🟢 AÇIK' if sunucu_ayarlari['kufur_filtresi'] else '🔴 KAPALI'}")

@bot.command()
@yetkili_kontrol()
async def reklamengel(ctx):
    sunucu_ayarlari["reklam_filtresi"] = not sunucu_ayarlari["reklam_filtresi"]
    await ctx.send(f"🔗 Reklam: {'🟢 AÇIK' if sunucu_ayarlari['reklam_filtresi'] else '🔴 KAPALI'}")

@bot.command()
@yetkili_kontrol()
async def spamengel(ctx):
    sunucu_ayarlari["spam_filtresi"] = not sunucu_ayarlari["spam_filtresi"]
    await ctx.send(f"⚡ Spam: {'🟢 AÇIK' if sunucu_ayarlari['spam_filtresi'] else '🔴 KAPALI'}")

@bot.command()
@yetkili_kontrol()
async def logayarla(ctx, channel: discord.TextChannel):
    sunucu_ayarlari["log_kanali"] = channel.id
    await ctx.send(f"📁 Log kanalı {channel.mention} yapıldı.")

@bot.command(name="hosgeldin-ve-baybay-ayarla")
@yetkili_kontrol()
async def hosgeldin_baybay_ayarla(ctx, channel: discord.TextChannel):
    sunucu_ayarlari["giris_cikis_kanali"] = channel.id
    await ctx.send(f"✨ Giriş-Çıkış kanalı {channel.mention} yapıldı.")

@bot.command()
@yetkili_kontrol()
async def karaliste(ctx):
    await ctx.send(f"🚫 Yasaklılar: {', '.join(yasakli_kelimeler) if yasakli_kelimeler else 'Boş.'}")

@bot.command()
@yetkili_kontrol()
async def sil(ctx, sayi: int):
    await ctx.channel.purge(limit=min(sayi + 1, 101))
    await ctx.send("🗑️ Temizlendi.", delete_after=3)

@bot.command()
@yetkili_kontrol()
async def sustur(ctx, member: discord.Member, sure: str):
    birim = sure[-1]
    deger = int(sure[:-1])
    dt = timedelta(minutes=deger) if birim == 'm' else (timedelta(hours=deger) if birim == 'h' else timedelta(days=deger))
    await member.timeout(dt)
    await ctx.send(f"🔇 {member.mention} {sure} susturuldu.")

@bot.command()
@yetkili_kontrol()
async def ac(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 {member.mention} açıldı.")

@bot.command()
@yetkili_kontrol()
async def nuke(ctx):
    ch = await ctx.guild.create_text_channel(name=ctx.channel.name, category=ctx.channel.category, topic=ctx.channel.topic)
    await ctx.channel.delete()
    await ch.send("💥 **Kanal Sıfırlandı!** ✨")

@bot.command()
async def para(ctx, member: discord.Member = None):
    h = member or ctx.author
    await ctx.send(f"💰 {h.mention}: **{ekonomi_cuzdan.get(h.id, 100)} BTS Parası**")

@bot.command()
async def slots(ctx, miktar: int):
    c = ekonomi_cuzdan.get(ctx.author.id, 100)
    if miktar <= 0 or miktar > c: return await ctx.send("❌ Bakiye yetersiz!")
    res = [random.choice(["🍒", "🍇", "🍋", "🍊", "🍉"]) for _ in range(3)]
    if res[0] == res[1] == res[2]:
        ekonomi_cuzdan[ctx.author.id] = c + (miktar * 3)
        await ctx.send(f"| {res[0]} | {res[1]} | {res[2]} |\n🎉 3'te 3!")
    else:
        ekonomi_cuzdan[ctx.author.id] = c - miktar
        await ctx.send(f"| {res[0]} | {res[1]} | {res[2]} |\n😔 Kaybettin.")

@bot.command()
async def spty(ctx, member: discord.Member = None):
    h = member or ctx.author
    sp = next((a for a in h.activities if isinstance(a, discord.Spotify)), None)
    if not sp: return await ctx.send("🎵 Spotify dinlemiyor.")
    embed = discord.Embed(title=f"🎧 {h.name} Spotify", color=discord.Color.green())
    embed.add_field(name="🎵 Şarkı", value=sp.title)
    embed.add_field(name="🎤 Sanatçı", value=", ".join(sp.artists))
    embed.set_thumbnail(url=sp.album_cover_url)
    await ctx.send(embed=embed)

@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🌸 Bot Menüsü 🌸", description=f"Merhaba {ctx.author.mention}!", color=discord.Color.gold())
    embed.add_field(name="🛡️ Filtreler", value="`kufurengel`, `reklamengel`, `spamengel`", inline=False)
    embed.add_field(name="🎮 Eğlence", value="`slaps`, `kiss`, `ship`, `slots`, `askolcer`", inline=False)
    embed.add_field(name="💰 Ekonomi", value="`para`", inline=False)
    embed.add_field(name="ℹ️ Bilgi", value="`spty`, `kullanici`, `sunucu`", inline=False)
    await ctx.send(embed=embed)

# Token güvenliği için Render Çevre Değişkenini okuyoruz
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
        import discord
from discord.ext import commands
import random
import asyncio
from datetime import timedelta, datetime
import os
from threading import Thread
from flask import Flask

# Yan taraftaki iltifatlar.py dosyasından çekiyoruz
from iltifatlar import iltifatlar, selam_cevaplari

# --- 🌐 Render Web Service Kapanma Önleyici (Flask) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot aktif ve 7/24 çalışıyor! 🌸"

def run_web():
    # Render'ın dinamik olarak atadığı portu yakalıyoruz (Hata almamak için çok önemli!)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Sunucuyu bot başlamadan hemen önce hayata geçiriyoruz
keep_alive()
# -----------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

sunucu_ayarlari = {
    "kufur_filtresi": False,
    "reklam_filtresi": False,
    "spam_filtresi": False,
    "log_kanali": None,
    "giris_cikis_kanali": None
}

yasakli_kelimeler = ["küfür1", "küfür2", "argo1"]
ekonomi_cuzdan = {}
spam_takip = {}

def matematik_sorusu_uret():
    tipler = ['toplama', 'cikarma', 'carpma', 'us']
    secilen = random.choice(tipler)
    if secilen == 'toplama':
        a, b = random.randint(100, 999), random.randint(100, 999)
        return f"{a}+{b}", str(a + b)
    elif secilen == 'cikarma':
        a, b = random.randint(100, 999), random.randint(10, 99)
        return f"{a}-{b}", str(a - b)
    elif secilen == 'carpma':
        a, b = random.randint(5, 15), random.randint(6, 9)
        return f"{a}*{b}", str(a * b)
    elif secilen == 'us':
        a = random.choice([11, 12, 13, 14, 15, 20, 25])
        return f"{a}^2", str(a ** 2)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower() == "sa":
        await message.channel.send(f"Aleyküm Selam {message.author.mention}, hoş geldin! 🌸✨")
        return

    if sunucu_ayarlari["kufur_filtresi"]:
        for kelime in yasakli_kelimeler:
            if kelime in message.content.lower():
                try:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, lütfen kelimelerimize dikkat edelim!", delete_after=5)
                    if sunucu_ayarlari["log_kanali"]:
                        log_ch = bot.get_channel(sunucu_ayarlari["log_kanali"])
                        if log_ch: await log_ch.send(f"🛡️ **Küfür Engellendi:** {message.author.name} -> `{message.content}`")
                except: pass
                return

    if sunucu_ayarlari["reklam_filtresi"]:
        if "http://" in message.content.lower() or "https://" in message.content.lower() or "discord.gg" in message.content.lower():
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda reklam yapmak yasaktır!", delete_after=5)
                if sunucu_ayarlari["log_kanali"]:
                    log_ch = bot.get_channel(sunucu_ayarlari["log_kanali"])
                    if log_ch: await log_ch.send(f"🛡️ **Reklam Engellendi:** {message.author.name} -> `{message.content}`")
            except: pass
            return

    if sunucu_ayarlari["spam_filtresi"]:
        now = datetime.utcnow()
        user_id = message.author.id
        if user_id not in spam_takip: spam_takip[user_id] = []
        spam_takip[user_id].append(now)
        spam_takip[user_id] = [t for t in spam_takip[user_id] if (now - t).total_seconds() <= 3]
        if len(spam_takip[user_id]) > 4:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, lütfen spam yapma.", delete_after=5)
                return
            except: pass

    zar = random.randint(1, 100)
    if zar <= 2:
        await message.channel.send(f"{message.author.mention} {random.choice(iltifatlar)}")
    elif zar > 2 and zar <= 10:
        soru, cevap = matematik_sorusu_uret()
        await message.channel.send(f"🧠 **Hızlı Soru!** {message.author.mention}, cevap nedir?\n👉 `{soru}` (15 saniyen var!)")
        def check(m): return m.author == message.author and m.channel == message.channel
        try:
            cevap_mesaj = await bot.wait_for('message', check=check, timeout=15.0)
            if cevap_mesaj.content.strip() == cevap:
                ekonomi_cuzdan[message.author.id] = ekonomi_cuzdan.get(message.author.id, 100) + 50
                await message.channel.send(f"🎉 Doğru! **50 BTS Parası** kazandın! 💰")
            else: await message.channel.send(f"❌ Yanlış! Cevap `{cevap}` olmalıydı.")
        except asyncio.TimeoutError: await message.channel.send(f"⏰ Süre doldu! Cevap `{cevap}` olmalıydı.")

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    if sunucu_ayarlari["giris_cikis_kanali"]:
        ch = bot.get_channel(sunucu_ayarlari["giris_cikis_kanali"])
        if ch: await ch.send(f"{random.choice(selam_cevaplari)} {member.mention}! 🥳")

@bot.event
async def on_member_remove(member):
    if sunucu_ayarlari["giris_cikis_kanali"]:
        ch = bot.get_channel(sunucu_ayarlari["giris_cikis_kanali"])
        if ch: await ch.send(f"👋 `{member.name}` sunucudan ayrıldı. 😔")

def yetkili_kontrol():
    async def predicate(ctx): return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

@bot.command()
@yetkili_kontrol()
async def ayarlar(ctx):
    embed = discord.Embed(title="🛡️ Sunucu Ayarları", color=discord.Color.blue())
    embed.add_field(name="🤬 Küfür Filtresi", value="🟢 AÇIK" if sunucu_ayarlari["kufur_filtresi"] else "🔴 KAPALI", inline=True)
    embed.add_field(name="🔗 Reklam Filtresi", value="🟢 AÇIK" if sunucu_ayarlari["reklam_filtresi"] else "🔴 KAPALI", inline=True)
    embed.add_field(name="⚡ Spam Filtresi", value="🟢 AÇIK" if sunucu_ayarlari["spam_filtresi"] else "🔴 KAPALI", inline=True)
    await ctx.send(embed=embed)

@bot.command()
@yetkili_kontrol()
async def kufurengel(ctx):
    sunucu_ayarlari["kufur_filtresi"] = not sunucu_ayarlari["kufur_filtresi"]
    await ctx.send(f"🤬 Küfür: {'🟢 AÇIK' if sunucu_ayarlari['kufur_filtresi'] else '🔴 KAPALI'}")

@bot.command()
@yetkili_kontrol()
async def reklamengel(ctx):
    sunucu_ayarlari["reklam_filtresi"] = not sunucu_ayarlari["reklam_filtresi"]
    await ctx.send(f"🔗 Reklam: {'🟢 AÇIK' if sunucu_ayarlari['reklam_filtresi'] else '🔴 KAPALI'}")

@bot.command()
@yetkili_kontrol()
async def spamengel(ctx):
    sunucu_ayarlari["spam_filtresi"] = not sunucu_ayarlari["spam_filtresi"]
    await ctx.send(f"⚡ Spam: {'🟢 AÇIK' if sunucu_ayarlari['spam_filtresi'] else '🔴 KAPALI'}")

@bot.command()
@yetkili_kontrol()
async def logayarla(ctx, channel: discord.TextChannel):
    sunucu_ayarlari["log_kanali"] = channel.id
    await ctx.send(f"📁 Log kanalı {channel.mention} yapıldı.")

@bot.command(name="hosgeldin-ve-baybay-ayarla")
@yetkili_kontrol()
async def hosgeldin_baybay_ayarla(ctx, channel: discord.TextChannel):
    sunucu_ayarlari["giris_cikis_kanali"] = channel.id
    await ctx.send(f"✨ Giriş-Çıkış kanalı {channel.mention} yapıldı.")

@bot.command()
@yetkili_kontrol()
async def karaliste(ctx):
    await ctx.send(f"🚫 Yasaklılar: {', '.join(yasakli_kelimeler) if yasakli_kelimeler else 'Boş.'}")

@bot.command()
@yetkili_kontrol()
async def sil(ctx, sayi: int):
    await ctx.channel.purge(limit=min(sayi + 1, 101))
    await ctx.send("🗑️ Temizlendi.", delete_after=3)

@bot.command()
@yetkili_kontrol()
async def sustur(ctx, member: discord.Member, sure: str):
    birim = sure[-1]
    deger = int(sure[:-1])
    dt = timedelta(minutes=deger) if birim == 'm' else (timedelta(hours=deger) if birim == 'h' else timedelta(days=deger))
    await member.timeout(dt)
    await ctx.send(f"🔇 {member.mention} {sure} susturuldu.")

@bot.command()
@yetkili_kontrol()
async def ac(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 {member.mention} açıldı.")

@bot.command()
@yetkili_kontrol()
async def nuke(ctx):
    ch = await ctx.guild.create_text_channel(name=ctx.channel.name, category=ctx.channel.category, topic=ctx.channel.topic)
    await ctx.channel.delete()
    await ch.send("💥 **Kanal Sıfırlandı!** ✨")

@bot.command()
async def para(ctx, member: discord.Member = None):
    h = member or ctx.author
    await ctx.send(f"💰 {h.mention}: **{ekonomi_cuzdan.get(h.id, 100)} BTS Parası**")

@bot.command()
async def slots(ctx, miktar: int):
    c = ekonomi_cuzdan.get(ctx.author.id, 100)
    if miktar <= 0 or miktar > c: return await ctx.send("❌ Bakiye yetersiz!")
    res = [random.choice(["🍒", "🍇", "🍋", "🍊", "🍉"]) for _ in range(3)]
    if res[0] == res[1] == res[2]:
        ekonomi_cuzdan[ctx.author.id] = c + (miktar * 3)
        await ctx.send(f"| {res[0]} | {res[1]} | {res[2]} |\n🎉 3'te 3!")
    else:
        ekonomi_cuzdan[ctx.author.id] = c - miktar
        await ctx.send(f"| {res[0]} | {res[1]} | {res[2]} |\n😔 Kaybettin.")

@bot.command()
async def spty(ctx, member: discord.Member = None):
    h = member or ctx.author
    sp = next((a for a in h.activities if isinstance(a, discord.Spotify)), None)
    if not sp: return await ctx.send("🎵 Spotify dinlemiyor.")
    embed = discord.Embed(title=f"🎧 {h.name} Spotify", color=discord.Color.green())
    embed.add_field(name="🎵 Şarkı", value=sp.title)
    embed.add_field(name="🎤 Sanatçı", value=", ".join(sp.artists))
    embed.set_thumbnail(url=sp.album_cover_url)
    await ctx.send(embed=embed)
@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🌸 Bot Menüsü 🌸", description=f"Merhaba {ctx.author.mention}!", color=discord.Color.gold())
    embed.add_field(name="🛡️ Filtreler", value="`kufurengel`, `reklamengel`, `spamengel`", inline=False)
    embed.add_field(name="🎮 Eğlence", value="`slaps`, `kiss`, `ship`, `slots`, `askolcer`", inline=False)
    embed.add_field(name="💰 Ekonomi", value="`para`", inline=False)
    embed.add_field(name="ℹ️ Bilgi", value="`spty`, `kullanici`, `sunucu`", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))

