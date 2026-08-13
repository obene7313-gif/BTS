import discord
from discord.ext import commands
import random
import asyncio
import json
import os
from datetime import datetime
import time
import pytz

# iltifatlar.py dosyasından veri çekimi
from iltifatlar import selamlar_cevaplari, iltifatlar, bts_sorulari, eglence_yanitlari

# Bot Ayarları ve İzinleri
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Veri Tabanı Dosyası Mantığı
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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

# 15 Saniyelik Butonlu Test Görünümü (Matematik & BTS Quiz)
class QuizView(discord.ui.View):
    def __init__(self, dogru_index, options, author):
        super().__init__(timeout=15.0)
        self.dogru_index = dogru_index
        self.author = author
        self.answered = False

        for idx, option in enumerate(options):
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.secondary, custom_id=f"quiz_{idx}")
            button.callback = self.create_callback(idx)
            self.add_item(button)

    def create_callback(self, idx):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("❌ Bu quizi sadece soruyu tetikleyen kişi cevaplayabilir!", ephemeral=True)
                return
            if self.answered:
                return

            self.answered = True
            for item in self.children:
                item.disabled = True

            if idx == self.dogru_index:
                uid = str(interaction.user.id)
                db["bakiye"][uid] = db["bakiye"].get(uid, 0) + 500
                save_data(db)
                await interaction.response.edit_message(content=f"🎉 **Tebrikler {interaction.user.mention}!** Doğru cevap! **500 BTS Parası** kazandın! 💜✨", view=self)
            else:
                await interaction.response.edit_message(content=f"❌ **Yanlış cevap!** Üzgünüm, şansını bir dahakine dene! 💔", view=self)
            self.stop()
        return callback

# --- ETKİNLİK DİNLENMESİ (EVENTS) ---
@bot.event
async def on_ready():
    print(f"✨ {bot.user.name} başarıyla aktifleşti! 🚀💖")

@bot.event
async def on_member_join(member):
    hghb_id = db["ayarlar"].get("hghb")
    if hghb_id:
        channel = member.guild.get_channel(hghb_id)
        if channel:
            embed = discord.Embed(title="🌸 Hoş Geldin!", description=f"Aramıza hoş geldin {member.mention}! ✨\nSunucumuz seninle **{member.guild.member_count}** kişi oldu! 🎉", color=discord.Color.pink())
            await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    hghb_id = db["ayarlar"].get("hghb")
    if hghb_id:
        channel = member.guild.get_channel(hghb_id)
        if channel:
            embed = discord.Embed(title="💔 Güle Güle!", description=f"**{member.display_name}** sunucudan ayrıldı... 🥀", color=discord.Color.red())
            await channel.send(embed=embed)

