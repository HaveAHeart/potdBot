import configparser
import math
import os
import random
import re
import sched
import threading
import time

import nhentai
import psycopg2
import requests
import vk_api
import vk_api.upload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

config = configparser.ConfigParser()
config.read('params.ini')
tkn = config['VK_MSG']['token']
session = config['VK_MSG']['session']
key = config['VK_MSG']['key']
server = config['VK_MSG']['server']
ts = config['VK_MSG']['ts']

s = sched.scheduler(time.time, time.sleep)

# TODO - move all the phrases to the outer .txt files
# TODO - add requirements to the outer .txt file

# DAILY POTD sources
# if the new potd has been just chosen
with open('src/dailyNew.txt', 'r', encoding="utf-8") as f:
    dailyNewPatterns = f.readlines()
# if the potd was already rolled today
with open('src/dailyResult.txt', 'r', encoding="utf-8") as f:
    dailyResultPatterns = f.readlines()
# random pre-result intro message
with open('src/dailyRandom.txt', 'r', encoding="utf-8") as f:
    dailyRandomMsg = f.readlines()
# other text sources for daily rolling
with open('src/dailyUtility.txt', 'r', encoding="utf-8") as f:
    dailyUtility = f.readlines()

# STATS sources
# line patterns for result
with open('src/statPatterns.txt', 'r', encoding="utf-8") as f:
    statPatterns = f.readlines()
# other text sources for stats
with open('src/statUtility.txt', 'r', encoding="utf-8") as f:
    statUtility = f.readlines()

# REGISTRATION sources
# line patterns for successful registration
with open('src/regSucPatterns.txt', 'r', encoding="utf-8") as f:
    regSucPatterns = f.readlines()
# line patterns for failed registration
with open('src/regFailPatterns.txt', 'r', encoding="utf-8") as f:
    regFailPatterns = f.readlines()

# ANNUAL POTD sources
# if the annual potd has been just chosen
with open('src/annualNew.txt', 'r', encoding="utf-8") as f:
    annualNewPatterns = f.readlines()
# if the annual potd was already rolled this year
with open('src/annualResult.txt', 'r', encoding="utf-8") as f:
    annualResultPatterns = f.readlines()

# HELP sources
# help message
with open('src/helpMsg.txt', 'r', encoding="utf-8") as f:
    helpMsg = "\n".join(f.readlines())

# PATHETIC sources
# morgenstern messages
with open('src/morgenMsg.txt', 'r', encoding="utf-8") as f:
    morgenMsg = f.readlines()
# mashup messages
with open('src/patheticMsg.txt', 'r', encoding="utf-8") as f:
    packeticMsg = f.readlines()
# mashup ids - audio and owner
with open('src/mashupList.txt', 'r', encoding="utf-8") as f:
    mashupList = []
    tmp = f.readlines()
    for idPair in tmp:
        mashupList.append([idPair.split(" ")])

# BONK sources
# bonk if no target is chosen
with open('src/soloBonk.txt', 'r', encoding="utf-8") as f:
    soloBonkMsg = f.readlines()
# bonk if there is a target
with open('src/duoBonk.txt', 'r', encoding="utf-8") as f:
    duoBonkMsg = f.readlines()

# HORNY sources
# intro messages
with open('src/horny_intro.txt', 'r', encoding="utf-8") as f:
    hornyFirstMsg = f.readlines()
# service stuff for link/errors
with open('src/hornyUtility.txt', 'r', encoding="utf-8") as f:
    hornyUtility = f.readlines()

# ROLL sources
# intro messages
with open('src/rollIntro.txt', 'r', encoding="utf-8") as f:
    rollIntro = f.readlines()
# messages with results
with open('src/rollMsg.txt', 'r', encoding="utf-8") as f:
    rollMsg = f.readlines()


def get_horny_att(vk_upload, tn):
    response = requests.get(tn)
    file = open("tmp_dj_tn.jpg", "wb")  # TODO - do smth with var names
    file.write(response.content)
    file.close()

    ph = vk_upload.photo_messages("tmp_dj_tn.jpg")
    owner = ph[0].get('owner_id')
    media = ph[0].get('id')
    accessKey = ph[0].get('access_key')
    att = "photo{}_{}_{}".format(owner, media, accessKey)

    os.remove("tmp_dj_tn.jpg")
    return att


def register(conn, userid, chatid, name, surname):
    sql = "SELECT * FROM pidorbot.register(%s, %s, %s, %s);"
    print('кто-то регается...\n')

    cur = conn.cursor()
    cur.execute(sql, (userid, chatid, name, surname))
    conn.commit()
    row = cur.fetchone()
    cur.close()
    return row


