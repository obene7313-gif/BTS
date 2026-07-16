import discord
from discord.ext import commands
import random
import asyncio
import os
from datetime import datetime
from threading import Thread
from flask import Flask

# --- İLTİFAT VE SELAM LİSTELERİNİ ÇEKME ---
try:
    from iltifatlar import iltifat_listesi, selam_cevaplari
except ImportError:
    iltifat_listesi = ["Harikasın! ✨"]
    selam_cevaplari = ["Hoş geldin canım! ⭐"]

# --- FLASK WEB SERVER (Render Aktif Tutma İçin) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot BTS is Active!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- VERİTABANI SİMÜLASYONU (Hafıza) ---
sunucu_ayarlari = {
    "kufur_engel": False,
    "reklam_engel": False,
    "spam_engel": False,
    "log_kanal_id": None,
    "welcome_kanal_id": None,
    "kara_liste": ["piç", "sik", "orospu", "göt"] # Varsayılan örnek yasaklı kelimeler
}

user_data = {}  # Ekonomi (Para) verileri
last_message_time = {} # Spam engeli için süre takibi

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"para": 100} # Başlangıç bakiyesi 100 BTS
    return user_data[user_id]

# --- KÜFÜR VE REKLAM KONTROL LİSTELERİ ---
KUFUR_KOKLERI = ["amk", "aq", "orospu", "sik", "piç", "göt", "yarrak", "pezevenk"]
REKLAM_UZANTILARI = ["http://", "https://", "discord.gg/", ".com", ".net", ".org", "www."]

# --- BOT HAZIR OLDUĞUNDA ---
@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} olarak başarıyla giriş yaptı! 🌸🚀")
    await bot.change_presence(activity=discord.Game(name="!yardim | BTS 💖"))

# --- ÜYE GİRİŞ / ÇIKIŞ SİSTEMİ ---
@bot.event
async def on_member_join(member):
    kanal_id = sunucu_ayarlari["welcome_kanal_id"]
    if kanal_id:
        kanal = bot.get_channel(kanal_id)
        if kanal:
            # 100'lük selam listesinden rastgele bir tane seçer
            selam = random.choice(selam_cevaplari)
            await kanal.send(f"📥 **{member.mention}** geldi! {selam}")

@bot.event
async def on_member_remove(member):
    kanal_id = sunucu_ayarlari["welcome_kanal_id"]
    if kanal_id:
        kanal = bot.get_channel(kanal_id)
        if kanal:
            await kanal.send(f"📤 **{member.name}** sunucudan ayrıldı, görüşmek üzere... 💔")