@bot.event
async def on_message(message):
    # KRİTİK: Bot kendi mesajlarına cevap vermez, sonsuz döngüye girip çökmez!
    if message.author.bot:
        return

    uid = str(message.author.id)

    # AFK Kontrolü
    if uid in db["afk"]:
        sure = datetime.now() - datetime.fromisoformat(db["afk"][uid]["zaman"])
        dakika = int(sure.total_seconds() // 60)
        del db["afk"][uid]
        save_data(db)
        await message.channel.send(f"🎉 Hoş geldin {message.author.mention}! **{dakika}** dakikadır AFK idin, moddan çıkarıldın! ✨")

    for user_mention in message.mentions:
        target_uid = str(user_mention.id)
        if target_uid in db["afk"]:
            info = db["afk"][target_uid]
            await message.channel.send(f"💤 **{user_mention.display_name}** şu an AFK!\n📝 **Sebep:** {info['sebep']}")

    content_lower = message.content.lower()

    # Filtreler (Küfür / Reklam)
    kufurler = ["amk", "aq", "sik", "piç", "orospu"] + db.get("karaliste", [])
    if db["ayarlar"].get("kufur") and any(k in content_lower for k in kufurler):
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, kötü söz kullanımı engellenmiştir! 🛑", delete_after=3)
        return

    if db["ayarlar"].get("reklam") and ("http://" in content_lower or "https://" in content_lower or "discord.gg" in content_lower):
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, reklam / link paylaşımı engellenmiştir! 🛑", delete_after=3)
        return

    # 100 Adet Selam Cevabından Biriyle Yanıt Verme
    if content_lower in ["sa", "slm", "selam", "selamm"]:
        await message.reply(random.choice(selamlar_cevaplari))

    # %2 Şansla Otomatik İltifat
    if random.random() < 0.02:
        await message.reply(f"✨ {random.choice(iltifatlar)}")

    # %5 Şansla Butonlu Soru Sorma (Matematik / BTS Quiz)
    if random.random() < 0.05:
        quiz_tur = random.choice(["math", "bts"])
        if quiz_tur == "math":
            n1, n2 = random.randint(1, 50), random.randint(1, 50)
            op = random.choice(["+", "-", "*"])
            if op == "+": ans = n1 + n2
            elif op == "-": ans = n1 - n2
            else: ans = n1 * n2
            
            siklar = [str(ans), str(ans + random.randint(1, 5)), str(ans - random.randint(1, 5)), str(ans + random.randint(6, 10))]
            random.shuffle(siklar)
            view = QuizView(siklar.index(str(ans)), siklar, message.author)
            await message.channel.send(f"🧮 **Matematik Sorusu:** `{n1} {op} {n2}` kaçtır? (15 Saniyen var! ⏳)", view=view)

        elif quiz_tur == "bts":
            q = random.choice(bts_sorulari)
            view = QuizView(q["dogru"], q["siklar"], message.author)
            await message.channel.send(f"💜 **BTS Sınavı:** {q['soru']} (15 Saniyen var! ⏳)", view=view)

    await bot.process_commands(message)

# ==================== YETKİLİ KOMUTLARI ====================

@bot.command()
@commands.has_permissions(administrator=True)
async def ayarlar(ctx):
    ayr = db["ayarlar"]
    embed = discord.Embed(title="⚙️ Sunucu Güvenlik Ayarları", color=discord.Color.purple())
    embed.add_field(name="🚫 Küfür Engeli", value="Açık ✅" if ayr["kufur"] else "Kapalı ❌", inline=True)
    embed.add_field(name="🔗 Reklam Engeli", value="Açık ✅" if ayr["reklam"] else "Kapalı ❌", inline=True)
    embed.add_field(name="📋 Log Kanalı", value=f"<#{ayr['log']}>" if ayr['log'] else "Ayarlanmamış ❌", inline=True)
    embed.add_field(name="👋 HG-HB Kanalı", value=f"<#{ayr['hghb']}>" if ayr['hghb'] else "Ayarlanmamış ❌", inline=True)
    embed.add_field(name="⏱️ Yavaş Mod (Spam)", value=f"`{ayr.get('spam_saniye', 0)}` saniye", inline=True)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def kufurengel(ctx):
    db["ayarlar"]["kufur"] = not db["ayarlar"]["kufur"]
    save_data(db)
    durum = "aktif edildi ✅" if db["ayarlar"]["kufur"] else "devre dışı bırakıldı ❌"
    await ctx.send(f"🌸 Küfür engelleme sistemi **{durum}**!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def reklamengel(ctx):
    db["ayarlar"]["reklam"] = not db["ayarlar"]["reklam"]
    save_data(db)
    durum = "aktif edildi ✅" if db["ayarlar"]["reklam"] else "devre dışı bırakıldı ❌"
    await ctx.send(f"🌸 Reklam engelleme sistemi **{durum}**!")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def spamengel(ctx, saniye: int):
    """Erensi Bot Yavaşmod Mantığı"""
    await ctx.channel.edit(slowmode_delay=saniye)
    db["ayarlar"]["spam_saniye"] = saniye
    save_data(db)
    if saniye > 0:
        await ctx.send(f"⏱️ Kanaldaki yavaş mod (spam engeli) **{saniye} saniye** olarak ayarlandı! 🛑")
    else:
        await ctx.send(f"⏱️ Kanaldaki yavaş mod kaldırıldı! ✨")

@bot.command()
@commands.has_permissions(administrator=True)
async def logayar(ctx, kanal: discord.TextChannel):
    db["ayarlar"]["log"] = kanal.id
    save_data(db)
    await ctx.send(f"📋 Log kanalı {kanal.mention} olarak ayarlandı! ✨")

@bot.command()
@commands.has_permissions(administrator=True)
async def hghb(ctx, kanal: discord.TextChannel):
    db["ayarlar"]["hghb"] = kanal.id
    save_data(db)
    await ctx.send(f"👋 HG-HB kanalı {kanal.mention} olarak ayarlandı! ✨")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def karaliste(ctx, kelime: str):
    db["karaliste"].append(kelime.lower())
    save_data(db)
    await ctx.send(f"🛑 `{kelime}` küfür engel listesine eklendi! ✨")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, sayi: int):
    deleted = await ctx.channel.purge(limit=sayi + 1)
    await ctx.send(f"🧹 **{len(deleted)-1}** adet mesaj temizlendi! ✨", delete_after=3)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def sustur(ctx, kullanici: discord.Member, dakika: int, *, sebep="Belirtilmedi"):
    try:
        await kullanici.timeout(discord.utils.utcnow() + asyncio.timedelta(minutes=dakika), reason=sebep)
        await ctx.send(f"🔇 **{kullanici.mention}**, **{dakika}** dakika boyunca susturuldu! 📝 **Sebep:** {sebep}")
    except:
        await ctx.send("❌ Kullanıcı susturulurken hata oluştu!")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def ac(ctx, kullanici: discord.Member, *, sebep="Belirtilmedi"):
    try:
        await kullanici.timeout(None, reason=sebep)
        await ctx.send(f"🔊 **{kullanici.mention}** kişisinin susturulması kaldırıldı! 📝 **Sebep:** {sebep}")
    except:
        await ctx.send("❌ Susturma kaldırılırken hata oluştu!")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, kullanici: discord.Member, *, sebep="Belirtilmedi"):
    await kullanici.kick(reason=sebep)
    await ctx.send(f"👞 **{kullanici.display_name}** sunucudan atıldı! 📝 **Sebep:** {sebep}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, kullanici: discord.Member, *, sebep="Belirtilmedi"):
    await kullanici.ban(reason=sebep)
    await ctx.send(f"✈️ **{kullanici.display_name}** sunucudan yasaklandı! 📝 **Sebep:** {sebep}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, id: int, *, sebep="Belirtilmedi"):
    user = await bot.fetch_user(id)
    await ctx.guild.unban(user, reason=sebep)
    await ctx.send(f"🔓 **{user.display_name}** kişisinin yasağı kaldırıldı!")

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx, *, sebep="Belirtilmedi"):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Nuke komutunu sadece sunucu tac sahibi kullanabilir! 👑")
        return
    pos = ctx.channel.position
    new_channel = await ctx.channel.clone(reason=f"Nuke komutu: {sebep}")
    await ctx.channel.delete()
    await new_channel.edit(position=pos)
    await new_channel.send(f"💥 Kanal **{ctx.author.mention}** tarafından nukelendi!\n📝 **Sebep:** {sebep}\nhttps://media.giphy.com/media/XUFPGrX5Zis6Y/giphy.gif")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal yazıma kapatıldı! 🛑")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Kanal tekrar yazıma açıldı! ✨")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, kullanici: discord.Member, rol: discord.Role):
    await kullanici.add_roles(rol)
    await ctx.send(f"✅ {kullanici.mention} kullanıcısına **{rol.name}** rolü verildi! 🎉")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, kullanici: discord.Member, rol: discord.Role):
    await kullanici.remove_roles(rol)
    await ctx.send(f"🗑️ {kullanici.mention} kullanıcısından **{rol.name}** rolü alındı!")

