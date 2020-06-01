import discord
from discord.ext import commands

from checks import is_rl_or_higher_check, is_mm_or_higher_check
from cogs.Raiding.afk_check import AfkCheck
from cogs.Raiding.fametrain import FameTrain
from cogs.Raiding.headcount import Headcount
from cogs.Raiding.realmclear import RealmClear
from cogs.Raiding.vc_select import VCSelect


class Raiding(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.command(usage="!afk <location>")
    @commands.guild_only()
    @commands.check(is_rl_or_higher_check)
    # TODO: add check that guild has no running afk up
    async def afk(self, ctx, *, location):
        """Starts an AFK check for the location specified."""
        if ctx.author.id in self.client.raid_db[ctx.guild.id]['leaders']:
            return await ctx.send("You cannot start another AFK while an AFK check is still up.")
        self.client.raid_db[ctx.guild.id]['leaders'].append(ctx.author.id)
        setup = VCSelect(self.client, ctx)
        data = await setup.start()
        if isinstance(data, tuple):
            (raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel, setup_msg) = data
        else:
            self.client.raid_db[ctx.guild.id]['leaders'].remove(ctx.author.id)
            return
        afk = AfkCheck(self.client, ctx, location, raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel, setup_msg)
        await afk.start()
        self.client.raid_db[ctx.guild.id]['leaders'].remove(ctx.author.id)


    @commands.command(usage="!headcount", aliases=["hc"])
    @commands.guild_only()
    @commands.check(is_rl_or_higher_check)
    async def headcount(self, ctx):
        """Starts a headcount for the type of run specified."""
        setup = VCSelect(self.client, ctx, headcount=True)
        data = await setup.start()
        if isinstance(data, tuple):
            (raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel, setup_msg) = data
        else:
            return
        hc = Headcount(self.client, ctx, hcchannel, vcchannel, setup_msg)
        await hc.start()


    @commands.command(usage="!lock")
    @commands.guild_only()
    @commands.check(is_rl_or_higher_check)
    async def lock(self, ctx):
        """Locks the raiding voice channel"""
        setup = VCSelect(self.client, ctx, lock=True)
        data = await setup.start()
        if isinstance(data, tuple):
            (raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel, setup_msg) = data
        else:
            return
        await setup_msg.delete()
        vc_name = vcchannel.name
        # if " <-- Join!" in vc_name:
        #     vc_name = vc_name.split(" <")[0]
        #     await vcchannel.edit(name=vc_name)
        await vcchannel.set_permissions(raiderrole, connect=False, view_channel=True, speak=False)
        embed = discord.Embed(description=f"{vcchannel.name} Has been Locked!", color=discord.Color.red())
        await ctx.send(embed=embed)


    @commands.command(usage="!unlock")
    @commands.guild_only()
    @commands.check(is_rl_or_higher_check)
    async def unlock(self, ctx):
        """Unlocks the raiding voice channel"""
        setup = VCSelect(self.client, ctx, unlock=True)
        data = await setup.start()
        if isinstance(data, tuple):
            (raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel, setup_msg) = data
        else:
            return
        await setup_msg.delete()
        # if " <-- Join!" not in vcchannel.name:
        #     await vcchannel.edit(name=vcchannel.name + " <-- Join!")
        await vcchannel.set_permissions(raiderrole, connect=True, view_channel=True, speak=False)
        embed = discord.Embed(description=f"{vcchannel.name} Has been Unlocked!", color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(usage="!clean")
    @commands.guild_only()
    @commands.check(is_rl_or_higher_check)
    async def clean(self, ctx):
        """Clean out & lock a voice channel"""
        setup = VCSelect(self.client, ctx, clean=True)
        data = await setup.start()
        if isinstance(data, tuple):
            (raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel, setup_msg) = data
        else:
            return
        await setup_msg.delete()
        for member in vcchannel.members:
            if member.top_role < rlrole:
                if member.voice:
                    await member.move_to(channel=None)
        vc_name = vcchannel.name
        if " <-- Join!" in vc_name:
            vc_name = vc_name.split(" <")[0]
            await vcchannel.edit(name=vc_name)
        await vcchannel.set_permissions(raiderrole, connect=False, view_channel=True, speak=False)
        embed = discord.Embed(title="Done Cleaning!", description=f"{vcchannel.name} has been cleaned and locked.",
                              color=discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(usage="!fametrain <location>", aliases=['ft'])
    @commands.guild_only()
    @commands.check(is_rl_or_higher_check)
    async def fametrain(self, ctx, *, location):
        """Start an AFK check for a fametrain"""
        if ctx.author.id in self.client.raid_db[ctx.guild.id]['leaders']:
            return await ctx.send("You cannot start another AFK while an AFK check is still up.")
        self.client.raid_db[ctx.guild.id]['leaders'].append(ctx.author.id)
        setup = VCSelect(self.client, ctx)
        data = await setup.start()
        if isinstance(data, tuple):
            (raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel, setup_msg) = data
        else:
            return
        ft = FameTrain(self.client, ctx, location, raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel, setup_msg)
        await ft.start()
        self.client.raid_db[ctx.guild.id]['leaders'].remove(ctx.author.id)

    @commands.command(usage="!realmclear <location>", aliases=["rc"])
    @commands.guild_only()
    @commands.check(is_rl_or_higher_check)
    async def realmclear(self, ctx, *, location):
        """Start an AFK Check for Realm Clearing"""
        if ctx.author.id in self.client.raid_db[ctx.guild.id]['leaders']:
            return await ctx.send("You cannot start another AFK while an AFK check is still up.")
        self.client.raid_db[ctx.guild.id]['leaders'].append(ctx.author.id)
        setup = VCSelect(self.client, ctx)
        data = await setup.start()
        if isinstance(data, tuple):
            (raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel, setup_msg) = data
        else:
            return
        rc = RealmClear(self.client, ctx, location, raidnum, inraiding, invet, inevents, raiderrole, rlrole, hcchannel, vcchannel,setup_msg)
        await rc.start()
        self.client.raid_db[ctx.guild.id]['leaders'].remove(ctx.author.id)

    @commands.command(usage="!markmap/mm [number(s)]", aliases=["mm"])
    # @commands.cooldown(1, 70, commands.BucketType.guild)
    @commands.guild_only()
    @commands.check(is_mm_or_higher_check)
    async def markmap(self, ctx, *numbers):
        """Mark the current map with specified numbers"""
        await ctx.message.delete()
        if ctx.author.id in self.client.mapmarkers:
            rc = self.client.mapmarkers[ctx.author.id]
            if rc:
                await rc.markmap(ctx, False, numbers)
            else:
                await ctx.send("This realm clearing has ended!")
        else:
            await ctx.send("You aren't marking for any realm clearing sessions!")


    @commands.command(usage="!unmarkmap/umm [number(s)]", aliases=["umm"])
    @commands.guild_only()
    @commands.check(is_mm_or_higher_check)
    async def unmarkmap(self, ctx, *numbers):
        """Unmark the map with specified numbers"""
        await ctx.message.delete()
        if ctx.author.id in self.client.mapmarkers:
            rc = self.client.mapmarkers[ctx.author.id]
            if rc:
                await rc.markmap(ctx, True, numbers)
            else:
                await ctx.send("This realm clearing has ended!")
        else:
            await ctx.send("You aren't marking for any realm clearing sessions!")


    @commands.command(usage="!eventspawn [event]", aliases=['es'])
    @commands.guild_only()
    @commands.check(is_mm_or_higher_check)
    async def eventspawn(self, ctx, event):
        """Mark when an event spawns"""
        await ctx.message.delete()
        if ctx.author.id in self.client.mapmarkers:
            rc = self.client.mapmarkers[ctx.author.id]
            if rc:
                await rc.eventspawn(ctx, False, event)
            else:
                await ctx.send("This realm clearing has ended!")
        else:
            await ctx.send("You aren't marking for any realm clearing sessions!")


    @commands.command(usage="!uneventspawn [event]", aliases=['ues'])
    @commands.guild_only()
    @commands.check(is_mm_or_higher_check)
    async def uneventspawn(self, ctx, event):
        """Unmark an event spawn"""
        await ctx.message.delete()
        if ctx.author.id in self.client.mapmarkers:
            rc = self.client.mapmarkers[ctx.author.id]
            if rc:
                await rc.eventspawn(ctx, True, event)
            else:
                await ctx.send("This realm clearing has ended!")
        else:
            await ctx.send("You aren't marking for any realm clearing sessions!")


def setup(client):
    client.add_cog(Raiding(client))