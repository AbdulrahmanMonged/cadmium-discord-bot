import os
import discord
from discord import Embed
from discord.commands import SlashCommandGroup
from discord.ext import commands, pages
import psycopg
import datetime
DB_URI = os.getenv("DB_URI")

class ReportModal(discord.ui.Modal):
    def __init__(self, bot, ctx, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(style=discord.InputTextStyle.paragraph,label="Report Message", max_length=1024))
        self.bot = bot
        self.ctx = ctx
        
    async def callback(self, interaction: discord.Interaction):
        await self.send_report(str(self.children[0].value))
        await interaction.response.send_message("Message has been sent successfully to support.")
    
    async def send_report(self, message:str):
        report_channel : discord.TextChannel = await self.bot.fetch_channel(1162121251075129415)
        embed = Embed(title="Report", description="Sent by {0}".format(self.ctx.author), timestamp=datetime.datetime.now())
        embed.add_field(name="Message Body", value=message, inline=False)
        await report_channel.send(embed=embed)

class PageTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_prefix(self, ctx):
        async with await psycopg.AsyncConnection.connect(DB_URI) as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT guild_prefix FROM GUILD where GUILD_ID = %s", (ctx.guild.id,))
                results = await cursor.fetchone()
                current_prefix = results[0].strip(" ")
                return current_prefix

    def get_commands(self, cog_name, current_prefix , ctx) -> list:
        cog = self.bot.get_cog(f'{cog_name}')
        emoji = self.bot.get_emoji(1159303926454169680)
        list1 = []
        commands = [command for command in cog.get_commands()]
        n = len(commands)
        x1 = n/3 - n//3
        z2=0
        for num in range(1,(n//3)+1):
            x = num*3
            list2 = [m for m in commands[z2:x]]
            z2 = x
            list1.append(list2)
        if x1 > 0:
            list2 = [item for item in commands[int((n-(x1*3))):]]
            list1.append(list2)  
        help_command = [Embed(title=f"Page {num+1}", color=ctx.author.color) for num in range(len(list1))] 
        
        for embed in help_command:
            for command in list1[help_command.index(embed)]:
                embed.add_field(name=f"**{current_prefix}{str(command.name)}**", value="\n{0} {1}\n".format(emoji ,str(command.description)), inline=False)
                if ctx.author.avatar != None:
                    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
                else:
                    embed.set_author(name=ctx.author.name)
                embed.set_footer(text="Use {0}help <command name> to get more information".format(current_prefix), icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        return help_command
        
    
    @commands.slash_command(description="Help command", name="help")
    async def help_commands(self, ctx: discord.ApplicationContext):
        current_prefix = await self.get_prefix(ctx)
        page_buttons = [
            pages.PaginatorButton(
                "first", label="<<-", style=discord.ButtonStyle.green
            ),
            pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True
            ),
            pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Invite Bot To the Server!", row=2, style=discord.ButtonStyle.link, url='https://discord.com/api/oauth2/authorize?client_id=1130152470627229858&permissions=18855442771062&scope=bot'))
        cogs = ['Interactions', 'Moderation', 'Music' ,'Utility', ]
        emoji = ['😙', '⚒', '🎶' ,'⚙' ]
        page_groups = [
            pages.PageGroup(
                pages=self.get_commands(f'{cog}', current_prefix , ctx),
                label=f"{cog} Group page.",
                emoji = emoji[cogs.index(cog)],
                description=f"This page has {cog} Commands.",
                custom_buttons=page_buttons,
                use_default_buttons=False,
                custom_view=view,
            ) for cog in cogs]
        paginator = pages.Paginator(pages=page_groups,
                                    show_menu=True,
                                    show_indicator=True,
                                    use_default_buttons=False,
                                    custom_buttons=page_buttons,
                                    custom_view=view)
        await paginator.respond(ctx.interaction, ephemeral=False)

    @commands.command()
    async def help(self, ctx, *, command_name : str = None):
        found = False
        current_prefix = await self.get_prefix(ctx)
        if command_name != None:
            for command in self.bot.walk_commands():
                if command.name == command_name:
                    try:
                        found = True
                        description=f"{command.help}"
                        embed = Embed(title="**{0}{1}**".format(current_prefix, command.name), description=f"{command.help}".format(current_prefix), timestamp=ctx.message.created_at, colour=ctx.author.color)
                        if ctx.author.avatar != None:
                            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
                        else:
                            embed.set_author(name=ctx.author.name)
                        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
                        await ctx.send(embed=embed)
                    except Exception as e:
                        await ctx.send(e)
            if not found:
                await ctx.send("Invaild Command name.\nSyntax is: `{0}help command_name`\nLike {0}help avatar\nYou can get all commands using </help:1130171436573655091>".format(current_prefix))
        else:   
            await ctx.send("Invaild Command name.\nSyntax is: `{0}help command_name`\nFor example: {0}help avatar\nYou can get all commands using </help:1130171436573655091>".format(current_prefix))
    
    @commands.slash_command(description="Report an error")
    async def report(self, ctx: discord.ApplicationContext):
        modal = ReportModal(title="Report", bot=self.bot, ctx=ctx)
        await ctx.send_modal(modal)
        
        
def setup(bot):
    bot.add_cog(PageTest(bot))