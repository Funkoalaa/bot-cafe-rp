import discord
from discord.ext import commands
import re
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# ---------------- CONFIG ----------------

ALLOWED_CHANNELS = {"🛎️ᝰᐟ𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒆𝒔"}
ORDERS_CHANNEL_NAME = "🛎️ᝰᐟ𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒆𝒔"

# ---------------- PRIX ----------------

PRICES = {
    "croissant": 1.2,
    "cookie": 2.2,
    "donut": 2.5,
    "cappuccino": 3.5,
    "espresso": 2.0,
    "milkshake": 4.5,
    "bubble_tea": 4.9,
    "pancakes": 3.8
}

# ---------------- MOTS CLÉS ----------------

KEYWORDS = {
    "croissant": ["croissant"],
    "cookie": ["cookie", "cookies"],
    "donut": ["donut", "donuts"],
    "cappuccino": ["cappuccino"],
    "espresso": ["espresso", "expresso"],
    "milkshake": ["milkshake"],
    "bubble_tea": ["bubble tea"],
    "pancakes": ["pancake", "pancakes"]
}

# ---------------- TEXTES RP ----------------

WELCOME_TEXT = (
    "Derrière le comptoir, la barista ajuste son tablier avec douceur.\n"
    "☕ « Bonjour et bienvenue au **Galop Gourmand** ! "
    "Que puis-je vous servir aujourd’hui ? »"
)

PAYMENT_TEXT = (
    "Elle pianote doucement sur la caisse avant de relever les yeux.\n"
    "✨ « Parfait ! Cela vous fera un total de **{total}💰**.\n"
    "Veuillez effectuer le paiement avec DraftBot. »"
)

GOODBYE_TEXT = (
    "La barista vous tend votre commande avec un sourire chaleureux.\n"
    "☕ « Merci pour votre visite au **Galop Gourmand** !\n"
    "Nous vous souhaitons une excellente dégustation. »"
)

# ---------------- IMAGES ----------------

WELCOME_IMAGE = "https://cdn.discordapp.com/attachments/1463232375487070415/1463232376875520053/image.png"
PAYMENT_IMAGE = "https://cdn.discordapp.com/attachments/1463232375487070415/1463232400002777109/image.png"
GOODBYE_IMAGE = "https://cdn.discordapp.com/attachments/1463232375487070415/1463232447041896488/image.png"

# ---------------- COMMANDES EN ATTENTE ----------------

pending_orders = {}

# ---------------- BOT ----------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- FONCTIONS ----------------

def parse_orders(text):

    orders = {}

    for item, keys in KEYWORDS.items():

        for key in keys:

            matches = re.findall(rf"(\d*)\s*{key}", text.lower())

            for m in matches:

                qty = int(m) if m.isdigit() else 1

                orders[item] = orders.get(item, 0) + qty

    return orders


def calculate_total(order):

    total = 0

    for item, qty in order.items():

        total += PRICES[item] * qty

    return total

# ---------------- READY ----------------

@bot.event
async def on_ready():

    print(f"Connecté en tant que {bot.user}")

# ---------------- MESSAGES ----------------

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.name not in ALLOWED_CHANNELS:
        return

    text = message.content.lower()

    # ---------------- ACCUEIL ----------------

    greetings = ["bonjour", "salut", "coucou", "hello", "bonsoir"]

    if any(g in text for g in greetings):

        embed = discord.Embed(description=WELCOME_TEXT)

        embed.set_image(url=WELCOME_IMAGE)

        await message.channel.send(embed=embed)

        return

    # ---------------- CONFIRMATION PAIEMENT ----------------

    if text == "payé" and message.author.id in pending_orders:

        order_data = pending_orders.pop(message.author.id)

        total = order_data["total"]

        items = order_data["items"]

        embed = discord.Embed(
            description=f"✅ Paiement confirmé.\nPréparation de la commande...\n\n💰 Total payé : **{total}💰**"
        )

        embed.set_image(url=PAYMENT_IMAGE)

        await message.channel.send(embed=embed)

        # salon commandes

        for ch in message.guild.text_channels:

            if ch.name == ORDERS_CHANNEL_NAME:

                order_text = " | ".join(
                    [f"{q}x {i}" for i, q in items.items()]
                )

                await ch.send(
                    f"🧾 Commande de {message.author.mention} : {order_text}"
                )

        goodbye_embed = discord.Embed(description=GOODBYE_TEXT)

        goodbye_embed.set_image(url=GOODBYE_IMAGE)

        await message.channel.send(embed=goodbye_embed)

        return

    # ---------------- NOUVELLE COMMANDE ----------------

    order = parse_orders(text)

    if order:

        total = calculate_total(order)

        pending_orders[message.author.id] = {
            "items": order,
            "total": total
        }

        order_list = "\n".join(
            [f"• {qty}x {item}" for item, qty in order.items()]
        )

        embed = discord.Embed(
            title="☕ Commande prise",
            description=(
                f"🧾 **Votre commande :**\n"
                f"{order_list}\n\n"
                f"💰 **Total : {total}💰**\n\n"
                f"Merci de payer avec DraftBot :\n"
                f"`/pay Café {total}`\n\n"
                f"Une fois le paiement effectué,\n"
                f"écrivez simplement **payé** ici."
            )
        )

        embed.set_image(url=PAYMENT_IMAGE)

        await message.channel.send(embed=embed)

    await bot.process_commands(message)

# ---------------- LANCEMENT ----------------

bot.run(TOKEN)

