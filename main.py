import discord
from discord.ext import commands
import random
import asyncio
import os
from datetime import datetime, timedelta, timezone # pytz yerine dahili zaman modülleri eklendi
from threading import Thread
from flask import Flask

# --- İLTİFAT VE SELAM LİSTELERİNİ ÇEKME VE KONTROL ---
try:
    from iltifatlar import iltifatlar, selam_cevaplari
    
    # Eğer listeler bir şekilde iç içe liste olarak geldiyse düzeltiyoruz
    if len(iltifatlar) == 1 and isinstance(iltifatlar[0], list):
        iltifat_listesi = iltifatlar[0]
    else:
        iltifat_listesi = iltifatlar
        
    if len(selam_cevaplari) == 1 and isinstance(selam_cevaplari[0], list):
        selam_listesi = selam_cevaplari[0]
    else:
        selam_listesi = selam_cevaplari
except ImportError:
    # Dosya okunamazsa yedek koruma listesi
    iltifat_listesi = ["Harikasın! ✨", "Gözlerin parıldıyor! 🌟"]
    selam_listesi = ["Hoş geldin canım! ⭐️", "Selamlar güzellik! 🥰"]
    
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
    "kara_liste": ["piç", "sik", "orospu", "göt"]
}

user_data = {}  
last_message_time = {} 

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"para": 100}
    return user_data[user_id]

KUFUR_KOKLERI = ["amk", "aq", "orospu", "sik", "piç", "göt", "yarrak", "pezevenk"]
REKLAM_UZANTILARI = ["http://", "https://", "discord.gg/", ".com", ".net", ".org", "www."]

BTS_SORULARI = [
    {"soru": "BTS hangi yıl çıkış yapmıştır?", "şıklar": ["A) 2010", "B) 2013", "C) 2015", "D) 2016"], "cevap": "B"},
    {"soru": "BTS grubunun lideri kimdir?", "şıklar": ["A) Jimin", "B) Jungkook", "C) RM", "D) Suga"], "cevap": "C"},
    {"soru": "BTS'in en büyük üyesi (Madnae) kimdir?", "şıklar": ["A) Jin", "B) J-Hope", "C) V", "D) RM"], "cevap": "A"},
    {"soru": "BTS fandomunun adı nedir?", "şıklar": ["A) Blink", "B) Once", "C) ARMY", "D) EXO-L"], "cevap": "C"},
    {"soru": "Grubun ana dansçısı ve umut kaynağı kimdir?", "şıklar": ["A) Suga", "B) J-Hope", "C) Jin", "D) V"], "cevap": "B"},
    {"soru": "BTS'in 'Golden Maknae' unvanına sahip üyesi kimdir?", "şıklar": ["A) Jungkook", "B) Jimin", "C) V", "D) Suga"], "cevap": "A"}
]

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} olarak başarıyla giriş yaptı! 🌸🚀")
    await bot.change_presence(activity=discord.Game(name="!yardim | BTS 💖"))

@bot.event
async def on_member_join(member):
    kanal_id = sunucu_ayarlari["welcome_kanal_id"]
    if kanal_id:
        kanal = bot.get_channel(kanal_id)
        if kanal:
                        secilen_selam = random.choice(selam_listesi)
                        await kanal.send(f"👑 **{member.mention}** geldi! {secilen_selam}")
        

