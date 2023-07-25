# Database connection
import sqlite3
from typing import Optional
# import csv

# discordpy library for bot
import discord
# discordpy used for bot.tree.command
from discord.ext import commands

import typing

from discord import app_commands
from discord.app_commands import Choice

import random
import asyncio
import traceback

# myenv\Scripts\activate to go into virtal envi

# discord bot token to talk with code
TOKEN = "MTEyMTYyMzc0NzY0OTA5MzYzMg.GToqgQ.yi37Pehcy8H47fksB-VfspND4z90Obo57ysvfo"

# send connection for quizQuestions
def get_QT_connection():
    connection = sqlite3.connect('quizQuestions.db')
    return connection

def get_LB_connection():
    connection = sqlite3.connect('leaderboard.db')
    return connection


# ------------------------------------------------------------------------

# check if user is in the leaderboard and return that row
# if user is not in leaderboard row returns with a 0 value
def check_user(userName):
    connection = get_LB_connection()
    cursor = connection.cursor()


    select_query = "SELECT user FROM leaderboard WHERE user = ?"
    val = userName
    cursor.execute(select_query, [val])
    rows = cursor.fetchall()

    connection.close()
    return rows

# ------------------------------------------------------------------------

# Discord user name is set to check if user has been added already
# if user is added already returns " was added"
# else returns " is already added!"
def set(userName):
    connection = get_LB_connection()
    cursor = connection.cursor()
    qs = ''

    rows = check_user(userName)
    
    if len(rows) == 0:
        sql = "INSERT INTO leaderboard (user, user_diff, points) VALUES (?,?,?)"
        val = (userName, 'easy',0)
        cursor.execute(sql, val)
        connection.commit()
        sql = "INSERT INTO leaderboard (user, user_diff, points) VALUES (?,?,?)"
        val = (userName, 'hard',0)
        cursor.execute(sql, val)
        connection.commit()
        qs += userName + " was added!"
    else:
        qs += userName + " is already added!"
        

    connection.close()
    return qs

# ------------------------------------------------------------------------

# Gets user points from leaderboard
# Checks if user is in leaderboard first
# then runs SQL command to find User and Points
def get_points(userName, difficulty):
    connection = get_LB_connection()
    cursor = connection.cursor()
    qs = ''

    
    rows = check_user(userName)
    if len(rows) == 0:
        qs += "You have to run the $joinQuiz command first!"
        return qs

    sql = "SELECT user, points FROM leaderboard WHERE (user = ? AND USER_DIFF = ?)"
    val = userName, difficulty
    cursor.execute(sql, val)
    rows = cursor.fetchall()

    qs += "Difficulty: " + difficulty + "\n"
    for user, points in rows:
        qs += "{} has {} points!".format(user, points)   
    
    connection.close()
    return qs

# ------------------------------------------------------------------------

# Returns the first 10 users in leaderboard
# future idea is to set up the menu system 
def get_leaderboard(difficulty):
    connection = get_LB_connection()
    cursor = connection.cursor()
    leaderBoard = ''
    id = 1

    select_query = "SELECT * FROM leaderboard WHERE USER_DIFF = ? ORDER BY points DESC LIMIT 10"
    cursor.execute(select_query, [difficulty])
    scores = cursor.fetchall()

    leaderBoard += "Difficulty: " + difficulty + "\n"
    for item in scores:
        # leaderBoard += str(id) + '. ' + item[0] + ": " + item[1] + " score " + str(item[2]) + "\n"
        leaderBoard += str(id) + '. ' + item[0] + ": " + str(item[2]) + " points. \n"
        id += 1

    connection.close()
    return leaderBoard

# ------------------------------------------------------------------------