def randomize(conn, chatid):
    sql = "SELECT * FROM pidorbot.randomize(%s);"
    print('кто-то рандомит обычного...\n')

    cur = conn.cursor()
    cur.execute(sql, (chatid,))
    conn.commit()
    ret = cur.fetchone()
    cur.close()
    return ret


def godovaliy(conn, chatid):
    sql = "SELECT * FROM pidorbot.godovaliy(%s);"
    print('кто-то рандомит годовалого...\n')

    cur = conn.cursor()
    cur.execute(sql, (chatid,))
    conn.commit()
    ret = cur.fetchone()
    cur.close()
    return ret


def stats(conn, chatid):
    sql = "SELECT * FROM pidorbot.stats(%s);"
    print('кто-то просит стату...\n')

    cur = conn.cursor()
    cur.execute(sql, (chatid,))
    conn.commit()
    ret = []
    row = cur.fetchone()
    while row is not None:
        ret.append(row)
        row = cur.fetchone()
    cur.close()
    return ret


def send_vk_msg(vk, event, msg, attachment):
    if attachment is None:
        vk.messages.send(
            key=key,
            server=server,
            ts=ts,
            random_id=get_random_id(),
            message=msg,
            chat_id=event.chat_id
        )
    else:
        vk.messages.send(
            key=key,
            server=server,
            ts=ts,
            random_id=get_random_id(),
            message=msg,
            attachment=attachment,
            chat_id=event.chat_id
        )


def get_name(vk, from_id):
    info = vk.users.get(user_ids=from_id)[0]
    return [info.get('first_name'), info['last_name']]


def get_dj_and_cover(vk_upload):
    djId = nhentai.get_random_id()
    dj = nhentai.get_doujin(djId)

    tn = dj.thumbnail
    att = get_horny_att(vk_upload, tn)

    tags_raw = dj.tags
    artists = []
    tags = []
    langs = []
    hmsg = ""
    for tag in tags_raw:
        if tag.type == 'tag':
            tags.append(tag.name)
        if tag.type == 'language':
            langs.append(tag.name)
        if tag.type == 'artist':
            artists.append(tag.name)
    hmsg = hmsg + 'Авторы: ' + ", ".join(artists) + "\n"
    hmsg = hmsg + 'Языки: ' + ", ".join(langs) + "\n"
    hmsg = hmsg + 'Тэги: ' + ", ".join(tags) + "\n"
    return [hmsg, att, djId]


def friday(vk, cid):  # piwas exclusive
    vk.messages.send(
        key=key,
        server=server,
        ts=ts,
        random_id=get_random_id(),
        message='С пятницей, господа!',
        chat_id=cid
    )
    print('С пятницей, работяги!')


def getTimeUntilFriday():
    targetTime = (24 + 20) * 60 * 60  # next day(Fri), 19:00
    timeFromTarget = ((time.time() + (60 * 60 * 3) - targetTime) % (60 * 60 * 24 * 7))  # GMT +03:00
    print(timeFromTarget)
    timeUntilTarget = (60 * 60 * 24 * 7) - timeFromTarget
    print(timeUntilTarget)
    return round(timeUntilTarget)


def runFriday(vk):
    while True:
        timeUntilFriday = getTimeUntilFriday()
        print('Friday timer is set, time until message - ' + str(timeUntilFriday) + ' sec')
        s.enter(timeUntilFriday, 2, friday, argument=(vk, '2'))
        s.run()
        print('friday message sent!')


def genocide(vk, event):  # piwas exclusive
    send_vk_msg(vk, event, '@ant1quar, в лучший из миров очередь, но у вас привелегии', None)


