import discord
from discord import app_commands
from discord.ext import commands
import random
import typing
import requests
import io

from keep_alive import keep_alive
keep_alive()



# --- Bot Setup ---
intents = discord.Intents.default()
# Crucial Intents: members/presences are required to check the owner's status!
intents.message_content = True
intents.members = True 
intents.presences = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# ---------------- AI Helper Function (Conceptual) ----------------
# NOTE: This function is simplified for the context of this example.
async def generate_ai_response(query: str) -> str:
    """Simulates an AI response using Google Search and formatting."""
    try:
        # Placeholder for Google Search tool call
        search_results = await google.search.queries([query])
        
        final_answer = f"🧠 **AI Answer:**\n"
        
        if search_results and search_results[0].get('snippet'):
            snippet = search_results[0].get('snippet')
            source_title = search_results[0].get('title', 'Unknown Source')
            source_url = search_results[0].get('url', 'No Link')
            
            final_answer += f"> {snippet}\n\n"
            final_answer += f"*(Source: [{source_title}]({source_url}))*"
        else:
            final_answer += "I searched the web, but I couldn't find a clear answer to that question."
        
        return final_answer
        
    except Exception:
        return "❌ **Error:** Sorry, I couldn't process that request right now."

# ---------------- OWNER CHECK / WEBHOOK IMPERSONATION (Unchanged) ----------------

async def get_owner_status(guild: discord.Guild) -> discord.Status:
    owner = guild.owner
    if owner:
        return owner.status
    return discord.Status.offline

async def send_as_owner(channel: discord.TextChannel, message_content: str, owner: discord.Member):
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, user__id=bot.user.id, name="OwnerBotHook")
    if not webhook:
        webhook = await channel.create_webhook(name="OwnerBotHook")
    
    try:
        await webhook.send(
            message_content,
            username=owner.display_name,
            avatar_url=owner.display_avatar.url,
        )
    except Exception as e:
        print(f"Webhook send error: {e}")
        await channel.send(f"⚠️ **[Owner Mode Failed]** {message_content}")

# ---------------- EVENT LISTENER (Auto AI Chat) ----------------

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user or message.guild is None:
        await bot.process_commands(message)
        return

    if bot.user.mentioned_in(message):
        mention_string = f'<@{bot.user.id}>'
        question = message.content.replace(mention_string, '').strip()

        if not question:
            await message.channel.send(f"👋 {message.author.mention}, I'm here! Ask me a question.")
            await bot.process_commands(message)
            return
            
        guild_owner = message.guild.owner
        owner_status = await get_owner_status(message.guild)
        
        is_owner_offline = owner_status in (discord.Status.offline, discord.Status.invisible)
        
        async with message.channel.typing():
            ai_response = await generate_ai_response(question)
        
        if is_owner_offline:
            plain_response = ai_response.replace("🧠 **AI Answer:**\n", "").replace("*(Source:", "\n*(Source:")
            await send_as_owner(message.channel, plain_response, guild_owner)
            
        else:
            await message.reply(ai_response)
        
    await bot.process_commands(message)


# ---------------- SLASH COMMANDS (General & Moderation) ----------------

# (All existing commands remain here for a complete, runnable file)

@bot.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("👋 Hello! I’m your GamerSatu bot — ready to assist you!")

@bot.tree.command(name="help", description="Show all available commands")
async def help(interaction: discord.Interaction):
    help_text = (
        "📘 **GamerSatu Bot Commands:**\n"
        "**AI Chat/Owner Mode:**\n"
        "**@GamerSatuBot [question]** → Auto AI Chat (Owner Mode if owner is offline).\n"
        "`/ask [question]` → Ask the bot a question (Always Basic Mode).\n"
        "\n"
        "**Fun (New!):**\n"
        "`/8ball [question]` → Ask the magic 8-ball a question.\n"
        "`/flip` → Flip a coin.\n"
        "`/pat [member]` → Give a user a virtual pat.\n"
        "\n"
        "**Utility & Info:**\n"
        "`/hello` → Say hello to the bot\n"
        "`/help` → Show this help message\n"
        "`/automeme` → Get a random meme\n"
        "`/dashboard` → Show bot dashboard info\n"
        "`/members` → Show total members in server\n"
        "`/serverinfo` → Display server name and ID\n"
        "`/otherbots` → List popular external bots (e.g., Dyno, MEE6)\n"
        "\n"
        "**Moderation:**\n"
        "`/kick` → Remove a member from the server\n"
        "`/ban` → Permanently block a member from the server"
    )
    await interaction.response.send_message(help_text)

@bot.tree.command(name="automeme", description="Send a random meme")
async def automeme(interaction: discord.Interaction):
    memes = [
        "https://i.imgur.com/W3duR07.png",
        "https://i.imgur.com/2s8R0Zi.jpeg",
        "https://i.imgur.com/VZ5zQFv.png"
    ]
    meme = random.choice(memes)
    await interaction.response.send_message(f"😂 Here's your meme!\n{meme}")

