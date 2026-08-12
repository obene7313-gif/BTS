import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import asyncio
import datetime 
from flask import Flask
from threading import Thread
import os

# --- DIŞ DOSYADAN VERİ ÇEKME (TAM EŞLEŞME) ---
try:
    from iltifatlar import iltifatlar, selam_cevaplari
except ImportError:
    iltifatlar = ["✨ Çok tatlısın!", "🌟 Bugün harika görünüyorsun!", "💖 Harikasın!"]
    selam_cevaplari = ["👋 Aleykümselam, hoş geldin!", "✨ Selam! Naber?"]

# --- FLASK WEB SUNUCUSU ---
app = Flask('')

@app.route('/')
def home():
    return "🤖 Bot 7/24 Aktif ve Güvenli!"

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

# --- VERİTABANI VE AYARLAR ---
server_settings = {
    "kufurengel": False,
    "reklamengel": False,
    "spamengel": False,
    "log_kanal": None,
    "welcome_kanal": None,
    "karaliste": ["pic", "orospu", "sik", "yarrak", "sg", "Allah", "ALLAHINI", "allahını", "peygamber", "anani", "kuranini", "aq", "amk"]
}

bts_puan = {}
afk_users = {}
user_last_msg_time = {}

# --- GIF LİSTELERİ ---
SLAP_GIFS = [
    "https://tenor.com/view/slap-in-the-face-angry-gif-14689404",
    "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
    "https://media.giphy.com/media/j3iGKfA0I8vA8O6y3D/giphy.gif",
    "https://media.giphy.com/media/Zau0yRL15t84yiy043/giphy.gif",
    "https://media.giphy.com/media/l3YSimA8CV1k41b1u/giphy.gif",
    "https://media.giphy.com/media/10g452xT6T1E76/giphy.gif",
    "https://media.giphy.com/media/k1uUC6wAR8KRE13x6e/giphy.gif",
    "https://media.giphy.com/media/vxvNnIYvkYVT2/giphy.gif",
    "https://media.giphy.com/media/m6a85fepf4Ndm/giphy.gif",
    "https://media.giphy.com/media/3XlEk2CQAOMGY/giphy.gif"
]

KISS_GIFS = [
    "https://tenor.com/view/anime-kiss-gif-25745155",
    "https://media.giphy.com/media/klipy-kiss-video-love-you/giphy.gif",
    "https://media.giphy.com/media/G3va39rn8E4A8/giphy.gif",
    "https://media.giphy.com/media/Fq2l9lvd03O7K/giphy.gif",
    "https://media.giphy.com/media/bm2O3nXTcKJeU/giphy.gif",
    "https://media.giphy.com/media/vUrwEOLtBVkje/giphy.gif",
    "https://media.giphy.com/media/wO1d03OaL3I9M304fO/giphy.gif",
    "https://media.giphy.com/media/Kro48m8WZXlIs/giphy.gif",
    "https://media.giphy.com/media/JYf5fJ9jO0Lmg/giphy.gif",
    "https://media.giphy.com/media/l41YoV54ZT260P452/giphy.gif"
]

HUG_GIFS = [
    "https://tenor.com/view/hug-anime-love-gif-25644292",
    "https://media.giphy.com/media/u9BxFE6NoGZv2/giphy.gif",
    "https://media.giphy.com/media/108M7gCS1JSoO4/giphy.gif",
    "https://media.giphy.com/media/sUIZWMnfd4Mb6/giphy.gif",
    "https://media.giphy.com/media/qS8eagmBvLd3G/giphy.gif",
    "https://media.giphy.com/media/du4D05yXEFv32/giphy.gif",
    "https://media.giphy.com/media/3M4NpbLCTxBqU/giphy.gif",
    "https://media.giphy.com/media/Vp2yB6w1O032U/giphy.gif",
    "https://media.giphy.com/media/OD1fLytI52fTO/giphy.gif",
    "https://media.giphy.com/media/5Oq4PP6cT2p9A/giphy.gif"
]