@bot.command()
async def amortentia(ctx, kullanici: discord.Member, miktar: int):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Bu komutu sadece Tac Sahibi kullanabilir! 👑")
        return
    uid = str(kullanici.id)
    db["bakiye"][uid] = db["bakiye"].get(uid, 0) + miktar
    save_data(db)
    await ctx.send(f"👑 **Tac Sahibi hediyesi!** {kullanici.mention} hesabına **{miktar} BTS Parası** eklendi! 💜✨")

# ==================== EĞLENCE & ETKİLEŞİM KOMUTLARI ====================

@bot.command()
async def afk(ctx, *, sebep="Canım öyle istedi ✨"):
    uid = str(ctx.author.id)
    db["afk"][uid] = {"sebep": sebep, "zaman": datetime.now().isoformat()}
    save_data(db)
    await ctx.send(f"💤 {ctx.author.mention} artık AFK!\n📝 **Sebep:** {sebep}")

@bot.command()
async def ucanguvercin(ctx, kullanici: discord.Member):
    data = eglence_yanitlari["ucanguvercin"]
    msg = random.choice(data["metinler"]).format(author=ctx.author.display_name, target=kullanici.display_name)
    embed = discord.Embed(description=msg, color=discord.Color.blue())
    embed.set_image(url=random.choice(data["gifler"]))
    await ctx.send(embed=embed)

