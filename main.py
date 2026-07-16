import discord
from discord.ext import commands
import random
import asyncio
from datetime import timedelta, datetime
import os

# Yan taraftaki dosyadan iltifatları ve selamlamaları çekiyoruz
from iltifatlar import iltifatlar, selam_cevaplari

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
                        if log_ch: 
                            await log_ch.send(f"🛡️ **Küfür Engellendi:** {message.author.tag} -> `{message.content}`")
                except:
                    pass
                return

    if sunucu_ayarlari["reklam_filtresi"]:
        if "http://" in message.content.lower() or "https://" in message.content.lower() or "discord.gg" in message.content.lower():
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda reklam yapmak yasaktır!", delete_after=5)
                if sunucu_ayarlari["log_kanali"]:
                    log_ch = bot.get_channel(sunucu_ayarlari["log_kanali"])
                    if log_ch: 
                        await log_ch.send(f"🛡️ **Reklam Engellendi:** {message.author.tag} -> `{message.content}`")
            except:
                pass
            return

    if sunucu_ayarlari["spam_filtresi"]:
        now = datetime.utcnow()
        user_id = message.author.id
        if user_id not in spam_takip: 
            spam_takip[user_id] = []
        spam_takip[user_id].append(now)
        spam_takip[user_id] = [t for t in spam_takip[user_id] if (now - t).total_seconds() <= 3]
        if len(spam_takip[user_id]) > 4:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, lütfen spam yapma.", delete_after=5)
                return
            except:
                pass

    # %2 ihtimalle rastgele iltifat gönderir
    zar = random.randint(1, 100)
    if zar <= 2:
        benzersiz_iltifat = random.choice(iltifatlar)
        await message.channel.send(f"{message.author.mention} {benzersiz_iltifat}")
    elif zar > 2 and zar <= 10:
        soru, cevap = matematik_sorusu_uret()
        await message.channel.send(f"🧠 **Hızlı Soru!** {message.author.mention}, cevap nedir?\n👉 `{soru}` (15 saniyen var!)")
        def check(m): 
            return m.author == message.author and m.channel == message.channel
        try:
            cevap_mesaj = await bot.wait_for('message', check=check, timeout=15.0)
            if cevap_mesaj.content.strip() == cevap:
                ekonomi_cuzdan[message.author.id] = ekonomi_cuzdan.get(message.author.id, 0) + 50
                await message.channel.send(f"🎉 Doğru cevap {message.author.mention}! **50 BTS Parası** kazandın! 💰")
            else:
                await message.channel.send(f"❌ Yanlış cevap! Doğru yanıt `{cevap}` olmalıydı.")
        except asyncio.TimeoutError:
            await message.channel.send(f"⏰ Süre doldu! Yanıt `{cevap}` olmalıydı.")

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    if sunucu_ayarlari["giris_cikis_kanali"]:
        ch = bot.get_channel(sunucu_ayarlari["giris_cikis_kanali"])
        if ch: 
            await ch.send(f"{random.choice(selam_cevaplari)} {member.mention}! 🥳")

@bot.event
async def on_member_remove(member):
    if sunucu_ayarlari["giris_cikis_kanali"]:
        ch = bot.get_channel(sunucu_ayarlari["giris_cikis_kanali"])
        if ch: 
            await ch.send(f"👋 `{member.tag}` sunucudan ayrıldı. 😔")

def yetkili_kontrol():
    async def predicate(ctx): 
        return ctx.author.guild_permissions.administrator
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
    await ctx.send(f"🤬 Küfür filtresi: {'🟢 AÇIK' if sunucu_ayarlari['kufur_filtresi'] else '🔴 KAPALI'}")

@bot.command()
@yetkili_kontrol()
async def reklamengel(ctx):
    sunucu_ayarlari["reklam_filtresi"] = not sunucu_ayarlari["reklam_filtresi"]
    await ctx.send(f"🔗 Reklam filtresi: {'🟢 AÇIK' if sunucu_ayarlari['reklam_filtresi'] else '🔴 KAPALI'}")