PIGEON_GIFS = [
    "https://tenor.com/view/pigeon-kick-funny-birds-gif-14470635",
    "https://media.giphy.com/media/10G2KL3M84a3M4/giphy.gif",
    "https://media.giphy.com/media/l3vRfzpAnT5jYcT0E/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWR3ZXA4aTFzb3NxbXZscmdxZGg5YXRmd3N2bXRxdWVwbWhvYzB5NyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Lq0h93752f6J9tijrh/giphy.gif",
    "https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHIzOTlhZjUzNzNhNTBkNDc5ZDg4MWE5M2FiNmFlNmExNDcyYzMwNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HlHFRb4OMYYYn33/giphy.gif",
    "https://media.giphy.com/media/gyAgy6L3QO91tMvVj1/giphy.gif",
    "https://media.giphy.com/media/13CoXDiaCcCoyk/giphy.gif",
    "https://media.giphy.com/media/mAuMfYoYSssO4/giphy.gif",
    "https://media.giphy.com/media/xT9IgzoKnwFNmISR8I/giphy.gif"
]

EAT_GIFS = [
    "https://media.giphy.com/media/13m24iFmhomZi0/giphy.gif",
    "https://media.giphy.com/media/A441LVT23vU40/giphy.gif",
    "https://media.giphy.com/media/CgKFTMMFDESNW/giphy.gif",
    "https://media.giphy.com/media/Y4paqA3S1B2A108x2t/giphy.gif",
    "https://media.giphy.com/media/aI995sEg48cb6/giphy.gif",
    "https://media.giphy.com/media/fCBy3fthPAtJ3uInm2/giphy.gif",
    "https://media.giphy.com/media/wMdf4s69lD250fP2O3/giphy.gif",
    "https://media.giphy.com/media/3q3QK6KyDVUBzfiGTY/giphy.gif",
    "https://media.giphy.com/media/vXne31R6C291s/giphy.gif",
    "https://media.giphy.com/media/3o85xGocUH8RYoDKKs/giphy.gif"
]

