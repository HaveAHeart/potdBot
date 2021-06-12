import random

from botFunctions.utils import send_vk_msg

# PATHETIC sources
# morgenstern messages
with open('src/morgenMsg.txt', 'r', encoding="utf-8") as f:
    morgenMsg = f.readlines()


def doMorgen(vk, event):
    send_vk_msg(vk, event, random.choice(morgenMsg), None)