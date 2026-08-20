import discord
from discord.ext import commands
import random
import asyncio
import json
import os
from datetime import datetime, timedelta
import time
import pytz
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# --- HARİCİ KÜTÜPHANESİZ 7/24 WEBSERVER ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("Bot 7/24 Aktif! 🌸✨".encode('utf-8'))

    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()

# --- VERİ ÇEKİMİ ---
try:
    from iltifatlar import selamlar_cevaplari, iltifatlar, bts_sorulari, eglence_yanitlari
except ImportError:
    selamlar_cevaplari = ["Aleykümselam hoş geldin! 🌸✨", "Selammm şekerim! 💖"]
    iltifatlar = ["Bugün yine parıldıyorsun! ✨🌸", "Gülüşün sunucuyu aydınlatıyor! 💖"]
    bts_sorulari = [{"soru": "BTS hangi yıl çıkış yaptı?", "siklar": ["2013", "2015", "2012", "2014"], "dogru": 0}]
    eglence_yanitlari = {}

# Bot Ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if "bakiye" not in data: data["bakiye"] = {}
                if "afk" not in data: data["afk"] = {}
                if "haftalik" not in data: data["haftalik"] = {}
                if "ayarlar" not in data: data["ayarlar"] = {"kufur": False, "reklam": False, "log": None, "hghb": None, "spam_saniye": 0}
                if "karaliste" not in data: data["karaliste"] = []
                return data
            except:
                pass
    return {
        "bakiye": {}, 
        "afk": {}, 
        "haftalik": {},
        "ayarlar": {"kufur": False, "reklam": False, "log": None, "hghb": None, "spam_saniye": 0}, 
        "karaliste": []
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()

# --- SORU / QUIZ GÖRÜNÜMÜ (HATA VERMEYEN DÜZELTİLMİŞ YAPI) ---
class QuizView(discord.ui.View):
    def __init__(self, dogru_index, options):
        super().__init__(timeout=30.0)
        self.dogru_index = dogru_index
        self.is_finished = False

        for idx, option in enumerate(options):
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.secondary, custom_id=f"quiz_{idx}")
            button.callback = self.create_callback(idx)
            self.add_item(button)

    def create_callback(self, idx):
        async def callback(interaction: discord.Interaction):
            if self.is_finished:
                await interaction.response.send_message("🌸 Bu yarışma zaten bitti şekerim! ✨", ephemeral=True)
                return

            clicked_button = [item for item in self.children if item.custom_id == f"quiz_{idx}"][0]

            if idx == self.dogru_index:
                self.is_finished = True
                clicked_button.style = discord.ButtonStyle.success
                
                for item in self.children:
                    item.disabled = True

                uid = str(interaction.user.id)
                db["bakiye"][uid] = db["bakiye"].get(uid, 0) + 500
                save_data(db)

                # Düzeltildi: Önce defer yapıp sonra mesajı güncelliyoruz ki Discord Zaman Aşımı Hatası vermesin
                await interaction.response.defer()
                await interaction.message.edit(
                    content=f"🎉 **Doğru Cevap!** {interaction.user.mention} doğru şıkkı buldu ve **500 BTS Parası** kazandı! Yeni bakiye: `{db['bakiye'][uid]}` 💖✨", 
                    view=self
                )
                self.stop()
            else:
                clicked_button.disabled = True
                clicked_button.style = discord.ButtonStyle.danger
                
                await interaction.response.defer()
                await interaction.message.edit(
                    content=f"💥 **{interaction.user.mention}** yanlış şıkka bastı! Ama yarışma devam ediyor, doğruyu bulana kadar denemeye devam edin! 🌸✨", 
                    view=self
                )
        return callback

# --- KOLAY MATEMATİK SORUSU ÜRETİCİ ---
def kolay_matematik_uret():
    islem_turu = random.choice(["+", "-", "*"])
    
    if islem_turu == "+":
        n1, n2 = random.randint(5, 30), random.randint(5, 30)
        ans = n1 + n2
        soru_metni = f"{n1} + {n2}"
    elif islem_turu == "-":
        n1 = random.randint(10, 40)
        n2 = random.randint(1, n1)
        ans = n1 - n2
        soru_metni = f"{n1} - {n2}"
    else:
        n1, n2 = random.randint(2, 9), random.randint(2, 9)
        ans = n1 * n2
        soru_metni = f"{n1} x {n2}"

    siklar = [str(ans), str(ans + random.choice([2, 3])), str(ans - random.choice([1, 2])), str(ans + 5)]
    siklar = list(dict.fromkeys(siklar))
    while len(siklar) < 4:
        farkli_sik = str(ans + random.randint(6, 15))
        if farkli_sik not in siklar:
            siklar.append(farkli_sik)
            
    random.shuffle(siklar)
    return soru_metni, ans, siklar