# --- BTS TRIVIA SORULARI (GENİŞLETİLMİŞ) ---
bts_sorulari = [
    {"soru": "BTS hangi yıl çıkış yapmıştır?", "cevap": "2013", "siklar": ["2011", "2012", "2013", "2014"]},
    {"soru": "BTS'in açılımı nedir?", "cevap": "Bangtan Sonyeondan", "siklar": ["Bangtan Boys", "Bangtan Sonyeondan", "Beyond The Scene", "Born To Slay"]},
    {"soru": "BTS'in lideri kimdir?", "cevap": "RM", "siklar": ["Jin", "Suga", "RM", "Jimin"]},
    {"soru": "BTS'in en büyük üyesi (en yaşlısı) kimdir?", "cevap": "Jin", "siklar": ["Jin", "Suga", "RM", "J-Hope"]},
    {"soru": "BTS'in en küçük üyesi (maknae) kimdir?", "cevap": "Jungkook", "siklar": ["Jimin", "V", "Jungkook", "RM"]},
    {"soru": "BTS'in resmi fandom adı nedir?", "cevap": "A.R.M.Y", "siklar": ["BLINK", "A.R.M.Y", "EXO-L", "STAY"]},
    {"soru": "BTS hangi şirket çatısı altında kurulmuştur?", "cevap": "Big Hit (HYBE)", "siklar": ["SM", "YG", "JYP", "Big Hit (HYBE)"]},
    {"soru": "BTS'in çıkış şarkısı hangisidir?", "cevap": "No More Dream", "siklar": ["No More Dream", "Boy In Luv", "Dope", "I Need U"]},
    {"soru": "Hangi üyenin sahne adı 'V' harfinden oluşur?", "cevap": "Taehyung", "siklar": ["Jimin", "Taehyung", "Jungkook", "Suga"]},
    {"soru": "BTS'in Billboard Hot 100 listesinde 1 numara olan ilk tamamen İngilizce şarkısı hangisidir?", "cevap": "Dynamite", "siklar": ["Butter", "Dynamite", "Life Goes On", "Permission to Dance"]},
    {"soru": "Min Yoongi hangi üyenin gerçek adıdır?", "cevap": "Suga", "siklar": ["Suga", "J-Hope", "Jin", "RM"]},
    {"soru": "Jung Hoseok'un sahne adı nedir?", "cevap": "J-Hope", "siklar": ["RM", "Suga", "J-Hope", "V"]},
    {"soru": "BTS'in sembolikleşen rengi hangisidir?", "cevap": "Mor", "siklar": ["Pembe", "Mavi", "Mor", "Siyah"]},
    {"soru": "'I purple you' (Boralhae) sözünü hangi üye literatüre kazandırmıştır?", "cevap": "V", "siklar": ["RM", "Jimin", "V", "Jungkook"]},
    {"soru": "Suga'nın solo projelerinde kullandığı diğer sahne adı nedir?", "cevap": "Agust D", "siklar": ["Agust D", "Gloss", "Min PD", "Lil Meow"]},
    {"soru": "Hangi BTS üyesi modern dans geçmişine sahiptir ve Busan Sanat Lisesi'ne birincilikle girmiştir?", "cevap": "Jimin", "siklar": ["J-Hope", "Jimin", "V", "Jungkook"]},
    {"soru": "BTS'in 'Love Yourself' albüm serisinin ünlü başlık şarkısı hangisidir?", "cevap": "Fake Love", "siklar": ["DNA", "Fake Love", "Idol", "Run"]},
    {"soru": "Hangi üye grubun 'Golden Maknae'si olarak bilinir?", "cevap": "Jungkook", "siklar": ["Jimin", "V", "Jungkook", "Jin"]},
    {"soru": "BTS hayranlarının resmi ışıklı çubuğunun (lightstick) adı nedir?", "cevap": "Army Bomb", "siklar": ["Muster Stick", "Army Bomb", "Bangtan Light", "Purple Rod"]},
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
    {"soru": "BTS üyelerinden hangileri Daegu doğumludur?", "cevap": "Suga & V", "siklar": ["Suga & V", "RM & Jimin", "Jin & J-Hope", "Jungkook & Jin"]},
    {"soru": "BTS'in hayır kurumu UNICEF ile birlikte yürüttüğü kampanyanın adı nedir?", "cevap": "Love Myself", "siklar": ["Save Me", "Love Myself", "End Violence", "Be Yourself"]},
    {"soru": "J-Hope'un Becky G ile işbirliği yaptığı solo hit şarkısı hangisidir?", "cevap": "Chicken Noodle Soup", "siklar": ["More", "Arson", "Daydream", "Chicken Noodle Soup"]},
    {"soru": "BTS'in Grammy Ödülleri'nde sahne alan ilk Koreli grup olduğu yıl hangisidir?", "cevap": "2020", "siklar": ["2018", "2019", "2020", "2021"]},
    {"soru": "Jin'in BT21 karakteri olan beyaz alpakaya ne ad verilir?", "cevap": "RJ", "siklar": ["RJ", "Koya", "Tata", "Mang"]},
    {"soru": "BTS'in 2016 yılında yayınlanan ve 'Kan, ter ve gözyaşlarımı al' sözleriyle bilinen ünlü şarkısı hangisidir?", "cevap": "Blood Sweat & Tears", "siklar": ["Wings", "Blood Sweat & Tears", "Save Me", "Fire"]},
    {"soru": "Jungkook'un solo şarkısı 'Euphoria' hangi albüm projesinde yer alır?", "cevap": "Love Yourself: Answer", "siklar": ["Love Yourself: Tear", "Love Yourself: Her", "Love Yourself: Answer", "Wings"]},
    {"soru": "RM'in BT21 karakteri olan uykucu koalanın adı nedir?", "cevap": "Koya", "siklar": ["Koya", "Shooky", "Mang", "Chimmy"]},
    {"soru": "BTS'in 'Seven' şarkısını söyleyen üyesi kimdir?", "cevap": "Jungkook", "siklar": ["Jungkook", "Jimin", "V", "Jin"]},
    {"soru": "BTS'in 'Like Crazy' şarkısıyla Billboard Hot 100 listesinde 1 numara olan solo üyesi kimdir?", "cevap": "Jimin", "siklar": ["Jimin", "Suga", "RM", "J-Hope"]},
    {"soru": "Suga'nın 'D-DAY' solo albümündeki başlık şarkısı hangisidir?", "cevap": "Haegeum", "siklar": ["Haegeum", "Daechwita", "People", "AMYGDALA"]},
    {"soru": "V'nin çıkardığı ilk resmi solo albümün adı nedir?", "cevap": "Layover", "siklar": ["Layover", "Indigo", "FACE", "GOLDEN"]},
    {"soru": "RM'in 2022 sonunda çıkardığı solo albümün adı nedir?", "cevap": "Indigo", "siklar": ["Indigo", "Mono", "Right Place, Wrong Person", "RPWP"]},
    {"soru": "Jungkook'un 2023 yılında çıkardığı ilk solo albümünün adı nedir?", "cevap": "GOLDEN", "siklar": ["GOLDEN", "EUPHORIA", "SEVEN", "3D"]},
    {"soru": "Jin'in askerliğe gitmeden önce yayınladığı duygusal solo şarkının adı nedir?", "cevap": "The Astronaut", "siklar": ["The Astronaut", "Super Tuna", "Abyss", "Tonight"]},
    {"soru": "J-Hope'un Lollapalooza festivalinde ana sanatçı (headliner) olarak sahne aldığı yıl hangisidir?", "cevap": "2022", "siklar": ["2020", "2021", "2022", "2023"]}
]