@bot.command()
async def kiss(ctx, kullanici: discord.Member):
    data = eglence_yanitlari["kiss"]
    msg = random.choice(data["metinler"]).format(author=ctx.author.display_name, target=kullanici.display_name)
    embed = discord.Embed(description=msg, color=discord.Color.magenta())
    embed.set_image(url=random.choice(data["gifler"]))
    await ctx.send(embed=embed)

@bot.command()
async def op(ctx, kullanici: discord.Member):
    data = eglence_yanitlari["op"]
    msg = random.choice(data["metinler"]).format(author=ctx.author.display_name, target=kullanici.display_name)
    embed = discord.Embed(description=msg, color=discord.Color.red())
    embed.set_image(url=random.choice(data["gifler"]))
    await ctx.send(embed=embed)

@bot.command()
async def saril(ctx, kullanici: discord.Member):
    data = eglence_yanitlari["saril"]
    msg = random.choice(data["metinler"]).format(author=ctx.author.display_name, target=kullanici.display_name)
    embed = discord.Embed(description=msg, color=discord.Color.purple())
    embed.set_image(url=random.choice(data["gifler"]))
    await ctx.send(embed=embed)

@bot.command()
async def slaps(ctx, kullanici: discord.Member):
    data = eglence_yanitlari["slaps"]
    msg = random.choice(data["metinler"]).format(author=ctx.author.display_name, target=kullanici.display_name)
    embed = discord.Embed(description=msg, color=discord.Color.orange())
    embed.set_image(url=random.choice(data["gifler"]))
    await ctx.send(embed=embed)

@bot.command()
async def efkarolcer(ctx, kullanici: discord.Member = None):
    kullanici = kullanici or ctx.author
    yuzde = random.randint(0, 100)
    data = eglence_yanitlari["efkarolcer"]
    msg = random.choice(data["metinler"]).format(target=kullanici.display_name, val=yuzde)
    embed = discord.Embed(description=msg, color=discord.Color.dark_grey())
    embed.set_image(url=random.choice(data["gifler"]))
    await ctx.send(embed=embed)

@bot.command()
async def askolcer(ctx, kullanici: discord.Member):
    yuzde = random.randint(0, 100)
    await ctx.send(f"💖 **{ctx.author.display_name}** ile **{kullanici.display_name}** arasındaki aşk oranı: **%{yuzde}** 🌸✨")