# --- ETKİNLİKLER ---
@bot.event
async def on_ready():
    print(f"🌸✨ {bot.user.name} ışıl ışıl aktifleşti! 💖🚀")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"🌸 **Eksik Bilgi!** Lütfen komutu doğru şekilde kullan şekerim. ✨")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("🌸 Lütfen geçerli bir kullanıcı veya sayı gir tatlım! ✨")
    else:
        print(f"Hata oluştu: {error}")

@bot.event
async def on_member_join(member):
    hghb_id = db["ayarlar"].get("hghb")
    if hghb_id:
        channel = member.guild.get_channel(hghb_id)
        if channel:
            embed = discord.Embed(title="🌸 Ailemize Hoş Geldin! ✨", description=f"Aramıza hoş geldin {member.mention}! 💖\nSunucumuz seninle beraber **{member.guild.member_count}** kişi oldu! 🎉🌸", color=discord.Color.from_rgb(255, 182, 193))
            await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    hghb_id = db["ayarlar"].get("hghb")
    if hghb_id:
        channel = member.guild.get_channel(hghb_id)
        if channel:
            embed = discord.Embed(title="🥀 Görüşmek Üzere...", description=f"**{member.display_name}** aramızdan ayrıldı, seni özleyeceğiz! 💔🌸", color=discord.Color.purple())
            await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = str(message.author.id)

    if uid in db["afk"]:
        sure = datetime.now() - datetime.fromisoformat(db["afk"][uid]["zaman"])
        dakika = int(sure.total_seconds() // 60)
        del db["afk"][uid]
        save_data(db)
        await message.channel.send(f"🎉 **Hoş geldin {message.author.mention}!** **{dakika}** dakikadır AFK idin, moddan çıkarıldın! ✨🌸")

    for user_mention in message.mentions:
        target_uid = str(user_mention.id)
        if target_uid in db["afk"]:
            info = db["afk"][target_uid]
            await message.channel.send(f"💤 **{user_mention.display_name}** şu an dinleniyor!\n📝 **Sebep:** {info['sebep']} 🌸✨")

    content_lower = message.content.lower()

    kufurler = ["amk", "aq", "sik", "piç", "orospu"] + db.get("karaliste", [])
    if db["ayarlar"].get("kufur") and any(k in content_lower for k in kufurler):
        await message.delete()
        await message.channel.send(f"🌸 {message.author.mention}, lütfen tatlı dilimizi koruyalım! Kötü sözler yasak ✨", delete_after=3)
        return

    if db["ayarlar"].get("reklam") and ("http://" in content_lower or "https://" in content_lower or "discord.gg" in content_lower):
        await message.delete()
        await message.channel.send(f"🌸 {message.author.mention}, sunucumuzda reklam ve link paylaşımı yasaktır! 💖", delete_after=3)
        return

    if content_lower in ["sa", "slm", "selam", "selamm"]:
        await message.reply(random.choice(selamlar_cevaplari))

    if random.random() < 0.02:
        await message.reply(f"🌸✨ {random.choice(iltifatlar)}")

    # %7 Çıkma İhtimali - %70 Matematik / %30 BTS
    if random.random() < 0.07:
        quiz_tur = random.choices(["math", "bts"], weights=[70, 30])[0]
        
        if quiz_tur == "math":
            soru_metni, ans, siklar = kolay_matematik_uret()
            view = QuizView(siklar.index(str(ans)), siklar)
            await message.channel.send(f"🧮 **KOLAY MATEMATİK SORUSU!** 🌸✨\n\n**{soru_metni} = ?**\n*Cevaplamak için 30 saniyeniz var! Herkes doğruyu bulana kadar deneyebilir!*", view=view)
        elif quiz_tur == "bts":
            q = random.choice(bts_sorulari)
            view = QuizView(q["dogru"], q["siklar"])
            await message.channel.send(f"💜 **BTS BİLGİ SORUSU!** ✨🌸\n\n{q['soru']}\n*Cevaplamak için 30 saniyeniz var! Herkes doğruyu bulana kadar deneyebilir!*", view=view)

    await bot.process_commands(message)

# ==================== YETKİLİ KOMUTLARI ====================

@bot.command()
@commands.has_permissions(administrator=True)
async def ayarlar(ctx):
    ayr = db["ayarlar"]
    embed = discord.Embed(title="⚙️ Sunucu Güvenlik & Sevgi Ayarları 🌸", color=discord.Color.pink())
    embed.add_field(name="🚫 Küfür Engeli", value="Açık ✅" if ayr["kufur"] else "Kapalı ❌", inline=True)
    embed.add_field(name="🔗 Reklam Engeli", value="Açık ✅" if ayr["reklam"] else "Kapalı ❌", inline=True)
    embed.add_field(name="📋 Log Kanalı", value=f"<#{ayr['log']}>" if ayr['log'] else "Ayarlanmamış ❌", inline=True)
    embed.add_field(name="👋 HG-HB Kanalı", value=f"<#{ayr['hghb']}>" if ayr['hghb'] else "Ayarlanmamış ❌", inline=True)
    embed.add_field(name="⏱️ Yavaş Mod", value=f"`{ayr.get('spam_saniye', 0)}` saniye", inline=True)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def kufurengel(ctx):
    db["ayarlar"]["kufur"] = not db["ayarlar"]["kufur"]
    save_data(db)
    durum = "aktif edildi 🌸✅" if db["ayarlar"]["kufur"] else "devre dışı bırakıldı ✨❌"
    await ctx.send(f"💖 Küfür engelleme sistemi **{durum}**!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def reklamengel(ctx):
    db["ayarlar"]["reklam"] = not db["ayarlar"]["reklam"]
    save_data(db)
    durum = "aktif edildi 🌸✅" if db["ayarlar"]["reklam"] else "devre dışı bırakıldı ✨❌"
    await ctx.send(f"💖 Reklam engelleme sistemi **{durum}**!")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def spamengel(ctx, saniye: int):
    await ctx.channel.edit(slowmode_delay=saniye)
    db["ayarlar"]["spam_saniye"] = saniye
    save_data(db)
    if saniye > 0:
        await ctx.send(f"⏱️ Kanaldaki yavaş mod **{saniye} saniye** olarak ayarlandı! 🛑🌸")
    else:
        await ctx.send(f"⏱️ Yavaş mod kaldırıldı, mesajlaşabilirsiniz! ✨💖")

@bot.command()
@commands.has_permissions(administrator=True)
async def logayar(ctx, kanal: discord.TextChannel):
    db["ayarlar"]["log"] = kanal.id
    save_data(db)
    await ctx.send(f"📋 Log kanalı {kanal.mention} olarak belirlendi! 🌸✨")

@bot.command()
@commands.has_permissions(administrator=True)
async def hghb(ctx, kanal: discord.TextChannel):
    db["ayarlar"]["hghb"] = kanal.id
    save_data(db)
    await ctx.send(f"👋 Hoş geldin kanalı {kanal.mention} olarak ayarlandı! ✨💖")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def karaliste(ctx, kelime: str):
    db["karaliste"].append(kelime.lower())
    save_data(db)
    await ctx.send(f"🛑 `{kelime}` sözcüğü karalisteye eklendi! 🌸")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int):
    deleted = await ctx.channel.purge(limit=sayi + 1)
    await ctx.send(f"🧹 **{len(deleted)-1}** adet mesaj pırıl pırıl temizlendi! 🌸✨", delete_after=3)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def sustur(ctx, kullanici: discord.Member, dakika: int, *, sebep="Belirtilmedi"):
    try:
        await kullanici.timeout(timedelta(minutes=dakika), reason=sebep)
        await ctx.send(f"🔇 **{kullanici.mention}**, **{dakika}** dakika boyunca dinlenmeye alındı! 🌸\n📝 **Sebep:** {sebep}")
    except:
        await ctx.send("❌ Kullanıcı susturulurken hata oluştu!")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def ac(ctx, kullanici: discord.Member, *, sebep="Belirtilmedi"):
    try:
        await kullanici.timeout(None, reason=sebep)
        await ctx.send(f"🔊 **{kullanici.mention}** tekrar konuşabilir! ✨💖")
    except:
        await ctx.send("❌ Susturma kaldırılırken hata oluştu!")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, kullanici: discord.Member, *, sebep="Belirtilmedi"):
    await kullanici.kick(reason=sebep)
    await ctx.send(f"👞 **{kullanici.display_name}** sunucudan uğurlandı! 📝 **Sebep:** {sebep} 🌸")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, kullanici: discord.Member, *, sebep="Belirtilmedi"):
    await kullanici.ban(reason=sebep)
    await ctx.send(f"✈️ **{kullanici.display_name}** sunucudan yasaklandı! 📝 **Sebep:** {sebep} 🥀")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, id: int, *, sebep="Belirtilmedi"):
    user = await bot.fetch_user(id)
    await ctx.guild.unban(user, reason=sebep)
    await ctx.send(f"🔓 **{user.display_name}** kişisinin yasağı kaldırıldı! ✨🌸")

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx, *, sebep="Belirtilmedi"):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("👑 Bu özel komutu sadece Tac Sahibi kullanabilir! ✨")
        return
    pos = ctx.channel.position
    new_channel = await ctx.channel.clone(reason=f"Nuke: {sebep}")
    await ctx.channel.delete()
    await new_channel.edit(position=pos)
    await new_channel.send(f"💥 Kanal **{ctx.author.mention}** tarafından yenilendi!\n📝 **Sebep:** {sebep} 🌸✨")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal yazıma kilitlendi! 🛑🌸")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Kanal tekrar yazıma açıldı! ✨💖")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, kullanici: discord.Member, rol: discord.Role):
    await kullanici.add_roles(rol)
    await ctx.send(f"✅ {kullanici.mention} kullanıcısına **{rol.name}** rolü verildi! 🎉🌸")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, kullanici: discord.Member, rol: discord.Role):
    await kullanici.remove_roles(rol)
    await ctx.send(f"🗑️ {kullanici.mention} kullanıcısından **{rol.name}** rolü alındı! ✨")

