import os
import random
import nhentai
import requests

from botFunctions.utils import send_vk_msg

# HORNY sources
# intro messages
with open('src/horny_intro.txt', 'r', encoding="utf-8") as f:
    hornyFirstMsg = f.readlines()
# service stuff for link/errors
with open('src/hornyUtility.txt', 'r', encoding="utf-8") as f:
    hornyUtility = f.readlines()


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


def get_horny_att(vk_upload, tn):
    response = requests.get(tn)
    file = open("tmp_dj_tn.jpg", "wb")
    file.write(response.content)
    file.close()

    ph = vk_upload.photo_messages("tmp_dj_tn.jpg")
    owner = ph[0].get('owner_id')
    media = ph[0].get('id')
    accessKey = ph[0].get('access_key')
    att = "photo{}_{}_{}".format(owner, media, accessKey)

    os.remove("tmp_dj_tn.jpg")
    return att


def doHorny(vk, event, vk_upload):
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
