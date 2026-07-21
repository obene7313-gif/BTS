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

# --- DIÅ DOSYADAN VERÄ° Ã‡EKME (TAM EÅLEÅME) ---
try:
    from iltifatlar import iltifatlar, selam_cevaplari
except ImportError:
    iltifatlar = ["Ã‡ok tatlÄ±sÄ±n!", "BugÃ¼n harika gÃ¶rÃ¼nÃ¼yorsun!", "HarikasÄ±n!"]
    selam_cevaplari = ["AleykÃ¼mselam, hoÅŸ geldin", "Selam! Naber?"]

# --- FLASK WEB SUNUCUSU ---
app = Flask('')

@app.route('/')
def home():
    return "Bot 7/24 Aktif ve GÃ¼venli!"

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

# --- VERÄ°TABANI VE AYARLAR ---
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

# --- BTS TRIVIA SORULARI (50 ADET) ---
bts_sorulari = [
    {"soru": "BTS hangi yÄ±l Ã§Ä±kÄ±ÅŸ yapmÄ±ÅŸtÄ±r?", "cevap": "2013", "siklar": ["2011", "2012", "2013", "2014"]},
    {"soru": "BTS'in aÃ§Ä±lÄ±mÄ± nedir?", "cevap": "Bangtan Sonyeondan", "siklar": ["Bangtan Boys", "Bangtan Sonyeondan", "Beyond The Scene", "Born To Slay"]},
    {"soru": "BTS'in lideri kimdir?", "cevap": "RM", "siklar": ["Jin", "Suga", "RM", "Jimin"]},
    {"soru": "BTS'in en bÃ¼yÃ¼k Ã¼yesi (en yaÅŸlÄ±sÄ±) kimdir?", "cevap": "Jin", "siklar": ["Jin", "Suga", "RM", "J-Hope"]},
    {"soru": "BTS'in en kÃ¼Ã§Ã¼k Ã¼yesi (maknae) kimdir?", "cevap": "Jungkook", "siklar": ["Jimin", "V", "Jungkook", "RM"]},
    {"soru": "BTS'in resmi fandom adÄ± nedir?", "cevap": "A.R.M.Y", "siklar": ["BLINK", "A.R.M.Y", "EXO-L", "STAY"]},
    {"soru": "BTS hangi ÅŸirketetetin Ã§atÄ±sÄ± altÄ±nda kurulmuÅŸtur?", "cevap": "Big Hit (HYBE)", "siklar": ["SM", "YG", "JYP", "Big Hit (HYBE)"]},
    {"soru": "BTS'in Ã§Ä±kÄ±ÅŸ ÅŸarkÄ±sÄ± hangisidir?", "cevap": "No More Dream", "siklar": ["No More Dream", "Boy In Luv", "Dope", "I Need U"]},
    {"soru": "Hangi Ã¼yenin sahne adÄ± 'V' harfinden oluÅŸur?", "cevap": "Taehyung", "siklar": ["Jimin", "Taehyung", "Jungkook", "Suga"]},
    {"soru": "BTS'in Billboard Hot 100 listesinde 1 numara olan ilk tamamen Ä°ngilizce ÅŸarkÄ±sÄ± hangisidir?", "cevap": "Dynamite", "siklar": ["Butter", "Dynamite", "Life Goes On", "Permission to Dance"]},
    {"soru": "Min Yoongi hangi Ã¼yenin gerÃ§ek adÄ±dÄ±r?", "cevap": "Suga", "siklar": ["Suga", "J-Hope", "Jin", "RM"]},
    {"soru": "Jung Hoseok'un sahne adÄ± nedir?", "cevap": "J-Hope", "siklar": ["RM", "Suga", "J-Hope", "V"]},
    {"soru": "BTS'in resmi rengi veya sembolikleÅŸen rengi hangisidir?", "cevap": "Mor", "siklar": ["Pembe", "Mavi", "Mor", "Siyah"]},
    {"soru": "'I purple you' (Sizi morluyorum) sÃ¶zÃ¼nÃ¼ hangi Ã¼ye literatÃ¼re kazandÄ±rmÄ±ÅŸtÄ±r?", "cevap": "V", "siklar": ["RM", "Jimin", "V", "Jungkook"]},
    {"soru": "Suga'nÄ±n solo projelerinde kullandÄ±ÄŸÄ± diÄŸer sahne adÄ± nedir?", "cevap": "Agust D", "siklar": ["Agust D", "Gloss", "Min PD", "Lil Meow"]},
    {"soru": "Hangi BTS Ã¼yesi modern dans geÃ§miÅŸine sahiptir ve Busan Sanat Lisesi'ne birincilikle girmiÅŸtir?", "cevap": "Jimin", "siklar": ["J-Hope", "Jimin", "V", "Jungkook"]},
    {"soru": "BTS'in 'Love Yourself' albÃ¼m serisinin Ã¼nlÃ¼ baÅŸlÄ±k ÅŸarkÄ±sÄ± hangisidir?", "cevap": "Fake Love", "siklar": ["DNA", "Fake Love", "Idol", "Run"]},
    {"soru": "Hangi Ã¼ye grubun 'Golden Maknae'si (AltÄ±n KÃ¼Ã§Ã¼k) olarak bilinir?", "cevap": "Jungkook", "siklar": ["Jimin", "V", "Jungkook", "Jin"]},
    {"soru": "BTS'in hayranlarÄ± iÃ§in tasarladÄ±ÄŸÄ± resmi Ä±ÅŸÄ±klÄ± Ã§ubuÄŸun (lightstick) adÄ± nedir?", "cevap": "Army Bomb", "siklar": ["Muster Stick", "Army Bomb", "Bangtan Light", "Purple Rod"]},
    {"soru": "BTS, BirleÅŸmiÅŸ Milletler (UN) genel kurulunda ilk kez hangi yÄ±l konuÅŸma yapmÄ±ÅŸtÄ±r?", "cevap": "2018", "siklar": ["2016", "2017", "2018", "2019"]},
    {"soru": "BTS'in popÃ¼ler reality ÅŸov programÄ±nÄ±n adÄ± nedir?", "cevap": "Run BTS!", "siklar": ["BTS In The Soop", "Run BTS!", "Rookie King", "American Hustle Life"]},
    {"soru": "Kim Seokjin'in lakaplarÄ±ndan biri hangisidir?", "cevap": "Worldwide Handsome", "siklar": ["Worldwide Handsome", "Golden Boy", "Gucci Boy", "Sunshine"]},
    {"soru": "Grubun ana dansÃ§Ä±sÄ± ve koreografi lideri kimdir?", "cevap": "J-Hope", "siklar": ["Jimin", "J-Hope", "Jungkook", "V"]},
    {"soru": "BTS'in Line Friends ile iÅŸbirliÄŸi yaparak oluÅŸturduÄŸu karakter serisinin adÄ± nedir?", "cevap": "BT21", "siklar": ["BTS-Toons", "BT21", "Bangtan Pets", "Line-BTS"]},
    {"soru": "Jungkook'un BT21 karakterinin adÄ± nedir?", "cevap": "Cooky", "siklar": ["Tata", "Chimmy", "Cooky", "Koya"]},
    {"soru": "RM'in IQ seviyesinin kaÃ§ olduÄŸu bilinmektedir?", "cevap": "148", "siklar": ["120", "135", "148", "160"]},
    {"soru": "BTS'in Halsey ile dÃ¼et yaptÄ±ÄŸÄ± popÃ¼ler ÅŸarkÄ± hangisidir?", "cevap": "Boy With Luv", "siklar": ["Idol", "Boy With Luv", "On", "Stay Gold"]},
    {"soru": "Suga'nÄ±n BT21 karakterinin adÄ± nedir?", "cevap": "Shooky", "siklar": ["Shooky", "Mang", "RJ", "Van"]},
    {"soru": "BTS'in hangi albÃ¼mÃ¼ onlara ilk kez bir Daesang (YÄ±lÄ±n AlbÃ¼mÃ¼) Ã¶dÃ¼lÃ¼ kazandÄ±rmÄ±ÅŸtÄ±r?", "cevap": "The Most Beautiful Moment in Life: Young Forever", "siklar": ["Wings", "Dark & Wild", "The Most Beautiful Moment in Life: Young Forever", "Love Yourself: Tear"]},
    {"soru": "Hangi ÅŸarkÄ±da 'Geonbae (Åerefe)' kelimesi sÄ±kÃ§a geÃ§er ve parti havasÄ±ndadÄ±r?", "cevap": "Dionysus", "siklar": ["Dionysus", "Fire", "Idol", "Dope"]},
    {"soru": "BTS'in 2020 yÄ±lÄ±nda Ã§Ä±kardÄ±ÄŸÄ± 'Map of the Soul: 7' albÃ¼mÃ¼nÃ¼n sert ve gÃ¼Ã§lÃ¼ baÅŸlÄ±k ÅŸarkÄ±sÄ± hangisidir?", "cevap": "ON", "siklar": ["Black Swan", "ON", "Louder Than Bombs", "Filter"]},
    {"soru": "V'nin (Taehyung) oynadÄ±ÄŸÄ± tarihi Kore dizisinin adÄ± nedir?", "cevap": "Hwarang", "siklar": ["Hwarang", "Goblin", "The King", "Dream High"]},
    {"soru": "Hangi Ã¼ye solak olmasÄ±na raÄŸmen saÄŸ elini de Ã§ok aktif kullanabilir?", "cevap": "V", "siklar": ["RM", "Suga", "V", "Jimin"]},
    {"soru": "Jimin'in solo ÅŸarkÄ±larÄ±ndan biri hangisidir?", "cevap": "Lie", "siklar": ["Lie", "Awake", "Intro: Persona", "Epiphany"]},
    {"soru": "BTS Ã¼yelerinden hangisi Daegu doÄŸumludur?", "cevap": "Suga & V", "siklar": ["Suga & V", "RM & Jimin", "Jin & J-Hope", "Jungkook & Jin"]},
    {"soru": "BTS'in hayÄ±r kurumu UNICEF ile birlikte yÃ¼rÃ¼ttÃ¼ÄŸÃ¼ kampanyanÄ±n adÄ± nedir?", "cevap": "Love Myself", "siklar": ["Save Me", "Love Myself", "End Violence", "Be Yourself"]},
    {"soru": "J-Hope'un Becky G ile iÅŸbirliÄŸi yaptÄ±ÄŸÄ± solo hit ÅŸarkÄ±sÄ± hangisidir?", "cevap": "Chicken Noodle Soup", "siklar": ["More", "Arson", "Daydream", "Chicken Noodle Soup"]},
    {"soru": "BTS'in Grammy Ã–dÃ¼lleri'nde sahne alan ilk Koreli grup olduÄŸu yÄ±l hangisidir?", "cevap": "2020", "siklar": ["2018", "2019", "2020", "2021"]},
    {"soru": "Jin'in BT21 karakteri olan beyaz alpakaya ne ad verilir?", "cevap": "RJ", "siklar": ["RJ", "Koya", "Tata", "Mang"]},
    {"soru": "BTS'in 2016 yÄ±lÄ±nda yayÄ±nlanan ve 'Kan, ter ve gÃ¶zyaÅŸlarÄ±mÄ± al' sÃ¶zleriyle bilinen Ã¼nlÃ¼ ÅŸarkÄ±sÄ± hangisidir?", "cevap": "Blood Sweat & Tears", "siklar": ["Wings", "Blood Sweat & Tears", "Save Me", "Fire"]},
    {"soru": "Jungkook'un solo ÅŸarkÄ±sÄ± 'Euphoria' hangi albÃ¼m projesinde yer alÄ±r?", "cevap": "Love Yourself: Answer", "siklar": ["Love Yourself: Tear", "Love Yourself: Her", "Love Yourself: Answer", "Wings"]},
    {"soru": "RM'in BT21 karakteri olan uykucu koalanÄ±n adÄ± nedir?", "cevap": "Koya", "siklar": ["Koya", "Shooky", "Mang", "Chimmy"]},
    {"soru": "BTS'in 'Black Swan' ÅŸarkÄ±sÄ±nÄ±n ilk koreografi videosunda hangi tarz dans Ã¶n plana Ã§Ä±kmÄ±ÅŸtÄ±r?", "cevap": "Modern Bale / Ã‡aÄŸdaÅŸ Dans", "siklar": ["Hip-hop", "Breakdance", "Modern Bale / Ã‡aÄŸdaÅŸ Dans", "Poping"]},
    {"soru": "Suga'nÄ±n mÃ¼zik yaparken ve piyano Ã§alarken sÄ±klÄ±kla bahsettiÄŸi favori rengi nedir?", "cevap": "Kahverengi", "siklar": ["Siyah", "Beyaz", "Kahverengi", "Mavi"]},
    {"soru": "BTS'in 'Yet To Come' konseri 2022 yÄ±lÄ±nda Kore'nin hangi ÅŸehrinde gerÃ§ekleÅŸmiÅŸtir?", "cevap": "Busan", "siklar": ["Seul", "Busan", "Incheon", "Daegu"]},
    {"soru": "Hangi BTS klibi tren garÄ±, lunapark ve kÄ±ÅŸ temalarÄ± iÃ§erir, derin dostluÄŸu anlatÄ±r?", "cevap": "Spring Day", "siklar": ["Spring Day", "Run", "I Need U", "Life Goes On"]},
    {"soru": "J-Hope'un BT21 karakteri olan maskeli atÄ±n adÄ± nedir?", "cevap": "Mang", "siklar": ["Mang", "Cooky", "Tata", "RJ"]},
    {"soru": "BTS Ã¼yelerinin tamamÄ±nÄ±n dostluk dÃ¶vmesi olarak yaptÄ±rdÄ±ÄŸÄ± sayÄ± hangisidir?", "cevap": "7", "siklar": ["1", "7", "13", "0"]},
    {"soru": "V'nin BT21 karakteri olan kalp kafalÄ± uzaylÄ±nÄ±n adÄ± nedir?", "cevap": "Tata", "siklar": ["Tata", "Chimmy", "Koya", "RJ"]},
    {"soru": "Jimin'in BT21 karakteri olan sarÄ± kapÃ¼ÅŸonlu kÃ¶peÄŸin adÄ± nedir?", "cevap": "Chimmy", "siklar": ["Chimmy", "Cooky", "Shooky", "Van"]}
]
BTS_MEMBERS = {
    "RM": {
        "isim": "Kim Namjoon",
        "dogum": "12 EylÃ¼l 1994",
        "gorev": "Lider, RapÃ§i",
        "emoji": "ğŸ¨",
        "renk": discord.Color.blue()
    },
    "Jin": {
        "isim": "Kim Seokjin",
        "dogum": "4 AralÄ±k 1992",
        "gorev": "Vokalist",
        "emoji": "ğŸ¦™",
        "renk": discord.Color.red()
    },
    "Suga": {
        "isim": "Min Yoongi",
        "dogum": "9 Mart 1993",
        "gorev": "RapÃ§i, ProdÃ¼ktÃ¶r",
        "emoji": "ğŸ±",
        "renk": discord.Color.dark_grey()
    },
    "J-Hope": {
        "isim": "Jung Hoseok",
        "dogum": "18 Åubat 1994",
        "gorev": "DansÃ§Ä±, RapÃ§i",
        "emoji": "ğŸ¿ï¸",
        "renk": discord.Color.orange()
    },
    "Jimin": {
        "isim": "Park Jimin",
        "dogum": "13 Ekim 1995",
        "gorev": "Ana DansÃ§Ä±, Vokalist",
        "emoji": "ğŸ¥",
        "renk": discord.Color.gold()
    },
    "V": {
        "isim": "Kim Taehyung",
        "dogum": "30 AralÄ±k 1995",
        "gorev": "Vokalist",
        "emoji": "ğŸ¯",
        "renk": discord.Color.purple()
    },
    "Jungkook": {
        "isim": "Jeon Jungkook",
        "dogum": "1 EylÃ¼l 1997",
        "gorev": "Ana Vokalist",
        "emoji": "ğŸ°",
        "renk": discord.Color.green()
    }
}