@bot.command()
@yetkili_kontrol()
async def spamengel(ctx):
    sunucu_ayarlari["spam_filtresi"] = not sunucu_ayarlari["spam_filtresi"]
    await ctx.send(f"⚡ Spam filtresi: {'🟢 AÇIK' if sunucu_ayarlari['spam_filtresi'] else '🔴 KAPALI'}")

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
    await ctx.send(f"🚫 Yasaklı Kelimeler: {', '.join(yasakli_kelimeler) if yasakli_kelimeler else 'Boş.'}")

@karaliste.command(name="ekle")
@yetkili_kontrol()
async def karaliste_ekle(ctx, kelime: str):
    yasakli_kelimeler.append(kelime.lower())
    await ctx.send(f"✅ `{kelime}` eklendi.")

@karaliste.command(name="cikar")
@yetkili_kontrol()
async def karaliste_cikar(ctx, kelime: str):
    if kelime.lower() in yasakli_kelimeler:
        yasakli_kelimeler.remove(kelime.lower())
        await ctx.send(f"✅ `{kelime}` çıkarıldı.")

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
    if birim == 'm': dt = timedelta(minutes=deger)
    elif birim == 'h': dt = timedelta(hours=deger)
    else: dt = timedelta(days=deger)
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
    await ch.send("💥 **Kanal Sıfırlandı (Nuke)!** ✨")

