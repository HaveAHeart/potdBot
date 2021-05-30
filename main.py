import configparser
import random
import time

import psycopg2
import requests
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


config = configparser.ConfigParser()
config.read('params.ini')
tkn = config['VK_MSG']['token']
session = config['VK_MSG']['session']
key = config['VK_MSG']['key']
server = config['VK_MSG']['server']
ts = config['VK_MSG']['ts']

randomMsg = ['Новый пидор дня: @id{0}({1} {2}),\n а его личный пассив: @id{3}({4} {5})\n',
             'Текущий пидор дня: @id{0}({1} {2}),\n а его личный пассив: @id{3}({4} {5})\n',
             'САМООТСОС!\n',
             'Система поиска пидорасов активирована']
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
           ' Все комманды прописываются через @piwass']
morgMsg = ['Тут должны были быть треки моргена, но @deffichento(данный господин) наложил на него вето']
AUDIO_LIST_P = [
    [149642725, 456240733],
    [149642725, 456240540],
    [149642725, 456240537],
    [149642725, 456239941],
    [149642725, 456240255],
    [149642725, 456239961],
    [149642725, 456240281]
]


def register(conn, userid, chatid, name, surname):
    sql = "SELECT * FROM pidorbot.register(%s, %s, %s, %s);"
    print('register started')
    cur = conn.cursor()
    cur.execute(sql, (userid, chatid, name, surname))

    conn.commit()
    row = cur.fetchone()
    print(row)

    cur.close()
    return row


def randomize(conn, chatid):
    sql = "SELECT * FROM pidorbot.randomize(%s);"
    cur = conn.cursor()
    cur.execute(sql, (chatid,))

    conn.commit()
    ret = cur.fetchone()
    print(ret)

    cur.close()
    return ret


def godovaliy(conn, chatid):
    sql = "SELECT * FROM pidorbot.godovaliy(%s);"
    cur = conn.cursor()
    cur.execute(sql, (chatid,))

    conn.commit()
    ret = cur.fetchone()
    print(ret)

    cur.close()
    return ret


def stats(conn, chatid):
    sql = "SELECT * FROM pidorbot.stats(%s);"
    cur = conn.cursor()
    cur.execute(sql, (chatid,))

    conn.commit()
    ret = []
    row = cur.fetchone()
    while row is not None:
        print(row)
        ret.append(row)
        row = cur.fetchone()
    cur.close()
    return ret


def get_name(vk, from_id):
    info = vk.users.get(user_ids=from_id)[0]
    return [info.get('first_name'), info['last_name']]


def runBot():
    host = config['DB']['host']
    database = config['DB']['database']
    user = config['DB']['user']
    password = config['DB']['password']
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)

    vk_session = vk_api.VkApi(token=tkn)
    longpoll = VkBotLongPoll(vk_session, session)
    vk = vk_session.get_api()

    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if 'рандом' in str(event) or 'hfyljv' in str(event):
                    if event.from_chat:
                        cid = event.chat_id
                        ret = randomize(conn, cid)

                        vk.messages.send(
                            key=key,
                            server=server,
                            ts=ts,
                            random_id=get_random_id(),
                            message=randomMsg[3],
                            chat_id=event.chat_id
                        )

                        if ret[0]:
                            msg = randomMsg[0].format(ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])
                        else:
                            msg = randomMsg[1].format(ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])

                        if ret[1] == ret[4]:
                            msg = msg + randomMsg[2]

                        vk.messages.send(
                            key=key,
                            server=server,
                            ts=ts,
                            random_id=get_random_id(),
                            message=msg,
                            chat_id=event.chat_id
                        )

                if 'статистика' in str(event) or 'cnfnbcnbrf' in str(event) or 'стата' in str(event) or 'cnfnf' in str(
                        event):

                    cid = event.chat_id
                    ret = stats(conn, cid)

                    msg = statMsg[0]
                    for row in ret:
                        msg = msg + statMsg[1].format(row[0], row[1], row[2], row[3])

                    if event.from_chat:
                        vk.messages.send(
                            key=key,
                            server=server,
                            ts=ts,
                            random_id=get_random_id(),
                            message=msg,
                            chat_id=event.chat_id
                        )

                if 'регистрация' in str(event) or 'htubcnhfwbz' in str(event) or 'рега' in str(event) or 'htuf' in str(
                        event):
                    if event.from_chat:
                        uid = event.object.get('from_id')
                        cid = event.chat_id

                        name_surname = get_name(vk, uid)

                        ret = register(conn, uid, cid, name_surname[0], name_surname[1])

                        if ret[0]:
                            msg = regMsg[0]
                        else:
                            msg = regMsg[1].format(uid)

                        vk.messages.send(
                            key=key,
                            server=server,
                            ts=ts,
                            random_id=get_random_id(),
                            message=msg,
                            chat_id=event.chat_id
                        )

                if 'годовалый' in str(event) or 'ujljdfksq' in str(event):
                    cid = event.chat_id
                    ret = godovaliy(conn, cid)

                    if ret[0]:
                        msg = godovaliyMsg[0].format(ret[1], ret[2], ret[3])
                    else:
                        msg = godovaliyMsg[1].format(ret[1], ret[2], ret[3])

                    if event.from_chat:
                        vk.messages.send(
                            key=key,
                            server=server,
                            ts=ts,
                            random_id=get_random_id(),
                            message=msg,
                            chat_id=event.chat_id
                        )

                if 'помощь' in str(event) or 'gjvjom' in str(event) or 'хелпа' in str(event) or '[tkgf' in str(event):
                    if event.from_chat:
                        msg = helpMsg[0]

                        vk.messages.send(
                            key=key,
                            server=server,
                            ts=ts,
                            random_id=get_random_id(),
                            message=msg,
                            chat_id=event.chat_id
                        )

                if 'моргенштерн' in str(event) or 'морген' in str(event) or 'morgenshtern' in str(
                        event) or 'MORGENSHTERN' in str(event):
                    if event.from_chat:
                        vk.messages.send(
                            key=key,
                            server=server,
                            ts=ts,
                            random_id=get_random_id(),
                            message=morgMsg[0],
                            chat_id=event.chat_id
                        )

                if 'дайте пакетик' in str(event):
                    if event.from_chat:
                        random_audio = random.choice(AUDIO_LIST_P)
                        vk.messages.send(
                            key=key,
                            server=server,
                            ts=ts,
                            random_id=get_random_id(),
                            message='С вас 5 рублей',
                            attachment=f"audio{random_audio[0]}_{random_audio[1]}",
                            chat_id=event.chat_id
                        )

    except requests.exceptions.ReadTimeout:
        print("\n Переподключение к серверам ВК \n")
        time.sleep(3)


if __name__ == '__main__':
    print('bot started!')
    runBot()
