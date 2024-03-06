import discord
import os
from discord.ext import commands
import psycopg

DB_URI = os.getenv("DB_URI")

class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Member Update (Promote, Demote, Update)"))
        self.add_item(discord.ui.InputText(label="Member ID"))
        self.add_item(discord.ui.InputText(label="Member Rank[OPTIONAL]", required=False, placeholder=1))
        
    async def callback(self, interaction: discord.Interaction):
        await self.update_member(int(self.children[1].value), str(self.children[0].value).lower() , int(self.children[2].value))
        await interaction.response.send_message("MEMBER UPDATED SUCCESSFULLY WITH ID {}".format(int(self.children[1].value)))
    
    async def update_member(self, id:int, word:str, rank: int):
         async with await psycopg.AsyncConnection.connect(DB_URI) as db:
            async with db.cursor() as cursor:
                if word == "promote":
                    rank = 1
                    await cursor.execute("UPDATE USERS set USER_LVL = %s where USER_ID = %s", (rank,id,))
                elif word == "demote":
                    rank = 0
                    await cursor.execute("UPDATE USERS set USER_LVL = %s where USER_ID = %s", (rank,id,))
                elif word == "update":
                    await cursor.execute("UPDATE USERS set USER_LVL =  %s where USER_ID = %s", (rank,id,))
                await db.commit()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def is_admin(self, member : discord.Member):
        async with await psycopg.AsyncConnection.connect(DB_URI) as db:
            async with db.cursor() as cursor:
                await cursor.execute("SELECT USER_LVL FROM USERS where USER_ID = %s", (member.id,))
                results = await cursor.fetchone()
                print(results[0])
                return results[0]
            
    @commands.slash_command(description="MODAL TEST", guild_ids=[1130150209536671745])
    async def reload_cog(self, ctx: discord.ApplicationContext, *, arg):
        member_rank = await self.is_admin(ctx.author)
        if member_rank == 99:
            self.bot.reload_extension(f'cogs.{arg.lower()}')
            await ctx.respond(f"{arg} EXTENSION IS RELOADED")
        else:
            await ctx.respond("THIS IS FOR ADMIN ONLY!")
    
    @commands.slash_command(description="MODAL TEST", guild_ids=[1130150209536671745])
    async def member_update(self, ctx: discord.ApplicationContext):
        """Shows an example of a modal dialog being invoked from a slash command."""
        member_rank = await self.is_admin(ctx.author)
        if member_rank == 99:
            modal = MyModal(title="Updating a member")
            await ctx.send_modal(modal)
        else:
            await ctx.send("THIS IS FOR ADMIN ONLY")
    
def setup(bot):
    bot.add_cog(Admin(bot))                 
        
        
        
        