@bot.command()
@yetkili_kontrol()
async def rolver(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send("✅ Rol verildi.")

@bot.command()
@yetkili_kontrol()
async def rolal(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send("✅ Rol alındı.")

@bot.command()
@yetkili_kontrol()
async def ban(ctx, member: discord.Member, *, sebep="Yok"):
    await member.ban(reason=sebep)
    await ctx.send(f"🚫 {member.tag} banlandı.")

@bot.command()
@yetkili_kontrol()
async def kick(ctx, member: discord.Member, *, sebep="Yok"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.tag} atıldı.")

@bot.command()
@yetkili_kontrol()
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal kilitlendi.")

@bot.command()
@yetkili_kontrol()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Kanal açıldı.")

@bot.command()
async def para(ctx, member: discord.Member = None):
    h = member or ctx.author
    await ctx.send(f"💰 {h.mention}: **{ekonomi_cuzdan.get(h.id, 100)} BTS Parası**")

@bot.command()
async def slots(ctx, miktar: int):
    c = ekonomi_cuzdan.get(ctx.author.id, 100)
    if miktar <= 0 or miktar > c: 
        return await ctx.send("❌ Bakiye yetersiz!")
    res = [random.choice(["🍒", "🍇", "🍋", "🍊", "🍉"]) for _ in range(3)]
    sonuc = f" | {res[0]} | {res[1]} | {res[2]} | "
    if res[0] == res[1] == res[2]:
        ekonomi_cuzdan[ctx.author.id] = c + (miktar * 3)
        await ctx.send(f"{sonuc}\n🎉 3'te 3! Üç katı kazandın!")
    elif res[0] == res[1] or res[1] == res[2] or res[0] == res[2]:
        ekonomi_cuzdan[ctx.author.id] = c + miktar
        await ctx.send(f"{sonuc}\n✨ Çift yakaladın!")
    else:
        ekonomi_cuzdan[ctx.author.id] = c - miktar
        await ctx.send(f"{sonuc}\n😔 Kaybettin.")

@bot.command()
async def spty(ctx, member: discord.Member = None):
    h = member or ctx.author
    sp = next((a for a in h.activities if isinstance(a, discord.Spotify)), None)
    if not sp: 
        return await ctx.send("🎵 Spotify dinlemiyor.")
    embed = discord.Embed(title=f"🎧 {h.name} Spotify", color=discord.Color.green())
    embed.add_field(name="🎵 Şarkı", value=sp.title)
    embed.add_field(name="🎤 Sanatçı", value=", ".join(sp.artists))
    embed.set_thumbnail(url=sp.album_cover_url)
    await ctx.send(embed=embed)

@bot.command()
async def kullanici(ctx, member: discord.Member = None):
    h = member or ctx.author
    embed = discord.Embed(title=f"👤 {h.name}", color=discord.Color.purple())
    embed.add_field(name="📅 Açılış", value=h.created_at.strftime("%d/%m/%Y"))
    embed.add_field(name="📥 Giriş", value=h.joined_at.strftime("%d/%m/%Y"))
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    embed = discord.Embed(title=f"📊 {ctx.guild.name}", color=discord.Color.orange())
    embed.add_field(name="👥 Üye", value=str(ctx.guild.member_count))
    await ctx.send(embed=embed)

@bot.command()
async def askolcer(ctx, member: discord.Member):
    o = random.randint(0, 100)
    await ctx.send(f"❤️ {ctx.author.mention} x {member.mention} -> **%{o}**")

@bot.command()
async def efkarolcer(ctx):
    await ctx.send(f"🚬 {ctx.author.mention} efkarınız: **%{random.randint(0, 100)}**")

@bot.command()
async def sanslisayi(ctx):
    await ctx.send(f"🍀 {ctx.author.mention} şanslı sayın: **{random.randint(1, 100)}**")

slap_gifs = ["https://media.giphy.com/media/Gf3Aut3eBNbTw/giphy.gif"]
kiss_gifs = ["https://media.giphy.com/media/G3va31WUtFxQI/giphy.gif"]
hug_gifs = ["https://media.giphy.com/media/142te9HA8mMKs/giphy.gif"]

@bot.command()
async def slaps(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("⚠️ Lütfen tokatlamak istediğin birini etiketle!")
    embed = discord.Embed(description=f"💥 {ctx.author.mention}, {member.mention} kullanıcısına tokat attı!")
    embed.set_image(url=random.choice(slap_gifs))
    await ctx.send(embed=embed)

@bot.command()
async def kiss(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("⚠️ Lütfen öpmek istediğin birini etiketle!")
    embed = discord.Embed(description=f"💋 {ctx.author.mention}, {member.mention} kullanıcısını öptü!")
    embed.set_image(url=random.choice(kiss_gifs))
    await ctx.send(embed=embed)

@bot.command()
async def sarıl(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("⚠️ Lütfen sarılmak istediğin birini etiketle!")
    embed = discord.Embed(description=f"🤗 {ctx.author.mention}, {member.mention} kullanıcısına sarıldı!")
    embed.set_image(url=random.choice(hug_gifs))
    await ctx.send(embed=embed)

@bot.command()
async def ship(ctx):
    uyeler = [m for m in ctx.guild.members if not m.bot and m != ctx.author]
    if not uyeler:
        return await ctx.send("❌ Shiplemek için sunucuda başka kimse yok.")
    sec = random.choice(uyeler)
    sec_oran = random.randint(10, 100)
    await ctx.send(f"💞 {ctx.author.mention} x {sec.mention} -> **%{sec_oran}** ✨⭐")

@bot.command(name="ship2")
async def ship2(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("⚠️ Lütfen shiplemek istediğin bir üyeyi etiketle!")
    await ctx.send(f"💞 {ctx.author.mention} x {member.mention}\n**Oran: %99999** 🔥\n✨🌟 **BU AŞK ÖLÇÜLEMEZ!** 🌟✨")

@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🌸 Bot Komut Menüsü 🌸", color=discord.Color.gold())
    embed.add_field(name="🛡️ Filtreler", value="`Kürür`, `Reklam`, `Spam`, `SA-AS`", inline=False)
    embed.add_field(name="⚙️ Ayarlar", value="`ayarlar`, `kufurengel`, `reklamengel`, `spamengel`, `logayarla`, `hosgeldin-ve-baybay-ayarla`", inline=False)
    embed.add_field(name="🎮 Eğlence & Aksiyon", value="`slaps`, `kiss`, `sarıl`, `ship`, `ship2`, `askolcer`, `efkarolcer`, `sanslisayi`, `para`, `slots`, `spty`", inline=False)
    await ctx.send(embed=embed)

# Render veya diğer hosting servislerinde güvenle çalışması için Token'ı Environment'tan çekiyoruz
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
    