BTS_MEMBERS = {
    "RM": {
        "isim": "Kim Namjoon",
        "dogum": "12 Eylül 1994",
        "gorev": "Lider, Rapçi",
        "emoji": "🐨",
        "renk": discord.Color.blue()
    },
    "Jin": {
        "isim": "Kim Seokjin",
        "dogum": "4 Aralık 1992",
        "gorev": "Vokalist",
        "emoji": "🦙",
        "renk": discord.Color.red()
    },
    "Suga": {
        "isim": "Min Yoongi",
        "dogum": "9 Mart 1993",
        "gorev": "Rapçi, Prodüktör",
        "emoji": "🐱",
        "renk": discord.Color.dark_grey()
    },
    "J-Hope": {
        "isim": "Jung Hoseok",
        "dogum": "18 Şubat 1994",
        "gorev": "Dansçı, Rapçi",
        "emoji": "🐿️",
        "renk": discord.Color.orange()
    },
    "Jimin": {
        "isim": "Park Jimin",
        "dogum": "13 Ekim 1995",
        "gorev": "Ana Dansçı, Vokalist",
        "emoji": "🐥",
        "renk": discord.Color.gold()
    },
    "V": {
        "isim": "Kim Taehyung",
        "dogum": "30 Aralık 1995",
        "gorev": "Vokalist",
        "emoji": "🐯",
        "renk": discord.Color.purple()
    },
    "Jungkook": {
        "isim": "Jeon Jungkook",
        "dogum": "1 Eylül 1997",
        "gorev": "Ana Vokalist",
        "emoji": "🐰",
        "renk": discord.Color.green()
    }
}

def get_turkey_time():
    return datetime.datetime.now(pytz.timezone('Europe/Istanbul'))

# --- BUTONLU OYUN GÖRÜNÜMÜ ---
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
                await interaction.response.send_message(f"🎉 Doğru Cevap! {interaction.user.mention} 50 💜 BTS Parası kazandı! Yeni bakiye: **{bts_puan[u_id]}**")
                await interaction.message.edit(view=None)
            else:
                await interaction.response.send_message("❌ Yanlış şık! Tekrar dene.", ephemeral=True)
        return callback

# --- EVENTLER ---
@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} olarak giriş yaptı.")
    await bot.change_presence(activity=discord.Game(name="!yardim | Koruma & Müzik & Eğlence 💜"))

@bot.event
async def on_member_join(member):
    if server_settings["welcome_kanal"]:
        channel = bot.get_channel(server_settings["welcome_kanal"])
        if channel:
            await channel.send(f"📥 Hoş geldin {member.mention}! Sunucumuza neşe getirdin ✨🎉")

@bot.event
async def on_member_remove(member):
    if server_settings["welcome_kanal"]:
        channel = bot.get_channel(server_settings["welcome_kanal"])
        if channel:
            await channel.send(f"📤 **{member.name}** sunucudan ayrıldı. Görüşmek üzere! 👋")

