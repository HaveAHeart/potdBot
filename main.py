import configparser
import random
import time
import nhentai
import psycopg2
import requests
import vk_api
import re
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import vk_api.upload
import os

config = configparser.ConfigParser()
config.read('params.ini')
tkn = config['VK_MSG']['token']
session = config['VK_MSG']['session']
key = config['VK_MSG']['key']
server = config['VK_MSG']['server']
ts = config['VK_MSG']['ts']

# TODO - move all the phrases to the outer .txt files

randomMsg = ['Новый пидор дня: @id{0}({1} {2}),\n а его личный пассив: @id{3}({4} {5})\n',
             'Текущий пидор дня: @id{0}({1} {2}),\n а его личный пассив: @id{3}({4} {5})\n'
             'А потом у них было много секса, но мы это не покажем...\n',
             'САМООТСОС!\n']
with open('dailyRandom.txt', 'r', encoding="utf-8") as f:
    dailyRandomMsg = f.readlines()
statMsg = ['Итого, стата:\n',
           '@id{0}({1} {2}):  количество раз: {3}\n']
regMsg = ['А ты уже)0))\n',
          'Я записал @id{0}(тебя) в тетрадочку...\n']
godovaliyMsg = ['Новый годовалый:\n @id{0}({1} {2})\n',
                'Текущий годовалый:\n @id{0}({1} {2})\n']
helpMsg = ['Список комманд:\n\n'
           ' • регистрация/рега - записаться в пидорасы\n'
           ' • рандом - вращайте барабан\n'
           ' • годовалый - подебитель года\n'
           ' • стата/статистика - счет древних шизов\n\n'
           ' • ролл - роллим от 1 до 100. Зато честно!\n'
           ' • хорни - 🌚\n'
           ' • боньк - прописать человечку боньк (цель задаётся через ссылку - собачкой или как вам угодно)\n\n'
           ' Все комманды прописываются через @piwass или /\n'
           ' Приятного времяпрепровождения 🌚🌚🌚']
morgMsg = ['Тут должны были быть треки моргена, но @deffichento(данный господин) наложил на него вето']
packeticMsg = ['С вас 5 рублей']
hornyServiceMsg = ['nhentai.net/g/{}',
                   'Не могу законнектиться. Тыкай @deffichento, чтоб подрубил впн\n']
with open('soloBonk.txt', 'r', encoding="utf-8") as f:
    soloBonkMsg = f.readlines()
with open('duoBonk.txt', 'r', encoding="utf-8") as f:
    duoBonkMsg = f.readlines()
with open('horny_intro.txt', 'r', encoding="utf-8") as f:
    hornyFirstMsg = f.readlines()

AUDIO_LIST_P = [
    [149642725, 456240733],
    # [149642725, 456240540],
    # [149642725, 456240537],
    # [149642725, 456239941],
    # [149642725, 456240255],
    # [149642725, 456239961],
    # [149642725, 456240281]
]


def get_horny_att(vk_upload, tn):
    response = requests.get(tn)
    file = open("tmp_dj_tn.jpg", "wb")  # TODO - do smth with var names
    file.write(response.content)
    file.close()

    ph = vk_upload.photo_messages("tmp_dj_tn.jpg")
    owner = ph[0].get('owner_id')
    media = ph[0].get('id')
    accesskey = ph[0].get('access_key')
    att = "photo{}_{}_{}".format(owner, media, accesskey)

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


def runBot():
    host = config['DB']['host']
    database = config['DB']['database']
    user = config['DB']['user']
    password = config['DB']['password']
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)

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
                                msg = randomMsg[0].format(ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])
                            else:
                                msg = randomMsg[1].format(ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])
                            if ret[1] == ret[4]:
                                msg = msg + randomMsg[2]

                            send_vk_msg(vk, event, random.choice(dailyRandomMsg), None)
                            send_vk_msg(vk, event, msg, None)

                    if any(cmd in cmd_in for cmd in ('ролл', 'roll')):
                        roll = random.randint(1, 100)

                        # TODO - move all the phrases to the outer .txt file
                        send_vk_msg(vk, event, 'Крутите барабан...', None)

                        msg = 'И вам выпало {}. Даже не знаю, радоваться или плакать...'.format(roll)
                        send_vk_msg(vk, event, msg, None)

                    elif any(cmd in cmd_in for cmd in ('статистика', 'стата')):
                        if event.from_chat:
                            cid = event.chat_id
                            ret = stats(conn, cid)
                            msg = statMsg[0]
                            for row in ret:
                                msg = msg + statMsg[1].format(row[0], row[1], row[2], row[3])
                            send_vk_msg(vk, event, msg, None)

                    elif any(cmd in cmd_in for cmd in ('регистрация', 'рега')):
                        if event.from_chat:
                            uid = event.object.get('from_id')
                            cid = event.chat_id
                            name_surname = get_name(vk, uid)
                            ret = register(conn, uid, cid, name_surname[0], name_surname[1])
                            if ret[0]:
                                msg = regMsg[0]
                            else:
                                msg = regMsg[1].format(uid)
                            send_vk_msg(vk, event, msg, None)

                    elif any(cmd in cmd_in for cmd in ('годовалый', 'год')):
                        cid = event.chat_id
                        ret = godovaliy(conn, cid)
                        if ret[0]:
                            msg = godovaliyMsg[0].format(ret[1], ret[2], ret[3])
                        else:
                            msg = godovaliyMsg[1].format(ret[1], ret[2], ret[3])
                        send_vk_msg(vk, event, msg, None)

                    elif any(cmd in cmd_in for cmd in ('помощь', 'хелпа')):
                        if event.from_chat:
                            msg = helpMsg[0]
                            send_vk_msg(vk, event, msg, None)

                    elif any(cmd in cmd_in for cmd in ('моргенштерн', 'морген', 'morgenshtern')):
                        if event.from_chat:
                            send_vk_msg(vk, event, morgMsg[0], None)

                    elif any(cmd in cmd_in for cmd in ('дайте пакетик', 'pathetic', 'пакет')):
                        if event.from_chat:
                            random_audio = random.choice(AUDIO_LIST_P)
                            att = f"audio{random_audio[0]}_{random_audio[1]}"
                            send_vk_msg(vk, event, packeticMsg[0], att)

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
                                # TODO make function for all this crap
                                nhid = nhentai.get_random_id()
                                dj = nhentai.get_doujin(nhid)

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

                                send_vk_msg(vk, event, random.choice(hornyFirstMsg), None)
                                send_vk_msg(vk, event, "", att)
                                send_vk_msg(vk, event, hornyServiceMsg[0].format(nhid), None)
                                send_vk_msg(vk, event, hmsg, None)

                            except:
                                send_vk_msg(vk, event, random.choice(hornyFirstMsg), None)
                                send_vk_msg(vk, event, hornyServiceMsg[1], None)

        except requests.exceptions.ReadTimeout:
            print("\n Переподключение к серверам ВК \n")
            time.sleep(3)
        except requests.exceptions.ConnectionError:
            print("\n Беды с коннекшном, опять играешься с ВПНом? \n")
            time.sleep(3)
        except:
            print("\n НЕИЗВЕСТНАЯ АШИПКА АТТЕНШОН \n")

            time.sleep(3)


if __name__ == '__main__':
    print('bot started!')
    runBot()