def get_turkey_time():
    return datetime.datetime.now(pytz.timezone('Europe/Istanbul'))

# --- BUTONLU OYUN GÃ–RÃœNÃœMÃœ ---
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
                await interaction.response.send_message("âŒ Bu soru zaten cevaplandÄ±!", ephemeral=True)
                return
            
            if str(sik) == str(self.dogru_cevap):
                self.cevaplandi = True
                self.stop()
                u_id = interaction.user.id
                bts_puan[u_id] = bts_puan.get(u_id, 100) + 50
                await interaction.response.send_message(f"ğŸ‰ DoÄŸru Cevap! {interaction.user.mention} 50 BTS ParasÄ± kazandÄ±! Yeni bakiye: {bts_puan[u_id]}")
                await interaction.message.edit(view=None)
            else:
                await interaction.response.send_message("âŒ YanlÄ±ÅŸ ÅŸÄ±k! Tekrar dene.", ephemeral=True)
        return callback

# --- EVENTLER ---
@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} olarak giriÅŸ yaptÄ±.")
    await bot.change_presence(activity=discord.Game(name="!yardim | Koruma & EÄŸlence"))

@bot.event
async def on_member_join(member):
    if server_settings["welcome_kanal"]:
        channel = bot.get_channel(server_settings["welcome_kanal"])
        if channel:
            await channel.send(f"ğŸ“¥ HoÅŸ geldin {member.mention}! Sunucumuza neÅŸe getirdin.")