@bot.event
async def on_member_remove(member):
    kanal_id = sunucu_ayarlari["welcome_kanal_id"]
    if kanal_id:
        kanal = bot.get_channel(kanal_id)
        if kanal:
            await kanal.send(f"📤 **{member.name}** sunucudan ayrıldı, görüşmek üzere... 💔")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg_lower = message.content.lower()

            if msg_lower in ["sa", "selam", "slm", "merhaba", "mrb"]:
        secilen_selam = random.choice(selam_listesi)
        await message.channel.send(secilen_selam)
        return

            

    # SPAM ENGEL
    if sunucu_ayarlari["spam_engel"]:
        now = datetime.now()
        user_id = message.author.id
        if user_id in last_message_time:
            gecen_sure = (now - last_message_time[user_id]).total_seconds()
            if gecen_sure < 1.0:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, çok hızlı mesaj gönderiyorsun!", delete_after=3)
                return
        last_message_time[user_id] = now

    # KÜFÜR ENGEL
    if sunucu_ayarlari["kufur_engel"]:
        if any(kok in msg_lower for kok in KUFUR_KOKLERI) or any(kelime in msg_lower for kelime in sunucu_ayarlari["kara_liste"]):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, küfürlü/yasaklı kelime kullanmak yasaktır!", delete_after=5)
            return

    # REKLAM ENGEL
    if sunucu_ayarlari["reklam_engel"]:
        if any(link in msg_lower for link in REKLAM_UZANTILARI):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, reklam/link paylaşımı yasaktır!", delete_after=5)
            return

    # %3 İltifat
    if random.random() < 0.03:
                        secilen_iltifat = random.choice(iltifat_listesi)
        await message.channel.send(f"{message.author.mention} {secilen_iltifat}")
            
    # %7 Yarışma Sistemi (Süre 30 Saniye)
    if random.random() < 0.07:
        if random.random() < 0.75:
            sayi1 = random.randint(1, 20)
            sayi2 = random.randint(1, 15)
            islem = random.choice(["+", "-", "*"])
            
            if islem == "+": dogru_sonuc = sayi1 + sayi2
            elif islem == "-": dogru_sonuc = sayi1 - sayi2
            else: dogru_sonuc = sayi1 * sayi2

            yanlislar = set()
            while len(yanlislar) < 3:
                sapma = random.randint(-10, 10)
                aday = dogru_sonuc + sapma
                if aday != dogru_sonuc and aday > 0:
                    yanlislar.add(aday)
            
            sik_havuzu = [dogru_sonuc] + list(yanlislar)
            random.shuffle(sik_havuzu)
            
            harfler = ["A", "B", "C", "D"]
            siklar_metni = [f"{harfler[i]}) {sik_havuzu[i]}" for i in range(4)]
            dogru_harf = harfler[sik_havuzu.index(dogru_sonuc)]
            
            soru_metni = f"🧮 **HIZLI MATEMATİK YARIŞMASI!**\nSoru: **{sayi1} {islem} {sayi2} = ?**"
        else:
            bts_soru = random.choice(BTS_SORULARI)
            soru_metni = f"💜 **BTS BİLGİ YARIŞMASI!**\nSoru: **{bts_soru['soru']}**"
            siklar_metni = bts_soru["şıklar"]
            dogru_harf = bts_soru["cevap"]

        final_mesaj = f"{soru_metni}\n\n" + "\n".join(siklar_metni) + "\n\n*Cevap vermek için sadece harfi (**A, B, C veya D**) yazın! Süre 30 Saniye!*"
        await message.channel.send(final_mesaj)

        def check(m):
            return m.channel == message.channel and m.content.strip().upper() == dogru_harf and not m.author.bot

        try:
            kazanan_mesaj = await bot.wait_for('message', check=check, timeout=30.0)
            kazanan = kazanan_mesaj.author
            user_profil = get_user(kazanan.id)
            user_profil["para"] += 50
            await message.channel.send(f"🎉 Tebrikler {kazanan.mention}! Doğru harfi (**{dogru_harf}**) bildin ve **50 BTS Parası** kazandın! 💰 Güncel Bakiye: {user_profil['para']} BTS")
        except asyncio.TimeoutError:
            await message.channel.send(f"⏰ Süre bitti! Doğru cevap **{dogru_harf}** şıkkı olmalıydı.")

    await bot.process_commands(message)

# ====================================================================
# 🛡️ YETKİLİ & YÖNETİM KOMUTLARI
# ====================================================================

@bot.command()
@commands.has_permissions(administrator=True)
async def ayarlar(ctx):
    embed = discord.Embed(title="🛡️ Sunucu Filtre Ayarları", color=discord.Color.blue())
    embed.add_field(name="🤬 Küfür Engeli", value="🟢 Aktif" if sunucu_ayarlari["kufur_engel"] else "🔴 Pasif", inline=True)
    embed.add_field(name="🔗 Reklam Engeli", value="🟢 Aktif" if sunucu_ayarlari["reklam_engel"] else "🔴 Pasif", inline=True)
    embed.add_field(name="⚡ Spam Engeli", value="🟢 Aktif" if sunucu_ayarlari["spam_engel"] else "🔴 Pasif", inline=True)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def kufurengel(ctx):
    sunucu_ayarlari["kufur_engel"] = not sunucu_ayarlari["kufur_engel"]
    await ctx.send(f"🤬 Küfür filtresi **{'açıldı 🟢' if sunucu_ayarlari['kufur_engel'] else 'kapatıldı 🔴'}**.")

