import configparser
import time

import psycopg2
import requests
import vk_api
import vk_api.upload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from botFunctions import bonk, chatHelp, friday, godovaliy, horny, morgen, pathetic, potd, register, roll, stats

config = configparser.ConfigParser()
config.read('params.ini')
tkn = config['VK_MSG']['token']
session = config['VK_MSG']['session']


def printStats():
    bonk.printInitStats()
    friday.printInitStats()
    godovaliy.printInitStats()
    horny.printInitStats()
    morgen.printInitStats()
    pathetic.printInitStats()
    potd.printInitStats()
    register.printInitStats()
    roll.printInitStats()
    stats.printInitStats()


def runBot():
    host = config['DB']['host']
    database = config['DB']['database']
    user = config['DB']['user']
    password = config['DB']['password']
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    vk_session = vk_api.VkApi(token=tkn)
    vk = vk_session.get_api()
    vk_upload = vk_api.upload.VkUpload(vk)
    friday.doFriday(vk, vk_upload)

    while True:
        try:
            vk_session = vk_api.VkApi(token=tkn)
            longpoll = VkBotLongPoll(vk_session, session)
            vk = vk_session.get_api()
            vk_upload = vk_api.upload.VkUpload(vk)

            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    cmd_in = event.object.get('text')
                    print(cmd_in)

                    if any(cmd in cmd_in for cmd in ('боньк',)):
                        if event.from_chat:
                            bonk.doBonk(vk, event)

                    elif any(cmd in cmd_in for cmd in ('рандом', 'пидор')):
                        if event.from_chat:
                            potd.potdRequest(conn, vk, event)

                    elif any(cmd in cmd_in for cmd in ('статистика', 'стата')):
                        if event.from_chat:
                            stats.doStats(conn, vk, event)

                    elif any(cmd in cmd_in for cmd in ('регистрация', 'рега')):
                        if event.from_chat:
                            register.doRegister(conn, vk, event)

                    elif any(cmd in cmd_in for cmd in ('годовалый', 'год')):
                        if event.from_chat:
                            godovaliy.doGodovaliy(conn, vk, event)

                    elif any(cmd in cmd_in for cmd in ('помощь', 'хелпа')):
                        if event.from_chat:
                            chatHelp.doHelp(vk, event)

                    elif any(cmd in cmd_in for cmd in ('моргенштерн', 'морген', 'morgenshtern')):
                        if event.from_chat:
                            morgen.doMorgen(vk, event)

                    elif any(cmd in cmd_in for cmd in ('дайте пакетик', 'pathetic', 'пакет')):
                        if event.from_chat:
                            pathetic.doPathetic(vk, event)

                    elif any(cmd in cmd_in for cmd in ('хорни', 'прон')):
                        if event.from_chat:
                            horny.doHorny(vk, event, vk_upload)

                    elif any(cmd in cmd_in for cmd in ('ролл', 'roll')):
                        if event.from_chat:
                            roll.doRoll(vk, event)

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
    printStats()
    print('bot started!')
    runBot()