@bot.command()
async def amortentia(ctx, kullanici: discord.Member, miktar: int):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("👑 Bu ikramı sadece Tac Sahibi yapabilir! ✨")
        return
    uid = str(kullanici.id)
    db["bakiye"][uid] = db["bakiye"].get(uid, 0) + miktar
    save_data(db)
    await ctx.send(f"👑 **Tac Sahibi İkramı!** {kullanici.mention} hesabına **{miktar} BTS Parası** eklendi! 💜✨🌸")

# ==================== EĞLENCE & OYUN MİNİ-GAMES ====================

@bot.command()
async def adamasmaca(ctx):
    kelimeler = ["bts", "jungkook", "jimin", "suga", "rm", "jhope", "jin", "v", "amortentia", "kpop", "muzik", "discord", "magaza", "straykids", "blackpink"]
    secilen = random.choice(kelimeler).lower()
    tahmin_edilen = ["_"] * len(secilen)
    kalan_hak = 6
    kullanilan_harfler = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and len(m.content) == 1

    msg = await ctx.send(f"🎮 **Adam Asmaca Başladı!** 🌸\nWord: `{' '.join(tahmin_edilen)}` \nKalan Hak: **{kalan_hak}** ❤️\nBir harf yazın!")

    while kalan_hak > 0 and "_" in tahmin_edilen:
        try:
            response = await bot.wait_for("message", check=check, timeout=30.0)
            harf = response.content.lower()

            if harf in kullanilan_harfler:
                await ctx.send("🌸 Bu harfi zaten denemiştin şekerim, başka bir harf dene!", delete_after=3)
                continue

            kullanilan_harfler.append(harf)

            if harf in secilen:
                for i in range(len(secilen)):
                    if secilen[i] == harf:
                        tahmin_edilen[i] = harf
                
                await msg.edit(content=f"🎉 **Doğru Harf!** 🌸\nWord: `{' '.join(tahmin_edilen)}` \nKalan Hak: **{kalan_hak}** ❤️\nDenediğin Harfler: `{', '.join(kullanilan_harfler)}`")
            else:
                kalan_hak -= 1
                await msg.edit(content=f"❌ **Yanlış Harf!** 🌸\nWord: `{' '.join(tahmin_edilen)}` \nKalan Hak: **{kalan_hak}** ❤️\nDenediğin Harfler: `{', '.join(kullanilan_harfler)}`")

        except asyncio.TimeoutError:
            await ctx.send(f"⏱️ **Süre Doldu!** Adam asmaca oyunu bitti. Doğru kelime: `{secilen}` idi 🌸")
            return

    if "_" not in tahmin_edilen:
        uid = str(ctx.author.id)
        db["bakiye"][uid] = db["bakiye"].get(uid, 0) + 300
        save_data(db)
        await ctx.send(f"🎊 **TEBRİKLER {ctx.author.mention}!** Kelimeyi bildin: `{secilen.upper()}`! Hesabına **300 BTS Parası** eklendi! 💜✨")
    else:
        await ctx.send(f"🥀 **Kaybettin!** Adam asıldı... Doğru kelime `{secilen.upper()}` idi. Şansını tekrar dene! 🌸")