# Gets Discord Name and gameScore
# Checks if gameScore is higher, same, or lower than user points
# If gameScore is higher than current user points, update leaderboard table
def highScore(userName, gameScore, difficulty):
    connection = get_LB_connection()
    cursor = connection.cursor()
    msq = ''
    userScore = ''
    difficulty = difficulty.lower()

    # and WHERE diff = "Easy or Hard"
    sql = "SELECT user, points FROM leaderboard WHERE (user = ? AND USER_DIFF = ?)"
    val = userName, difficulty
    cursor.execute(sql, val)
    rows = cursor.fetchall()
    
    for x in rows:
        userScore = x[1]
       
    # if gameScore is higher than userScore update leaderboard table with new value
    # return there has been a new high score
    if gameScore > userScore:
        # update score in database
        sql = "UPDATE leaderboard SET points= ? WHERE (user = ? AND USER_DIFF = ?)"
        values = (gameScore, userName, difficulty)
        cursor.execute(sql, values)
        connection.commit()

        msq += str(userName) + " has a new high score! Total points: " + str(gameScore)
        
    # if gameScore equals userScore return high score has been tied with 
    elif gameScore == userScore:
        msq += str(userName) + " tied with their current high score of " + str(userScore)
        
    # if gameScore is less than userScore return gameScore and high score
    elif gameScore < userScore:
        msq += str(userName) + " your score is " + str(gameScore) + "! Your high score is: " + str(userScore)
        
    connection.close()
    return msq
    
    # ---------------------------------------------------------------------------

# ------------------------------------------------------------------------

def get_questionID_list(difficulty):
    connection = get_QT_connection()
    cursor = connection.cursor()

    questID = []
    select_list = "SELECT ID FROM quiz WHERE DIFFICULTY = ? ORDER by RANDOM() limit 50"
    cursor.execute(select_list, [difficulty])
    results = cursor.fetchall()

    for x in results:
        questID.append(x[0])

    cursor.close()

    return questID

# Question returns Random Question from quiz table
# returns: questID, qs, answerList, realAnswer
def get_question(randomID):
    connection = get_QT_connection()
    cursor = connection.cursor()

    questID = ''
    qs = ''
    answerList = ''
    realAnswer = ''
    id = 1
    counter = 0


    # From data base choice a random row
    # select_query = "SELECT * FROM Quiz generateRandomRow order by RANDOM() limit 1 WHERE DIFFICULTY = 'Easy'"
    # select_query = "SELECT * FROM quiz WHERE DIFFICULTY = ? ORDER by RANDOM() limit 1"
    select_query = "SELECT * FROM quiz WHERE ID = ? "
    # send SQL code to database
    cursor.execute(select_query, [randomID])
    # fetch the whole row and save it to result
    result = cursor.fetchall()

    # if row[5] is empty return real and false answer
    # return 1.True 2. False

    for row in result:
        qs += "**Question:** \n"
        qs += row[2]
        answer = []
        questype = 0

        #[(0, 'ID', 'INTEGER', 0, None, 1), (1, 'DIFFICULTY', 'TEXT', 1, None, 0), 
    # (2, 'QUESTION', 'TEXT', 1, None, 0), (3, 'RANSWER', 'TEXT', 1, None, 0), 
    # (4, 'FANSWER1', 'TEXT', 1, None, 0), (5, 'FANSWER2', 'TEXT', 1, None, 0), 
    # (6, 'FANSWER3', 'TEXT', 1, None, 0)]

        # checks if column 5 is empty if it is only record 2 answers 
        # return questype 2 to only display 2 buttons
        if row[5] == '':
            questype = 2
            while counter < 2:
                r = random.randint(3, 4)
                if r not in answer:
                    answerList += str(id) + ". " + row[r] + "\n"
                    if row[r] == row[3]:
                        temp = id
                        # store the correct answer
                        realAnswer = temp
                        

                    id += 1
                    counter += 1
                    answer.append(r) 
        else:
            questype = 4
            while counter < 4:
                r = random.randint(3, 6)
                if r not in answer:
                    answerList += str(id) + ". " + row[r] + "\n"
                    if row[r] == row[3]:
                        temp = id
                        # store the correct answer
                        realAnswer = temp
                        

                    id += 1
                    counter += 1
                    answer.append(r)       
    
    connection.close()
    return qs, answerList, realAnswer, questype