@bot.tree.command(name="dashboard", description="Show bot dashboard info")
async def dashboard(interaction: discord.Interaction):
    await interaction.response.send_message("📊 **GamerSatu Dashboard:**\nStatus: ✅ Online\nVersion: 1.0.0")

@bot.tree.command(name="members", description="Show total members in this server")
async def members(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message(f"👥 **Total Members:** {guild.member_count}")

@bot.tree.command(name="serverinfo", description="Show server info")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message(
        f"🖥️ **Server Name:** {guild.name}\n🆔 **Server ID:** {guild.id}"
    )

@bot.tree.command(name="otherbots", description="List popular external bots like Carl-bot, Dyno, MEE6")
async def otherbots(interaction: discord.Interaction):
    bot_list = (
        "💡 **Popular Discord Bots for Moderation/Features:**\n"
        "* **Carl-bot:** Reaction Roles and Logging.\n"
        "* **Dyno:** Versatile Moderation, Fun, and Utility.\n"
        "* **MEE6:** Custom Commands, Levels, and Welcome Messages.\n"
        "* **ProBot:** Welcoming and Server Management.\n"
        "\n*To use their commands, ensure these bots are added to your server.*"
    )
    await interaction.response.send_message(bot_list)

@bot.tree.command(name="ask", description="Ask the bot a question (Always runs in Basic Mode)")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    ai_response = await generate_ai_response(question)
    await interaction.followup.send(ai_response)

@bot.tree.command(name="kick", description="Remove a member from the server")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: typing.Optional[str] = "No reason provided"):
    if member.top_role >= interaction.guild.me.top_role or member == interaction.user or member == interaction.guild.me:
        await interaction.response.send_message("❌ Cannot kick this member.", ephemeral=True)
        return
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(title="👋 Member Kicked", description=f"**{member.display_name}** has been kicked by **{interaction.user.display_name}**.", color=discord.Color.orange())
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I do not have permission to kick this member. Check my role permissions.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="Permanently block a member from the server")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: typing.Optional[str] = "No reason provided"):
    if member.top_role >= interaction.guild.me.top_role or member == interaction.user or member == interaction.guild.me:
        await interaction.response.send_message("❌ Cannot ban this member.", ephemeral=True)
        return
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(title="🔨 Member Banned", description=f"**{member.display_name}** has been permanently banned by **{interaction.user.display_name}**.", color=discord.Color.red())
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I do not have permission to ban this member. Check my role permissions.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An unexpected error occurred: {e}", ephemeral=True)

@kick.error
@ban.error
async def moderation_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("🛑 **Permission Denied!** You must have the necessary server permissions (Kick/Ban Members) to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An unknown error occurred.", ephemeral=True)

# ---------------- SLASH COMMANDS (Fun - NEW) ----------------

@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question")
async def eightball(interaction: discord.Interaction, question: str):
    responses = [
        "🎱 Yes, definitely.",
        "🎱 It is certain.",
        "🎱 Without a doubt.",
        "🎱 Yes.",
        "🎱 You may rely on it.",
        "🎱 As I see it, yes.",
        "🎱 Most likely.",
        "🎱 Outlook good.",
        "🎱 Signs point to yes.",
        "🎱 Reply hazy, try again.",
        "🎱 Ask again later.",
        "🎱 Better not tell you now.",
        "🎱 Cannot predict now.",
        "🎱 Concentrate and ask again.",
        "🎱 Don't count on it.",
        "🎱 My reply is no.",
        "🎱 My sources say no.",
        "🎱 Outlook not so good.",
        "🎱 Very doubtful.",
    ]
    response = random.choice(responses)
    await interaction.response.send_message(f"🤔 **Question:** {question}\n✨ **8-Ball Says:** {response}")

@bot.tree.command(name="flip", description="Flip a coin (Heads or Tails)")
async def flip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 **Flipping coin...** The result is **{result}!**")

@bot.tree.command(name="pat", description="Give a member a virtual pat")
async def pat(interaction: discord.Interaction, member: discord.Member):
    if member == interaction.user:
        message = f"😅 {interaction.user.mention} pats themselves. Self-care is important!"
    elif member == bot.user:
        message = f"💖 Thank you for the pat, {interaction.user.mention}! I appreciate it!"
    else:
        message = f"🤗 {interaction.user.mention} gently gives {member.mention} a comforting pat!"
    
    await interaction.response.send_message(message)


# ------------------------------------------------


bot.run("MTQzNTI4MjYxNDQ5OTE0Nzg0Ng.Gt_zuQ.K48QUOw4OwEHz6ulHZw355ABr2M0quTOinHRDc")