async def afk_kontrol(message):
    if message.author.id in afk_users:
        veri = afk_users.pop(message.author.id)
        gecen = datetime.datetime.now() - veri["zaman"]
        dakika, saniye = divmod(int(gecen.total_seconds()), 60)

        await message.channel.send(
            f"👋 Hoş geldin {message.author.mention}! "
            f"**{dakika} dakika {saniye} saniye** AFK kaldın ✨", delete_after=8)

    for uye in message.mentions:
        if uye.id in afk_users:
            veri = afk_users[uye.id]
            gecen = datetime.datetime.now() - veri["zaman"]
            dakika, saniye = divmod(int(gecen.total_seconds()), 60)

            await message.channel.send(
                f"💤 **{uye.display_name}** AFK.\n"
                f"📝 **Sebep:** {veri['sebep']}\n"
                f"⏳ **Süre:** {dakika} dk {saniye} sn")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 1. Önce Komutları Çalıştır
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
        
    await afk_kontrol(message)

    msg_content = message.content.lower()
    log_kanal = bot.get_channel(server_settings["log_kanal"]) if server_settings["log_kanal"] else None

    # SA-AS
    if msg_content in ["sa", "selam", "sa hq"]:
        rastgele_selam = random.choice(selam_cevaplari)
        await message.channel.send(f"{message.author.mention} {rastgele_selam}")
        return

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

    # Oransal Tetikleyiciler
    zar = random.random()

    # 1. %3 İltifat
    if zar < 0.03:
        await message.channel.send(f"{message.author.mention} {random.choice(iltifatlar)}")
        return

    # 2. %2 BTS Sorusu
    elif zar < 0.05:
        soru_data = random.choice(bts_sorulari)
        siklar = soru_data["siklar"].copy()
        random.shuffle(siklar)
        
        view = GameView(soru_data["cevap"], siklar)
        msg = await message.channel.send(f"💜 **BTS TRIVIA SORUSU!** 👑\n**{soru_data['soru']}**\n*Doğru şıkkı işaretle! (Süre: 15sn)*", view=view)
        
        await asyncio.sleep(15)
        if not view.cevaplandi:
            try:
                await msg.edit(content=f"⏱️ Süre doldu! Doğru cevap **{soru_data['cevap']}** olacaktı.", view=None)
            except:
                pass
        return

    # 3. %7 Matematik Sorusu
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

if islem == "+":
    cevap = num1 + num2
elif islem == "-":
    cevap = num1 - num2
elif islem == "*":
    cevap = num1 * num2
else:
    cevap = 0
    
# --- İKİ AŞAMALI AFK SİSTEMİ ---
@bot.command()
async def afk(ctx, *, sebep=None):
    if ctx.author.bot:
        return

    if ctx.author.id in afk_users:
        veri = afk_users.pop(ctx.author.id)
        gecen = datetime.datetime.now() - veri["zaman"]
        gun = gecen.days
        saat, kalan = divmod(gecen.seconds, 3600)
        dakika, saniye = divmod(kalan, 60)

        sure = []
        if gun: sure.append(f"{gun} gün")
        if saat: sure.append(f"{saat} saat")
        if dakika: sure.append(f"{dakika} dakika")
        if saniye: sure.append(f"{saniye} saniye")

        embed = discord.Embed(title="👋 AFK Modu Kapatıldı", description=f"Tekrar hoş geldin {ctx.author.mention}! 🎉", color=discord.Color.green())
        embed.add_field(name="⏳ AFK Süresi", value=", ".join(sure) if sure else "1 saniyeden az", inline=False)
        await ctx.send(embed=embed)
        return

    if not sebep:
        sebep = "Sebep belirtilmedi."

    afk_users[ctx.author.id] = {"sebep": sebep, "zaman": datetime.datetime.now()}

    embed = discord.Embed(title="💤 AFK Modu Açıldı", color=discord.Color.orange())
    embed.add_field(name="👤 Kullanıcı", value=ctx.author.mention, inline=False)
    embed.add_field(name="📝 Sebep", value=sebep, inline=False)
    embed.set_footer(text="AFK modundan çıkmak için tekrar !afk yaz. ✨")
    await ctx.send(embed=embed)

# --- EĞLENCE KOMUTLARI (GIF VE EMOJİ DESTEKLİ) ---
@bot.command()
async def ucanguvercin(ctx, member: discord.Member):
    gif = random.choice(PIGEON_GIFS)
    await ctx.send(f"🕊️ {ctx.author.mention}, {member.mention} kullanıcısına uçarak gelen çatık kaşlı bir güvercin fırlattı!\n💥 **Tekme atıyor bu güvercin sana!**\n{gif}")