# --- MESAJ ETKİLEŞİMLERİ VE FİLTRELER ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg_lower = message.content.lower()

    # --- 1. OTOMATİK SELAM CEVABI ---
    if msg_lower == "sa":
        await message.channel.send("Aleyküm Selam, hoş geldin! 🌸✨")
        return

    # --- 2. LOG KANALI YARDIMCI FONKSİYONU ---
    async def log_gonder(icerik):
        if sunucu_ayarlari["log_kanal_id"]:
            log_kanali = bot.get_channel(sunucu_ayarlari["log_kanal_id"])
            if log_kanali:
                await log_kanali.send(icerik)

    # --- 3. SPAM ENGEL SİSTEMİ ---
    if sunucu_ayarlari["spam_engel"]:
        now = datetime.now()
        user_id = message.author.id
        if user_id in last_message_time:
            gecen_sure = (now - last_message_time[user_id]).total_seconds()
            if gecen_sure < 1.0: # 1 saniyeden kısa sürede mesaj atarsa
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, çok hızlı mesaj gönderiyorsun! (Spam Filtresi)", delete_after=3)
                await log_gonder(f"🚨 **Spam Engellendi:** {message.author.mention} hızlı mesaj gönderdi.")
                return
        last_message_time[user_id] = now

    # --- 4. KÜFÜR ENGEL SİSTEMİ ---
    if sunucu_ayarlari["kufur_engel"]:
        if any(kok in msg_lower for kok in KUFUR_KOKLERI) or any(kelime in msg_lower for kelime in sunucu_ayarlari["kara_liste"]):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda küfürlü/yasaklı kelime kullanılması yasaktır!", delete_after=5)
            await log_gonder(f"🚨 **Küfür/Yasaklı Kelime Engellendi:** {message.author.mention} -> `{message.content}`")
            return

    # --- 5. REKLAM ENGEL SİSTEMİ ---
    if sunucu_ayarlari["reklam_engel"]:
        if any(link in msg_lower for link in REKLAM_UZANTILARI):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda link/reklam paylaşımı yasaktır!", delete_after=5)
            await log_gonder(f"🚨 **Reklam Engellendi:** {message.author.mention} -> `{message.content}`")
            return

    # --- 6. RASTGELE İLTİFAT SİSTEMİ (%2) ---
    if random.random() < 0.02:
        iltifat = random.choice(iltifat_listesi)
        await message.channel.send(f"{message.author.mention} {iltifat}")

    # --- 7. MATEMATİK SORU YARIŞMASI (%8) ---
    if random.random() < 0.08:
        sayi1 = random.randint(1, 50)
        sayi2 = random.randint(1, 50)
        islem = random.choice(["+", "-", "*"])
        
        if islem == "+": dogru_cevap = sayi1 + sayi2
        elif islem == "-": dogru_cevap = sayi1 - sayi2
        else: dogru_cevap = sayi1 * sayi2

        await message.channel.send(f"🧮 **HIZLI MATEMATİK YARIŞMASI!** \nSoru: **{sayi1} {islem} {sayi2} = ?** \n*15 saniye içinde ilk doğru cevap verene **50 BTS Parası** ödül var!*")

        def check(m):
            return m.channel == message.channel and m.content.strip() == str(dogru_cevap) and not m.author.bot

        try:
            kazanan_mesaj = await bot.wait_for('message', check=check, timeout=15.0)
            kazanan = kazanan_mesaj.author
            user_profil = get_user(kazanan.id)
            user_profil["para"] += 50
            await message.channel.send(f"🎉 Tebrikler {kazanan.mention}! Doğru cevabı (**{dogru_cevap}**) verdin ve **50 BTS Parası** kazandın! Yeni bakiyen: 💰 {user_profil['para']} BTS")
        except asyncio.TimeoutError:
            await message.channel.send(f"⏰ Süre bitti! Kimse doğru cevap veremedi. Doğru cevap **{dogru_cevap}** olmalıydı.")

    await bot.process_commands(message)

# ====================================================================
# 🛡️ YETKİLİ & YÖNETİM KOMUTLARI
# ====================================================================

