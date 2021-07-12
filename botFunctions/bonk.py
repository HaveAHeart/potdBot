import os
import random
import re

from botFunctions.utils import get_name, send_vk_msg

# BONK sources
# bonk if no target is chosen
with open('src/soloBonk.txt', 'r', encoding="utf-8") as f:
    soloBonkMsg = f.readlines()
# bonk if there is a target
with open('src/duoBonk.txt', 'r', encoding="utf-8") as f:
    duoBonkMsg = f.readlines()


def printCons():
    print(random.choice(soloBonkMsg))


def printInitStats():
    pattern = "Bonk sources:\nSolo phrases(no target): {}\nDuo phrases(1 target): {}\n"
    print(pattern.format(len(soloBonkMsg), len(duoBonkMsg)))


def doBonk(vk, event):
    target = re.findall(r"(\[(id|club)[0-9]+\|@?\w+\])$", event.object.get('text'))

    uid = event.object.get('from_id')
    name_surname = " ".join(get_name(vk, uid))

    if len(target) == 0:
        msg = random.choice(soloBonkMsg).format(name_surname)
        send_vk_msg(vk, event, msg, None)
    else:
        msg = random.choice(duoBonkMsg).format(name_surname, target[0][0])
        send_vk_msg(vk, event, msg, None)
