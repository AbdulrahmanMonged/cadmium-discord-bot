import discord
from discord.ext import commands, tasks, pages
import wavelink
import datetime
import os



ID = os.getenv("ID")
KEY = os.getenv("KEY")

class ControlPanel(discord.ui.View):
    def __init__(self, vc, ctx, messages):
        super().__init__()
        self.vc = vc
        self.ctx: discord.ApplicationContext = ctx
        self.main_messages = messages
    
    
    @discord.ui.button(label="Resume/Pause", style=discord.ButtonStyle.blurple)
    async def resume_and_pause(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        if self.vc.is_paused():
            await self.vc.resume()
            await interaction.response.edit_message(content="Resumed", view=self)
        else:
            await self.vc.pause()
            await interaction.response.edit_message(content="Paused", view=self)

    @discord.ui.button(label="Queue", style=discord.ButtonStyle.blurple)
    async def queue(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        if self.vc.queue.is_empty:
            return await interaction.response.send_message("the queue is empty smh", ephemeral=True)
    
        embed = discord.Embed(title="Queue", color=self.ctx.author.color, timestamp=self.ctx.message.created_at)
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if self.ctx.author.avatar != None:
            embed.set_author(name=self.ctx.author, icon_url=self.ctx.author.avatar)
        else:
            embed.set_author(name=self.ctx.author)
        queue = self.vc.queue.copy()
        list1 = []
        users = [song for song in queue]
        n = len(users)
        x1 = n/15 - n//15
        z2=0
        for num in range(1,(n//15)+1):
            x = num*6
            list2 = [m for m in users[z2:x]]
            z2 = x
            list1.append(list2)
        if x1 > 0:
            list2 = [item for item in users[int((n-(x1*15))):]]
            list1.append(list2)  
        help_command = [discord.Embed(title=f"Page {num+1}", color=self.ctx.author.color) for num in range(len(list1))] 
        for embed in help_command:
            for song in list1[help_command.index(embed)]:
                try:
                    embed.add_field(name=f"{users.index(song) + 1} - {song.title}", value="Author: {0}".format(song.author), inline=True)
                except Exception as e:
                    embed.add_field(name=f"{users.index(song) + 1} - {song.title}", value="", inline=True)
                embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
                if self.ctx.author.avatar != None:
                    embed.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.avatar)
                else:
                    embed.set_author(name=self.ctx.author.name)
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
        await self.ctx.send("Queue:")
        await paginator.send(self.ctx)
    
    @discord.ui.button(label="Shuffle", style=discord.ButtonStyle.blurple)
    async def shuffle(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        try:
            if self.vc.queue.count < 1:
                self.vc.queue.shuffle()
                await interaction.response.send_message("Shuffling Current Queue...", ephemeral=True)
                return await self.queue(interaction=interaction)

        except Exception as e:
            print(e)
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.blurple)
    async def skip(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = False
        if self.vc.queue.is_empty:
            return await interaction.response.send_message("the queue is empty smh", ephemeral=True)

        try:
            next_song = self.vc.queue.get()
            await self.vc.play(next_song)
            message = None
            for id in self.main_messages:
                if id == self.ctx.guild.id:
                    message = self.main_messages[id]
            if message != None:
                embed = message.embeds[0]
                embed.description = f"{self.vc.current.title}"
                embed.set_image(url=f"{self.vc.current.artwork}")
                embed.set_field_at(0, name="Duration", value=f"`{str(datetime.timedelta(milliseconds=self.vc.current.length))}`")
                embed.set_field_at(1, name="URL: ", value=f"[Click me!]({str(self.vc.current.uri)})", inline=True)
                try:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{self.vc.queue[0].title}`", inline=False )
                except Exception as e:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{None}`", inline=False )
                if self.vc.queue.count < 1:
                    self.children[2].disabled = True
                    self.children[3].disabled = True
                await message.edit(embed=embed, view=self)
            await interaction.response.edit_message(content="SKIPPED", view=self)

        except Exception as e:
            return await interaction.response.send_message(f"The queue is empty! {e}", ephemeral=True)
        
    
    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.red)
    async def disconnect(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user == self.ctx.author:
            return await interaction.response.send_message("You can't do that. run the command yourself to use these buttons", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await self.vc.disconnect()
        await interaction.response.edit_message(content="Disconnect :P", view=self)
    
    

class Music(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.main_messages = {}
        self.main_channels = {}


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackStartEventPayload):
        vc: payload.player = payload.player
        message = None
        for id in self.main_messages:
            if id == vc.guild.id:
                message = self.main_messages[id]
        channel = self.main_channels[vc.guild.id]

        if vc.loop:
            return await vc.play(payload.track)
        
        try:
            next_song = vc.queue.get()
        except Exception as e:
            next_song = None
        
        if not vc.queue.is_empty and not vc.playing and next_song != None:
            await vc.play(next_song)
            await channel.send(f"Now playing: {next_song.title}")
            if message != None:
                embed = message.embeds[0]
                embed.description= f"{vc.current.title}"
                embed.set_image(url=f"{vc.current.artwork}")
                embed.set_field_at(0, name="Duration", value=f"`{str(datetime.timedelta(milliseconds=vc.current.length))}`")
                embed.set_field_at(1, name="URL: ", value=f"[Click me!]({str(vc.current.uri)})", inline=True)
                try:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{vc.queue[0].title}`", inline=False )
                except Exception as e:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{None}`", inline=False )
                await message.edit(embed=embed)

    @commands.command(help="""Plays music From Youtube
                      
         Ex:
         {0}play `spotify_song_url`
         {0}play `spotify_playlist_url`
         {0}play `song_name`
         {0}play `song url`
         {0}play `youtube Playlist url`
        """, description="Plays from Youtube And Spotify")
    async def play(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        if vc.queue.is_empty and not vc.playing:
            try:
                tracks : wavelink.Search = await wavelink.Playable.search(search)
                if len(tracks) >= 5 and len(search) >= 60:
                    message = await ctx.send(content=f"```\nADDING {len(tracks)} SONGS TO QUEUE\n```")
                    for track in tracks:
                        await vc.queue.put_wait(track)
                        if not vc.playing and len(vc.queue) < 2:
                            playing = vc.queue.get()
                            await vc.play(playing)
                            await ctx.send(f'Playing `{playing.title}`')
                        await message.edit(f'```\nADDING {len(tracks)} SONGS TO QUEUE \n{len(tracks) - tracks.tracks.index(track)} SONGS LEFT TO BE ADDED\n\nAdded {track.title} to the queue...\n```')
                    await message.edit(f'```\nSUCCESSFULLY ADDED {len(tracks)} TO QUEUE \nIN: {datetime.timedelta(seconds=len(tracks))}\n\nThe Number of Songs in QUEUE {len(vc.queue)} to the queue...```')
                else:
                    await vc.queue.put_wait(tracks[0])
                    playing = vc.queue.get()
                    await vc.play(playing)
                    await ctx.send(f'Playing `{playing.title}`')
            except TypeError:
                tracks_yt : wavelink.Search = await wavelink.Playable.search(search)
                playlist = tracks_yt.tracks
                message = await ctx.send(content=f"```\nADDING {len(playlist)} SONGS TO QUEUE\n```")
                for track in playlist:
                    await vc.queue.put_wait(track)
                    if not vc.playing and len(vc.queue) < 2:
                        playing = vc.queue.get()
                        await vc.play(playing)
                        await ctx.send(f'Playing `{playing.title}`')
                    await message.edit(f'```\nADDING {len(playlist)} SONGS TO QUEUE \n{0} SONGS LEFT TO BE ADDED\n\nAdded {track.title} to the queue...\n```')
                await message.edit(f'```\nSUCCESSFULLY ADDED {len(playlist)} TO QUEUE \nIN: {datetime.timedelta(seconds=len(playlist))}\n\nThe Number of Songs in QUEUE {len(vc.queue)} to the queue...```')
            except Exception as e:
                await ctx.send("PLEASE USE A VALID URL!")
                await ctx.send(e)
                print(e)
        else:
            try:
                tracks : wavelink.Search = await wavelink.Playable.search(search)
                if len(tracks) >= 5 and len(search) >= 60:
                    message = await ctx.send(content=f"```\nADDING {len(tracks)} SONGS TO QUEUE\n```")
                    for track in tracks:
                        await vc.queue.put_wait(track)
                        await message.edit(f'```\nADDING {len(tracks)} SONGS TO QUEUE \n{len(tracks) - tracks.tracks.index(track)} SONGS LEFT TO BE ADDED\n\nAdded {track.title} to the queue...\n```')
                else:
                    await vc.queue.put_wait(tracks[0])
                    await ctx.send(f'Added `{tracks[0].title}` to the queue...')
            except TypeError:
                tracks_yt : wavelink.Search = await wavelink.Playable.search(search)
                playlist = tracks_yt.tracks
                message = await ctx.send(content=f"```\nADDING {len(playlist)} SONGS TO QUEUE\n```")
                for track in playlist:
                    await vc.queue.put_wait(track)
                    if not vc.playing and len(vc.queue) < 2:
                        playing = vc.queue.get()
                        await vc.play(playing)
                        await ctx.send(f'Playing `{playing.title}`')
                    await message.edit(f'```\nADDING {len(playlist)} SONGS TO QUEUE \n{len(tracks) - tracks.tracks.index(track)} SONGS LEFT TO BE ADDED\n\nAdded {track.title} to the queue...\n```')
                await message.edit(f'```\nSUCCESSFULLY ADDED {len(playlist)} TO QUEUE \nIN: {datetime.timedelta(seconds=len(playlist))}\n\nThe Number of Songs in QUEUE {len(vc.queue)} to the queue...```')
            except Exception as e:
                await ctx.send("PLEASE USE A VALID URL!")
                await ctx.send(e)
                print(e)
        self.main_channels[ctx.guild.id] = ctx.channel
        try:
            if vc.loop: 
                return
        except Exception:
            setattr(vc, "loop", False)
        
    @commands.command(help="""Panel to control your music
                      This includes: 
                      Resume/Pause Button,
                      Queue Button,
                      Skip Button,
                      Disconnect Button
                      
                      Ex:
                      {0}panel""", description="Panel to control your music")
    async def panel(self, ctx: commands.Context):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("The Bot hasn't joined any channel yet.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.playing:
            return await ctx.send("First Play some music.")
        
        embed = discord.Embed(title="Currently Playing: ", description=f"{vc.current.title}", color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_image(url=f"{vc.current.artwork}")
        embed.add_field(name="Duration", value=f"`{str(datetime.timedelta(milliseconds=vc.current.length))}`")
        embed.add_field(name="URL: ", value=f"[Click me!]({str(vc.current.uri)})", inline=True)
        try:
            embed.add_field(name="Next Song: ", value=f"`{vc.queue[0].title}`", inline=False )
        except Exception:
            embed.add_field(name="Next Song: ", value="`NONE`", inline=False )
        embed.set_footer(text="Cadmium", icon_url="https://i.ibb.co/ypybNCS/image-1.png")
        if ctx.author.avatar != None:
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
        else:
            embed.set_author(name=ctx.author)
        view = ControlPanel(vc, ctx, self.main_messages)
        if vc.queue.count < 1:
                    view.children[2].disabled = True
                    view.children[3].disabled = True
        message = await ctx.send(embed=embed, view=view)
        print(self.main_messages)
        self.main_messages[message.guild.id] = message

    @commands.command(help="""Pauses current Song
                      
                      Ex:
                      {0}pause""",
                      description="Pauses Current Song")
    async def pause(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.playing:
            return await ctx.send("first play some music")

        await vc.pause()
        await ctx.send("paused your music.")
        
    @commands.command(help="""Resumes current paused Song
                      
                      Ex:
                      {0}resume""", description="Resumes Current paused Song")
    async def resume(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        if vc.is_playing():
            return await ctx.send("music is already playing!")

        await vc.resume()
        await ctx.send("the music is back on!")
        
    @commands.command(help="""Skips current song
                      
                      Ex:
                      {0}skip""", description="Skips Current Song")
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.playing:
            return await ctx.send("first play some music")
        
        try:
            next_song = vc.queue.get()
            await vc.play(next_song)
            await ctx.send(f"Now playing: {next_song.title}")
            message = None
            for id in self.main_messages:
                if id == ctx.guild.id:
                    message = self.main_messages[id]
            if message != None:
                embed = message.embeds[0]
                embed.description= f"{vc.current.title}"
                embed.set_image(url=f"{vc.current.artwork}")
                embed.set_field_at(0, name="Duration", value=f"`{str(datetime.timedelta(milliseconds=vc.current.length))}`")
                embed.set_field_at(1, name="URL: ", value=f"[Click me!]({str(vc.current.uri)})", inline=True)
                
                try:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{vc.queue[0].title}`", inline=False )
                except Exception as e:
                    embed.set_field_at(2, name="Next Song: ", value=f"`{None}`", inline=False )
                view = ControlPanel(vc, ctx, self.main_messages)
                if vc.queue.count < 1:
                    view.children[2].disabled = True
                    view.children[3].disabled = True
                await message.edit(embed=embed, view=view)
        except Exception as e:
            await ctx.send(e)
            return await ctx.send("The queue is empty!")
        
        
    @commands.command(help="""Disconnect the bot from current channel
                      
                      Ex:
                      {0}disconnect""",
                      description="Disconnect the bot from the Voice chat")
    async def disconnect(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        await vc.disconnect()
        await ctx.send("DISCONNECTED")
        
    @commands.command(help="""Loop current Song
                      
                      Ex:
                      {0}loop""", description="Loops current Song")
    async def loop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        vc: wavelink.Player = ctx.voice_client
        if not vc.playing:
            return await ctx.send("first play some music.")
        try: 
            vc.queue.loop = True
        except:
            setattr(vc, "loop", False)
        if vc.queue.loop:
            return await ctx.send("Looping: `{0.title}`".format(vc.current))
        else:
            return await ctx.send("no more loop time.")
        
    @commands.command(help="""Shuffle Current Playlist
                
                      Ex:
                      {0}shuffle""", description="Shuffles current Playlist")
    async def shuffle(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        vc: wavelink.Player = ctx.voice_client
        if not vc.playing:
            return await ctx.send("first play some music.")
        if vc.queue.count:
            vc.queue.shuffle()
            await ctx.send("Shuffling Current Playlist")
            return await self.queue(ctx)
        return await ctx.send("You must play Two songs at least...")

    @commands.command(help="""Gets current queue
                      
                      Ex:
                      {0}queue""",
                      description="Returns back current Queue")
    async def queue(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        vc: wavelink.Player = ctx.voice_client

        if vc.queue.is_empty:
            return await ctx.send("the queue is empty.")
             
        queue = vc.queue.copy()
        list1 = []
        users = [song for song in queue]
        n = len(users)
        x1 = n/15 - n//15
        z2=0
        for num in range(1,(n//15)+1):
            x = num*6
            list2 = [m for m in users[z2:x]]
            z2 = x
            list1.append(list2)
        if x1 > 0:
            list2 = [item for item in users[int((n-(x1*15))):]]
            list1.append(list2)  
        help_command = [discord.Embed(title=f"Page {num+1}", color=ctx.author.color) for num in range(len(list1))] 
        for embed in help_command:
            for song in list1[help_command.index(embed)]:
                try:
                    embed.add_field(name=f"{users.index(song) + 1} - {song.title}", value="Author: {0}".format(song.author), inline=True)
                except Exception as e:
                    embed.add_field(name=f"{users.index(song) + 1} - {song.title}", value="", inline=True)
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
        await ctx.send("Queue:")
        await paginator.send(ctx)


    @commands.command(help="""Controls volume
                      
                      Ex:
                      {0}volume 100
                      {0}volume 50""", description="Controls Volume")
    async def volume(self, ctx: commands.Context, volume: int):
        if not ctx.voice_client:
            return await ctx.send("The Bot isn't in a voice channel.")
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first.")
        else:
            vc: wavelink.Player = ctx.voice_client
        if not vc.playing:
            return await ctx.send("first play some music.")
        
        if volume > 100:
            return await ctx.send('thats way to high')
        elif volume < 0:
            return await ctx.send("thats way to low")
        await ctx.send(f"Set the volume to `{volume}%`")
        return await vc.set_volume(volume) 
        
def setup(bot):
    bot.add_cog(Music(bot))
    
