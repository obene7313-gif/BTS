import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import asyncio
import datetime
import pytz
from flask import Flask
from threading import Thread
import os

# --- DIŞ DOSYADAN VERİ ÇEKME ---
try:
    from iltifatlar import iltifatlar, selamlamalar
except ImportError:
    iltifatlar = ["Çok tatlısın!", "Bugün harika görünüyorsun!", "Harikasın!"]
    selamlamalar = ["Aleykümselam, hoş geldin", "Selam! Naber?"]

# --- FLASK WEB SUNUCUSU (7/24 Aktif Tutmak İçin) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot 7/24 Aktif ve Güvenli!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    Thread(target=run).start()

# --- BOT AYARLARI ---
intents = discord.Intents.all()

class UltraBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_command('yardim')

bot = UltraBot(command_prefix="!", intents=intents)

# --- VERİTABANI VE AYARLAR SİMÜLASYONU ---
server_settings = {
    "kufurengel": False,
    "reklamengel": False,
    "spamengel": False,
    "log_kanal": None,
    "welcome_kanal": None,
    "karaliste": ["pic", "orospu", "sik", "amk"]
}

bts_puan = {}
afk_users = {}
user_last_msg_time = {}

# --- BTS TRIVIA SORULARI HAVUZU (50 ADET) ---
bts_sorulari = [
    {"soru": "BTS hangi yıl çıkış yapmıştır?", "cevap": "2013", "siklar": ["2011", "2012", "2013", "2014"]},
    {"soru": "BTS'in açılımı nedir?", "cevap": "Bangtan Sonyeondan", "siklar": ["Bangtan Boys", "Bangtan Sonyeondan", "Beyond The Scene", "Born To Slay"]},
    {"soru": "BTS'in lideri kimdir?", "cevap": "RM", "siklar": ["Jin", "Suga", "RM", "Jimin"]},
    {"soru": "BTS'in en büyük üyesi (en yaşlısı) kimdir?", "cevap": "Jin", "siklar": ["Jin", "Suga", "RM", "J-Hope"]},
    {"soru": "BTS'in en küçük üyesi (maknae) kimdir?", "cevap": "Jungkook", "siklar": ["Jimin", "V", "Jungkook", "RM"]},
    {"soru": "BTS'in resmi fandom adı nedir?", "cevap": "A.R.M.Y", "siklar": ["BLINK", "A.R.M.Y", "EXO-L", "STAY"]},
    {"soru": "BTS hangi şirketetin çatısı altında kurulmuştur?", "cevap": "Big Hit (HYBE)", "siklar": ["SM", "YG", "JYP", "Big Hit (HYBE)"]},
    {"soru": "BTS'in çıkış şarkısı hangisidir?", "cevap": "No More Dream", "siklar": ["No More Dream", "Boy In Luv", "Dope", "I Need U"]},
    {"soru": "Hangi üyenin sahne adı 'V' harfinden oluşur?", "cevap": "Taehyung", "siklar": ["Jimin", "Taehyung", "Jungkook", "Suga"]},
    {"soru": "BTS'in Billboard Hot 100 listesinde 1 numara olan ilk tamamen İngilizce şarkısı hangisidir?", "cevap": "Dynamite", "siklar": ["Butter", "Dynamite", "Life Goes On", "Permission to Dance"]},
    {"soru": "Min Yoongi hangi üyenin gerçek adıdır?", "cevap": "Suga", "siklar": ["Suga", "J-Hope", "Jin", "RM"]},
    {"soru": "Jung Hoseok'un sahne adı nedir?", "cevap": "J-Hope", "siklar": ["RM", "Suga", "J-Hope", "V"]},
    {"soru": "BTS'in resmi rengi veya sembolikleşen rengi hangisidir?", "cevap": "Mor", "siklar": ["Pembe", "Mavi", "Mor", "Siyah"]},
    {"soru": "'I purple you' (Sizi morluyorum) sözünü hangi üye literatüre kazandırmıştır?", "cevap": "V", "siklar": ["RM", "Jimin", "V", "Jungkook"]},
    {"soru": "Suga'nın solo projelerinde kullandığı diğer sahne adı nedir?", "cevap": "Agust D", "siklar": ["Agust D", "Gloss", "Min PD", "Lil Meow"]},
    {"soru": "Hangi BTS üyesi modern dans geçmişine sahiptir ve Busan Sanat Lisesi'ne birincilikle girmiştir?", "cevap": "Jimin", "siklar": ["J-Hope", "Jimin", "V", "Jungkook"]},
    {"soru": "BTS'in 'Love Yourself' albüm serisinin ünlü başlık şarkısı hangisidir?", "cevap": "Fake Love", "siklar": ["DNA", "Fake Love", "Idol", "Run"]},
    {"soru": "Hangi üye grubun 'Golden Maknae'si (Altın Küçük) olarak bilinir?", "cevap": "Jungkook", "siklar": ["Jimin", "V", "Jungkook", "Jin"]},
    {"soru": "BTS'in hayranları için tasarladığı resmi ışıklı çubuğun (lightstick) adı nedir?", "cevap": "Army Bomb", "siklar": ["Muster Stick", "Army Bomb", "Bangtan Light", "Purple Rod"]},
    {"soru": "BTS, Birleşmiş Milletler (UN) genel kurulunda ilk kez hangi yıl konuşma yapmıştır?", "cevap": "2018", "siklar": ["2016", "2017", "2018", "2019"]},
    {"soru": "BTS'in popüler reality şov programının adı nedir?", "cevap": "Run BTS!", "siklar": ["BTS In The Soop", "Run BTS!", "Rookie King", "American Hustle Life"]},
    {"soru": "Kim Seokjin'in lakaplarından biri hangisidir?", "cevap": "Worldwide Handsome", "siklar": ["Worldwide Handsome", "Golden Boy", "Gucci Boy", "Sunshine"]},
    {"soru": "Grubun ana dansçısı ve koreografi lideri kimdir?", "cevap": "J-Hope", "siklar": ["Jimin", "J-Hope", "Jungkook", "V"]},
    {"soru": "BTS'in Line Friends ile işbirliği yaparak oluşturduğu karakter serisinin adı nedir?", "cevap": "BT21", "siklar": ["BTS-Toons", "BT21", "Bangtan Pets", "Line-BTS"]},
    {"soru": "Jungkook'un BT21 karakterinin adı nedir?", "cevap": "Cooky", "siklar": ["Tata", "Chimmy", "Cooky", "Koya"]},
    {"soru": "RM'in IQ seviyesinin kaç olduğu bilinmektedir?", "cevap": "148", "siklar": ["120", "135", "148", "160"]},
    {"soru": "BTS'in Halsey ile düet yaptığı popüler şarkı hangisidir?", "cevap": "Boy With Luv", "siklar": ["Idol", "Boy With Luv", "On", "Stay Gold"]},
    {"soru": "Suga'nın BT21 karakterinin adı nedir?", "cevap": "Shooky", "siklar": ["Shooky", "Mang", "RJ", "Van"]},
    {"soru": "BTS'in hangi albümü onlara ilk kez bir Daesang (Yılın Albümü) ödülü kazandırmıştır?", "cevap": "The Most Beautiful Moment in Life: Young Forever", "siklar": ["Wings", "Dark & Wild", "The Most Beautiful Moment in Life: Young Forever", "Love Yourself: Tear"]},
    {"soru": "Hangi şarkıda 'Geonbae (Şerefe)' kelimesi sıkça geçer ve parti havasındadır?", "cevap": "Dionysus", "siklar": ["Dionysus", "Fire", "Idol", "Dope"]},
    {"soru": "BTS'in 2020 yılında çıkardığı 'Map of the Soul: 7' albümünün sert ve güçlü başlık şarkısı hangisidir?", "cevap": "ON", "siklar": ["Black Swan", "ON", "Louder Than Bombs", "Filter"]},
    {"soru": "V'nin (Taehyung) oynadığı tarihi Kore dizisinin adı nedir?", "cevap": "Hwarang", "siklar": ["Hwarang", "Goblin", "The King", "Dream High"]},
    {"soru": "Hangi üye solak olmasına rağmen sağ elini de çok aktif kullanabilir?", "cevap": "V", "siklar": ["RM", "Suga", "V", "Jimin"]},
    {"soru": "Jimin'in solo şarkılarından biri hangisidir?", "cevap": "Lie", "siklar": ["Lie", "Awake", "Intro: Persona", "Epiphany"]},
    {"soru": "BTS üyelerinden hangisi Daegu doğumludur?", "cevap": "Suga & V", "siklar": ["Suga & V", "RM & Jimin", "Jin & J-Hope", "Jungkook & Jin"]},
    {"soru": "BTS'in hayır kurumu UNICEF ile birlikte yürüttüğü kampanyanın adı nedir?", "cevap": "Love Myself", "siklar": ["Save Me", "Love Myself", "End Violence", "Be Yourself"]},
    {"soru": "J-Hope'un Becky G ile işbirliği yaptığı solo hit şarkısı hangisidir?", "cevap": "Chicken Noodle Soup", "siklar": ["More", "Arson", "Daydream", "Chicken Noodle Soup"]},
    {"soru": "BTS'in Grammy Ödülleri'nde sahne alan ilk Koreli grup olduğu yıl hangisidir?", "cevap": "2020", "siklar": ["2018", "2019", "2020", "2021"]},
    {"soru": "Jin'in BT21 karakteri olan beyaz alpakaya ne ad verilir?", "cevap": "RJ", "siklar": ["RJ", "Koya", "Tata", "Mang"]},
    {"soru": "BTS'in 2016 yılında yayınlanan ve 'Kan, ter ve gözyaşlarımı al' sözleriyle bilinen ünlü şarkısı hangisidir?", "cevap": "Blood Sweat & Tears", "siklar": ["Wings", "Blood Sweat & Tears", "Save Me", "Fire"]},
    {"soru": "Jungkook'un solo şarkısı 'Euphoria' hangi albüm projesinde yer alır?", "cevap": "Love Yourself: Answer", "siklar": ["Love Yourself: Tear", "Love Yourself: Her", "Love Yourself: Answer", "Wings"]},
    {"soru": "RM'in BT21 karakteri olan uykucu koalanın adı nedir?", "cevap": "Koya", "siklar": ["Koya", "Shooky", "Mang", "Chimmy"]},
    {"soru": "BTS'in 'Black Swan' şarkısının ilk koreografi videosunda hangi tarz dans ön plana çıkmıştır?", "cevap": "Modern Bale / Çağdaş Dans", "siklar": ["Hip-hop", "Breakdance", "Modern Bale / Çağdaş Dans", "Poping"]},
    {"soru": "Suga'nın müzik yaparken ve piyano çalarken sıklıkla bahsettiği favori rengi nedir?", "cevap": "Kahverengi", "siklar": ["Siyah", "Beyaz", "Kahverengi", "Mavi"]},
    {"soru": "BTS'in 'Yet To Come' konseri 2022 yılında Kore'nin hangi şehrinde gerçekleşmiştir?", "cevap": "Busan", "siklar": ["Seul", "Busan", "Incheon", "Daegu"]},
    {"soru": "Hangi BTS klibi tren garı, lunapark ve kış temaları içerir, derin dostluğu anlatır?", "cevap": "Spring Day", "siklar": ["Spring Day", "Run", "I Need U", "Life Goes On"]},
    {"soru": "J-Hope'un BT21 karakteri olan maskeli atın adı nedir?", "cevap": "Mang", "siklar": ["Mang", "Cooky", "Tata", "RJ"]},
    {"soru": "BTS üyelerinin tamamının dostluk dövmesi olarak yaptırdığı sayı hangisidir?", "cevap": "7", "siklar": ["1", "7", "13", "0"]},
    {"soru": "V'nin BT21 karakteri olan kalp kafalı uzaylının adı nedir?", "cevap": "Tata", "siklar": ["Tata", "Chimmy", "Koya", "RJ"]},
    {"soru": "Jimin'in BT21 karakteri olan sarı kapüşonlu köpeğin adı nedir?", "cevap": "Chimmy", "siklar": ["Chimmy", "Cooky", "Shooky", "Van"]}
]

