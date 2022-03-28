from discord.ext import commands
import discord
from textwrap import dedent
import json
from dotenv import load_dotenv
import qrcode
import re
import os
import subprocess

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

    @commands.command()
    async def run_snippet(self, ctx):
        """
        Run provided C++ code
        """
        # Get program from message
        command_str = os.getenv("PREFIX") + "run_snippet"
        code: str = ctx.message.content
        # Remove command from message
        code = code.replace(command_str, "")
        # Remove any excess whitespace
        code = code.strip()
        # Remove any '`' characters
        code = code.strip("`")
        # Remove potential leading cpp code specifier
        code = code.lstrip("Ccp+")

        # Prevent use of bad actors in code
        # Uncomment if running on your local system.
        # I run this in a docker container locally, so there's
        # no risk of damage to my own system
        '''
        if re.search("system\(|fork\(|[oi]?fstream|fopen\(|FILE", code):
            await ctx.message.reply(dedent(
                """
                You have a call to one of the following:
                `system`
                `fork`
                `File operations such as fstream or fopen`
                somewhere in your code, which is not allowed. Run the code yourself if you want to test it.
                """
            ))
            return
        '''

        # Finally, output to a file and compile using g++
        with open("program.cpp", "w+") as source:
            source.write(code)

        try:
            result = subprocess.run(["g++", "--std=c++17", "-Wall", "-Wfatal-errors", "program.cpp"], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            # Alert user to compile errors
            await ctx.message.reply("Double-check your code, there was a compile error:\n```\n" + e.stdout + "\n```")
            os.remove("program.cpp")
            return

        with open("output.txt", "w+") as output:
            try:
                result = subprocess.run(["./a.out"], check=True, stdout=output, stderr=subprocess.STDOUT, universal_newlines=True, timeout=8)
            except subprocess.CalledProcessError as e:
                # Alert user to program exiting abnormally
                await ctx.message.reply("Your code died horribly:\n```\n" + e.output + "```")
            except subprocess.TimeoutExpired:
                # Alert user to program taking too long
                await ctx.message.reply("Your code took too long to run.")

        output_file = discord.File("output.txt")
        await ctx.message.reply(file=output_file)

        os.remove("output.txt")
        os.remove("program.cpp")
        os.remove("a.out")