import argparse
import datetime
from discord.ext import tasks, commands
import discord
from logging import getLogger

from race import Race

logger = getLogger('kiite')


class Kiite(commands.Cog, name="kiite"):
    """
    Usage: !kiite COMMAND [ARGS]
    """

    def __init__(self, bot):
        self.bot = bot
        self.races = {}

    def race(self, ctx, hash):
        if hash not in self.races:
            raise commands.CommandInvokeError(
                'Not found race: {}'.format(hash))

        return self.races[hash]

    @classmethod
    def __parse_timestamp(cls, timestr):
        # HH:MM
        try:
            timestamp = datetime.datetime.strptime(timestr, '%H:%M')
            date = datetime.date.today()
            timestamp = timestamp.replace(
                year=date.year, month=date.month, day=date.day)
            return timestamp
        except ValueError:
            pass

        # yyyy/mm/dd HH:MM
        try:
            timestamp = datetime.datetime.strptime(timestr, '%Y/%m/%d %H:%M')
            return timestamp
        except ValueError:
            pass

        raise commands.CommandInvokeError(
            'invalid datetime format: {} \n \
                datetime should be following as <HH:MM> or <"yyyy/mm/dd HH:MM"> '
            .format(timestr))

    @commands.command(description="Open a race")
    async def open(self, ctx, start_time_str):
        """ 
        usage: !kiite open TIMESTRING

            TIMESTRING: A string indicates a start time of the race.
                        The string must be following the format "hh:mm" or "yyyy/mm/dd hh:mm".
        """

        start_time = self.__parse_timestamp(start_time_str)
        race = Race(ctx.message.id, ctx.channel.id, start_time)
        self.races[race.hash()] = race
        await ctx.channel.send(race.template())

    @commands.command(description="Close the race")
    async def close(self, ctx, hash):
        """ 
        usage: !kiite close HASH

            HASH: A hash of the race.
        """

        del self.races[hash]
        await ctx.channel.send("Deleted: {}".format(hash))

    @commands.command(description="Entry the race")
    async def entry(self, ctx, hash, url, *args):
        """ 
        usage: !kiite entry HASH URL [--name NAME]

            HASH: A hash of the race.
            URL: Your streaming url.
            --name NAME: Your name (optional, default is username of Discord)
        """

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--name", help="name of runner (default: username of Discord)")
        args = parser.parse_args(args)

        name = args.name if args.name else ctx.message.author.name

        race = self.race(ctx, hash)
        race.entry(name, url)
        await ctx.channel.send(race.template())

    @commands.command(description="Retire the race")
    async def retire(self, ctx, hash, *args):
        """ 
        usage: !kiite retire HASH [--name NAME]

            HASH: A hash of the race.
            --name NAME: Your name (optional, default is username of Discord)
        """

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--name", help="name of runner (default: username of Discord)")
        args = parser.parse_args(args)

        name = args.name if args.name else ctx.message.author.name

        race = self.race(ctx, hash)
        race.retire(name)
        await ctx.channel.send(race.template())

    @commands.command(description="Display a template of the race")
    async def template(self, ctx, hash, *args):
        """ 
        usage: !kiite template HASH [--nico]

            HASH: A hash of the race.
            --nico: A option to display the description for niconico.
        """

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--nico", action="store_true", help="print the template for niconico")
        args = parser.parse_args(args)

        race = self.race(ctx, hash)
        await ctx.channel.send(race.template(args.nico))

    @commands.command(description="Display list of the races")
    async def races(self, ctx):
        """ 
        usage: !kiite races
        """

        s = ""
        for race in self.races.values():
            s += race.overview() + "\n"

        if not s:
            s = "None"

        await ctx.channel.send(s)

    async def cog_command_error(self, ctx, error):
        logger.error(error)
        await ctx.channel.send("[ERROR] " + str(error))

    @tasks.loop(hours=24)
    async def clean_races(self):
        now = datetime.datetime.now()
        for k, race in list(self.races.items()):
            diff = race.timestamp - now
            if diff.day > 0:
                del self.races[k]

        s = ""
        for race in self.races.values():
            s += race.overview() + "\n"

        logger.info("clean up races, rests: \n " + s)


def setup(bot):
    return bot.add_cog(Kiite(bot))
