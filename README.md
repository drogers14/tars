# TARS
Python-powered Discord bot with rudimentary chat capabilities.

## Developing locally
### Requirements:
Python 3.10

### Running
```
pip install -r requirements.txt
python bot.py
```

I strongly recommend creating a virtual environment if you plan to develop
on your local machine.  

This bot also contains a function that allows for arbitrary code execution (ACE)
in [cogs/functions.py](cogs/functions.py). Be sure to uncomment the block
which analyzes potential bad actors if you run this locally, instead of in a
virtual machine or Docker container.  

A Makefile is provided if you wish to build and run a Docker image/container
based on this project. Simply create a `.env` file with your bot's private token
and the command prefix you wish to use. For example:
```
TOKEN=<your_very_long_discord_bot_private_token>
PREFIX=%
```

Then run
```
make
make run
```