@bot.command()
async def kacsm(ctx, kullanici: discord.Member = None):
    hedef = kullanici if kullanici else ctx.author
    cm = random.randint(0, 50)

    cumleler_kucuk = [
        f"📏 {hedef.mention} kişisinin ölçümü yapıldı: **{cm} cm**! Minnakmış laa bu 🌸🤏",
        f"📏 **{hedef.display_name}** için sonuç: **{cm} cm**! Bayağı minnakmış laa bu, cebimde taşırım ben bunu! ✨💖",
        f"📏 **{hedef.display_name}** boyutu: **{cm} cm**! Minnakmış laa bu, nazar değmesin tatlılığa! 🌸🥺"
    ]

    cumleler_orta = [
        f"📏 {hedef.mention} ölçüldü: **{cm} cm**! Oha bununki ne kadar da büyük! 🌸✨",
        f"📏 **{hedef.display_name}** sonuçları şok etti: **{cm} cm**! Oha bununki ne kadar da büyük, maşallah deyin! 💖🔥"
    ]

    cumleler_buyuk = [
        f"📏 {hedef.mention} ölçüldü: **{cm} cm**! Mutantmış olm sen gibi bu ne böyle?! 🚨🌸",
        f"📏 **{hedef.display_name}** rekor kırdı: **{cm} cm**! Mutantmış olm sen, insani boyutları aşmışsın! 💖😱"
    ]

    if cm <= 17:
        mesaj = random.choice(cumleler_kucuk)
    elif cm <= 30:
        mesaj = random.choice(cumleler_orta)
    else:
        mesaj = random.choice(cumleler_buyuk)

    await ctx.send(mesaj)

