import discord
from discord.ext import commands
import random
import asyncio
from datetime import timedelta
import os
from threading import Thread
from flask import Flask
import string

# --- 🌐 7/24 AKTİF KALMA (WEB SERVER) SİSTEMİ ---
app = Flask('')

@app.route('/')
def home():
    return "Bot 7/24 Aktif!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ------------------------------------------------

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

kara_liste = ["salak", "aptal", "gerizekali"] 

kufur_filtresi_aktif = False
reklam_filtresi_aktif = False
spam_filtresi_aktif = False
hosgeldin_kanali_id = None
log_kanali_id = None
kullanici_mesajlari = {}

# --- 💰 EKONOMİ & MIX SORU SİSTEMİ VERİLERİ ---
bts_paralari = {}  # {kullanici_id: miktar}
aktif_soru_cevap = None  # {"soru": "...", "cevap": "..."}
aktif_soru_kanali = None

# Karışık Soru Havuzu (BTS + Kolay Matematik)
soru_havuzu = [
    # BTS Soruları
    {"soru": "BTS hangi yılda çıkış yapmıştır? (Sadece yıl girin)", "cevap": "2013"},
    {"soru": "BTS grubunun toplam kaç üyesi vardır? (Sadece sayı girin)", "cevap": "7"},
    {"soru": "BTS'in en büyük (yaşça) üyesi kimdir?", "cevap": "jin"},
    {"soru": "BTS'in lideri kimdir? (Sahne adı)", "cevap": "rm"},
    {"soru": "BTS hayran kitlesinin adı nedir?", "cevap": "army"},
    {"soru": "Grubun en küçük üyesi (maknae) kimdir?", "cevap": "jungkook"},
    
    # Kolay Matematik Soruları
    {"soru": "Hızlıca Çöz! ⚡\n**15 + 27 kaçtır?**", "cevap": "42"},
    {"soru": "Hızlıca Çöz! ⚡\n**8 x 7 kaçtır?**", "cevap": "56"},
    {"soru": "Hızlıca Çöz! ⚡\n**120 / 4 kaçtır?**", "cevap": "30"},
    {"soru": "Hızlıca Çöz! ⚡\n**95 - 36 kaçtır?**", "cevap": "59"},
    {"soru": "Hızlıca Çöz! ⚡\n**6 x 6 + 4 kaçtır?**", "cevap": "40"},
    {"soru": "Hızlıca Çöz! ⚡\n**50'nin yarısı kaçtır?**", "cevap": "25"}
]

# İltifat Havuzu
iltifatlar = [
    "Ya senin bu tatlılığın ne olacak? Sunucuya neşe saçıyorsun resmen! ✨",
    "Mesajını gördüm de, parmaklarından bal damlıyor sanki... 🥰",
    "Sen yazınca bu kanal bir başka güzel oluyor, hep yaz sen! 🌸",
    "Kalbinin güzelliği attığın mesajlara yansımış resmen, harikasın! 💜",
    "Bu sunucunun en parlak yıldızı kesinlikle sensin! ⭐"
]

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} olarak başarıyla giriş yaptı!')

