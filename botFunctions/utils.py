import configparser
import os

from vk_api.utils import get_random_id

config = configparser.ConfigParser()
config.read('params.ini')
tkn = config['VK_MSG']['token']
session = config['VK_MSG']['session']
key = config['VK_MSG']['key']
server = config['VK_MSG']['server']
ts = config['VK_MSG']['ts']


def getRelPath(relPart):
    cur_path = os.path.dirname(__file__)
    return os.path.relpath(relPart, cur_path)


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


def send_friday_msg(vk, vk_upload, cid, picPath):  # piwas exclusive
    ph = vk_upload.photo_messages(picPath)
    owner = ph[0].get('owner_id')
    media = ph[0].get('id')
    accessKey = ph[0].get('access_key')
    att = "photo{}_{}_{}".format(owner, media, accessKey)

    vk.messages.send(
        key=key,
        server=server,
        ts=ts,
        random_id=get_random_id(),
        message='С пятницей, господа!',
        attachment=att,
        chat_id=cid
    )
    print('Fri msg sent!')


def get_name(vk, from_id):
    info = vk.users.get(user_ids=from_id)[0]
    return [info.get('first_name'), info['last_name']]
