import discord
from discord.ext import commands, tasks, pages
from discord import Embed
import psutil


ts = 0
tm = 0
th = 0
td = 0

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptime.start()
        
        
    @tasks.loop(seconds=1.1)
    async def uptime(self):
        global ts, tm, th, td
        ts += 1
        if ts == 60:
            tm += 1
            ts = 0
            if tm == 60:
                th += 1
                tm = 0
                if th == 24:
                    td += 1
                    th = 0
                        
    @uptime.before_loop
    async def uptime_beforeloop(self):
        await self.bot.wait_until_ready()
    
    @commands.command(help="""It's used when you do want to know when a user joined the server
                      Ex:
                      {0}joined 
                      {0}joined user name
                      {0}joined user id`
                      {0}joined user mention\n
                      """, description="Returns back when the user has joined the server")
    async def joined(self, ctx: commands.Context, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        join_date = member.joined_at
        embed = Embed(title=f"{member.name} joined at: {join_date.strftime('%d %B, %Y')}", colour=member.colour,timestamp
        =ctx.message.created_at)
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author)
        await ctx.send(embed=embed)
        
    @commands.command(help="""It's used when you do want to know more information about a particular user
                      Ex:
                      {0}userinfo 
                      {0}userinfo user name
                      {0}userinfo user id
                      {0}userinfo user mention\n
                      """, description="Returns back user's Information")
    async def userinfo(self, ctx: commands.Context, user: discord.Member = None):
        if user == None:
            user = ctx.author
        user_roles = [role.mention for role in user.roles[1:]]
        if len(user_roles) == 0:
            user_roles = ["None"]
        embed = Embed(title=f"{user.name}'s info.",description=f"Here is {user.name}'s stats.", color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.add_field(name="Name", value=str(user), inline=True)
        embed.add_field(name="Created at", value=user.created_at.strftime('%d %B, %Y'), inline=True)
        embed.add_field(name="Joined server at", value=user.joined_at.strftime("%d %B, %Y"), inline=True)
        embed.add_field(name="Current Roles", value=", ".join(user_roles))
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if user.avatar != None:
            embed.set_thumbnail(url=user.avatar)
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author)
        await ctx.send(embed=embed)
        
        
    @commands.command(help="""It returns back bot's information
                      Those informations Containts: Bot's name,
                      Ownership name,
                      How long has the Bot been online,
                      Cpu Usage And Ram Usage.
                      
                      Ex:
                      {0}botinfo\n""", description="Returns back the bot's Information")
    async def botinfo(self, ctx: commands.Context):
        owner = await self.bot.fetch_user(1128420485294731264)
        embed = Embed(title="**Cadmium**", description=f"Here's {self.bot.user.name}\'s stats.", timestamp=ctx.message.created_at, colour=ctx.author.color, url="https://discord.com/api/oauth2/authorize?client_id=1130152470627229858&permissions=18855442771062&scope=bot")
        embed.add_field(name="Owner", value=owner.name, inline=True)
        embed.add_field(name="Online since", value=f"{td} Days, {th} Hours, {tm} Minutes", inline=True)
        embed.add_field(name="CPU Usage", value=f"{psutil.cpu_percent(1)}%", inline=True)
        embed.add_field(name="RAM Usage", value=f"{psutil.disk_usage('/').percent}%",inline=True)
        embed.set_thumbnail(url=self.bot.user.avatar)
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        await ctx.send(embed=embed)
    
    @commands.command(help="""Returns avatar of a member (if the avatar exists)
                      
                      Ex:
                      {0}avatar  -> Returns back your Avatar
                      {0}avatar `id` -> Note That this can get anyone's avatar whether they're in the server or not.
                      {0}avatar `user mention`\n""",
                      description="Returns back user's Avatar whether they're in the server or not typing their ID")
    async def avatar(self, ctx: commands.Context, *, member: discord.Member | str = None):
        if member == None:
            member = ctx.author
        try:
            if member.isdigit():
                new_member: discord.Member = await self.bot.fetch_user(int(member))
                member = new_member
        except Exception as e:
                print("Didn't found")
        finally:
            if member.avatar != None:
                embed = Embed(title=f"{member.name}'s Avatar.", colour=ctx.author.color, timestamp=ctx.message.created_at)
                embed.set_image(url=member.avatar)
                embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
                if ctx.author.avatar != None:
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
                else:
                    embed.set_author(name=ctx.author.name)
                await ctx.reply(embed=embed)
            else:
                await ctx.reply(f"**{member.name}** Has no avatar.")
            
    @commands.command(help="""Returns roles of a member.
                      
                      Ex:
                      {0}roles -> Returns back your roles
                      {0}roles `user name`
                      {0}roles `id`
                      {0}roles `user mention`\n""",
                      description="Returns back user's Roles")
    async def roles(self, ctx: commands.Context, *, member: discord.Member = None):
        if member == None:
            member = ctx.author
        roles = ""
        for role in member.roles[1:]:
            roles += f"{role.name}, "
        if roles == "":
            roles = "None"
        embed = Embed(title="{0.name}'s Roles:\n".format(member), description=f"{roles}", colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
            await ctx.send(embed=embed)
            
    @commands.command(help="""Returns banner of a member(if they has one)
                      
                      Ex:
                      {0}banner 
                      {0}banner `user id` -> Note That this can get anyone's banner whether they're in the server or not.
                      {0}banner `user mention`\n""", description="Returns back user's Banner whether they're in the server or not typing their ID")
    async def banner(self, ctx: commands.Context, *, user: discord.Member | str = None):
        if user == None:
            user = ctx.author
        try:
            if user.isdigit():
                new_member: discord.Member = await self.bot.fetch_user(int(user))
                user = new_member
        except Exception as e:
                print("Didn't found")
        finally:
            if user.banner != None:
                embed= Embed(title=f"{user.name}'s banner.", timestamp=ctx.message.created_at, color=ctx.author.color)
                embed.set_image(url=user.banner.url)
                embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
                if ctx.author.avatar != None:
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
                else:
                    embed.set_author(name=ctx.author.name) 
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{user.name} has no banner")
            
            
    @commands.command(help="""Returns all users' name in addition to their IDs in the current server
                    
                      Ex:
                      {0}getusers""", 
                      description="Returns all users in the server")
    async def getusers(self, ctx):
        list1 = []
        users = [user for user in ctx.message.guild.members]
        n = len(users)
        x1 = n/10 - n//10
        z2=0
        for num in range(1,(n//10)+1):
            x = num*6
            list2 = [m for m in users[z2:x]]
            z2 = x
            list1.append(list2)
        if x1 > 0:
            list2 = [item for item in users[int((n-(x1*10))):]]
            list1.append(list2)  
        help_command = [Embed(title=f"Page {num+1}") for num in range(len(list1))] 
        for embed in help_command:
            for user in list1[help_command.index(embed)]:
                embed.add_field(name=f"{user.name}", value=user.id, inline=True)
                embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
                if ctx.author.avatar != None:
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
                else:
                    embed.set_author(name=ctx.author.name)
        paginator = pages.Paginator(pages=help_command, use_default_buttons=False)
        paginator.add_button(
            pages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.green)
        )
        paginator.add_button(
            pages.PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True
            )
        )
        paginator.add_button(
            pages.PaginatorButton("next", style=discord.ButtonStyle.green)
        )
        await ctx.send("Current users in the server are:")
        await paginator.send(ctx)
        
    @commands.command(help="""Returns current guild's admins' names in addition to their IDs
                      
                      Ex:
                      {0}getadmins""", description="Returns Current guild's Admins")
    async def getadmins(self, ctx):
        list1 = []
        users = [user for user in ctx.message.guild.members if user.guild_permissions.administrator == True and user.bot != True]
        n = len(users)
        x1 = n/10 - n//10
        z2=0
        for num in range(1,(n//10)+1):
            x = num*6
            list2 = [m for m in users[z2:x]]
            z2 = x
            list1.append(list2)
        if x1 > 0:
            list2 = [item for item in users[int((n-(x1*10))):]]
            list1.append(list2)  
        help_command = [Embed(title=f"Page {num+1}") for num in range(len(list1))] 
        for embed in help_command:
            for user in list1[help_command.index(embed)]:
                embed.add_field(name=f"{user.name}", value=user.id, inline=True)
                embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
                if ctx.author.avatar != None:
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
                else:
                    embed.set_author(name=ctx.author.name)
        paginator = pages.Paginator(pages=help_command, use_default_buttons=False)
        paginator.add_button(
            pages.PaginatorButton("prev", label="<", style=discord.ButtonStyle.green)
        )
        paginator.add_button(
            pages.PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True
            )
        )
        paginator.add_button(
            pages.PaginatorButton("next", style=discord.ButtonStyle.green)
        )
        await ctx.send("Current Admins in the server are:")
        await paginator.send(ctx)
     
         
    @commands.command(help="""Returns current Servers's Information.
                      This includes:
                      Server name,
                      Server Owner<
                      Server ID,
                      When the Server Created at,
                      How many members in the server,
                      How many Roles in the server
                      
                      Ex:
                      {0}serverinfo""", 
                      description="Returns Server's Infos")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = Embed(title="Server info.", colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.add_field(name="Name", value=guild.name, inline=False)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
        embed.add_field(name="ID", value=guild.id, inline=False)
        embed.add_field(name="Created at", value=guild.created_at.strftime('%d %B, %Y'), inline=False)
        embed.add_field(name="Member count", value=guild.member_count, inline=False)
        embed.add_field(name="Roles count", value=len(guild.roles), inline=False)
        embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
        await ctx.send(embed=embed)
        
    @commands.command(help="""returns channel information
                      This includes:
                      Ctegory,
                      When the channel has been created,
                      Name of the channel,
                      Url for the channel
                      
                      Ex:
                      {0}channelinfo 
                      {0}channelinfo `channel name`
                      {0}channelinfo `channel id`
                      {0}channelinfo `channel mention`""",
                      description="Returns Channels's info")
    async def channelinfo(self, ctx: commands.Context, * , channel: discord.abc.GuildChannel = None):
        if channel == None:
            channel = ctx.channel
        embed = Embed(title="Channel info", color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.add_field(name="Category", value=channel.category, inline=False)
        embed.add_field(name="Created at", value=channel.created_at, inline=False)
        embed.add_field(name="Name", value=channel.name, inline=False)
        embed.add_field(name="Jump URL", value=channel.jump_url, inline=False)
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author.name)
        await ctx.send(embed=embed)

    
def setup(bot):
    bot.add_cog(Utility(bot))