@bot.command()
@commands.has_permissions(administrator=True)
async def reklamengel(ctx):
    sunucu_ayarlari["reklam_engel"] = not sunucu_ayarlari["reklam_engel"]
    await ctx.send(f"🔗 Reklam filtresi **{'açıldı 🟢' if sunucu_ayarlari['reklam_engel'] else 'kapatıldı 🔴'}**.")

@bot.command()
@commands.has_permissions(administrator=True)
async def spamengel(ctx):
    sunucu_ayarlari["spam_engel"] = not sunucu_ayarlari["spam_engel"]
    await ctx.send(f"⚡ Spam filtresi **{'açıldı 🟢' if sunucu_ayarlari['spam_engel'] else 'kapatıldı 🔴'}**.")

@bot.command()
@commands.has_permissions(administrator=True)
async def logayarla(ctx, kanal: discord.TextChannel):
    sunucu_ayarlari["log_kanal_id"] = kanal.id
    await ctx.send(f"📋 Log kanalı {kanal.mention} yapıldı!")

@bot.command(name="hosgeldin-ve-baybay-ayarla")
@commands.has_permissions(administrator=True)
async def welcome_ayarla(ctx, kanal: discord.TextChannel):
    sunucu_ayarlari["welcome_kanal_id"] = kanal.id
    await ctx.send(f"👋 Giriş-Çıkış kanalı {kanal.mention} yapıldı!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int):
    await ctx.channel.purge(limit=sayi + 1)
    await ctx.send(f"🗑️ **{sayi}** adet mesaj temizlendi.", delete_after=3)

# ====================================================================
# 🎮 EĞLENCE & ETKİLEŞİM KOMUTLARI
# ====================================================================

@bot.command()
async def slaps(ctx, member: discord.Member):
    gifs = [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbms1OXVwMTN0bXl6cXp3dWptb3Y2Zmxtb3AwYm5kdmsyeDlybzg2ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GceBmw5whL17gB7K4H/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnptamR3ZXdrb3dndG5hZXlyYmRpdndmZmtwYW92MWx3NWFxajc2MCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Zau0yrl17uzdEXiD9S/giphy.gif"
    ]
    await ctx.send(f"👋 {ctx.author.mention}, {member.mention} üyesini evire çevire tokatladı!\n{random.choice(gifs)}")

@bot.command()
async def kiss(ctx, member: discord.Member):
    gifs = [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbXN6dW55b3A0aW9oMnlpdDdmN2psdmMxZmk1bmptNmV0ZHp0ZnppZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FqSPe99hkAo6S07SdB/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDVqNjhvZnYyeDQwM3I1OGNlbWFpZDVxcWoxbms5ajYxbGwwbXJzMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QGc8RgRvOB9F869p1D/giphy.gif"
    ]
    await ctx.send(f"💋 {ctx.author.mention}, {member.mention} üyesine kocaman sulu bir öpücük kondurdu!\n{random.choice(gifs)}")

@bot.command()
async def sarıl(ctx, member: discord.Member):
    gifs = [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHIwd3p3Nm9tdTBoMDdtNjhyMzJsdWFmOHI0c2xkbXZ4ZDR6eWx6biZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lrr9rHuoJOE0w/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW8zYno2MWp6Z3Z2bnY2bTZreHZreW40aDJ5eGZsdXBnOXBrY2txNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5OqXb948EBkyUcnwHt/giphy.gif"
    ]
    await ctx.send(f"🤗 {ctx.author.mention}, {member.mention} üyesine sımsıkı sarıldı!\n{random.choice(gifs)}")

@bot.command(name="uçangüvercin")
async def ucanguvercin(ctx, member: discord.Member):
    gif = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbXZuMWV1amMxNXl5cDZ3dW80dG9nNnk4Yzg5dXBveTN5d3Q1NndhdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l3q2K1M66D069Jp6M/giphy.gif"
    await ctx.send(f"🕊️ {member.mention}, Çatık kaşlı bir güvercin uçarak sana doğru geliyor... **Tekme atıyor bu güvercin sana!** 🥊💥\n{gif}")

@bot.command()
async def askolcer(ctx, member: discord.Member):
    await ctx.send(f"❤️ {ctx.author.mention} ile {member.mention} arasındaki aşk oranı: **%{random.randint(0, 100)}**")

@bot.command()
async def efkarolcer(ctx):
    await ctx.send(f"🚬 {ctx.author.mention} o anki efkar durumun: **%{random.randint(0, 100)}** yak yak...")

@bot.command()
async def sanslisayi(ctx):
    await ctx.send(f"🍀 {ctx.author.mention}, bugün senin şanslı sayın: **{random.randint(1, 100)}**")

@bot.command()
async def ship(ctx):
    aktifs = [m for m in ctx.guild.members if not m.bot and m != ctx.author]
    if not aktifs: return await ctx.send("Kullanıcı bulunamadı.")
    await ctx.send(f"💖 **Şans Eseri Shiplendiniz!** \n💞 {ctx.author.mention} & {random.choice(aktifs).mention} \n💘 Aşk Oranı: **%{random.randint(0, 100)}**")

@bot.command()
async def ship2(ctx, member: discord.Member):
    await ctx.send(f"❤️‍🔥 **AMANSIZ BİR AŞK!** \n💞 {ctx.author.mention} & {member.mention} \n🔥 Aşk Oranı: **%99999** \n🏆 *Bu aşk ölçülemez, siz birbiriniz için yaratılmışsınız!*")

@bot.command()
async def saat(ctx):
    # Dış kütüphane bağımlılığı tamamen kaldırıldı, Türkiye saati el ile senkronize edildi.
    tz_turkey = timezone(timedelta(hours=3))
    su_an = datetime.now(tz_turkey).strftime("%H:%M:%S")
    tarih = datetime.now(tz_turkey).strftime("%d/%m/%Y")
    await ctx.send(f"⏰ {ctx.author.mention}, şu an canlı zaman dilimi:\n📅 Tarih: **{tarih}**\n⏱️ Saat: **{su_an}**")

# ====================================================================
# 💰 EKONOMİ & CÜZDAN SİSTEMİ
# ====================================================================

@bot.command()
async def para(ctx, member: discord.Member = None):
    hedef = member or ctx.author
    profil = get_user(hedef.id)
    await ctx.send(f"💰 {hedef.mention} cüzdanında **{profil['para']} BTS Parası** var.")

@bot.command()
async def slots(ctx, miktar: int):
    profil = get_user(ctx.author.id)
    
    if miktar <= 0:
        await ctx.send("❌ Lütfen 0'dan büyük geçerli bir para miktarı girin canım!")
        return
        
    if profil["para"] < miktar:
        await ctx.send(f"❌ Cüzdanında yeterli para yok tatlım! Güncel Bakiyen: **{profil['para']} BTS**")
        return
    
    emojiler = ["🍒", "🍋", "🍇", "💎", "🔔"]
    s1, s2, s3 = random.choice(emojiler), random.choice(emojiler), random.choice(emojiler)
    
    mesaj = await ctx.send("🎰 **Slots makinesi dönüyor...**")
    await asyncio.sleep(1.5)
    
    if s1 == s2 == s3:
        kazanc = miktar * 4
        profil["para"] += kazanc
        await mesaj.edit(content=f"[ {s1} | {s2} | {s3} ]\n🎉 **MÜKEMMEL! 3'te 3 YAPTIN!** \n💰 **+{kazanc} BTS** kazandın! Yeni Bakiyen: **{profil['para']} BTS**")
    elif s1 == s2 or s2 == s3 or s1 == s3:
        kazanc = int(miktar * 1.5)
        profil["para"] += kazanc
        await mesaj.edit(content=f"[ {s1} | {s2} | {s3} ]\n✨ **Çift Yakaladın!** \n💰 **+{kazanc} BTS** kazandın! Yeni Bakiyen: **{profil['para']} BTS**")
    else:
        profil["para"] -= miktar
        await mesaj.edit(content=f"[ {s1} | {s2} | {s3} ]\n😭 **Şanssız günündesin, kaybettin!** \n💸 **-{miktar} BTS** cüzdandan gitti. Kalan Bakiyen: **{profil['para']} BTS**")

@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🤖 BTS Bot Komut Menüsü", color=discord.Color.green())
    embed.add_field(name="🛡️ Yönetim", value="`!ayarlar`, `!kufurengel`, `!reklamengel`, `!spamengel`, `!sil [sayı]`", inline=False)
    embed.add_field(name="🎮 Eğlence & Etkileşim", value="`!slaps`, `!kiss`, `!sarıl`, `!uçangüvercin`, `!askolcer`, `!efkarolcer`, `!sanslisayi`, `!ship`, `!ship2`, `!saat`", inline=False)
    embed.add_field(name="💰 Ekonomi", value="`!para`, `!slots [miktar]`", inline=False)
    await ctx.send(embed=embed)

keep_alive()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
            