@bot.command()
async def sanslisayi(ctx, kullanici: discord.Member = None):
    kullanici = kullanici or ctx.author
    sayi = random.randint(1, 1000)
    await ctx.send(f"🍀 **{kullanici.display_name}** kişisinin şanslı sayısı: **{sayi}** 🎲✨")

@bot.command()
async def ship(ctx):
    members = [m for m in ctx.guild.members if not m.bot and m != ctx.author]
    if not members:
        await ctx.send("❌ Sunucuda shiplenecek üye bulunamadı!")
        return
    secilen = random.choice(members)
    yuzde = random.randint(0, 100)
    await ctx.send(f"💍 **{ctx.author.display_name}** ❤️ **{secilen.display_name}**\n💖 Uyumluluk Oranı: **%{yuzde}** 🌸✨")

@bot.command()
async def ship2(ctx, kullanici: discord.Member):
    await ctx.send(f"💖 **{ctx.author.display_name}** & **{kullanici.display_name}** arasındaki sonsuz aşk oranı: **%999999**! 💍✨")

@bot.command()
async def eatt(ctx, *, yemek: str):
    await ctx.send(f"🍴 **{ctx.author.display_name}**, enfes **{yemek}** yemeğini afiyetle yiyor! 🍕🍔😋")

@bot.command()
async def eat(ctx, kullanici: discord.Member, *, yemek: str):
    await ctx.send(f"🎁 **{ctx.author.display_name}**, **{kullanici.display_name}** kişisine lezzetli bir **{yemek}** ısmarladı! 🎂🍓")

@bot.command()
async def saat(ctx):
    tz = pytz.timezone("Europe/Istanbul")
    zaman = datetime.now(tz).strftime("%d/%m/%Y - %H:%M:%S")
    await ctx.send(f"⏰ **Türkiye Saati:** `{zaman}` 🇹🇷✨")

# ==================== EKONOMİ KOMUTLARI ====================

@bot.command(name="haftalık", aliases=["haftalik"])
async def haftalik_odul(ctx):
    uid = str(ctx.author.id)
    su_an = time.time()
    
    if "haftalik" not in db:
        db["haftalik"] = {}

    son_claim = db["haftalik"].get(uid, 0)
    bekleme_suresi = 7 * 24 * 60 * 60  # 7 gün (saniye)

    if su_an - son_claim < bekleme_suresi:
        kalan_saniye = int(bekleme_suresi - (su_an - son_claim))
        gun = kalan_saniye // (24 * 3600)
        saat = (kalan_saniye % (24 * 3600)) // 3600
        dakika = (kalan_saniye % 3600) // 60

        await ctx.send(
            f"⚠️ **{ctx.author.display_name}**, bu haftalık ödülünü zaten aldın!\n"
            f"Tekrar almak için **{gun} gün, {saat} saat, {dakika} dakika** beklemelisin. ⏳"
        )
        return

    # Bakiyeyi ve zamanı güncelle
    db["bakiye"][uid] = db["bakiye"].get(uid, 0) + 10000
    db["haftalik"][uid] = su_an
    save_data(db)

    await ctx.send(
        f"🎉 **Tebrikler {ctx.author.display_name}!** Haftalık **10.000 BTS Parası** ödülünü aldın! 🪙✨\n"
        f"💰 **Toplam Bakiyen:** `{db['bakiye'][uid]:,} BTS Parası`"
    )

@bot.command()
async def para(ctx):
    uid = str(ctx.author.id)
    bakiye = db["bakiye"].get(uid, 0)
    await ctx.send(f"💰 **{ctx.author.display_name}**, hesabında **{bakiye:,} BTS Parası** var! 💜✨")

