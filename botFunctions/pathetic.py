import random

from botFunctions.utils import send_vk_msg

# PATHETIC sources
# mashup messages
with open('src/patheticMsg.txt', 'r', encoding="utf-8") as f:
    packeticMsg = f.readlines()
# mashup ids - audio and owner
with open('src/mashupList.txt', 'r', encoding="utf-8") as f:
    mashupList = []
    tmp = f.readlines()
    for idPair in tmp:
        mashupList.append([idPair.split(" ")])


def doPathetic(vk, event):
    random_audio = random.choice(mashupList)
    print(random_audio)
    att = f"audio{random_audio[0][0]}_{random_audio[0][1]}"
    send_vk_msg(vk, event, random.choice(packeticMsg), att)
