import sched
import threading
import time
import botFunctions.utils as utils

s = sched.scheduler(time.time, time.sleep)


def getTimeUntilFriday():
    targetTime = (24 + 18) * 60 * 60  # next day(Fri), 19:00
    timeFromTarget = ((time.time() + (60 * 60 * 3) - targetTime) % (60 * 60 * 24 * 7))  # GMT +03:00
    print(timeFromTarget)
    timeUntilTarget = (60 * 60 * 24 * 7) - timeFromTarget
    print(timeUntilTarget)
    return round(timeUntilTarget)


def runFriday(vk):
    while True:
        timeUntilFriday = getTimeUntilFriday()
        print('Friday timer is set, time until message - ' + str(timeUntilFriday) + ' sec')
        s.enter(timeUntilFriday, 1, utils.send_friday_msg, argument=(vk, '1'))
        s.run()
        print('friday message sent!')


def doFriday(vk):
    th = threading.Thread(target=runFriday, args=(vk,))
    th.start()