@bot.command()
@commands.has_permissions(administrator=True)
async def ayarlar(ctx):
    embed = discord.Embed(title="🛡️ Sunucu Filtre ve Sistem Ayarları", color=discord.Color.blue())
    embed.add_field(name="🤬 Küfür Engeli", value="🟢 Aktif" if sunucu_ayarlari["kufur_engel"] else "🔴 Pasif", inline=True)
    embed.add_field(name="🔗 Reklam Engeli", value="🟢 Aktif" if sunucu_ayarlari["reklam_engel"] else "🔴 Pasif", inline=True)
    embed.add_field(name="⚡ Spam Engeli", value="🟢 Aktif" if sunucu_ayarlari["spam_engel"] else "🔴 Pasif", inline=True)
    
    log_kanali = f"<#{sunucu_ayarlari['log_kanal_id']}>" if sunucu_ayarlari["log_kanal_id"] else "❌ Ayarlanmamış"
    welcome_kanali = f"<#{sunucu_ayarlari['welcome_kanal_id']}>" if sunucu_ayarlari["welcome_kanal_id"] else "❌ Ayarlanmamış"
    
    embed.add_field(name="📋 Log Kanalı", value=log_kanali, inline=False)
    embed.add_field(name="👋 Giriş-Çıkış Kanalı", value=welcome_kanali, inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def kufurengel(ctx):
    sunucu_ayarlari["kufur_engel"] = not sunucu_ayarlari["kufur_engel"]
    durum = "açıldı 🟢" if sunucu_ayarlari["kufur_engel"] else "kapatıldı 🔴"
    await ctx.send(f"🤬 Küfür filtresi başarıyla **{durum}**.")

@bot.command()
@commands.has_permissions(administrator=True)
async def reklamengel(ctx):
    sunucu_ayarlari["reklam_engel"] = not sunucu_ayarlari["reklam_engel"]
    durum = "açıldı 🟢" if sunucu_ayarlari["reklam_engel"] else "kapatıldı 🔴"
    await ctx.send(f"🔗 Reklam filtresi başarıyla **{durum}**.")

@bot.command()
@commands.has_permissions(administrator=True)
async def spamengel(ctx):
    sunucu_ayarlari["spam_engel"] = not sunucu_ayarlari["spam_engel"]
    durum = "açıldı 🟢" if sunucu_ayarlari["spam_engel"] else "kapatıldı 🔴"
    await ctx.send(f"⚡ Spam filtresi başarıyla **{durum}**.")

@bot.command()
@commands.has_permissions(administrator=True)
async def logayarla(ctx, kanal: discord.TextChannel):
    sunucu_ayarlari["log_kanal_id"] = kanal.id
    await ctx.send(f"📋 Raporlama log kanalı başarıyla {kanal.mention} olarak ayarlandı!")

@bot.command(name="hosgeldin-ve-baybay-ayarla")
@commands.has_permissions(administrator=True)
async def welcome_ayarla(ctx, kanal: discord.TextChannel):
    sunucu_ayarlari["welcome_kanal_id"] = kanal.id
    await ctx.send(f"👋 Giriş ve Çıkış bildirim kanalı başarıyla {kanal.mention} olarak ayarlandı!")

@bot.command()
@commands.has_permissions(administrator=True)
async def karaliste(ctx, islem=None, *, kelime=None):
    if not islem:
        liste = ", ".join(sunucu_ayarlari["kara_liste"]) if sunucu_ayarlari["kara_liste"] else "Yasaklı kelime yok."
        await ctx.send(f"🚫 **Sunucu Kara Listesi:**\n`{liste}`")
        return
    
    if islem.lower() == "ekle" and kelime:
        if kelime.lower() not in sunucu_ayarlari["kara_liste"]:
            sunucu_ayarlari["kara_liste"].append(kelime.lower())
            await ctx.send(f"✅ `{kelime}` kelimesi kara listeye eklendi.")
        else:
            await ctx.send("Bu kelime zaten kara listede var.")
            
    elif islem.lower() == "cikar" and kelime:
        if kelime.lower() in sunucu_ayarlari["kara_liste"]:
            sunucu_ayarlari["kara_liste"].remove(kelime.lower())
            await ctx.send(f"✅ `{kelime}` kelimesi kara listeden çıkarıldı.")
        else:
            await ctx.send("Bu kelime kara listede bulunamadı.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int):
    if sayi < 1:
        await ctx.send("Lütfen en az 1 mesaj sil belirtiniz.", delete_after=3)
        return
    deleted = await ctx.channel.purge(limit=sayi + 1)
    await ctx.send(f"🗑️ Başarıyla **{len(deleted)-1}** adet mesaj temizlendi.", delete_after=4)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def sustur(ctx, member: discord.Member, sure: str, *, sebep="Belirtilmedi"):
    # Süre formatı çözücü (örn: 5m, 2h, 1d)
    try:
        birim = sure[-1]
        miktar = int(sure[:-1])
        if birim == "m": zaman = asyncio.subprocess.timedelta(minutes=miktar)
        elif birim == "h": zaman = asyncio.subprocess.timedelta(hours=miktar)
        elif birim == "d": zaman = asyncio.subprocess.timedelta(days=miktar)
        else: raise Exception()
    except:
        await ctx.send("❌ Geçersiz süre formatı! Örn: `5m` (dakika), `2h` (saat), `1d` (gün)")
        return

    await member.timeout(zaman, reason=sebep)
    await ctx.send(f"🤐 {member.mention} üyesi **{sure}** boyunca susturuldu. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def ac(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 {member.mention} üyesinin susturulması kaldırıldı!")

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    kanal_konumu = ctx.channel.position
    yeni_kanal = await ctx.channel.clone(reason="Nuke işlemi")
    await ctx.channel.delete()
    await yeni_kanal.edit(position=kanal_konumu)
    await yeni_kanal.send("💥 Kanal başarıyla nükleer bomba ile temizlendi ve sıfırlandı! https://tenor.com/view/explosion-mushroom-cloud-atomic-bomb-bomb-boom-gif-4464835")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ {member.mention} isimli üyeye **{role.name}** rolü verildi.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"❌ {member.mention} isimli üyeden **{role.name}** rolü geri alındı.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member.name} sunucudan banlandı! Sebep: {sebep}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} sunucudan atıldı! Sebep: {sebep}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal başarıyla yazışmaya kapatıldı/kilitlendi.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Kanal tekrar yazışmaya açıldı.")

# ====================================================================
# 🎮 EĞLENCE & ETKİLEŞİM KOMUTLARI
# ====================================================================

@bot.command()
async def slaps(ctx, member: discord.Member):
    await ctx.send(f"👋 {ctx.author.mention}, {member.mention} üyesini evire çevire tokatladı! https://tenor.com/view/slap-bear-slap-me-gif-19194015")

@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"💋 {ctx.author.mention}, {member.mention} üyesine kocaman sulu bir öpücük kondurdu! https://tenor.com/view/anime-kiss-gif-25710543")

