# DiscordHoldem
DiscordHoldem is a Discord bot for handling Texas Holde'em tables across channels.

What is Discord? ([Discord](https://discordapp.com/))

How to write Discord Bot using Python? ([discord.py](https://github.com/Rapptz/discord.py))

# Screenshots

![Game flow](https://github.com/darkclif/DiscordHoldem/blob/master/media/holdem_1.png)

# How to setup the bot

1. I assume that you already have your BOT account created (if not visit [Discord Developer Panel](https://discordapp.com/developers/applications/))
2. Create file named _token.py in main directory and put there a line *token='YOUR_TOKEN'* where YOUR_TOKEN is a token taken from developer panel.
3. Add bot to your server ([Here is how](https://github.com/jagrosh/MusicBot/wiki/Adding-Your-Bot-To-Your-Server))
4. Run *py main.py*

# Commands

Command | Outcome
--------|--------
!a init | Initialize a poker table on current channel. There can be at most one table opened per channel.
!a close| Close a poker table on current channel. Bot will clean up messages and delete reactions.

After *init* command bot will create three messages and attach available reactions to the middle message.

First and last message are for pushing information. 
First is dedicated to push overall information about a table (player stand or sit; game starting)
Last is dedicated to push information about current game (player raise; fold; game results)

# How to play

Once you created the table you can make interaction with the game by reacting to main message created by bot.

Emoji | Outcome
------|--------
![Sit](https://github.com/darkclif/DiscordHoldem/blob/master/media/reactions/sit.svg)| Sit at the table
![Stand](https://github.com/darkclif/DiscordHoldem/blob/master/media/reactions/stand.svg)| Stand from a table
![Ready](https://github.com/darkclif/DiscordHoldem/blob/master/media/reactions/ready.svg)| Check yourself as ready to play
![Fold](https://github.com/darkclif/DiscordHoldem/blob/master/media/reactions/fold.svg)| Fold 
![Check/Call](https://github.com/darkclif/DiscordHoldem/blob/master/media/reactions/check_call.svg)| Check if no bet was placed or call to current bet
![Raise](https://github.com/darkclif/DiscordHoldem/blob/master/media/reactions/raise.svg)| Raise by amount of Big Blind
![All In](https://github.com/darkclif/DiscordHoldem/blob/master/media/reactions/all_in.svg)| Raise by all your money

To start playing sit at the table and check that you are ready, after period of time the game should start if there is enough ready players at the table. 
You will get your cards in private message. The value of current hand you get in private message will update after each game phase (flop, turn, river).
If you want to leave the game uncheck the ready button and you will be excluded from next game.

# TODO List

- [ ] Make bot handle a tie rounds and rounds where there is all-in player winning the pot.
- [ ] Optimize bot to update messages only once per request.