# --- 📥 HOŞ GELDİN & 📤 GÜLE GÜLE SİSTEMİ ---
@bot.event
async def on_member_join(member):
    global hosgeldin_kanali_id
    if hosgeldin_kanali_id:
        kanal = bot.get_channel(hosgeldin_kanali_id)
        if kanal:
            embed = discord.Embed(
                title="🌸 Aramıza Yeni Biri Katıldı!", 
                description=f"Hoş geldin {member.mention}! Sunucumuza neşe getirdin. ✨\nSeninle birlikte **{member.guild.member_count}** kişi olduk! 🎉", 
                color=discord.Color.from_rgb(255, 182, 193)
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await kanal.send(embed=embed)

@bot.event
async def on_member_remove(member):
    global hosgeldin_kanali_id
    if hosgeldin_kanali_id:
        kanal = bot.get_channel(hosgeldin_kanali_id)
        if kanal:
            embed = discord.Embed(
                title="💔 Aramızdan Biri Ayrıldı...", 
                description=f"Güle güle {member.name}... Gidişin bizi üzdü. 😔\nŞu an sunucuda **{member.guild.member_count}** kişi kaldık.", 
                color=discord.Color.dark_gray()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await kanal.send(embed=embed)

# --- 🛡️ MESAJ KONTROLLERİ (KORUMA, OYUN VE İLTİFAT SİSTEMLERİ) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    global kufur_filtresi_aktif, reklam_filtresi_aktif, spam_filtresi_aktif, kara_liste, aktif_soru_cevap, aktif_soru_kanali
    mesaj_silindi = False

    # 💬 SA-AS SİSTEMİ
    if message.content.lower() == "sa":
        await message.channel.send(f"Aleyküm Selam, hoş geldin {message.author.mention}! 😊")
        return

    # 👑 OYUN CEVAP KONTROLÜ
    if aktif_soru_cevap and message.channel.id == aktif_soru_kanali:
        if message.content.lower().strip() == aktif_soru_cevap["cevap"]:
            u_id = message.author.id
            bts_paralari[u_id] = bts_paralari.get(u_id, 0) + 100
            await message.channel.send(f"🎉 Tebrikler {message.author.mention}! Doğru cevabı verdin ve **100 BTS Parası** kazandın! 💰")
            aktif_soru_cevap = None
            aktif_soru_kanali = None
            return

    # Spam Filtresi
    if spam_filtresi_aktif:
        ust_id = message.author.id
        simdi = message.created_at.timestamp()
        if ust_id not in kullanici_mesajlari:
            kullanici_mesajlari[ust_id] = []
        kullanici_mesajlari[ust_id].append(simdi)
        kullanici_mesajlari[ust_id] = [t for t in kullanici_mesajlari[ust_id] if simdi - t < 3]
        if len(kullanici_mesajlari[ust_id]) > 4:
            await message.delete()
            mesaj_silindi = True
            await message.channel.send(f"⚠️ {message.author.mention}, lütfen bu kadar hızlı yazma!", delete_after=3)

    # Reklam Filtresi
    if reklam_filtresi_aktif and not mesaj_silindi:
        if "http://" in message.content.lower() or "https://" in message.content.lower() or "discord.gg" in message.content.lower():
            await message.delete()
            mesaj_silindi = True
            await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda link/reklam paylaşamazsın!", delete_after=5)

    # Gelişmiş Küfür Filtresi (Nokta atışı kelime kontrolü)
    if kufur_filtresi_aktif and not mesaj_silindi:
        temiz_mesaj = message.content.lower().translate(str.maketrans('', '', string.punctuation))
        kelimeler = temiz_mesaj.split()
        
        for kelime in kelimeler:
            if kelime in kara_liste:
                await message.delete()
                mesaj_silindi = True
                await message.channel.send(f"⚠️ {message.author.mention}, sunucuda yasaklı kelime kullanmak yasaktır!", delete_after=5)
                break

    # --- 🎭 RASTGELE ETKİNLİKLER ---
    if not mesaj_silindi and not message.content.startswith('!'):
        sans = random.randint(1, 100)
        
        # %10 ihtimalle rastgele soru sorma (BTS veya Matematik karışık gelir)
        if sans <= 10 and not aktif_soru_cevap:
            aktif_soru_cevap = random.choice(soru_havuzu)
            aktif_soru_kanali = message.channel.id
            embed = discord.Embed(
                title="🧠 ÖDÜLLÜ BİLGİ YARIŞMASI!", 
                description=f"{aktif_soru_cevap['soru']}\n\n*İlk doğru cevabı veren 100 BTS Parası kapar!*", 
                color=discord.Color.purple()
            )
            await message.channel.send(embed=embed)
            
        # %5 ihtimalle üyeye yürüme/iltifat etme sistemi
        elif sans > 10 and sans <= 15:
            secilen_iltifat = random.choice(iltifatlar)
            await message.channel.send(f"{message.author.mention} {secilen_iltifat}")

    await bot.process_commands(message)

# --- 🗑️ LOG SİSTEMİ ---
@bot.event
async def on_message_delete(message):
    global log_kanali_id
    if log_kanali_id and not message.author.bot:
        kanal = bot.get_channel(log_kanali_id)
        if kanal:
            embed = discord.Embed(title="🗑️ Bir Mesaj Silindi", color=discord.Color.red())
            embed.add_field(name="Mesaj Sahibi", value=message.author.mention, inline=True)
            embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
            embed.add_field(name="Silinen İçerik", value=message.content if message.content else "*İçerik yok veya görsel*", inline=False)
            await kanal.send(embed=embed)

# --- 💰 EKONOMİ KOMUTLARI ---
@bot.command()
async def para(ctx, member: discord.Member = None):
    if member is None: member = ctx.author
    miktar = bts_paralari.get(member.id, 0)
    await ctx.send(f"💰 {member.mention} kullanıcısının bakiyesi: **{miktar} BTS Parası**")

@bot.command()
async def slots(ctx, miktar: int):
    u_id = ctx.author.id
    mevcut_para = bts_paralari.get(u_id, 0)
    
    if miktar <= 0:
        await ctx.send("❌ Lütfen geçerli bir miktar girin!")
        return
    if mevcut_para < miktar:
        await ctx.send(f"❌ Yetersiz bakiye! Şu an sadece **{mevcut_para}** BTS Parasına sahipsin.")
        return
        
    slotlar = ["🍒", "🍇", "🍊", "💎", "👑"]
    sonuc = [random.choice(slotlar) for _ in range(3)]
    
    embed = discord.Embed(title="🎰 BTS SLOT MACHINE 🎰", color=discord.Color.orange())
    embed.description = f"**[ {sonuc[0]} | {sonuc[1]} | {sonuc[2]} ]**\n\n"
    
    if sonuc[0] == sonuc[1] == sonuc[2]:
        kazanc = miktar * 3
        bts_paralari[u_id] += kazanc
        embed.description += f"🎉 **MÜKEMMEL KAZANÇ!** Hepsi aynı geldi! \n**+{kazanc} BTS Parası** kazandın!"
        embed.color = discord.Color.green()
    elif sonuc[0] == sonuc[1] or sonuc[1] == sonuc[2] or sonuc[0] == sonuc[2]:
        kazanc = miktar * 1
        bts_paralari[u_id] += kazanc
        embed.description += f"✨ **GÜZEL KAZANÇ!** İki adet eşleşme yakaladın! \n**+{kazanc} BTS Parası** kazandın!"
        embed.color = discord.Color.green()
    else:
        bts_paralari[u_id] -= miktar
        embed.description += f"😔 **KAYBETTİN!** Hiçbiri eşleşmedi. \n**-{miktar} BTS Parası** hesabından düştü."
        embed.color = discord.Color.red()
        
    await ctx.send(embed=embed)

# --- ⚙️ AYAR VE KORUMA KOMUTLARI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def ayarlar(ctx):
    embed = discord.Embed(title="⚙️ Sunucu Koruma Paneli Ayarları", color=discord.Color.gold())
    embed.add_field(name="Küfür Filtresi", value="🟢 Aktif" if kufur_filtresi_aktif else "🔴 Kapalı", inline=True)
    embed.add_field(name="Reklam Filtresi", value="🟢 Aktif" if reklam_filtresi_aktif else "🔴 Kapalı", inline=True)
    embed.add_field(name="Spam Filtresi", value="🟢 Aktif" if spam_filtresi_aktif else "🔴 Kapalı", inline=True)
    embed.add_field(name="Kara Listedeki Kelimeler", value=", ".join(kara_liste) if kara_liste else "Boş", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def kufurengel(ctx):
    global kufur_filtresi_aktif
    kufur_filtresi_aktif = not kufur_filtresi_aktif
    await ctx.send(f"🛡️ Küfür filtresi: **{'Açıldı 🟢' if kufur_filtresi_aktif else 'Kapatıldı 🔴'}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def reklamengel(ctx):
    global reklam_filtresi_aktif
    reklam_filtresi_aktif = not reklam_filtresi_aktif
    await ctx.send(f"🔗 Reklam filtresi: **{'Açıldı 🟢' if reklam_filtresi_aktif else 'Kapatıldı 🔴'}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def spamengel(ctx):
    global spam_filtresi_aktif
    spam_filtresi_aktif = not spam_filtresi_aktif
    await ctx.send(f"⚡ Spam filtresi: **{'Açıldı 🟢' if spam_filtresi_aktif else 'Kapatıldı 🔴'}**")

@bot.command(name="logayarla")
@commands.has_permissions(administrator=True)
async def log_ayarla(ctx, kanal: discord.TextChannel):
    global log_kanali_id
    log_kanali_id = kanal.id
    await ctx.send(f"✅ Silinen mesaj logları artık {kanal.mention} kanalına gönderilecek.")

@bot.command(name="hosgeldin-ve-baybay-ayarla")
@commands.has_permissions(administrator=True)
async def hosgeldin_ve_baybay_ayarla(ctx, kanal: discord.TextChannel):
    global hosgeldin_kanali_id
    hosgeldin_kanali_id = kanal.id
    await ctx.send(f"✅ Hoş geldin ve Güle güle mesajları başarıyla {kanal.mention} olarak ayarlandı!")

@bot.group(invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def karaliste(ctx):
    await ctx.send(f"📋 **Mevcut Kara Liste:** {', '.join(kara_liste)}")

@karaliste.command()
async def ekle(ctx, kelime: str):
    global kara_liste
    if kelime.lower() not in kara_liste:
        kara_liste.append(kelime.lower())
        await ctx.send(f"✅ `{kelime}` kelimesi kara listeye eklendi.")

@karaliste.command()
async def cikar(ctx, kelime: str):
    global kara_liste
    if kelime.lower() in kara_liste:
        kara_liste.remove(kelime.lower())
        await ctx.send(f"🗑️ `{kelime}` kelimesi kara listeden çıkarıldı.")

# --- 🔨 GELİŞMİŞ MODERASYON KOMUTLARI ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int):
    if miktar > 100: miktar = 100
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f"🗑️ {miktar} adet mesaj başarıyla temizlendi.", delete_after=4)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def sustur(ctx, member: discord.Member, sure: str):
    try:
        zaman = int(sure[:-1])
        birim = sure[-1]
        if birim == 'm': sure_delta = timedelta(minutes=zaman)
        elif birim == 'h': sure_delta = timedelta(hours=zaman)
        elif birim == 'd': sure_delta = timedelta(days=zaman)
        else: raise ValueError
        await member.timeout(sure_delta, reason=f"{ctx.author} tarafından susturuldu.")
        await ctx.send(f"🔇 {member.mention} kullanıcısı {sure} boyunca susturuldu.")
    except:
        await ctx.send("❌ Hatalı süre formatı! Örnek kullanım: `!sustur @üye 15m` (m: dakika, h: saat, d: gün)")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def ac(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 {member.mention} kullanıcısının susturulması kaldırıldı.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def nuke(ctx):
    kanal_pozisyonu = ctx.channel.position
    yeni_kanal = await ctx.channel.clone(reason="Nuke işlemi")
    await ctx.channel.delete()
    await yeni_kanal.edit(position=kanal_pozisyonu)
    await yeni_kanal.send("💥 Kanal başarıyla sıfırlandı!")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ {member.mention} kişisine {role.name} rolü verildi.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"🗑️ {member.mention} kişisinden {role.name} rolü geri alındı.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🚫 {member.name} sunucudan kalıcı olarak yasaklandı. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} sunucudan atıldı. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal yeni mesaj gönderimine kapatıldı (Kilitlendi).")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.send("🔓 Kanalın kilidi açıldı, herkes yazabilir.")

# --- 🎮 BİLGİ VE EĞLENCE KOMUTLARI ---
@bot.command()
async def kullanici(ctx, member: discord.Member = None):
    if member is None: member = ctx.author
    embed = discord.Embed(title=f"👤 {member.name} Bilgileri", color=discord.Color.purple())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Hesap Açılış Tarihi", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Sunucuya Giriş Tarihi", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"🏰 {g.name} Sunucu Özeti", color=discord.Color.blue())
    if g.icon: embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="Üye Sayısı", value=str(g.member_count), inline=True)
    embed.add_field(name="Kanal Sayısı", value=str(len(g.channels)), inline=True)
    embed.add_field(name="Rol Sayısı", value=str(len(g.roles)), inline=True)
    embed.add_field(name="Sunucu Kurucusu", value=str(g.owner), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def askolcer(ctx, member: discord.Member):
    orand = random.randint(0, 100)
    b = "❤️" * (orand // 10) + "🖤" * (10 - (orand // 10))
    await ctx.send(f"💘 {ctx.author.mention} x {member.mention}\n**Aşk Oranı:** %{orand}\n{b}")

@bot.command()
async def efkarolcer(ctx):
    await ctx.send(f"🚬 {ctx.author.mention} Efkar Oranın: %{random.randint(0,100)}")

@bot.command()
async def sanslisayi(ctx):
    await ctx.send(f"🎲 {ctx.author.mention}, bugünkü şanslı sayın: **{random.randint(1,100)}**")

# Web sunucusunu başlat ve botu çalıştır
keep_alive()
token = os.environ.get('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("HATA: DISCORD_TOKEN bulunamadı! Lütfen Çevre Değişkenlerini kontrol edin.")
    import discord
from discord.ext import commands
import random
import asyncio
from datetime import timedelta
import os
from threading import Thread
from flask import Flask
import string

# --- 🌐 7/24 AKTİF KALMA (WEB SERVER) SİSTEMİ ---
app = Flask('')

@app.route('/')
def home():
    return "Bot 7/24 Aktif!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ------------------------------------------------

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

kara_liste = ["salak", "aptal", ""] 

kufur_filtresi_aktif = False
reklam_filtresi_aktif = False
spam_filtresi_aktif = False
hosgeldin_kanali_id = None
log_kanali_id = None
kullanici_mesajlari = {}

# --- 💰 EKONOMİ & MIX SORU SİSTEMİ VERİLERİ ---
bts_paralari = {}  # {kullanici_id: miktar}
aktif_soru_cevap = None  # {"soru": "...", "cevap": "..."}
aktif_soru_kanali = None

# Karışık Soru Havuzu (BTS + Kolay Matematik)
soru_havuzu = [
    # BTS Soruları
    {"soru": "BTS hangi yılda çıkış yapmıştır? (Sadece yıl girin)", "cevap": "2013"},
    {"soru": "BTS grubunun toplam kaç üyesi vardır? (Sadece sayı girin)", "cevap": "7"},
    {"soru": "BTS'in en büyük (yaşça) üyesi kimdir?", "cevap": "jin"},
    {"soru": "BTS'in lideri kimdir? (Sahne adı)", "cevap": "rm"},
    {"soru": "BTS hayran kitlesinin adı nedir?", "cevap": "army"},
    {"soru": "Grubun en küçük üyesi (maknae) kimdir?", "cevap": "jungkook"},
    
    # Kolay Matematik Soruları
    {"soru": "Hızlıca Çöz! ⚡\n**15 + 27 kaçtır?**", "cevap": "42"},
    {"soru": "Hızlıca Çöz! ⚡\n**8 x 7 kaçtır?**", "cevap": "56"},
    {"soru": "Hızlıca Çöz! ⚡\n**120 / 4 kaçtır?**", "cevap": "30"},
    {"soru": "Hızlıca Çöz! ⚡\n**95 - 36 kaçtır?**", "cevap": "59"},
    {"soru": "Hızlıca Çöz! ⚡\n**6 x 6 + 4 kaçtır?**", "cevap": "40"},
    {"soru": "Hızlıca Çöz! ⚡\n**50'nin yarısı kaçtır?**", "cevap": "25"}
]

# İltifat Havuzu
iltifatlar = [
    "Ya senin bu tatlılığın ne olacak? Sunucuya neşe saçıyorsun resmen! ✨",
    "Mesajını gördüm de, parmaklarından bal damlıyor sanki... 🥰",
    "Sen yazınca bu kanal bir başka güzel oluyor, hep yaz sen! 🌸",
    "Kalbinin güzelliği attığın mesajlara yansımış resmen, harikasın! 💜",
    "Bu sunucunun en parlak yıldızı kesinlikle sensin! ⭐"
]

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} olarak başarıyla giriş yaptı!')

# --- 📥 HOŞ GELDİN & 📤 GÜLE GÜLE SİSTEMİ ---
@bot.event
async def on_member_join(member):
    global hosgeldin_kanali_id
    if hosgeldin_kanali_id:
        kanal = bot.get_channel(hosgeldin_kanali_id)
        if kanal:
            embed = discord.Embed(
                title="🌸 Aramıza Yeni Biri Katıldı!", 
                description=f"Hoş geldin {member.mention}! Sunucumuza neşe getirdin. ✨\nSeninle birlikte **{member.guild.member_count}** kişi olduk! 🎉", 
                color=discord.Color.from_rgb(255, 182, 193)
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await kanal.send(embed=embed)

@bot.event
async def on_member_remove(member):
    global hosgeldin_kanali_id
    if hosgeldin_kanali_id:
        kanal = bot.get_channel(hosgeldin_kanali_id)
        if kanal:
            embed = discord.Embed(
                title="💔 Aramızdan Biri Ayrıldı...", 
                description=f"Güle güle {member.name}... Gidişin bizi üzdü. 😔\nŞu an sunucuda **{member.guild.member_count}** kişi kaldık.", 
                color=discord.Color.dark_gray()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            await kanal.send(embed=embed)

# --- 🛡️ MESAJ KONTROLLERİ (KORUMA, OYUN VE İLTİFAT SİSTEMLERİ) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    global kufur_filtresi_aktif, reklam_filtresi_aktif, spam_filtresi_aktif, kara_liste, aktif_soru_cevap, aktif_soru_kanali
    mesaj_silindi = False

    # 💬 SA-AS SİSTEMİ
    if message.content.lower() == "sa":
        await message.channel.send(f"Aleyküm Selam, hoş geldin {message.author.mention}! 😊")
        return

    # 👑 OYUN CEVAP KONTROLÜ
    if aktif_soru_cevap and message.channel.id == aktif_soru_kanali:
        if message.content.lower().strip() == aktif_soru_cevap["cevap"]:
            u_id = message.author.id
            bts_paralari[u_id] = bts_paralari.get(u_id, 0) + 100
            await message.channel.send(f"🎉 Tebrikler {message.author.mention}! Doğru cevabı verdin ve **100 BTS Parası** kazandın! 💰")
            aktif_soru_cevap = None
            aktif_soru_kanali = None
            return

    # Spam Filtresi
    if spam_filtresi_aktif:
        ust_id = message.author.id
        simdi = message.created_at.timestamp()
        if ust_id not in kullanici_mesajlari:
            kullanici_mesajlari[ust_id] = []
        kullanici_mesajlari[ust_id].append(simdi)
        kullanici_mesajlari[ust_id] = [t for t in kullanici_mesajlari[ust_id] if simdi - t < 3]
        if len(kullanici_mesajlari[ust_id]) > 4:
            await message.delete()
            mesaj_silindi = True
            await message.channel.send(f"⚠️ {message.author.mention}, lütfen bu kadar hızlı yazma!", delete_after=3)

    # Reklam Filtresi
    if reklam_filtresi_aktif and not mesaj_silindi:
        if "http://" in message.content.lower() or "https://" in message.content.lower() or "discord.gg" in message.content.lower():
            await message.delete()
            mesaj_silindi = True
            await message.channel.send(f"⚠️ {message.author.mention}, bu sunucuda link/reklam paylaşamazsın!", delete_after=5)

    # Gelişmiş Küfür Filtresi (Nokta atışı kelime kontrolü)
    if kufur_filtresi_aktif and not mesaj_silindi:
        temiz_mesaj = message.content.lower().translate(str.maketrans('', '', string.punctuation))
        kelimeler = temiz_mesaj.split()
        
        for kelime in kelimeler:
            if kelime in kara_liste:
                await message.delete()
                mesaj_silindi = True
                await message.channel.send(f"⚠️ {message.author.mention}, sunucuda yasaklı kelime kullanmak yasaktır!", delete_after=5)
                break

    # --- 🎭 RASTGELE ETKİNLİKLER ---
    if not mesaj_silindi and not message.content.startswith('!'):
        sans = random.randint(1, 100)
        
        # %10 ihtimalle rastgele soru sorma (BTS veya Matematik karışık gelir)
        if sans <= 10 and not aktif_soru_cevap:
            aktif_soru_cevap = random.choice(soru_havuzu)
            aktif_soru_kanali = message.channel.id
            embed = discord.Embed(
                title="🧠 ÖDÜLLÜ BİLGİ YARIŞMASI!", 
                description=f"{aktif_soru_cevap['soru']}\n\n*İlk doğru cevabı veren 100 BTS Parası kapar!*", 
                color=discord.Color.purple()
            )
            await message.channel.send(embed=embed)
            
        # %5 ihtimalle üyeye yürüme/iltifat etme sistemi
        elif sans > 10 and sans <= 15:
            secilen_iltifat = random.choice(iltifatlar)
            await message.channel.send(f"{message.author.mention} {secilen_iltifat}")

    await bot.process_commands(message)

# --- 🗑️ LOG SİSTEMİ ---
@bot.event
async def on_message_delete(message):
    global log_kanali_id
    if log_kanali_id and not message.author.bot:
        kanal = bot.get_channel(log_kanali_id)
        if kanal:
            embed = discord.Embed(title="🗑️ Bir Mesaj Silindi", color=discord.Color.red())
            embed.add_field(name="Mesaj Sahibi", value=message.author.mention, inline=True)
            embed.add_field(name="Kanal", value=message.channel.mention, inline=True)
            embed.add_field(name="Silinen İçerik", value=message.content if message.content else "*İçerik yok veya görsel*", inline=False)
            await kanal.send(embed=embed)

# --- 💰 EKONOMİ KOMUTLARI ---
@bot.command()
async def para(ctx, member: discord.Member = None):
    if member is None: member = ctx.author
    miktar = bts_paralari.get(member.id, 0)
    await ctx.send(f"💰 {member.mention} kullanıcısının bakiyesi: **{miktar} BTS Parası**")

@bot.command()
async def slots(ctx, miktar: int):
    u_id = ctx.author.id
    mevcut_para = bts_paralari.get(u_id, 0)
    
    if miktar <= 0:
        await ctx.send("❌ Lütfen geçerli bir miktar girin!")
        return
    if mevcut_para < miktar:
        await ctx.send(f"❌ Yetersiz bakiye! Şu an sadece **{mevcut_para}** BTS Parasına sahipsin.")
        return
        
    slotlar = ["🍒", "🍇", "🍊", "💎", "👑"]
    sonuc = [random.choice(slotlar) for _ in range(3)]
    
    embed = discord.Embed(title="🎰 BTS SLOT MACHINE 🎰", color=discord.Color.orange())
    embed.description = f"**[ {sonuc[0]} | {sonuc[1]} | {sonuc[2]} ]**\n\n"
    
    if sonuc[0] == sonuc[1] == sonuc[2]:
        kazanc = miktar * 3
        bts_paralari[u_id] += kazanc
        embed.description += f"🎉 **MÜKEMMEL KAZANÇ!** Hepsi aynı geldi! \n**+{kazanc} BTS Parası** kazandın!"
        embed.color = discord.Color.green()
    elif sonuc[0] == sonuc[1] or sonuc[1] == sonuc[2] or sonuc[0] == sonuc[2]:
        kazanc = miktar * 1
        bts_paralari[u_id] += kazanc
        embed.description += f"✨ **GÜZEL KAZANÇ!** İki adet eşleşme yakaladın! \n**+{kazanc} BTS Parası** kazandın!"
        embed.color = discord.Color.green()
    else:
        bts_paralari[u_id] -= miktar
        embed.description += f"😔 **KAYBETTİN!** Hiçbiri eşleşmedi. \n**-{miktar} BTS Parası** hesabından düştü."
        embed.color = discord.Color.red()
        
    await ctx.send(embed=embed)

# --- ⚙️ AYAR VE KORUMA KOMUTLARI ---
@bot.command()
@commands.has_permissions(administrator=True)
async def ayarlar(ctx):
    embed = discord.Embed(title="⚙️ Sunucu Koruma Paneli Ayarları", color=discord.Color.gold())
    embed.add_field(name="Küfür Filtresi", value="🟢 Aktif" if kufur_filtresi_aktif else "🔴 Kapalı", inline=True)
    embed.add_field(name="Reklam Filtresi", value="🟢 Aktif" if reklam_filtresi_aktif else "🔴 Kapalı", inline=True)
    embed.add_field(name="Spam Filtresi", value="🟢 Aktif" if spam_filtresi_aktif else "🔴 Kapalı", inline=True)
    embed.add_field(name="Kara Listedeki Kelimeler", value=", ".join(kara_liste) if kara_liste else "Boş", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def kufurengel(ctx):
    global kufur_filtresi_aktif
    kufur_filtresi_aktif = not kufur_filtresi_aktif
    await ctx.send(f"🛡️ Küfür filtresi: **{'Açıldı 🟢' if kufur_filtresi_aktif else 'Kapatıldı 🔴'}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def reklamengel(ctx):
    global reklam_filtresi_aktif
    reklam_filtresi_aktif = not reklam_filtresi_aktif
    await ctx.send(f"🔗 Reklam filtresi: **{'Açıldı 🟢' if reklam_filtresi_aktif else 'Kapatıldı 🔴'}**")

@bot.command()
@commands.has_permissions(administrator=True)
async def spamengel(ctx):
    global spam_filtresi_aktif
    spam_filtresi_aktif = not spam_filtresi_aktif
    await ctx.send(f"⚡ Spam filtresi: **{'Açıldı 🟢' if spam_filtresi_aktif else 'Kapatıldı 🔴'}**")

@bot.command(name="logayarla")
@commands.has_permissions(administrator=True)
async def log_ayarla(ctx, kanal: discord.TextChannel):
    global log_kanali_id
    log_kanali_id = kanal.id
    await ctx.send(f"✅ Silinen mesaj logları artık {kanal.mention} kanalına gönderilecek.")

@bot.command(name="hosgeldin-ve-baybay-ayarla")
@commands.has_permissions(administrator=True)
async def hosgeldin_ve_baybay_ayarla(ctx, kanal: discord.TextChannel):
    global hosgeldin_kanali_id
    hosgeldin_kanali_id = kanal.id
    await ctx.send(f"✅ Hoş geldin ve Güle güle mesajları başarıyla {kanal.mention} olarak ayarlandı!")

@bot.group(invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def karaliste(ctx):
    await ctx.send(f"📋 **Mevcut Kara Liste:** {', '.join(kara_liste)}")

@karaliste.command()
async def ekle(ctx, kelime: str):
    global kara_liste
    if kelime.lower() not in kara_liste:
        kara_liste.append(kelime.lower())
        await ctx.send(f"✅ `{kelime}` kelimesi kara listeye eklendi.")

@karaliste.command()
async def cikar(ctx, kelime: str):
    global kara_liste
    if kelime.lower() in kara_liste:
        kara_liste.remove(kelime.lower())
        await ctx.send(f"🗑️ `{kelime}` kelimesi kara listeden çıkarıldı.")

# --- 🔨 GELİŞMİŞ MODERASYON KOMUTLARI ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def sil(ctx, miktar: int):
    if miktar > 100: miktar = 100
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f"🗑️ {miktar} adet mesaj başarıyla temizlendi.", delete_after=4)

@bot.command()
@commands.has_permissions(moderate_members=True)
async def sustur(ctx, member: discord.Member, sure: str):
    try:
        zaman = int(sure[:-1])
        birim = sure[-1]
        if birim == 'm': sure_delta = timedelta(minutes=zaman)
        elif birim == 'h': sure_delta = timedelta(hours=zaman)
        elif birim == 'd': sure_delta = timedelta(days=zaman)
        else: raise ValueError
        await member.timeout(sure_delta, reason=f"{ctx.author} tarafından susturuldu.")
        await ctx.send(f"🔇 {member.mention} kullanıcısı {sure} boyunca susturuldu.")
    except:
        await ctx.send("❌ Hatalı süre formatı! Örnek kullanım: `!sustur @üye 15m` (m: dakika, h: saat, d: gün)")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def ac(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 {member.mention} kullanıcısının susturulması kaldırıldı.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def nuke(ctx):
    kanal_pozisyonu = ctx.channel.position
    yeni_kanal = await ctx.channel.clone(reason="Nuke işlemi")
    await ctx.channel.delete()
    await yeni_kanal.edit(position=kanal_pozisyonu)
    await yeni_kanal.send("💥 Kanal başarıyla sıfırlandı!")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolver(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ {member.mention} kişisine {role.name} rolü verildi.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def rolal(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"🗑️ {member.mention} kişisinden {role.name} rolü geri alındı.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🚫 {member.name} sunucudan kalıcı olarak yasaklandı. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} sunucudan atıldı. Sebep: {sebep}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal yeni mesaj gönderimine kapatıldı (Kilitlendi).")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.send("🔓 Kanalın kilidi açıldı, herkes yazabilir.")

# --- 🎮 BİLGİ VE EĞLENCE KOMUTLARI ---
@bot.command()
async def kullanici(ctx, member: discord.Member = None):
    if member is None: member = ctx.author
    embed = discord.Embed(title=f"👤 {member.name} Bilgileri", color=discord.Color.purple())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Hesap Açılış Tarihi", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Sunucuya Giriş Tarihi", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def sunucu(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"🏰 {g.name} Sunucu Özeti", color=discord.Color.blue())
    if g.icon: embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="Üye Sayısı", value=str(g.member_count), inline=True)
    embed.add_field(name="Kanal Sayısı", value=str(len(g.channels)), inline=True)
    embed.add_field(name="Rol Sayısı", value=str(len(g.roles)), inline=True)
    embed.add_field(name="Sunucu Kurucusu", value=str(g.owner), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def askolcer(ctx, member: discord.Member):
    orand = random.randint(0, 100)
    b = "❤️" * (orand // 10) + "🖤" * (10 - (orand // 10))
    await ctx.send(f"💘 {ctx.author.mention} x {member.mention}\n**Aşk Oranı:** %{orand}\n{b}")

@bot.command()
async def efkarolcer(ctx):
    await ctx.send(f"🚬 {ctx.author.mention} Efkar Oranın: %{random.randint(0,100)}")

@bot.command()
async def sanslisayi(ctx):
    await ctx.send(f"🎲 {ctx.author.mention}, bugünkü şanslı sayın: **{random.randint(1,100)}**")

# Web sunucusunu başlat ve botu çalıştır
keep_alive()
token = os.environ.get('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("HATA: DISCORD_TOKEN bulunamadı! Lütfen Çevre Değişkenlerini kontrol edin.")
        