# Class returns buttons for multiple choice questions
class multi_choice(discord.ui.View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.value = None

    @discord.ui.button(label='1', style=discord.ButtonStyle.success)
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = 1
        self.stop()
    
    @discord.ui.button(label='2', style=discord.ButtonStyle.success)
    async def count2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = 2
        self.stop()
    
    @discord.ui.button(label='3', style=discord.ButtonStyle.success)
    async def count3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = 3
        self.stop()
    
    @discord.ui.button(label='4', style=discord.ButtonStyle.success)
    async def count4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = 4
        self.stop()


    @discord.ui.button(label='Quit', style=discord.ButtonStyle.red)
    async def quitQuiz(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = "quit"
        self.stop()


# Class returns buttons for True And False Questions
class trueFalse_choice(discord.ui.View):
    def __init__(self,timeout):
        super().__init__(timeout=timeout)
        self.value = None

    @discord.ui.button(label='1', style=discord.ButtonStyle.success)
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = 1
        self.stop()
    
    @discord.ui.button(label='2', style=discord.ButtonStyle.success)
    async def count2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = 2
        self.stop()
    
    @discord.ui.button(label='Quit', style=discord.ButtonStyle.red)
    async def quitQuiz(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = "quit"
        self.stop()


    
    

# Class returns Quit button for just start of quiz
class quit_choice(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Quit', style=discord.ButtonStyle.red)
    async def quitQuiz(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = "quit"
        self.stop()
# ------------------------------------------------------------------------

# set_Question takes the questions difficulty, questions text, the correct answer, and either one false 
# for True and False answers or 3 false answers for multiple choice
# Saves values in DB which can be access through DBBrowser (SQlite) version
def set_question(difficulty, question, correct_answer, false_answer_1,false_answer_2,false_answer_3):
    connection = get_QT_connection()
    cursor = connection.cursor()
    # when making function to pass to DB. Set up True and False questions as
    # "True or False: + question"
    

    endMark = (".", " ", "!", ";", ":")
    checkQuestionMark = question[len(question)-1]
    if checkQuestionMark == '?':
        pass
    elif checkQuestionMark not in endMark:
        question += "?"
    elif checkQuestionMark in endMark:
        temp = question.rstrip(question[-1])
        question = temp + "?"

    if (false_answer_2 and false_answer_3) == None:
        false_answer_2 = ''
        false_answer_3 = ''

        question = "True or False: \n" + question

        tail_grab = "SELECT * FROM quiz ORDER BY ID DESC limit 1"
        cursor.execute(tail_grab)
        temp = cursor.fetchall()

        for x in temp:
            last_ID = x[0]
        new_ID = last_ID + 1

        insert_query = """
        INSERT INTO quiz(ID, DIFFICULTY, QUESTION, RANSWER, FANSWER1, FANSWER2, FANSWER3) 
        VALUES(?, ?, ?, ?, ?, ?, ?)
        """
        values = (new_ID, difficulty, question, correct_answer, false_answer_1,false_answer_2,false_answer_3)
        cursor.execute(insert_query, values)

        connection.commit()

        tail_grab = "SELECT * FROM quiz ORDER BY ID DESC limit 1"
        cursor.execute(tail_grab)
        temp = cursor.fetchall()
        print(temp)        

        return new_ID

    tail_grab = "SELECT * FROM quiz ORDER BY ID DESC limit 1"
    cursor.execute(tail_grab)
    temp = cursor.fetchall()

    for x in temp:
        last_ID = x[0]
    new_ID = last_ID + 1

    
    insert_query = """
        INSERT INTO quiz(ID, DIFFICULTY, QUESTION, RANSWER, FANSWER1, FANSWER2, FANSWER3) 
        VALUES(?, ?, ?, ?, ?, ?, ?)
    """
    values = (new_ID, difficulty, question, correct_answer, false_answer_1,false_answer_2,false_answer_3)
    cursor.execute(insert_query, values)
    connection.commit()

    return new_ID
    

# ------------------------------------------------------------------------

# Start of bot commands saved in a tree allowing the user to type "/"
# which shows all the commands able to be used.
# bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
class TheClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

intents = discord.Intents.all()
bot = TheClient(intents = intents)


@bot.event
async def on_ready():
    # print("Bot is ready")
    try:
        synced = await bot.tree.sync()
        # print(f"Synced {len(synced)} commands(s)")
    except Exception as e:
        print(e)

# ------------------------------------------------------------------------

@bot.tree.error
async def on_app_command_error(interaction, exc):
    print(f"{interaction.command.name} failed with error: {exc}")
    try:
        await interaction.response.send_message("Something went wrong...")
    except:
        pass
    await interaction.channel.send(f"Command `{interaction.command.name}` failed to execute.\nSending error report...")
    error_traceback = traceback.format_exception(type(exc), exc, exc.__traceback__) #C: Generates the Traceback of the command for greater detail.

    error_message = (f"{interaction.command.name} encountered the error: {exc}\nTraceback:\n{''.join(error_traceback)}\n\nTriggerer {interaction.user.mention}")

    num_chunks = (len(error_message) + 1899) // 1900

    dragonCoo = bot.get_user(535296675988897797)
    for i in range(num_chunks):
      chunk = error_message[i*1900:(i+1)*1900]
      await dragonCoo.send(f'```python\n{chunk}```')


# ------------------------------------------------------------------------
@bot.tree.command(name="joinquiz", description="Must run first as a first timer! It tracks your score to /leaderboard!")
async def joinQuiz(interaction: discord.Interaction):
    userName = interaction.user.name
    msq = set(userName)
    try:
        await interaction.response.send_message(msq)
    except Exception as error:
        if isinstance(error, discord.NotFound):
            if error.code== 10062:
                pass

# ------------------------------------------------------------------------

@bot.tree.command(name='quizhelp', description = "Shows all the commands to help you out in your quizy journey!")
async def helpcommand(intration: discord.Integration):
    # commands = [command.name for command in bot.tree.get_commands()]
    # temp = [command.description for command in bot.tree.get_commands()]
    # print(temp)

    embed = discord.Embed(title='Rules: ', description="Each Question will be given at random from either the Easy or Hard pool. You will have __1min__ to finish each question before it's marked "\
                          "wrong. Your goal is to last as long as you can until you run out of __Health Points which you start with 10__ when the quiz starts. \n" \
                        "To get higher on the leaderboard you have to beat your last run, which is to answer that many questions right before you run out of lives.", 
                        color=discord.Color.blue())
    for command in bot.tree.get_commands():
        embed.add_field(name=f"/{command.name}", value=command.description, inline=False)
    try:
        await intration.response.send_message(embed=embed)
    except Exception as error:
        if isinstance(error, discord.NotFound):
            if error.code== 10062:
                pass
# ------------------------------------------------------------------------

@bot.tree.command(name="points", description="Show your highscore for either Easy or Hard mode!")
@app_commands.choices(diff=[
    Choice(name='Easy', value='easy'),
    Choice(name='Hard', value='hard')
])
async def points(interation: discord.Interaction, diff: discord.app_commands.Choice[str]):
    userName = interation.user.name
    diff = diff.value
    try:
        msq = get_points(userName, diff)
        await interation.response.send_message(msq)
    except Exception as error:
        if isinstance(error, discord.NotFound):
            if error.code== 10062:
                pass
    
# ------------------------------------------------------------------------

@bot.tree.command(name="leaderboard", description="Shows the top 10 highscores for Easy or Hard mode!")
@app_commands.choices(diff=[
    Choice(name='Easy', value='easy'),
    Choice(name='Hard', value='hard')
])
async def leaderboard(interaction: discord.Interaction, diff: discord.app_commands.Choice[str]):
    difficulty = diff.value
    try:
        leaderBoard = get_leaderboard(difficulty)
        await interaction.response.send_message(leaderBoard)
    except Exception as error:
        if isinstance(error, discord.NotFound):
            if error.code== 10062:
                pass

    
# ------------------------------------------------------------------------

@bot.tree.command(name="question", description="Start your quiz challange! Remember only 1min per question.")
@app_commands.choices(diff=[
    Choice(name='easy', value='Easy'),
    discord.app_commands.Choice(name='hard', value='Hard')
])
async def question(interaction: discord.Interaction, diff: discord.app_commands.Choice[str]):
    difficulty = diff.value
    # print(difficulty)
    health = 10
    gameScore = 0
    

    userName = interaction.user.name
    rows = check_user(userName)
    if len(rows) == 0:
        qs = "You have to run the /joinQuiz command first!"
        await interaction.response.send_message(qs)
        return
    
    # print(usedQuest)
    embed = discord.Embed(
        title='Zenith Quiz',
        description=f"""
            Hello! Welcome to the Quiz of Zenith. You have selected {difficulty} difficulty! \n
            You have **10 health points** and you have **1 min** to answer each question. \n 
            After **1 min** the question will be marked wrong.
        """,
        color=discord.Color.blue()
    )

    embed.add_field(name='__You can quit the quiz at any time by hitting the "Quit" button.__', value="")
   

    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    await asyncio.sleep(10)

    # gets the first set of question ID's to choice from
    question_ID = get_questionID_list(difficulty)
    while health > 0:
        # questID, qs, answerList, realAnswer, questype = check_ID(usedQuest, difficulty)
        
        # if question_ID list length is 0
        # call get_questionID_list() to grab a new set of question IDs
        if len(question_ID) == 0:
            question_ID = get_questionID_list(difficulty)
        else:
            # if question_ID list isn't empty pop the one on top first
            questID = question_ID.pop()
            # Then pass the popped ID into get_question()
            qs, answerList, realAnswer, questype = get_question(questID)


        
        if questype == 4:
            view = multi_choice(timeout = 60.0)
        elif questype == 2:
            view = trueFalse_choice(timeout = 60.0)
        elif questype == 0:
            print("ERROR ERROR")

        # print(usedQuest)
        embed = discord.Embed(
            title='Zenith Quiz ' + "\t\t\tScore: " + str(gameScore),
            color=discord.Color.blue()
        )

        if difficulty == 'Easy':
            url = "https://cdn.discordapp.com/attachments/1044235479903633438/1127412631448326184/pixil-frame-0.png"
        elif difficulty == 'Hard':
            url = "https://cdn.discordapp.com/attachments/1044235479903633438/1127412631909703731/pixil-frame-1.png"


        embed.set_thumbnail(url=url)
        # embed.add_field(name='Points: ' + str(points), value='')
        embed.add_field(name=qs, value='>>> ' + answerList, inline=False)

        try:
            await interaction.edit_original_response(content=(""), embed=embed, view=view)
            
            await asyncio.sleep(1)
            await view.wait()
        except Exception as error:
            if isinstance(error, discord.NotFound):
                if error.code== 10062:
                    pass
     
        if view.value == 'quit':
            break
        elif view.value == realAnswer:
            gameScore += 1 
            answerEmbed = discord.Embed(
                title= str(interaction.user.name) + ' got it right! You got 1 point!' + '\nCurrent Score: ' + str(gameScore),
                color = discord.Color.green()
            )
        else:
            health = health - 1
            answerEmbed = discord.Embed(
                title= "Sorry that was the wrong answer! \n" \
                    "You have " + str(health) + " health point remaining. \n",
                color = discord.Color.red()
            )

        await interaction.edit_original_response(content=(''), embed=answerEmbed, view=None)
        await asyncio.sleep(1.5)
        # await guess.delete()

    drift_messages = ("The night holds its secrets close, and I am the keeper of its darkest truths.", 
                      "Lost in the labyrinth of your mind, I am the guide to your deepest fears.",
                      "Fear not the darkness, for within it lies the answers you seek.",
                      "In the realm of the unknown, I am the gatekeeper to the mysteries that lie beyond.",
                      "Do you believe in fate? Or do you think it can be rewritten with a single twist of destiny?",
                      "The clock is ticking, and with each passing second, I grow stronger. Can you hear it? Tick-tock, tick-tock...",
                      "Way to go! You're on fire!",
                      "Fantastic job! You've really outdone yourself this time!",
                      "Hip, hip, hooray! You've successfully finished. Keep up the fantastic work!",
                      "Congratulations! You did it! Great job!",
                      "Hooray! You completed the quiz with flying colors!",
                      "Well played! Your quiz success is truly impressive!",
                      "Oh, congratulations, you've reached the pinnacle of human intelligence.",
                      "Well, aren't you just a fountain of knowledge? I'm in awe.",
                      "Oh, please enlighten me with your unmatched wisdom. I'm on the edge of my virtual seat.",
                      "Well, color me impressed! I had no idea someone could be so adept at stating the obvious.",
                      "Oh, thank you for gracing me with your presence. I'm truly honored to be in the presence of greatness.",
                      "Oh, look who's here to save the day with their unparalleled problem-solving skills. Impressive!",
                      "Wow, you're really making progress. It only took you twice as long as everyone else!",
                      "Bravo! Your genius idea is truly out of this world. I mean, literally, it's so far-fetched.",
                      "Great job!",
                      "Well done!",
                      "You nailed it!",
                      "Fantastic work!",
                      "Outstanding performance!",
                      "Impressive effort!",
                      "Bravo!",
                      "You've exceeded expectations!",
                      "You're a rock star!",
                      "You're amazing!"
                      )
    random_Drift_Message = random.choice(drift_messages)

    embed2 = discord.Embed(
        title=random_Drift_Message,
        color=discord.Color.blue()
    )
    endMessage = highScore(userName, gameScore, difficulty)
    embed2.add_field(name = endMessage, value='')
    
    await interaction.edit_original_response(content=(''), embed=embed2, view=None)
    return

# ------------------------------------------------------------

@bot.tree.command(name="createquestion", description="Add your very own questions to the quiz pool!")
@app_commands.describe(
  question="The question's question",
  correct_answer="The question's correct answer",
  difficulty="Easy or Hard?",
  false_answer_1="The first false answer (if you only set one false, then it'll be a true or false question",
  false_answer_2="The second false answer",
  false_answer_3="The final incorrect answer"
)
async def question(interaction: discord.Interaction, difficulty: typing.Literal["Easy", "Hard"], question: str, correct_answer: str, false_answer_1: str, false_answer_2: str = None, false_answer_3: str = None):
    yes_list = ("yes", "y", "yes please", "yup", "yea")
    no_list = ("no", "no thanks", "nope")
    
    
    what_kind_of_question = 0 # 0 means multiple choice, 1 means true or false, 2 means invalid
    if false_answer_2 is None and false_answer_3 is None:
        what_kind_of_question = 1
    elif false_answer_2 is None and false_answer_3 is not None:
        what_kind_of_question = 2
    elif false_answer_2 is not None and false_answer_3 is None:
        what_kind_of_question = 2

    if what_kind_of_question == 2:
        await interaction.response.send_message(f"Invalid question. You need to set either just **false_answer_1** or both **false_answer_2 and false_answer_3**.")
        return
   
    if what_kind_of_question == 1:
        if correct_answer.lower() != "true" and correct_answer.lower() != "false":
            await interaction.response.send_message(f"Invalid question. You need to have the correct answer to be True or False.")
        elif false_answer_1.lower() != "true" and false_answer_1.lower() != "false":
            await interaction.response.send_message(f"Invalid question. You need to have the false answer to be True or False.")
        else:
            correct_answer = correct_answer.capitalize()
            false_answer_1 = false_answer_1.capitalize()
            await interaction.response.send_message(embed=discord.Embed(
                title="Do you want to enter this True or False question? \n"\
                    "Please type (yes/no).", 
                description=f"Difficulty: {difficulty}\nQuestion: {question}\nCorrect answer: {correct_answer}\nFalse answer 1: {false_answer_1}"), ephemeral=True)
            try:
                msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author.id == interaction.user.id)
                print("works")
            except asyncio.TimeoutError:
                await interaction.response.edit_message('User time out...')
                return
            else:
                if msg.content.lower() in yes_list:
                    await interaction.delete_original_response()
                    user_ID = set_question(difficulty, question, correct_answer, false_answer_1,false_answer_2,false_answer_3)
                    await interaction.channel.send(f"Question has been saved! \nYour question ID is: {user_ID}.")
                elif msg.content.lower() in no_list:
                    await interaction.delete_original_response()
                    await interaction.channel.send('Please retype **/createquestion** to make a new question.')
                else:
                    await interaction.channel.send("Miss input from user. Drift is getting closer.")
                await msg.delete()
                return
    else:
        await interaction.response.send_message(embed=discord.Embed(
            title="Do you want to add this multiple choice question?\n"\
                "Please type (yes/no).", 
            description=f"Difficulty: {difficulty}\nQuestion: {question}\nCorrect answer: {correct_answer}\nFalse answer 1: {false_answer_1}\nFalse answer 2: {false_answer_2}\nFalse answer 3: {false_answer_3}"))
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author.id == interaction.user.id)
        except asyncio.TimeoutError:
            await interaction.channel.send('User time out...')
            return
        else:
            if msg.content.lower() in yes_list:
                await interaction.delete_original_response()
                
                user_ID = set_question(difficulty, question, correct_answer, false_answer_1,false_answer_2,false_answer_3)
                await interaction.channel.send(f"Question has been saved! \nYour question ID is: {user_ID}.")
            elif msg.content.lower() in no_list:
                await interaction.delete_original_response()
                await interaction.channel.send('Please retype **/createquestion** to make a new question.')
            else:
                await interaction.channel.send("Miss input from user. Drift is getting closer.")
            await msg.delete()
            return

# ------------------------------------------------------------------------

# @bot.tree.command(name = "drift_error", description="Test command for error handling")
# async def test_error(interaction: discord.Interaction):
#     await interaction.response.send_message("Generating error...")
#     _ = int("Hello!")

# ------------------------------------------------------------------------


bot.run(TOKEN)