@bot.command()
async def saat(ctx):
    tr_time = get_turkey_time().strftime('%d/%m/%Y %H:%M:%S')
    await ctx.send(f"⏰ **Güncel Türkiye Saati ve Tarihi:** `{tr_time}` 🇹🇷✨")

@bot.command()
async def slaps(ctx, member: discord.Member):
    gif = random.choice(SLAP_GIFS)
    await ctx.send(f"🖐️ {ctx.author.mention}, {member.mention} kullanıcısını Osmanlı tokadıyla uçurdu! 💥\n{gif}")

@bot.command()
async def kiss(ctx, member: discord.Member):
    gif = random.choice(KISS_GIFS)
    await ctx.send(f"💋 {ctx.author.mention}, {member.mention} kullanıcısını sulu sulu öptü! 💖✨\n{gif}")

@bot.command()
async def saril(ctx, member: discord.Member):
    gif = random.choice(HUG_GIFS)
    await ctx.send(f"🤗 {ctx.author.mention}, {member.mention} kullanıcısına sımsıkı sarıldı! 🥰💖\n{gif}")
    
@bot.command()
async def op(ctx, member: discord.Member):
    gif = random.choice(KISS_GIFS)
    await ctx.send(f"🤗 {ctx.author.mention}, {member.mention} kullanıcısını öpücüğe boğdu! 💋✨\n{gif}")

@bot.command()
async def askolcer(ctx, member: discord.Member):
    oran = random.randint(0, 100)
    await ctx.send(f"❤️ {ctx.author.mention} ile {member.mention} arasındaki aşk oranı: **%{oran}** 💘🔥")

@bot.command()
async def efkarolcer(ctx):
    oran = random.randint(0, 100)
    await ctx.send(f"🚬 {ctx.author.mention} bugünkü efkar durumun: **%{oran}** ☕💔")

@bot.command()
async def sansolcer(ctx):
    oran = random.randint(0, 100)
    await ctx.send(f"🍀 {ctx.author.mention} bugünkü şans durumun: **%{oran}** 🎲✨")

@bot.command()
async def eatt(ctx, *, yemek: str):
    gif = random.choice(EAT_GIFS)
    await ctx.send(f"🍲 {ctx.author.mention} leziz bir **{yemek}** yiyor! Afiyet olsun! 😋🍴\n{gif}")

@bot.command()
async def eat(ctx, member: discord.Member, *, yemek: str):
    gif = random.choice(EAT_GIFS)
    await ctx.send(f"🍕 {ctx.author.mention}, {member.mention} kullanıcısına lezzetli bir **{yemek}** ikram etti! Afiyet olsun! 😋✨\n{gif}")

class BTSSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=isim, emoji=veri["emoji"])
            for isim, veri in BTS_MEMBERS.items()
        ]
        super().__init__(placeholder="Bir BTS üyesi seç...", options=options)

    async def callback(self, interaction: discord.Interaction):
        uye = BTS_MEMBERS[self.values[0]]
        embed = discord.Embed(title=f"{uye['emoji']} {self.values[0]}", color=uye["renk"])
        embed.add_field(name="👤 Gerçek Adı", value=uye["isim"], inline=False)
        embed.add_field(name="🎂 Doğum Tarihi", value=uye["dogum"], inline=False)
        embed.add_field(name="🎤 Görevi", value=uye["gorev"], inline=False)
        embed.set_footer(text="💜 BTS Bilgi Menüsü | Bangtan Sonyeondan")
        await interaction.response.edit_message(embed=embed, view=self.view)

class BTSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(BTSSelect())

@bot.command()
async def bts(ctx):
    embed = discord.Embed(
        title="💜 BTS Bilgi Menüsü 👑",
        description="Aşağıdaki menüden bilgi almak istediğin BTS üyesini seç ✨",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=BTSView())

@bot.command()
async def sanslisayi(ctx):
    sayi = random.randint(1, 100)
    await ctx.send(f"🎲 {ctx.author.mention}, bugün senin şanslı sayın: **{sayi}** ✨🔮")

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
    await ctx.send(f"💕 **Günün Shipi:** {m1.mention} X {m2.mention} | Kalp Oranı: **%{oran}** 💖🔥")