@bot.command()
async def afk(ctx, *, sebep="Canım öyle istedi ✨🌸"):
    uid = str(ctx.author.id)
    db["afk"][uid] = {"sebep": sebep, "zaman": datetime.now().isoformat()}
    save_data(db)
    await ctx.send(f"💤 {ctx.author.mention} artık AFK!\n📝 **Sebep:** {sebep} 🌸")

@bot.command()
async def ucanguvercin(ctx, kullanici: discord.Member):
    data = eglence_yanitlari.get("ucanguvercin", {})
    metinler = data.get("metinler", ["🕊️ {author}, {target} kişisine sevimli bir uçan güvercin gönderdi! 💖🌸"])
    gifler = data.get("gifler", ["https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHp1eXU1dmx2N3R1ZnZ4Z3lhbzRndTZ1cXV6ZnhmczJmbzA0Z21neCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l3vRf8U64f2YxL3i0/giphy.gif"])
    msg = random.choice(metinler).format(author=ctx.author.display_name, target=kullanici.display_name)
    embed = discord.Embed(description=msg, color=discord.Color.blue())
    embed.set_image(url=random.choice(gifler))
    await ctx.send(embed=embed)

@bot.command()
async def kiss(ctx, kullanici: discord.Member):
    data = eglence_yanitlari.get("kiss", {})
    metinler = data.get("metinler", ["💋 {author}, {target} kişisini tatlıca öptü! 💖✨"])
    gifler = data.get("gifler", ["https://media.giphy.com/media/G3va39rn8E4A8/giphy.gif"])
    msg = random.choice(metinler).format(author=ctx.author.display_name, target=kullanici.display_name)
    embed = discord.Embed(description=msg, color=discord.Color.magenta())
    embed.set_image(url=random.choice(gifler))
    await ctx.send(embed=embed)

@bot.command()
async def op(ctx, kullanici: discord.Member):
    await kiss(ctx, kullanici)