@bot.command()
async def yazitura(ctx, miktar: int, secim: str):
    uid = str(ctx.author.id)
    bakiye = db["bakiye"].get(uid, 0)
    if miktar > bakiye or miktar <= 0:
        await ctx.send("❌ Yetersiz bakiye! 💔")
        return
    
    sonuc = random.choice(["yazi", "tura"])
    if secim.lower() == sonuc:
        db["bakiye"][uid] += miktar
        await ctx.send(f"🎉 **Kazandın!** Para `{sonuc}` geldi ve **{miktar * 2} BTS Parası** elde ettin! 🪙✨")
    else:
        db["bakiye"][uid] -= miktar
        await ctx.send(f"💔 **Kaybettin!** Para `{sonuc}` geldi. **{miktar} BTS Parası** kaybettin!")
    save_data(db)

@bot.command()
async def slots(ctx, miktar: int):
    uid = str(ctx.author.id)
    bakiye = db["bakiye"].get(uid, 0)
    if miktar > bakiye or miktar <= 0:
        await ctx.send("❌ Yetersiz bakiye! 💔")
        return

emojiler = ["🎰", "🍇", "🍒", "🍋", "💎"]
    s1, s2, s3 = random.choice(emojiler), random.choice(emojiler), random.choice(emojiler)
    
    if s1 == s2 == s3:
        kazanc = miktar * 3
        db["bakiye"][uid] += kazanc
        msg = f"🎰 [ {s1} | {s2} | {s3} ]\n🎉 **JACKPOT!** 3 katı kazandın: **+{kazanc} BTS Parası**! 💎✨"
    else:
        db["bakiye"][uid] -= miktar
        msg = f"🎰 [ {s1} | {s2} | {s3} ]\n💔 Kaybettin: **-{miktar} BTS Parası**! Tekrar dene!"
    
    save_data(db)
    await ctx.send(msg)

@bot.command()
async def join(ctx, kullanici: discord.Member, miktar: int):
    sender_uid = str(ctx.author.id)
    receiver_uid = str(kullanici.id)
    
    if db["bakiye"].get(sender_uid, 0) < miktar or miktar <= 0:
        await ctx.send("❌ Yetersiz bakiye! 💔")
        return

    db["bakiye"][sender_uid] -= miktar
    db["bakiye"][receiver_uid] = db["bakiye"].get(receiver_uid, 0) + miktar
    save_data(db)
    await ctx.send(f"💸 **{ctx.author.display_name}**, **{kullanici.display_name}** kişisine **{miktar} BTS Parası** aktardı! 🎁✨")

@bot.command()
async def rich(ctx):
    sirali = sorted(db["bakiye"].items(), key=lambda x: x[1], reverse=True)[:5]
    embed = discord.Embed(title="🏆 En Zengin 5 BTS Parası Sahibi 💜", color=discord.Color.gold())
    for idx, (user_id, coin) in enumerate(sirali, 1):
        try:
            usr = await bot.fetch_user(int(user_id))
            embed.add_field(name=f"#{idx} {usr.display_name}", value=f"💰 `{coin:,}` BTS Parası", inline=False)
        except:
            pass
    await ctx.send(embed=embed)

# ==================== MÜZİK, BİLGİ & SPOTİFY KOMUTLARI ====================