@bot.command()
async def ship2(ctx, member: discord.Member):
    await ctx.send(f"💖 {ctx.author.mention} X {member.mention}\n**Aşk Oranı: %99999! Bu aşk ölçülemez!** 🔥💞")

# --- MÜZİK KOMUTU ---
@bot.command()
async def sarki(ctx, *, arama_veya_link: str):
    if not ctx.author.voice:
        await ctx.send("❌ Şarkı çalmak için öncelikle bir sesli kanala katılmalısın! 🎧")
        return
    
    channel = ctx.author.voice.channel
    try:
        if not ctx.voice_client:
            await channel.connect()
    except Exception as e:
        pass
        
    embed = discord.Embed(
        title="🎵 Müzik Oynatılıyor / Listeye Eklendi",
        description=f"🎧 **İstenen Şarkı / Link:** `{arama_veya_link}`\n🔊 **Kanal:** {channel.name}",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 İsteyen", value=ctx.author.mention, inline=True)
    embed.set_footer(text="✨ Kesintisiz Müzik Keyfi!")
    await ctx.send(embed=embed)

# --- EKONOMİ & OYUN ---
@bot.command()
async def para(ctx, member: discord.Member = None):
    target = member or ctx.author
    bakiye = bts_puan.get(target.id, 100)
    bts_puan[target.id] = bakiye
    await ctx.send(f"💰 {target.mention}: **{bakiye}** 💜 **BTS Parası**")

@bot.command(name="join")
async def pay(ctx, miktar: int, member: discord.Member):
    if member.id == ctx.author.id:
        await ctx.send("❌ Kendine para aktaramazsın!")
        return
    if miktar <= 0:
        await ctx.send("❌ Geçerli bir miktar girmelisin!")
        return

    gonderen_bakiye = bts_puan.get(ctx.author.id, 100)
    if gonderen_bakiye < miktar:
        await ctx.send(f"❌ Yetersiz bakiye! Mevcut bakiyen: **{gonderen_bakiye} BTS Parası** 💸")
        return

    bts_puan[ctx.author.id] = gonderen_bakiye - miktar
    bts_puan[member.id] = bts_puan.get(member.id, 100) + miktar

    await ctx.send(f"💸 {ctx.author.mention}, {member.mention} kullanıcısına **{miktar} BTS Parası** başarıyla aktardı! 🎉\n✨ Yeni Bakiyen: **{bts_puan[ctx.author.id]}**")

@bot.command()
async def amortentia(ctx, member: discord.Member, miktar: int):
    # Sadece Sunucu Sahibi (Taç Sahibi)
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("👑 Bu komutu yalnızca sunucu sahibi (taç sahibi) kullanabilir!")
        return

    if miktar <= 0:
        await ctx.send("❌ Geçerli bir miktar girin!")
        return

    bts_puan[member.id] = bts_puan.get(member.id, 100) + miktar
    await ctx.send(f"👑 **SİHİRLİ DOKUNUŞ!** Sunucu Sahibi {ctx.author.mention}, {member.mention} kullanıcısına **{miktar} BTS Parası** lütfetti! 💜✨\nYeni Bakiye: **{bts_puan[member.id]}**")

@bot.command()
async def rich(ctx):
    if not bts_puan:
        await ctx.send("📊 Henüz para verisi bulunmuyor.")
        return

    sirali = sorted(bts_puan.items(), key=lambda x: x[1], reverse=True)[:10]

    embed = discord.Embed(title="🏆 BTS Parası Zenginler Sıralaması (Top 10) 👑", color=discord.Color.gold())
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (user_id, puan) in enumerate(sirali):
        user = bot.get_user(user_id)
        user_name = user.name if user else f"Kullanıcı ({user_id})"
        embed.add_field(
            name=f"{medals[idx]} {user_name}",
            value=f"💎 **{puan}** BTS Parası",
            inline=False
        )
    
    embed.set_footer(text="🌟 Sen de oyunlara katılarak sıralamaya gir!")
    await ctx.send(embed=embed)

@bot.command()
async def slots(ctx, miktar: int):
    bakiye = bts_puan.get(ctx.author.id, 100)
    if miktar <= 0 or miktar > bakiye:
        await ctx.send("❌ Geçersiz miktar veya yetersiz bakiye! 💸")
        return
    
    slots_icons = ["🍒", "🍋", "🍇", "🍊", "💎", "💜"]
    r1, r2, r3 = random.choice(slots_icons), random.choice(slots_icons), random.choice(slots_icons)
    msg = f"🎰 **{ctx.author.name}** slots çeviriyor...\n| {r1} | {r2} | {r3} |\n"
    
    if r1 == r2 == r3:
        odul = miktar * 4
        bts_puan[ctx.author.id] = bakiye + odul
        await ctx.send(msg + f"🔥 **MÜKEMMEL! 3'te 3 Yaptın!** **{odul} BTS Parası** kazandın! 🎉💎")
    elif r1 == r2 or r2 == r3 or r1 == r3:
        odul = miktar * 2
        bts_puan[ctx.author.id] = bakiye + odul
        await ctx.send(msg + f"✨ **Güzel! Çift yakaladın.** **{odul} BTS Parası** kazandın! 🌟")
    else:
        bts_puan[ctx.author.id] = bakiye - miktar
        await ctx.send(msg + f"💥 **Kaybettin!** **{miktar} BTS Parası** cüzdanından uçtu. 💸")

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
        embed = discord.Embed(title=f"🎵 {target.name} Spotify Dinliyor 🎧", color=discord.Color.green())
        embed.add_field(name="🎶 Şarkı", value=spotify_act.title, inline=False)
        embed.add_field(name="🎤 Sanatçı", value=", ".join(spotify_act.artists), inline=False)
        embed.add_field(name="💿 Albüm", value=spotify_act.album, inline=False)
        embed.set_thumbnail(url=spotify_act.album_cover_url)
        embed.set_footer(text="✨ Keyifli Dinlemeler!")
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ {target.mention} şu an Spotify'da bir şey dinlemiyor veya durumu kapalı. 🎧")

@bot.command()
async def kullanici(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title=f"👤 Kullanıcı Bilgisi: {target.name} ✨", color=discord.Color.blue())
    embed.add_field(name="📅 Hesap Açılış Tarihi", value=target.created_at.strftime('%d/%m/%Y'), inline=True)
    embed.add_field(name="📥 Sunucuya Katılım", value=target.joined_at.strftime('%d/%m/%Y') if target.joined_at else "Bilinmiyor", inline=True)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    embed = discord.Embed(title=f"🏰 {ctx.guild.name} Sunucu Bilgileri", color=discord.Color.purple())
    embed.add_field(name="👥 Üye Sayısı", value=f"**{ctx.guild.member_count}** üye", inline=True)
    embed.add_field(name="👑 Sunucu Sahibi", value=f"<@{ctx.guild.owner_id}>", inline=True)
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="📜 Ultra Gelişmiş Komut Menüsü 👑", color=discord.Color.gold())
    embed.add_field(name="🛡️ Yetkili & Yönetim", value="`ayarlar`, `kufurengel`, `reklamengel`, `spamengel`, `logayarla`, `hosgeldin-ve-baybay-ayarla`, `karaliste`, `sil`, `sustur`, `ac`, `nuke`, `rolver`, `rolal`, `ban`, `kick`, `lock`, `unlock`", inline=False)
    embed.add_field(name="🎉 Eğlence & Etkileşim", value="`afk`, `ucanguvercin`, `saat`, `slaps`, `kiss`, `saril`, `op`, `askolcer`, `efkarolcer`, `sansolcer`, `sanslisayi`, `ship`, `ship2`, `eatt`, `eat`", inline=False)
    embed.add_field(name="💰 Ekonomi & Oyun", value="`para`, `join` (para transferi), `rich` (liderlik), `amortentia` (taç sahibine özel), `slots`", inline=False)
    embed.add_field(name="🎵 Müzik & Bilgi", value="`sarki`, `bts`, `spty`, `kullanici`, `sunucu`", inline=False)
    embed.set_footer(text="✨ Tüm komutlar sorunsuz çalışmaktadır.")
    await ctx.send(embed=embed)

# --- BOTU BAŞLATMA ---
keep_alive()
bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
        