@bot.command()
async def saril(ctx, kullanici: discord.Member):
    data = eglence_yanitlari.get("saril", {})
    metinler = data.get("metinler", ["🫂 {author}, {target} kişisine sıcacık sarıldı! 🌸✨"])
    gifler = data.get("gifler", ["https://media.giphy.com/media/3M4NpbLCTxBqU/giphy.gif"])
    msg = random.choice(metinler).format(author=ctx.author.display_name, target=kullanici.display_name)
    embed = discord.Embed(description=msg, color=discord.Color.purple())
    embed.set_image(url=random.choice(gifler))
    await ctx.send(embed=embed)

@bot.command()
async def slaps(ctx, kullanici: discord.Member):
    data = eglence_yanitlari.get("slaps", {})
    metinler = data.get("metinler", ["🖐️ {author}, {target} kişisine şaka yollu bir tokat attı! 🌸"])
    gifler = data.get("gifler", ["https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif"])
    msg = random.choice(metinler).format(author=ctx.author.display_name, target=kullanici.display_name)
    embed = discord.Embed(description=msg, color=discord.Color.orange())
    embed.set_image(url=random.choice(gifler))
    await ctx.send(embed=embed)

@bot.command()
async def eat(ctx, kullanici: discord.Member = None, *, yemek: str = "leziz bir tatlı"):
    if kullanici is None:
        await ctx.send(f"🍴 **{ctx.author.display_name}**, nefis bir **{yemek}** yiyor! 🍕🍔😋🌸")
    else:
        await ctx.send(f"🎁 **{ctx.author.display_name}**, **{kullanici.display_name}** kişisine **{yemek}** ısmarladı! 🎂🍓✨")

@bot.command()
async def efkarolcer(ctx, kullanici: discord.Member = None):
    kullanici = kullanici or ctx.author
    yuzde = random.randint(0, 100)
    await ctx.send(f"🚬 **{kullanici.display_name}** kişisinin bugün efkâr seviyesi: **%{yuzde}** 🌸✨")

@bot.command()
async def askolcer(ctx, kullanici: discord.Member):
    yuzde = random.randint(0, 100)
    await ctx.send(f"💖 **{ctx.author.display_name}** ile **{kullanici.display_name}** arasındaki tatlı aşk oranı: **%{yuzde}** 🌸✨")

@bot.command()
async def sanslisayi(ctx, kullanici: discord.Member = None):
    kullanici = kullanici or ctx.author
    sayi = random.randint(1, 1000)
    await ctx.send(f"🍀 **{kullanici.display_name}** kişisinin bugünkü şanslı sayısı: **{sayi}** 🎲✨")

@bot.command()
async def ship(ctx):
    members = [m for m in ctx.guild.members if not m.bot and m != ctx.author]
    if not members:
        await ctx.send("❌ Sunucuda shiplenecek tatlı bir üye bulunamadı!")
        return
    secilen = random.choice(members)
    yuzde = random.randint(0, 100)
    await ctx.send(f"💍 **{ctx.author.display_name}** ❤️ **{secilen.display_name}**\n💖 Uyumluluk Oranı: **%{yuzde}** 🌸✨")

@bot.command()
async def ship2(ctx, kullanici: discord.Member):
    await ctx.send(f"💖 **{ctx.author.display_name}** & **{kullanici.display_name}** arasındaki sonsuz aşk oranı: **%999999**! 💍✨🌸")

@bot.command()
async def saat(ctx):
    tz = pytz.timezone("Europe/Istanbul")
    zaman = datetime.now(tz).strftime("%d/%m/%Y - %H:%M:%S")
    await ctx.send(f"⏰ **Türkiye Saati:** `{zaman}` 🇹🇷✨🌸")

# ==================== EKONOMİ KOMUTLARI ====================

