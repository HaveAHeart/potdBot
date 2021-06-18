import random
import sched
import threading
import time
import botFunctions.utils as utils
import os

s = sched.scheduler(time.time, time.sleep)

picPaths = os.listdir('FridayPics/')


def getTimeUntilFriday():
    targetTime = (24 + 18) * 60 * 60  # next day(Fri), 19:00
    timeFromTarget = ((time.time() + (60 * 60 * 3) - targetTime) % (60 * 60 * 24 * 7))  # GMT +03:00
    print(timeFromTarget)
    timeUntilTarget = (60 * 60 * 24 * 7) - timeFromTarget
    print(timeUntilTarget)
    return round(timeUntilTarget)


def runFriday(vk, vk_upload):
    while True:
        print(picPaths)
        picPath = 'FridayPics/' + random.choice(picPaths)
        timeUntilFriday = getTimeUntilFriday()
        print('Friday timer is set, time until message - ' + str(timeUntilFriday) + ' sec')
        s.enter(timeUntilFriday, 1, utils.send_friday_msg, argument=(vk, vk_upload, '2', picPath))
        s.run()
        print('friday message sent!')


def doFriday(vk, vk_upload):
    th = threading.Thread(target=runFriday, args=(vk, vk_upload))
    th.start()