@bot.event
async def on_member_remove(member):
    if server_settings["welcome_kanal"]:
        channel = bot.get_channel(server_settings["welcome_kanal"])
        if channel:
            await channel.send(f"ğŸ“¤ **{member.name}** sunucudan ayrÄ±ldÄ±. GÃ¶rÃ¼ÅŸmek Ã¼zere!")

async def afk_kontrol(message):
    if message.author.id in afk_users:
        veri = afk_users.pop(message.author.id)

        gecen = datetime.datetime.now() - veri["zaman"]
        dakika, saniye = divmod(int(gecen.total_seconds()), 60)

        await message.channel.send(
            f"ğŸ‘‹ HoÅŸ geldin {message.author.mention}! "
            f"**{dakika} dakika {saniye} saniye** AFK kaldÄ±n.",delete_after=8)

    for uye in message.mentions:
        if uye.id in afk_users:
            veri = afk_users[uye.id]

            gecen = datetime.datetime.now() - veri["zaman"]
            dakika, saniye = divmod(int(gecen.total_seconds()), 60)

            await message.channel.send(
                f"ğŸ’¤ **{uye.display_name}** AFK.\n"
                f"**Sebep:** {veri['sebep']}\n"
                f"**SÃ¼re:** {dakika} dk {saniye} sn")
            
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 1. Ã–nce KomutlarÄ± Ã‡alÄ±ÅŸtÄ±r
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
        
    await afk_kontrol(message)

    # 2. AFK Etiket KontrolÃ¼
    for mention in message.mentions:
        if mention.id in afk_users:
            sebep = afk_users[mention.id]
            await message.channel.send(f"âš ï¸ {message.author.mention}, etiketlediÄŸin kullanÄ±cÄ± **{mention.name}** ÅŸu an AFK!\n**Sebep:** {sebep}")

    msg_content = message.content.lower()
    log_kanal = bot.get_channel(server_settings["log_kanal"]) if server_settings["log_kanal"] else None

    # SA-AS (ArtÄ±k 100 farklÄ± selam cÃ¼mlesinden rastgele Ã§eker!)
    if msg_content == "sa" or msg_content == "selam" or msg_content == "sa hq":
        rastgele_selam = random.choice(selam_cevaplari)
        await message.channel.send(f"{message.author.mention} {rastgele_selam}")
        return

    # KÃ¼fÃ¼r KorumasÄ±
    if server_settings["kufurengel"]:
        for sansur in server_settings["karaliste"]:
            if sansur in msg_content:
                try:
                    await message.delete()
                    if log_kanal:
                        await log_kanal.send(f"ğŸš« **KÃ¼fÃ¼r Engellendi:** {message.author.mention} -> {message.content}")
                except:
                    pass
                return

    # Reklam KorumasÄ±
    if server_settings["reklamengel"] and ("http" in msg_content or "discord.gg/" in msg_content):
        try:
            await message.delete()
            if log_kanal:
                await log_kanal.send(f"ğŸ”— **Reklam Engellendi:** {message.author.mention} -> {message.content}")
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
                await message.channel.send(f"âš ï¸ {message.author.mention}, lÃ¼tfen Ã§ok hÄ±zlÄ± mesaj gÃ¶nderme!", delete_after=3)
            except:
                pass
            return

    # Oransal Tetikleyiciler
    zar = random.random()

    # 1. %3 Ä°ltifat (300 farklÄ± iltifattan Ã§eker!)
    if zar < 0.03:
        await message.channel.send(f"{message.author.mention} {random.choice(iltifatlar)}")
        return

    # 2. %2 BTS Sorusu
    elif zar < 0.05:
        soru_data = random.choice(bts_sorulari)
        siklar = soru_data["siklar"].copy()
        random.shuffle(siklar)
        
        view = GameView(soru_data["cevap"], siklar)
        msg = await message.channel.send(f"ğŸ’œ **BTS TRIVIA SORUSU!**\n**{soru_data['soru']}**\n*DoÄŸru ÅŸÄ±kkÄ± iÅŸaretle! (SÃ¼re: 15sn)*", view=view)
        
        await asyncio.sleep(15)
        if not view.cevaplandi:
            try:
                await msg.edit(content=f"â±ï¸ SÃ¼re doldu! DoÄŸru cevap **{soru_data['cevap']}** olacaktÄ±.", view=None)
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

        else:
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
        msg = await message.channel.send(f"ğŸ“Š **MATEMATÄ°K SORUSU! ({seviye.replace('_', ' ').upper()})**\n**{num1} {gosterim_islem} {num2} = ?**\n*Cevaplamak iÃ§in 15 saniyen var!*", view=view)
        
        
        await asyncio.sleep(15)
        if not view.cevaplandi:
            try:
                await msg.edit(content=f"â±ï¸ SÃ¼re doldu! DoÄŸru cevap **{cevap}** olacaktÄ±.", view=None)
            except:
                pass
        return

# --- YETKÄ°LÄ° KOMUTLARI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def ayarlar(ctx):
    embed = discord.Embed(title="âš™ï¸ Sunucu AyarlarÄ±", color=discord.Color.blue())
    embed.add_field(name="KÃ¼fÃ¼r Filtresi", value="âœ… Aktif" if server_settings["kufurengel"] else "âŒ Pasif")
    embed.add_field(name="Reklam Filtresi", value="âœ… Aktif" if server_settings["reklamengel"] else "âŒ Pasif")
    embed.add_field(name="Spam Filtresi", value="âœ… Aktif" if server_settings["spamengel"] else "âŒ Pasif")
    embed.add_field(name="Log KanalÄ±", value=f"<#{server_settings['log_kanal']}>" if server_settings["log_kanal"] else "âŒ AyarlanmamÄ±ÅŸ")
    embed.add_field(name="GiriÅŸ-Ã‡Ä±kÄ±ÅŸ KanalÄ±", value=f"<#{server_settings['welcome_kanal']}>" if server_settings["welcome_kanal"] else "âŒ AyarlanmamÄ±ÅŸ")
    await ctx.send(embed=embed)