@bot.command(name="haftalık", aliases=["haftalik"])
async def haftalik_odul(ctx):
    uid = str(ctx.author.id)
    su_an = time.time()
    
    if "haftalik" not in db:
        db["haftalik"] = {}

    son_claim = db["haftalik"].get(uid, 0)
    bekleme_suresi = 7 * 24 * 60 * 60

    if su_an - son_claim < bekleme_suresi:
        kalan_saniye = int(bekleme_suresi - (su_an - son_claim))
        gun = kalan_saniye // (24 * 3600)
        saat = (kalan_saniye % (24 * 3600)) // 3600
        dakika = (kalan_saniye % 3600) // 60

        await ctx.send(
            f"🌸 **{ctx.author.display_name}**, ben seni unutur muyum hiç? 💕\n"
            f"Sana en son harçlığını zaten vermiştim! ✨\n"
            f"Yeni haftalık **10.000 BTS Parası** ödülün için **{gun} gün, {saat} saat, {dakika} dakika** sonra tekrar gel tamam mı? 💖"
        )
        return

    db["bakiye"][uid] = db["bakiye"].get(uid, 0) + 10000
    db["haftalik"][uid] = su_an
    save_data(db)

    await ctx.send(
        f"🎉 **Tebrikler {ctx.author.display_name}!** 🌸✨\n"
        f"Bu haftaki **10.000 BTS Parası** harçlığın hesabına aktarıldı! 🪙💖\n"
        f"💰 **Toplam Bakiyen:** `{db['bakiye'][uid]:,} BTS Parası` ✨"
    )

@bot.command()
async def para(ctx):
    uid = str(ctx.author.id)
    bakiye = db["bakiye"].get(uid, 0)
    await ctx.send(f"💰 **{ctx.author.display_name}**, cüzdanında **{bakiye:,} BTS Parası** var! 💜✨🌸")

@bot.command()
async def yazitura(ctx, miktar: int, secim: str):
    uid = str(ctx.author.id)
    bakiye = db["bakiye"].get(uid, 0)
    if miktar > bakiye or miktar <= 0:
        await ctx.send("❌ Yetersiz bakiye şekerim! 💔🌸")
        return
    
    sonuc = random.choice(["yazi", "tura"])
    if secim.lower() == sonuc:
        db["bakiye"][uid] += miktar
        await ctx.send(f"🎉 **Kazandın!** Para `{sonuc}` geldi ve **+{miktar} BTS Parası** kazandın! 🪙✨🌸")
    else:
        db["bakiye"][uid] -= miktar
        await ctx.send(f"💥 **Kaybettin!** Para `{sonuc}` geldi. **{miktar} BTS Parası** cüzdanından uçtu! 💸🌸")
    save_data(db)

@bot.command()
async def slots(ctx, miktar: int = 100):
    uid = str(ctx.author.id)
    bakiye = db["bakiye"].get(uid, 0)
    if miktar > bakiye or miktar <= 0:
        await ctx.send("❌ Yetersiz bakiye şekerim! 💔🌸")
        return

    emojiler = ["🍓", "🍒", "🍊", "🍇", "💎", "🍋"]
    s1, s2, s3 = random.choice(emojiler), random.choice(emojiler), random.choice(emojiler)
    
    if s1 == s2 == s3:
        net_kazanc = miktar * 2
        db["bakiye"][uid] += net_kazanc
        msg = f"🎰 **{ctx.author.display_name}** slots çeviriyor...\n| {s1} | {s2} | {s3} |\n\n🎉 **TEBRİKLER!** 3 tuttu ve **+{net_kazanc} BTS Parası** cüzdanına eklendi! 💎✨🌸"
    else:
        db["bakiye"][uid] -= miktar
        msg = f"🎰 **{ctx.author.display_name}** slots çeviriyor...\n| {s1} | {s2} | {s3} |\n\n💥 **Kaybettin! {miktar} BTS Parası** cüzdanından uçtu. 💸🌸"
    
    save_data(db)
    await ctx.send(msg)

@bot.command(aliases=["transfer", "iban"])
async def join(ctx, kullanici: discord.Member = None, miktar: int = None):
    if kullanici is None or miktar is None:
        await ctx.send("🌸 Lütfen kime ne kadar para göndereceğini yaz! Örn: `!transfer @kullanıcı 100` ✨")
        return

    sender_uid = str(ctx.author.id)
    receiver_uid = str(kullanici.id)
    
    if db["bakiye"].get(sender_uid, 0) < miktar or miktar <= 0:
        await ctx.send("❌ Yetersiz bakiye şekerim! 💔🌸")
        return

    db["bakiye"][sender_uid] -= miktar
    db["bakiye"][receiver_uid] = db["bakiye"].get(receiver_uid, 0) + miktar
    save_data(db)
    await ctx.send(f"💸 **{ctx.author.display_name}**, **{kullanici.display_name}** kişisine **{miktar} BTS Parası** hediye etti! 🎁✨🌸")

