import imp
from pprint import PrettyPrinter
from discord.ext import commands
import discord
from textwrap import dedent
import json
from dotenv import load_dotenv
import qrcode
import re
import os

load_dotenv()

PREFIX = os.getenv("PREFIX")

class Functions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def printing(self, ctx):
        """
        3D printing resources
        """
        await ctx.message.reply(
            dedent(
                """
                Slicing software:
                - Cura: <https://ultimaker.com/software/ultimaker-cura>
                - Slic3r: <https://slic3r.org/>
                - PrusaSlicer: <https://www.prusa3d.com/page/prusaslicer_424/>
                
                STL Files:
                - Thangs: <https://thangs.com/>
                - Thingiverse: <https://www.thingiverse.com/>

                3D Printing help:
                > Always feel free to ask here, if you need to. Ping Asterisk too, he's got a fair amount of knowledge.
                - Prusa Forums (more specific to Prusa printers): <https://forum.prusaprinters.org/>
                - Ender 3 Series forums on Creality: <https://forums.creality3dofficial.com/community/ender-3-series/>
                """
            )
        )

    @commands.command()
    async def qr(self, ctx):
        """
        Create a QR code

        Args:
        text: plain text or URL string
        settings: plain text argument preceded by double-dash (--)
            Options are:
            - border: int
            - fill_color/fill/fg/foreground: rgb tuple, i.e. (RRR, GGG, BBB)
            - back_color/back/bg/background: rgb tuple, i.e. (RRR, GGG, BBB)
        
        ex. > qr text fill (120, 120, 120) back (255, 255, 255)
        """
        # Default QR code settings
        fg_color = (0, 0, 0)
        bg_color = (255, 255, 255)
        border = 2

        # The entire command
        message_text = ctx.message.content

        # Text to be encoded (can be plain text or URL)
        text = message_text
        # Remove command prefix and options, leaving only the text
        text = text.replace(f"{PREFIX}qr", "")
        text = re.subn(r"--\w+ \(\d{1,3}, ?\d{1,3}, ?\d{1,3}\)|--\w+ \d+", "", text)[0]
        text = text.strip()

        # Ensure there is text to encode
        if not text:
            await ctx.message.reply("I need text to put into a QR code.")
            return

        print(f"Searching {message_text} for args")
        # Get arguments for command, if any
        settings = re.findall(r"(--\w+) (\(\d{1,3}, ?\d{1,3}, ?\d{1,3}\)|\d+)", message_text)
        if settings:
            # Each arg must have a corresponding value, otherwise return an error
            for opt in settings:
                if (len(opt)%2 != 0):
                    await ctx.message.reply("One or more of your arguments doesn't have a value attached. Double check your command!")
                    return
    
            for opt in settings:
                if opt[0] in ["--fill", "--fill_color", "--fg", "--foreground"]:
                    fg_color = eval(opt[1])
                elif opt[0] in ["--back", "--back_color", "--bg", "--background"]:
                    bg_color = eval(opt[1])
                elif opt[0] in ["--border"]:
                    border = eval(opt[1])

        # Final code generation
        qr = qrcode.QRCode(
            border=border
        )
        qr.add_data(text)
        img = qr.make_image(fill_color=fg_color, back_color=bg_color)
        # Save image to system temporarily while it gets attached to this reply
        img.save("qrcode.png")
        file = discord.File("qrcode.png")
        await ctx.message.reply(file=file, content=f"Here's your QR code for '{text}':")
        # Remove it once that's completed
        os.remove("qrcode.png")