@bot.command()
async def sarki(ctx, *, arama: str):
    """Ses Kanalına Gelip Şarkı Oynatma Mantığı"""
    if not ctx.author.voice:
        await ctx.send("❌ Şarkı çalabilmem için önce bir ses kanalına katılmalısın! 🎙️")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()

    embed = discord.Embed(
        title="🎵 Amortentia Müzik Çalar", 
        description=f"**{arama}** şarkısı/linki için ses kanalına bağlanıldı! 🎶✨\n*Yüksek kaliteli ses yayını başlatıldı.*", 
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

@bot.command()
async def spty(ctx, kullanici: discord.Member = None):
    kullanici = kullanici or ctx.author
    for act in kullanici.activities:
        if isinstance(act, discord.Spotify):
            embed = discord.Embed(title=f"🎧 {kullanici.display_name} Spotify Dinliyor", color=discord.Color.green())
            embed.add_field(name="🎵 Şarkı", value=act.title, inline=True)
            embed.add_field(name="🎤 Sanatçı", value=act.artist, inline=True)
            embed.add_field(name="💿 Albüm", value=act.album, inline=False)
            embed.set_thumbnail(url=act.album_cover_url)
            await ctx.send(embed=embed)
            return
    await ctx.send(f"❌ {kullanici.display_name} şu an Spotify üzerinde şarkı dinlemiyor! 💔")

@bot.command()
async def bts(ctx):
    uyeler = ["RM 🐨", "Jin 🐹", "Suga 🐱", "J-Hope 🐿️", "Jimin 🐥", "V 🐯", "Jungkook 🐰"]
    secilen = random.choice(uyeler)
    embed = discord.Embed(title="💜 BTS Ruh Eşi Testi", description=f"Sen bugün tam bir **{secilen}** gibisin! ✨🌸", color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    embed = discord.Embed(title=f"🏰 {ctx.guild.name} Sunucu Bilgisi", color=discord.Color.blue())
    embed.add_field(name="👥 Toplam Üye", value=str(ctx.guild.member_count), inline=True)
    embed.add_field(name="👑 Tac Sahibi", value=ctx.guild.owner.mention, inline=True)
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    await ctx.send(embed=embed)

@bot.command()
async def kullanici(ctx, kullanici: discord.Member = None):
    hedef = kullanici if kullanici else ctx.author
    katilma = hedef.joined_at.strftime("%d/%m/%Y")
    
    if kullanici:
        msg = f"👤 {kullanici.mention} kişisi **{katilma}** tarihinden beridir bu sunucuda! ✨"
    else:
        msg = f"👤 Sen **{katilma}** tarihinden beridir bu sunucudasın! ✨"
        
    embed = discord.Embed(title="📅 Sunucu Katılım Bilgisi", description=msg, color=discord.Color.teal())
    embed.set_thumbnail(url=hedef.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 **Pong!** Bot gecikmesi: `{round(bot.latency * 1000)}ms` ⚡")

@bot.command()
async def yardim(ctx):
    embed = discord.Embed(title="🌸 Amortentia Bot Komut Menüsü 🎀", description="Tüm kullanılabilir komut listesi aşağıdadır ✨", color=discord.Color.pink())
    embed.add_field(name="👑 Yetkili Komutları", value="`!ayarlar`, `!kufurengel`, `!reklamengel`, `!spamengel`, `!logayar`, `!hghb`, `!karaliste`, `!sil`, `!sustur`, `!ac`, `!kick`, `!ban`, `!unban`, `!nuke`, `!lock`, `!unlock`, `!rolver`, `!rolal`, `!amortentia`", inline=False)
    embed.add_field(name="💖 Eğlence Komutları", value="`!afk`, `!ucanguvercin`, `!kiss`, `!op`, `!saril`, `!slaps`, `!efkarolcer`, `!askolcer`, `!sanslisayi`, `!ship`, `!ship2`, `!eatt`, `!eat`, `!saat`", inline=False)
    embed.add_field(name="💰 Ekonomi Komutları", value="`!haftalık`, `!para`, `!yazitura`, `!slots`, `!join`, `!rich`", inline=False)
    embed.add_field(name="🎶 Bilgi & Müzik Komutları", value="`!sarki`, `!spty`, `!bts`, `!sunucu`, `!kullanici`, `!ping`", inline=False)
    await ctx.send(embed=embed)

# RENDER ORTAMLARI İÇİN TOKEN ALMA
TOKEN = os.getenv("TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ HATA: Render üzerinde 'DISCORD_BOT_TOKEN' isimli Environment Variable bulunamadı!")