@bot.command()
async def sarıl(ctx, member: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention}, {member.mention} üyesine sımsıkı sarıldı! https://tenor.com/view/hug-warm-hug-gif-23847852")

@bot.command()
async def askolcer(ctx, member: discord.Member):
    oran = random.randint(0, 100)
    await ctx.send(f"❤️ {ctx.author.mention} ile {member.mention} arasındaki aşk oranı: **%{oran}**")

@bot.command()
async def efkarolcer(ctx):
    oran = random.randint(0, 100)
    await ctx.send(f"🚬 {ctx.author.mention} o anki efkar durumun: **%{oran}** yak yak yak...")

@bot.command()
async def sanslisayi(ctx):
    sayi = random.randint(1, 100)
    await ctx.send(f"🍀 {ctx.author.mention}, bugün senin şanslı sayın: **{sayi}**")

@bot.command()
async def ship(ctx):
    aktifs = [m for m in ctx.guild.members if not m.bot and m != ctx.author]
    if not aktifs:
        await ctx.send("Sunucuda shipleşecek kimse yok canım!")
        return
    secilen = random.choice(aktifs)
    oran = random.randint(0, 100)
    await ctx.send(f"💖 **Şans Eseri Shiplendiniz!** \n💞 {ctx.author.mention}  &  {secilen.mention} \n💘 Aşk Oranı: **%{oran}**")

@bot.command()
async def ship2(ctx, member: discord.Member):
    await ctx.send(f"❤️‍🔥 **AMANSIZ BİR AŞK!** \n💞 {ctx.author.mention}  &  {member.mention} \n🔥 Aşk Oranı: **%99999** \n🏆 *Bu aşk ölçülemez, siz birbiriniz için yaratılmışsınız!*")

# ====================================================================
# 💰 EKONOMİ & OYUN KOMUTLARI
# ====================================================================

@bot.command()
async def para(ctx, member: discord.Member = None):
    hedef = member or ctx.author
    profil = get_user(hedef.id)
    await ctx.send(f"💰 {hedef.mention} cüzdanında **{profil['para']} BTS Parası** bulunuyor.")

@bot.command()
async def slots(ctx, miktar: int):
    profil = get_user(ctx.author.id)
    if miktar <= 0:
        await ctx.send("Lütfen geçerli bir miktar girin.")
        return
    if profil["para"] < miktar:
        await ctx.send("❌ Cüzdanında yeterli BTS Parası yok!")
        return

    emojiler = ["🍒", "🍋", "🍇", "💎", "🔔"]
    s1, s2, s3 = random.choice(emojiler), random.choice(emojiler), random.choice(emojiler)
    
    mesaj = await ctx.send("🎰 **Slots dönüyor...** \n[ 🟥 | 🟥 | 🟥 ]")
    await asyncio.sleep(1)
    await mesaj.edit(content=f"🎰 **Slots dönüyor...** \n[ {s1} | {s2} | {s3} ]")

    if s1 == s2 == s3:
        kazanc = miktar * 4
        profil["para"] += kazanc
        await ctx.send(f"🎉 **TEBRİKLER! 3'te 3 YAPTINIZ!** \n💰 **{kazanc} BTS Parası** kazandınız! Yeni Bakiyeniz: {profil['para']}")
    elif s1 == s2 or s2 == s3 or s1 == s3:
        kazanc = int(miktar * 1.5)
        profil["para"] += kazanc
        await ctx.send(f"✨ **Çift Yakaladınız!** \n💰 **{kazanc} BTS Parası** kazandınız! Yeni Bakiyeniz: {profil['para']}")
    else:
        profil["para"] -= miktar
        await ctx.send(f"😭 **Kaybettiniz!** \n💸 **{miktar} BTS Parası** cüzdandan uçtu. Kalan Bakiye: {profil['para']}")