def get_turkey_time():
    return datetime.datetime.now(pytz.timezone('Europe/Istanbul'))

# --- ORTAK BUTONLU OYUN GÖRÜNÜMÜ ---
class GameView(View):
    def __init__(self, dogru_cevap, siklar):
        super().__init__(timeout=15.0)
        self.dogru_cevap = dogru_cevap
        self.cevaplandi = False
        for sik in siklar:
            btn = Button(label=str(sik), style=discord.ButtonStyle.blurple)
            btn.callback = self.make_callback(sik)
            self.add_item(btn)

    def make_callback(self, sik):
        async def callback(interaction: discord.Interaction):
            if self.cevaplandi:
                await interaction.response.send_message("❌ Bu soru zaten cevaplandı!", ephemeral=True)
                return
            
            if str(sik) == str(self.dogru_cevap):
                self.cevaplandi = True
                self.stop()
                u_id = interaction.user.id
                bts_puan[u_id] = bts_puan.get(u_id, 100) + 50
                await interaction.response.send_message(f"🎉 Doğru Cevap! {interaction.user.mention} 50 BTS Parası kazandı! Yeni bakiye: {bts_puan[u_id]}")
                await interaction.message.edit(view=None)
            else:
                await interaction.response.send_message("❌ Yanlış şık! Tekrar dene.", ephemeral=True)
        return callback

