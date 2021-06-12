import random
from botFunctions.utils import send_vk_msg

# ROLL sources
# intro messages
with open('src/rollIntro.txt', 'r', encoding="utf-8") as f:
    rollIntro = f.readlines()
# messages with results
with open('src/rollMsg.txt', 'r', encoding="utf-8") as f:
    rollMsg = f.readlines()


def doRoll(vk, event):
    roll = random.randint(1, 100)
    send_vk_msg(vk, event, random.choice(rollIntro), None)
    send_vk_msg(vk, event, random.choice(rollMsg).format(roll), None)
