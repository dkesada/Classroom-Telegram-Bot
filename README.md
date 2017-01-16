# Telegram bot for student - teacher interaction
This bot is intended for university or highschool use. It serves as a way for the teacher to communicate messages to the students and for them to give feedback without any other platform appart from Telegram.

The teacher can give announcements through the bot to the students and these get to them without any of them knowing each others phone number. In addition, the students can send messages through the bot to the teacher anonymously as a way of giving him feedback or asking questions.

Lastly, the teacher can create a poll through the bot for the students to answer. The results get to the teacher when all students hace answered or when he calls down the poll.

To use it, you have to either execute the python file and have it running in your computer or create a python script and upload it to a server, so that it can be running indefinitely.
Alternatively, the bot saves who has entered your group, so you can power it off and when you power it back on the bot will still have
all the students registered, so it can resume it's normal functioning.

To begin using it, you have to create a Telegram bot with the Bot Father (@botfather) and get a token to put in the TOKEN variable. Here's a guide on creating your first bot https://core.telegram.org/bots if you have any doubts. After that, you can set a password for the teacher and another one for the students, so that when you first contact the bot, it can know wether it's supposed to treat you as the teacher or one of the students.
After you register as the teacher, you should be ready to go to wait for the students to contact the bot.

The bot is coded using the Telegram api and Nickoala's framework for making Telegram bots: Telepot (https://github.com/nickoala/telepot).
This framework has a nice introduction to creating bots, and it helps with various aspects of bot making. Adding new features to the bot is quite simple, so if you have some function you'd like to add, it should be straight forward enough.