# --- EVENTLER ---
@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} olarak giriş yaptı.")
    await bot.change_presence(activity=discord.Game(name="!yardim | Koruma & Eğlence"))

@bot.event
async def on_member_join(member):
    if server_settings["welcome_kanal"]:
        channel = bot.get_channel(server_settings["welcome_kanal"])
        if channel:
            await channel.send(f"📥 Hoş geldin {member.mention}! Sunucumuza neşe getirdin.")

@bot.event
async def on_member_remove(member):
    if server_settings["welcome_kanal"]:
        channel = bot.get_channel(server_settings["welcome_kanal"])
        if channel:
            await channel.send(f"📤 **{member.name}** sunucudan ayrıldı. Görüşmek üzere!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # --- AFK KONTROLÜ ---
    if message.author.id in afk_users:
        del afk_users[message.author.id]
        await message.channel.send(f"👋 Hoş geldin {message.author.mention}! Tekrar aktifsin, AFK modun kapatıldı.", delete_after=5)

    for mention in message.mentions:
        if mention.id in afk_users:
            sebep = afk_users[mention.id]
            await message.channel.send(f"⚠️ {message.author.mention}, etiketlediğin kullanıcı **{mention.name}** şu an AFK!\n**Sebep:** {sebep}")

    msg_content = message.content.lower()
    log_kanal = bot.get_channel(server_settings["log_kanal"]) if server_settings["log_kanal"] else None

    # SA-AS Sistemi
    if msg_content == "sa":
        rastgele_selam = random.choice(selamlamalar)
        await message.channel.send(f"{rastgele_selam} {message.author.mention}!")

    # Küfür Koruması
    if server_settings["kufurengel"]:
        for sansur in server_settings["karaliste"]:
            if sansur in msg_content:
                try:
                    await message.delete()
                    if log_kanal:
                        await log_kanal.send(f"🚫 **Küfür Engellendi:** {message.author.mention} -> {message.content}")
                except:
                    pass
                return

    # Reklam Koruması
    if server_settings["reklamengel"] and ("http" in msg_content or "discord.gg/" in msg_content):
        try:
            await message.delete()
            if log_kanal:
                await log_kanal.send(f"🔗 **Reklam Engellendi:** {message.author.mention} -> {message.content}")
        except:
            pass
        return

    # Spam Engeli
    if server_settings["spamengel"]:
        now = datetime.datetime.now()
        last_time = user_last_msg_time.get(message.author.id)
        user_last_msg_time[message.author.id] = now
        if last_time and (now - last_time).total_seconds() < 0.8:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, lütfen çok hızlı mesaj gönderme!", delete_after=3)
            except:
                pass
            return

    # --- ORANSAL TETİKLEYİCİLER ---
    zar = random.random()

    # 1. %3 İhtimalle İltifat
    if zar < 0.03:
        await message.channel.send(f"{message.author.mention} {random.choice(iltifatlar)}")
        await bot.process_commands(message)
        return

    # 2. %2 İhtimalle BTS Trivia Sorusu
    elif zar < 0.05:
        soru_data = random.choice(bts_sorulari)
        siklar = soru_data["siklar"].copy()
        random.shuffle(siklar)
        
        view = GameView(soru_data["cevap"], siklar)
        msg = await message.channel.send(f"💜 **BTS TRIVIA SORUSU!**\n**{soru_data['soru']}**\n*Doğru şıkkı işaretle! (Süre: 15sn)*", view=view)
        
        await asyncio.sleep(15)
        if not view.cevaplandi:
            try:
                await msg.edit(content=f"⏱️ Süre doldu! Doğru cevap **{soru_data['cevap']}** olacaktı.", view=None)
            except:
                pass
        await bot.process_commands(message)
        return

    # 3. %7 İhtimalle MATEMATİK Sorusu
    elif zar < 0.12:
        seviye = random.choice(["cok_kolay", "orta_zor", "ultra_zor"])
        
        if seviye == "cok_kolay":
            islem = random.choice(["+", "-", "*"])
            if islem == "*":
                num1 = random.randint(2, 9)
                num2 = random.randint(2, 9)
            else:
                num1 = random.randint(1, 15)
                num2 = random.randint(1, 15)
                
            cevap = num1 + num2 if islem == "+" else (num1 - num2 if islem == "-" else num1 * num2)
            
            siklar = {cevap}
            while len(siklar) < 4:
                yanlis = cevap + random.randint(-5, 5)
                siklar.add(yanlis)

        elif seviye == "orta_zor":
            islem = random.choice(["+", "-"])
            num1 = random.randint(100, 800)
            num2 = random.randint(100, 800)
            cevap = num1 + num2 if islem == "+" else num1 - num2
            
            siklar = {cevap}
            while len(siklar) < 4:
                yanlis = cevap + random.randint(-40, 40)
                siklar.add(yanlis)

        else: # ultra_zor
            islem = "*"
            num1 = random.randint(12, 45)
            num2 = random.randint(12, 45)
            cevap = num1 * num2
            
            siklar = {cevap}
            while len(siklar) < 4:
                sapma = random.randint(10, 120)
                yanlis = cevap + random.choice([sapma, -sapma])
                if yanlis != cevap:
                    siklar.add(yanlis)

        siklar_list = list(siklar)
        random.shuffle(siklar_list)
        
        gosterim_islem = "x" if islem == "*" else islem
        
        view = GameView(cevap, siklar_list)
        msg = await message.channel.send(f"📊 **MATEMATİK SORUSU! ({seviye.replace('_', ' ').upper()})**\n**{num1} {gosterim_islem} {num2} = ?**\n*Cevaplamak için 15 saniyen var!*", view=view)
        
        await asyncio.sleep(15)
        if not view.cevaplandi:
            try:
                await msg.edit(content=f"⏱️ Süre doldu! Doğru cevap **{cevap}** olacaktı.", view=None)
            except:
                pass
        await bot.process_commands(message)
        return

    # Eğer hiçbir ihtimal tetiklenmediyse komutları normal şekilde yürütür
    await bot.process_commands(message)
# --- YETKİLİ & YÖNETİM KOMUTLARI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def ayarlar(ctx):
    embed = discord.Embed(title="⚙️ Sunucu Ayarları", color=discord.Color.blue())
    embed.add_field(name="Küfür Filtresi", value="✅ Aktif" if server_settings["kufurengel"] else "❌ Pasif")
    embed.add_field(name="Reklam Filtresi", value="✅ Aktif" if server_settings["reklamengel"] else "❌ Pasif")
    embed.add_field(name="Spam Filtresi", value="✅ Aktif" if server_settings["spamengel"] else "❌ Pasif")
    embed.add_field(name="Log Kanalı", value=f"<#{server_settings['log_kanal']}>" if server_settings["log_kanal"] else "❌ Ayarlanmamış")
    embed.add_field(name="Giriş-Çıkış Kanalı", value=f"<#{server_settings['welcome_kanal']}>" if server_settings["welcome_kanal"] else "❌ Ayarlanmamış")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def kufurengel(ctx):
    server_settings["kufurengel"] = not server_settings["kufurengel"]
    durum = 'AÇIK' if server_settings['kufurengel'] else 'KAPALI'
    await ctx.send(f"🛡️ Küfür filtresi: **{durum}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def reklamengel(ctx):
    server_settings["reklamengel"] = not server_settings["reklamengel"]
    durum = 'AÇIK' if server_settings['reklamengel'] else 'KAPALI'
    await ctx.send(f"🛡️ Reklam filtresi: **{durum}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def spamengel(ctx):
    server_settings["spamengel"] = not server_settings["spamengel"]
    durum = 'AÇIK' if server_settings['spamengel'] else 'KAPALI'
    await ctx.send(f"🛡️ Spam filtresi: **{durum}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def logayarla(ctx, channel: discord.TextChannel):
    server_settings["log_kanal"] = channel.id
    await ctx.send(f"✅ Log kanalı başarıyla {channel.mention} olarak ayarlandı!")

@bot.command(name="hosgeldin-ve-baybay-ayarla")
@commands.has_permissions(administrator=True)
async def welcomeayarla(ctx, channel: discord.TextChannel):
    server_settings["welcome_kanal"] = channel.id
    await ctx.send(f"✅ Giriş-Çıkış mesaj kanalı {channel.mention} olarak ayarlandı!")

@bot.command()
@commands.has_permissions(administrator=True)
async def karaliste(ctx, islem=None, *, kelime=None):
    if not islem:
        await ctx.send(f"📝 **Yasaklı Kelimeler:** {', '.join(server_settings['karaliste'])}")
    elif islem == "ekle" and kelime:
        if kelime.lower() not in server_settings["karaliste"]:
            server_settings["karaliste"].append(kelime.lower())
            await ctx.send(f"✅ **{kelime}** yasaklı kelime listesine eklendi.")
    elif islem == "cikar" and kelime:
        if kelime.lower() in server_settings["karaliste"]:
            server_settings["karaliste"].remove(kelime.lower())
            await ctx.send(f"✅ **{kelime}** yasaklı kelime listesinden çıkarıldı.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int):
    await ctx.channel.purge(limit=sayi + 1)
    await ctx.send(f"🗑️ **{sayi}** adet mesaj temizlendi.", delete_after=4)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def sustur(ctx, member: discord.Member, sure: str, *, sebep="Belirtilmedi"):
    time_dict = {"m": 1, "h": 60, "d": 1440}
    unit = sure[-1]
    if unit not in time_dict or not sure[:-1].isdigit():
        await ctx.send("❌ Geçersiz süre formatı! Örn: 5m, 2h, 1d")
        return
    minutes = int(sure[:-1]) * time_dict[unit]
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=sebep)
    await ctx.send(f"🤐 {member.mention} **{sure}** boyunca susturuldu. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def ac(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 {member.mention} kullanıcısının susturulması kaldırıldı.")

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    pos = ctx.channel.position
    new_ch = await ctx.channel.clone(reason="Nuke İşlemi")
    await ctx.channel.delete()
    await new_ch.edit(position=pos)
    await new_ch.send("💥 Kanal başarıyla sıfırlandı (Nuke)!\nhttps://tenor.com/view/explosion-mushroom-cloud-atomic-bomb-bomb-boom-gif-4464835")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ {member.mention} isimli üyeye **{role.name}** rolü verildi.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"✅ {member.mention} isimli üyeden **{role.name}** rolü geri alındı.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 **{member.name}** sunucudan banlandı. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 **{member.name}** sunucudan atıldı. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal yazışmaya kapatıldı!")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Kanal tekrar yazışmaya açıldı.")

# --- AFK SİSTEMİ ---
@bot.command()
async def afk(ctx, *, sebep=None):
    if sebep is None:
        afk_users[ctx.author.id] = "Belirtilmedi"
        await ctx.send(f"💤 {ctx.author.mention}, başarıyla AFK moduna geçtin! İlk yazıldığında aktifleşirsin tatlış bir şey.")
    else:
        afk_users[ctx.author.id] = sebep
        await ctx.send(f"💤 {ctx.author.mention}, başarıyla AFK moduna geçtin!\n**Sebep:** {sebep}")

# --- EĞLENCE & ETKİLEŞİM KOMUTLARI ---
@bot.command()
async def uçangüvercin(ctx, member: discord.Member):
    await ctx.send(f"🕊️ {ctx.author.mention}, {member.mention} kullanıcısına uçarak gelen çatık kaşlı bir güvercin fırlattı!\n**Tekme atıyor bu güvercin sana!**\nhttps://tenor.com/view/pigeon-kick-funny-birds-gif-14470635")

@bot.command()
async def saat(ctx):
    tr_time = get_turkey_time().strftime('%d/%m/%Y %H:%M:%S')
    await ctx.send(f"⏰ **Güncel Türkiye Saati ve Tarihi:** {tr_time}")

@bot.command()
async def slaps(ctx, member: discord.Member):
    await ctx.send(f"🖐️ {ctx.author.mention}, {member.mention} kullanıcısını Osmanlı tokadıyla uçurdu!\nhttps://tenor.com/view/slap-in-the-face-angry-gif-14689404")

@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"💋 {ctx.author.mention}, {member.mention} kullanıcısını sulu sulu öptü!\nhttps://tenor.com/view/anime-kiss-gif-25745155")

@bot.command()
async def sarıl(ctx, member: discord.Member):
    await ctx.send(f"🤗 {ctx.author.mention}, {member.mention} kullanıcısına sımsıkı sarıldı!\nhttps://tenor.com/view/hug-anime-love-gif-25644292")

@bot.command()
async def askolcer(ctx, member: discord.Member):
    oran = random.randint(0, 100)
    await ctx.send(f"❤️ {ctx.author.mention} ile {member.mention} arasındaki aşk oranı: **%{oran}**")

@bot.command()
async def efkarolcer(ctx):
    oran = random.randint(0, 100)
    await ctx.send(f"🚬 {ctx.author.mention} bugünkü efkar durumun: **%{oran}**")

@bot.command()
async def sanslisayi(ctx):
    sayi = random.randint(1, 100)
    await ctx.send(f"🎲 {ctx.author.mention}, bugün senin şanslı sayın: **{sayi}**")

@bot.command()
async def ship(ctx):
    members = [m for m in ctx.guild.members if not m.bot]
    if len(members) < 2:
        return
    m1 = ctx.author
    m2 = random.choice(members)
    while m2.id == m1.id:
        m2 = random.choice(members)
    oran = random.randint(0, 100)
    await ctx.send(f"💕 **Günün Shipi:** {m1.mention} X {m2.mention} | Kalp Oranı: **%{oran}**")

@bot.command()
async def ship2(ctx, member: discord.Member):
    await ctx.send(f"💖 {ctx.author.mention} X {member.mention}\n**Aşk Oranı: %99999! Bu aşk ölçülemez!**")

# --- EKONOMİ & OYUN ---
@bot.command()
async def para(ctx, member: discord.Member = None):
    target = member or ctx.author
    bakiye = bts_puan.get(target.id, 100)
    bts_puan[target.id] = bakiye
    await ctx.send(f"💰 {target.mention}: **{bakiye} BTS Parası**")

@bot.command()
async def slots(ctx, miktar: int):
    bakiye = bts_puan.get(ctx.author.id, 100)
    if miktar <= 0 or miktar > bakiye:
        await ctx.send("❌ Geçersiz miktar veya yetersiz bakiye!")
        return
    
    slots_icons = ["🍒", "🍋", "🍇", "🍊", "💎"]
    r1, r2, r3 = random.choice(slots_icons), random.choice(slots_icons), random.choice(slots_icons)
    msg = f"🎰 **{ctx.author.name}** slots çeviriyor...\n| {r1} | {r2} | {r3} |\n"
    
    if r1 == r2 == r3:
        odul = miktar * 4
        bts_puan[ctx.author.id] = bakiye + odul
        await ctx.send(msg + f"🔥 **MÜKEMMEL! 3'te 3 Yaptın!** {odul} BTS Parası kazandın!")
    elif r1 == r2 or r2 == r3 or r1 == r3:
        odul = miktar * 2
        bts_puan[ctx.author.id] = bakiye + odul
        await ctx.send(msg + f"✨ **Güzel! Çift yakaladın.** {odul} BTS Parası kazandın!")
    else:
        bts_puan[ctx.author.id] = bakiye - miktar
        await ctx.send(msg + f"💥 **Kaybettin!** {miktar} BTS Parası cüzdanından uçtu.")

# --- BİLGİ & SİSTEM ---
@bot.command()
async def spty(ctx, member: discord.Member = None):
    target = member or ctx.author
    spotify_act = None
    for act in target.activities:
        if isinstance(act, discord.Spotify):
            spotify_act = act
            break
            
    if spotify_act:
        embed = discord.Embed(title=f"🎵 {target.name} Spotify Dinliyor", color=discord.Color.green())
        embed.add_field(name="Şarkı", value=spotify_act.title, inline=False)
        embed.add_field(name="Sanatçı", value=", ".join(spotify_act.artists), inline=False)
        embed.add_field(name="Albüm", value=spotify_act.album, inline=False)
        embed.set_thumbnail(url=spotify_act.album_cover_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ {target.mention} şu an Spotify'da bir şey dinlemiyor veya durumu kapalı.")

@bot.command()
async def kullanici(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title=f"👤 Kullanıcı Bilgisi: {target.name}", color=discord.Color.blue())
    embed.add_field(name="Hesap Açılış Tarihi", value=target.created_at.strftime('%d/%m/%Y'), inline=True)
    embed.add_field(name="Sunucuya Katılım", value=target.joined_at.strftime('%d/%m/%Y') if target.joined_at else "Bilinmiyor", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    await ctx.send(f"🏰 **{ctx.guild.name}** Sunucu Üye Sayısı: **{ctx.guild.member_count}**")

@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="📜 Ultra Gelişmiş Komut Menüsü", color=discord.Color.gold())
    embed.add_field(name="🛡️ Yetkili & Yönetim", value="ayarlar, kufurengel, reklamengel, spamengel, logayarla, hosgeldin-ve-baybay-ayarla, karaliste, sil, sustur, ac, nuke, rolver, rolal, ban, kick, lock, unlock", inline=False)
    embed.add_field(name="🎉 Eğlence & Etkileşim", value="afk, uçangüvercin, saat, slaps, kiss, sarıl, askolcer, efkarolcer, sanslisayi, ship, ship2", inline=False)
    embed.add_field(name="💰 Ekonomi & Sistem", value="para, slots, spty, kullanici, sunucu", inline=False)
    await ctx.send(embed=embed)

# --- BOTU BAŞLATMA ---
keep_alive()
bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
            