# ====================================================================
# ℹ️ BİLGI & SİSTEM KOMUTLARI
# ====================================================================

@bot.command()
async def spty(ctx, member: discord.Member = None):
    hedef = member or ctx.author
    spotify_activity = None
    for activity in hedef.activities:
        if isinstance(activity, discord.Spotify):
            spotify_activity = activity
            break
            
    if not spotify_activity:
        await ctx.send(f"🎵 {hedef.name} şu an Spotify'da şarkı dinlemiyor.")
        return

    embed = discord.Embed(title=f"🎵 {hedef.name} Spotify Dinliyor", color=spotify_activity.color)
    embed.add_field(name="Şarkı Adı:", value=spotify_activity.title, inline=False)
    embed.add_field(name="Sanatçı:", value=", ".join(spotify_activity.artists), inline=False)
    embed.add_field(name="Albüm:", value=spotify_activity.album, inline=False)
    embed.set_thumbnail(url=spotify_activity.album_cover_url)
    await ctx.send(embed=embed)

@bot.command()
async def kullanici(ctx, member: discord.Member = None):
    hedef = member or ctx.author
    kurulus = hedef.created_at.strftime("%d/%m/%Y %H:%M")
    katilis = hedef.joined_at.strftime("%d/%m/%Y %H:%M")
    
    embed = discord.Embed(title=f"ℹ️ {hedef.name} Profil Bilgileri", color=discord.Color.purple())
    embed.add_field(name="🗓️ Hesap Kuruluş Tarihi", value=kurulus, inline=True)
    embed.add_field(name="🚀 Sunucuya Katılım Tarihi", value=katilis, inline=True)
    embed.set_thumbnail(url=hedef.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    toplam_uye = ctx.guild.member_count
    await ctx.send(f"📊 **{ctx.guild.name}** sunucusunda toplam **{toplam_uye}** üye bulunuyor!")

@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🤖 BTS Bot Komut Menüsü", description="İşte bota ait tüm komutların detaylı listesi:", color=discord.Color.green())
    
    embed.add_field(name="🛡️ Yönetim Komutları (Adminler İçin)", 
                    value="`!ayarlar`, `!kufurengel`, `!reklamengel`, `!spamengel`, `!logayarla #kanal`, `!hosgeldin-ve-baybay-ayarla #kanal`, `!karaliste`, `!sil [sayı]`, `!sustur @üye [süre]`, `!ac @üye`, `!nuke`, `!rolver`, `!rolal`, `!ban`, `!kick`, `!lock`, `!unlock`", inline=False)
    
    embed.add_field(name="🎮 Eğlence & Etkileşim", 
                    value="`!slaps @üye`, `!kiss @üye`, `!sarıl @üye`, `!askolcer @üye`, `!efkarolcer`, `!sanslisayi`, `!ship`, `!ship2 @üye`", inline=False)
    
    embed.add_field(name="💰 Ekonomi", 
                    value="`!para`, `!slots [miktar]`", inline=False)
    
    embed.add_field(name="ℹ️ Sistem & Bilgi", 
                    value="`!spty`, `!kullanici`, `!sunucu`, `!yardim`", inline=False)
    
    embed.set_footer(text="Bot sorunsuz ve eksiksiz çalışmaktadır. 💖")
    await ctx.send(embed=embed)

# --- WEB SUNUCUSUNU AÇIP BOTU ÇALIŞTIRMA ---
keep_alive()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
            
