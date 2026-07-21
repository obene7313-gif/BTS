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
     msg = await message.channel.send(f"📊 **MATEMATİK SORUSU! ({seviye.replace('_', ' ').upper()})**\n**{num1} {gosterim_islem} {num2} = ?**\n*Cevaplamak için 15 saniyen var!*", view=view)
...
await msg.edit(content=f"⏱️ Süre doldu! Doğru cevap **{cevap}** olacaktı.", view=None)

        
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

@bot.command()
@commands.has_permissions(administrator=True)
async def kufurengel(ctx):
    server_settings["kufurengel"] = not server_settings["kufurengel"]
    durum = 'AÃ‡IK' if server_settings['kufurengel'] else 'KAPALI'
    await ctx.send(f"ğŸ›¡ï¸ KÃ¼fÃ¼r filtresi: **{durum}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def reklamengel(ctx):
    server_settings["reklamengel"] = not server_settings["reklamengel"]
    durum = 'AÃ‡IK' if server_settings['reklamengel'] else 'KAPALI'
    await ctx.send(f"ğŸ›¡ï¸ Reklam filtresi: **{durum}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def spamengel(ctx):
    server_settings["spamengel"] = not server_settings["spamengel"]
    durum = 'AÃ‡IK' if server_settings['spamengel'] else 'KAPALI'
    await ctx.send(f"ğŸ›¡ï¸ Spam filtresi: **{durum}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def logayarla(ctx, channel: discord.TextChannel):
    server_settings["log_kanal"] = channel.id
    await ctx.send(f"âœ… Log kanalÄ± baÅŸarÄ±yla {channel.mention} olarak ayarlandÄ±!")

@bot.command(name="hosgeldin-ve-baybay-ayarla")
@commands.has_permissions(administrator=True)
async def welcomeayarla(ctx, channel: discord.TextChannel):
    server_settings["welcome_kanal"] = channel.id
    await ctx.send(f"âœ… GiriÅŸ-Ã‡Ä±kÄ±ÅŸ mesaj kanalÄ± {channel.mention} olarak ayarlandÄ±!")

@bot.command()
@commands.has_permissions(administrator=True)
async def karaliste(ctx, islem=None, *, kelime=None):
    if not islem:
        await ctx.send(f"ğŸ“ **YasaklÄ± Kelimeler:** {', '.join(server_settings['karaliste'])}")
    elif islem == "ekle" and kelime:
        if kelime.lower() not in server_settings["karaliste"]:
            server_settings["karaliste"].append(kelime.lower())
            await ctx.send(f"âœ… **{kelime}** yasaklÄ± kelime listesine eklendi.")
    elif islem == "cikar" and kelime:
        if kelime.lower() in server_settings["karaliste"]:
            server_settings["karaliste"].remove(kelime.lower())
            await ctx.send(f"âœ… **{kelime}** yasaklÄ± kelime listesinden Ã§Ä±karÄ±ldÄ±.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int):
    await ctx.channel.purge(limit=sayi + 1)
    await ctx.send(f"ğŸ—‘ï¸ **{sayi}** adet mesaj temizlendi.", delete_after=4)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def sustur(ctx, member: discord.Member, sure: str, *, sebep="Belirtilmedi"):
    time_dict = {"m": 1, "h": 60, "d": 1440}
    unit = sure[-1]
    if unit not in time_dict or not sure[:-1].isdigit():
        await ctx.send("âŒ GeÃ§ersiz sÃ¼re formatÄ±! Ã–rn: 5m, 2h, 1d")
        return
    minutes = int(sure[:-1]) * time_dict[unit]
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=sebep)
    await ctx.send(f"ğŸ¤ {member.mention} **{sure}** boyunca susturuldu. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def ac(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"ğŸ”Š {member.mention} kullanÄ±cÄ±sÄ±nÄ±n susturulmasÄ± kaldÄ±rÄ±ldÄ±.")

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    pos = ctx.channel.position
    new_ch = await ctx.channel.clone(reason="Nuke Ä°ÅŸlemi")
    await ctx.channel.delete()
    await new_ch.edit(position=pos)
    await new_ch.send("ğŸ’¥ Kanal baÅŸarÄ±yla sÄ±fÄ±rlandÄ± (Nuke)!\nhttps://tenor.com/view/explosion-mushroom-cloud-atomic-bomb-bomb-boom-gif-4464835")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"âœ… {member.mention} isimli Ã¼yeye **{role.name}** rolÃ¼ verildi.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"âœ… {member.mention} isimli Ã¼yeden **{role.name}** rolÃ¼ geri alÄ±ndÄ±.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"ğŸ”¨ **{member.name}** sunucudan banlandÄ±. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"ğŸ‘¢ **{member.name}** sunucudan atÄ±ldÄ±. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("ğŸ”’ Kanal yazÄ±ÅŸmaya kapatÄ±ldÄ±!")

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"ğŸ“ Pong! Gecikme: **{latency}ms**")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("ğŸ”“ Kanal tekrar yazÄ±ÅŸmaya aÃ§Ä±ldÄ±.")

# --- Ä°KÄ° AÅAMALI AFK SÄ°STEMÄ° ---
@bot.command()
async def afk(ctx, *, sebep=None):
    if ctx.author.bot:
        return

    # AFK'dan Ã§Ä±k
    if ctx.author.id in afk_users:
        veri = afk_users.pop(ctx.author.id)
        gecen = datetime.datetime.now() - veri["zaman"]
        gun = gecen.days
        saat, kalan = divmod(gecen.seconds, 3600)
        dakika, saniye = divmod(kalan, 60)

        sure = []

        if gun:
            sure.append(f"{gun} gÃ¼n")
        if saat:
            sure.append(f"{saat} saat")
        if dakika:
            sure.append(f"{dakika} dakika")
        if saniye:
            sure.append(f"{saniye} saniye")

        embed = discord.Embed(title="ğŸ‘‹ AFK Modu KapatÄ±ldÄ±", description=f"Tekrar hoÅŸ geldin {ctx.author.mention}!", color=discord.Color.green())

        embed.add_field(name="â³ AFK SÃ¼resi",value=", ".join(sure) if sure else "1 saniyeden az",inline=False)
        await ctx.send(embed=embed)
        return

    if not sebep:
        sebep = "Sebep belirtilmedi."

    afk_users[ctx.author.id] = {"sebep": sebep, "zaman": datetime.datetime.now()}

    embed = discord.Embed(title="ğŸ’¤ AFK Modu AÃ§Ä±ldÄ±", color=discord.Color.orange())

    embed.add_field(name="ğŸ‘¤ KullanÄ±cÄ±", value=ctx.author.mention, inline=False)

    embed.add_field(name="ğŸ“ Sebep", value=sebep, inline=False)
    embed.set_footer(text="AFK modundan Ã§Ä±kmak iÃ§in tekrar !afk yaz.")
    await ctx.send(embed=embed)

# --- EÄLENCE KOMUTLARI ---
@bot.command()
async def uÃ§angÃ¼vercin(ctx, member: discord.Member):
    await ctx.send(f"ğŸ•Šï¸ {ctx.author.mention}, {member.mention} kullanÄ±cÄ±sÄ±na uÃ§arak gelen Ã§atÄ±k kaÅŸlÄ± bir gÃ¼vercin fÄ±rlattÄ±!\n**Tekme atÄ±yor bu gÃ¼vercin sana!**\nhttps://tenor.com/view/pigeon-kick-funny-birds-gif-14470635")

@bot.command()
async def saat(ctx):
    tr_time = get_turkey_time().strftime('%d/%m/%Y %H:%M:%S')
    await ctx.send(f"â° **GÃ¼ncel TÃ¼rkiye Saati ve Tarihi:** {tr_time}")

@bot.command()
async def slaps(ctx, member: discord.Member):
    await ctx.send(f"ğŸ–ï¸ {ctx.author.mention}, {member.mention} kullanÄ±cÄ±sÄ±nÄ± OsmanlÄ± tokadÄ±yla uÃ§urdu!\nhttps://tenor.com/view/slap-in-the-face-angry-gif-14689404")

@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"ğŸ’‹ {ctx.author.mention}, {member.mention} kullanÄ±cÄ±sÄ±nÄ± sulu sulu Ã¶ptÃ¼!\nhttps://tenor.com/view/anime-kiss-gif-25745155")

@bot.command()
async def sarÄ±l(ctx, member: discord.Member):
    await ctx.send(f"ğŸ¤— {ctx.author.mention}, {member.mention} kullanÄ±cÄ±sÄ±na sÄ±msÄ±kÄ± sarÄ±ldÄ±!\nhttps://tenor.com/view/hug-anime-love-gif-25644292")
    
@bot.command()
async def Ã¶p(ctx, member: discord.Member):
    await ctx.send(f"ğŸ¤— {ctx.author.mention}, {member.mention} kullanÄ±cÄ±sÄ±nÄ± Ã¶pÃ¼cÃ¼ÄŸe boÄŸdu. https://klipy.com/gifs/kiss-video-love-you")
    
@bot.command()
async def kiss(ctx, member: discord.Member):
    await ctx.send(f"ğŸ¤— {ctx.author.mention}, {member.mention} kullanÄ±cÄ±sÄ±nÄ± Ã¶pÃ¼cÃ¼ÄŸe boÄŸdu. https://klipy.com/gifs/kiss-video-love-you")

@bot.command()
async def askolcer(ctx, member: discord.Member):
    oran = random.randint(0, 100)
    await ctx.send(f"â¤ï¸ {ctx.author.mention} ile {member.mention} arasÄ±ndaki aÅŸk oranÄ±: **%{oran}**")

@bot.command()
async def efkarolcer(ctx):
    oran = random.randint(0, 100)
    await ctx.send(f"ğŸš¬ {ctx.author.mention} bugÃ¼nkÃ¼ efkar durumun: **%{oran}**")

@bot.command()
async def sansolcer(ctx):
    oran = random.randint(0, 100)
    await ctx.send(f"ğŸ€ {ctx.author.mention} bugÃ¼nkÃ¼ ÅŸans durumun: **%{oran}**")

class BTSSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=isim, emoji=veri["emoji"])
            for isim, veri in BTS_MEMBERS.items()
        ]

        super().__init__(
            placeholder="Bir BTS Ã¼yesi seÃ§...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        uye = BTS_MEMBERS[self.values[0]]

        embed = discord.Embed(
            title=f"{uye['emoji']} {self.values[0]}",
            color=uye["renk"]
        )

        embed.add_field(name="GerÃ§ek AdÄ±", value=uye["isim"], inline=False)
        embed.add_field(name="DoÄŸum Tarihi", value=uye["dogum"], inline=False)
        embed.add_field(name="GÃ¶revi", value=uye["gorev"], inline=False)
        embed.set_footer(text="ğŸ’œ BTS Bilgi MenÃ¼sÃ¼")

        await interaction.response.edit_message(embed=embed, view=self.view)

class BTSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(BTSSelect())

@bot.command()
async def bts(ctx):
    embed = discord.Embed(
        title="ğŸ’œ BTS Bilgi MenÃ¼sÃ¼",
        description="AÅŸaÄŸÄ±daki menÃ¼den bir BTS Ã¼yesi seÃ§.",
        color=discord.Color.purple()
    )

    await ctx.send(embed=embed, view=BTSView())


@bot.command()
async def sanslisayi(ctx):
    sayi = random.randint(1, 100)
    await ctx.send(f"ğŸ² {ctx.author.mention}, bugÃ¼n senin ÅŸanslÄ± sayÄ±n: **{sayi}**")

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
    await ctx.send(f"ğŸ’• **GÃ¼nÃ¼n Shipi:** {m1.mention} X {m2.mention} | Kalp OranÄ±: **%{oran}**")

@bot.command()
async def ship2(ctx, member: discord.Member):
    await ctx.send(f"ğŸ’– {ctx.author.mention} X {member.mention}\n**AÅŸk OranÄ±: %99999! Bu aÅŸk Ã¶lÃ§Ã¼lemez!**")

# --- EKONOMÄ° & OYUN ---
@bot.command()
async def para(ctx, member: discord.Member = None):
    target = member or ctx.author
    bakiye = bts_puan.get(target.id, 100)
    bts_puan[target.id] = bakiye
    await ctx.send(f"ğŸ’° {target.mention}: **{bakiye} BTS ParasÄ±**")

@bot.command()
async def slots(ctx, miktar: int):
    bakiye = bts_puan.get(ctx.author.id, 100)
    if miktar <= 0 or miktar > bakiye:
        await ctx.send("âŒ GeÃ§ersiz miktar veya yetersiz bakiye!")
        return
    
    slots_icons = ["ğŸ’", "ğŸ‹", "ğŸ‡", "ğŸŠ", "ğŸ’"]
    r1, r2, r3 = random.choice(slots_icons), random.choice(slots_icons), random.choice(slots_icons)
    msg = f"ğŸ° **{ctx.author.name}** slots Ã§eviriyor...\n| {r1} | {r2} | {r3} |\n"
    
    if r1 == r2 == r3:
        odul = miktar * 4
        bts_puan[ctx.author.id] = bakiye + odul
        await ctx.send(msg + f"ğŸ”¥ **MÃœKEMMEL! 3'te 3 YaptÄ±n!** {odul} BTS ParasÄ± kazandÄ±n!")
    elif r1 == r2 or r2 == r3 or r1 == r3:
        odul = miktar * 2
        bts_puan[ctx.author.id] = bakiye + odul
        await ctx.send(msg + f"âœ¨ **GÃ¼zel! Ã‡ift yakaladÄ±n.** {odul} BTS ParasÄ± kazandÄ±n!")
    else:
        bts_puan[ctx.author.id] = bakiye - miktar
        await ctx.send(msg + f"ğŸ’¥ **Kaybettin!** {miktar} BTS ParasÄ± cÃ¼zdanÄ±ndan uÃ§tu.")

# --- BÄ°LGÄ° & SÄ°STEM ---
@bot.command()
async def spty(ctx, member: discord.Member = None):
    target = member or ctx.author
    spotify_act = None
    for act in target.activities:
        if isinstance(act, discord.Spotify):
            spotify_act = act
            break
            
    if spotify_act:
        embed = discord.Embed(title=f"ğŸµ {target.name} Spotify Dinliyor", color=discord.Color.green())
        embed.add_field(name="ÅarkÄ±", value=spotify_act.title, inline=False)
        embed.add_field(name="SanatÃ§Ä±", value=", ".join(spotify_act.artists), inline=False)
        embed.add_field(name="AlbÃ¼m", value=spotify_act.album, inline=False)
        embed.set_thumbnail(url=spotify_act.album_cover_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"âŒ {target.mention} ÅŸu an Spotify'da bir ÅŸey dinlemiyor veya durumu kapalÄ±.")

@bot.command()
async def kullanici(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title=f"ğŸ‘¤ KullanÄ±cÄ± Bilgisi: {target.name}", color=discord.Color.blue())
    embed.add_field(name="Hesap AÃ§Ä±lÄ±ÅŸ Tarihi", value=target.created_at.strftime('%d/%m/%Y'), inline=True)
    embed.add_field(name="Sunucuya KatÄ±lÄ±m", value=target.joined_at.strftime('%d/%m/%Y') if target.joined_at else "Bilinmiyor", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    await ctx.send(f"ğŸ° **{ctx.guild.name}** Sunucu Ãœye SayÄ±sÄ±: **{ctx.guild.member_count}**")

@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="ğŸ“œ Ultra GeliÅŸmiÅŸ Komut MenÃ¼sÃ¼", color=discord.Color.gold())
    embed.add_field(name="ğŸ›¡ï¸ Yetkili & YÃ¶netim", value="ayarlar, kufurengel, reklamengel, spamengel, logayarla, hosgeldin-ve-baybay-ayarla, karaliste, sil, sustur, ac, nuke, rolver, rolal, ban, kick, lock, unlock", inline=False)
    embed.add_field(name="ğŸ‰ EÄŸlence & EtkileÅŸim", value="afk, uÃ§angÃ¼vercin, saat, slaps, kiss, sarÄ±l, askolcer, efkarolcer, sanslisayi, ship, ship2", inline=False)
    embed.add_field(name="ğŸ’° Ekonomi & Sistem", value="para, slots, spty, kullanici, sunucu", inline=False)
    await ctx.send(embed=embed)

# --- BOTU BAÅLATMA ---
keep_alive()
bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
