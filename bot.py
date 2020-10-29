from discord.ext import commands
from logging import getLogger, INFO, StreamHandler, Formatter

from kiite import Kiite
from help import Help

# Global variables
TOKEN = 'NzE4NDg0NDEyMTY5MzIyNTc5.Xtpizw.wVWUQG9OLweuwsuggB7yNnlVJDI'
logger = getLogger('kiite')
logger.setLevel(INFO)
handler = StreamHandler()
handler.setFormatter(Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s"))
logger.addHandler(handler)

bot = commands.Bot(command_prefix='!kiite ',
                   description='A bot to open and coordinate some races.',
                   help_command=Help())


@bot.event
async def on_ready():
    logger.info("Logged in as")
    logger.info("Name:" + bot.user.name)
    logger.info("ID: " + str(bot.user.id))
    logger.info('------')

bot.add_cog(Kiite(bot))
bot.run(TOKEN)