def runBot():
    host = config['DB']['host']
    database = config['DB']['database']
    user = config['DB']['user']
    password = config['DB']['password']
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    vk_session = vk_api.VkApi(token=tkn)
    vk = vk_session.get_api()

    th = threading.Thread(target=runFriday, args=(vk,))
    th.start()

    while True:
        try:
            vk_session = vk_api.VkApi(token=tkn)
            longpoll = VkBotLongPoll(vk_session, session)
            vk = vk_session.get_api()
            vk_upload = vk_api.upload.VkUpload(vk)

            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    cmd_in = str(event).lower()
                    if any(cmd in cmd_in for cmd in ('рандом', 'пидор')):
                        if event.from_chat:
                            cid = event.chat_id
                            ret = randomize(conn, cid)
                            if ret[0]:
                                msg = random.choice(dailyNewPatterns)
                            else:
                                msg = random.choice(dailyResultPatterns)
                            if ret[1] == ret[4]:
                                msg = msg + dailyUtility[0]
                            msg = msg.format(ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])

                            send_vk_msg(vk, event, random.choice(dailyRandomMsg), None)
                            send_vk_msg(vk, event, msg, None)

                    if any(cmd in cmd_in for cmd in ('ролл', 'roll')):
                        roll = random.randint(1, 100)
                        send_vk_msg(vk, event, random.choice(rollIntro), None)
                        send_vk_msg(vk, event, random.choice(rollMsg).format(roll), None)

                    elif any(cmd in cmd_in for cmd in ('статистика', 'стата')):
                        if event.from_chat:
                            cid = event.chat_id
                            ret = stats(conn, cid)
                            msg = statUtility[0] + '\n\n'
                            ptrn = random.choice(statPatterns)
                            for row in ret:
                                msg = msg + ptrn.format(row[0], row[1], row[2], row[3])
                            send_vk_msg(vk, event, msg, None)

                    elif any(cmd in cmd_in for cmd in ('регистрация', 'рега')):
                        if event.from_chat:
                            uid = event.object.get('from_id')
                            cid = event.chat_id
                            name_surname = get_name(vk, uid)
                            ret = register(conn, uid, cid, name_surname[0], name_surname[1])
                            if ret[0]:
                                msg = random.choice(regFailPatterns)
                            else:
                                msg = random.choice(regSucPatterns).format(uid)
                            send_vk_msg(vk, event, msg, None)

                    elif any(cmd in cmd_in for cmd in ('годовалый', 'год')):
                        cid = event.chat_id
                        ret = godovaliy(conn, cid)
                        if ret[0]:
                            msg = random.choice(annualNewPatterns).format(ret[1], ret[2], ret[3])
                        else:
                            msg = random.choice(annualResultPatterns).format(ret[1], ret[2], ret[3])
                        send_vk_msg(vk, event, msg, None)

                    elif any(cmd in cmd_in for cmd in ('помощь', 'хелпа')):
                        if event.from_chat:
                            send_vk_msg(vk, event, helpMsg, None)

                    elif any(cmd in cmd_in for cmd in ('моргенштерн', 'морген', 'morgenshtern')):
                        if event.from_chat:
                            send_vk_msg(vk, event, random.choice(morgenMsg), None)

                    elif any(cmd in cmd_in for cmd in ('дайте пакетик', 'pathetic', 'пакет')):
                        if event.from_chat:
                            random_audio = random.choice(mashupList)
                            print(random_audio)
                            att = f"audio{random_audio[0][0]}_{random_audio[0][1]}"
                            send_vk_msg(vk, event, random.choice(packeticMsg), att)

                    elif any(cmd in cmd_in for cmd in ('боньк',)):
                        if event.from_chat:
                            # TODO make function for all this crap

                            target = re.findall(r"(\[(id|club)[0-9]+\|@?\w+\])$", event.object.get('text'))
                            print(target)
                            print(event.object.get('text'))

                            uid = event.object.get('from_id')
                            name_surname = " ".join(get_name(vk, uid))

                            if len(target) == 0:
                                msg = random.choice(soloBonkMsg).format(name_surname)
                                send_vk_msg(vk, event, msg, None)
                            else:
                                msg = random.choice(duoBonkMsg).format(name_surname, target[0][0])
                                send_vk_msg(vk, event, msg, None)

                    elif any(cmd in cmd_in for cmd in ('хорни', 'прон')):
                        if event.from_chat:
                            try:
                                ret = get_dj_and_cover(vk_upload)
                                hmsg = ret[0]
                                cover = ret[1]
                                djId = ret[2]

                                send_vk_msg(vk, event, random.choice(hornyFirstMsg), None)
                                send_vk_msg(vk, event, "", cover)
                                send_vk_msg(vk, event, hornyUtility[0].format(djId), None)
                                send_vk_msg(vk, event, hmsg, None)

                            except:
                                send_vk_msg(vk, event, random.choice(hornyFirstMsg), None)
                                send_vk_msg(vk, event, hornyUtility[1], None)

                    elif any(cmd in cmd_in for cmd in ('немец', 'флюгер', 'шлёпа')):
                        if event.from_chat:
                            genocide(vk, event)

        except requests.exceptions.ReadTimeout:
            print("\n Переподключение к серверам ВК \n")
            time.sleep(3)
        except requests.exceptions.ConnectionError:
            print("\n Беды с коннекшном, опять играешься с ВПНом? \n")
            time.sleep(3)
        # except:
        #    print("\n НЕИЗВЕСТНАЯ АШИПКА АТТЕНШОН \n")

        #    time.sleep(3)


if __name__ == '__main__':
    print('bot started!')
    runBot()