@bot.command()
async def rich(ctx):
    sirali = sorted(db["bakiye"].items(), key=lambda x: x[1], reverse=True)[:5]
    embed = discord.Embed(title="🏆 Sunucunun En Zenginleri 💜🌸", color=discord.Color.gold())
    for idx, (user_id, coin) in enumerate(sirali, 1):
        try:
            usr = await bot.fetch_user(int(user_id))
            embed.add_field(name=f"#{idx} {usr.display_name}", value=f"💰 `{coin:,}` BTS Parası", inline=False)
        except:
            pass
    await ctx.send(embed=embed)

# ==================== BİLGİ & DİĞER KOMUTLAR ====================

@bot.command(aliases=["soru"])
async def quiz(ctx):
    q = random.choice(bts_sorulari)
    view = QuizView(q["dogru"], q["siklar"])
    await ctx.send(f"💜 **BTS BİLGİ SORUSU!** ✨🌸\n\n{q['soru']}\n*Cevaplamak için 30 saniyeniz var! Herkes doğruyu bulana kadar deneyebilir!*", view=view)

@bot.command(aliases=["mat", "matematiksorusu"])
async def matematik(ctx):
    soru_metni, ans, siklar = kolay_matematik_uret()
    view = QuizView(siklar.index(str(ans)), siklar)
    await ctx.send(f"🧮 **KOLAY MATEMATİK SORUSU!** 🌸✨\n\n**{soru_metni} = ?**\n*Cevaplamak için 30 saniyeniz var! Herkes doğruyu bulana kadar deneyebilir!*", view=view)

@bot.command()
async def bts(ctx):
    uyeler = ["RM 🐨", "Jin 🐹", "Suga 🐱", "J-Hope 🐿️", "Jimin 🐥", "V 🐯", "Jungkook 🐰"]
    secilen = random.choice(uyeler)
    embed = discord.Embed(title="💜 BTS Ruh Eşi Testi 🌸", description=f"Sen bugün tam bir **{secilen}** gibisin! ✨💖", color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    embed = discord.Embed(title=f"🏰 {ctx.guild.name} Sunucu Bilgisi 🌸", color=discord.Color.pink())
    embed.add_field(name="👥 Toplam Üye", value=str(ctx.guild.member_count), inline=True)
    embed.add_field(name="👑 Tac Sahibi", value=ctx.guild.owner.mention, inline=True)
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    await ctx.send(embed=embed)

@bot.command()
async def kullanici(ctx, kullanici: discord.Member = None):
    hedef = kullanici if kullanici else ctx.author
    katilma = hedef.joined_at.strftime("%d/%m/%Y")
    
    msg = f"👤 **{hedef.display_name}**, **{katilma}** tarihinden beridir aramızda! ✨🌸"
    embed = discord.Embed(title="📅 Sunucu Katılım Bilgisi 💖", description=msg, color=discord.Color.teal())
    embed.set_thumbnail(url=hedef.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 **Pong!** Bot gecikmesi: `{round(bot.latency * 1000)}ms` ⚡🌸")

@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🌸 Amortentia Bot Komut Menüsü ✨", description="Tüm komutlar sevgilerle hazırlandı ✨💖", color=discord.Color.pink())
    embed.add_field(name="👑 Yetkili Komutları", value="`!ayarlar`, `!kufurengel`, `!reklamengel`, `!spamengel`, `!logayar`, `!hghb`, `!karaliste`, `!sil`, `!sustur`, `!ac`, `!kick`, `!ban`, `!unban`, `!nuke`, `!lock`, `!unlock`, `!rolver`, `!rolal`, `!amortentia`", inline=False)
    embed.add_field(name="💖 Eğlence Komutları", value="`!adamasmaca`, `!kacsm`, `!afk`, `!ucanguvercin`, `!kiss`, `!op`, `!saril`, `!slaps`, `!efkarolcer`, `!askolcer`, `!sanslisayi`, `!ship`, `!ship2`, `!eat`, `!saat`", inline=False)
    embed.add_field(name="💰 Ekonomi Komutları", value="`!haftalık`, `!para`, `!yazitura`, `!slots`, `!join`, `!rich`", inline=False)
    embed.add_field(name="💜 Bilgi & Genel", value="`!soru`, `!matematik`, `!bts`, `!sunucu`, `!kullanici`, `!ping`", inline=False)
    await ctx.send(embed=embed)

# TOKEN VE BAŞLATMA
keep_alive()
TOKEN = os.getenv("TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ HATA: Render üzerinde 'TOKEN' bulunamadı!")
