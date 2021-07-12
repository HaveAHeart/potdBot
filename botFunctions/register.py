import random

from botFunctions.utils import get_name, send_vk_msg

# REGISTRATION sources
# line patterns for successful registration
with open('src/regSucPatterns.txt', 'r', encoding="utf-8") as f:
    regSucPatterns = f.readlines()
# line patterns for failed registration
with open('src/regFailPatterns.txt', 'r', encoding="utf-8") as f:
    regFailPatterns = f.readlines()


def printInitStats():
    pattern = "Register sources:\nSuccess messages: {}\nFail messages: {}\n"
    print(pattern.format(len(regSucPatterns), len(regFailPatterns)))


def register(conn, userid, chatid, name, surname):
    sql = "SELECT * FROM pidorbot.register(%s, %s, %s, %s);"
    print('кто-то регается...\n')

    cur = conn.cursor()
    cur.execute(sql, (userid, chatid, name, surname))
    conn.commit()
    row = cur.fetchone()
    cur.close()
    return row


def doRegister(conn, vk, event):
    uid = event.object.get('from_id')
    cid = event.chat_id
    name_surname = get_name(vk, uid)
    ret = register(conn, uid, cid, name_surname[0], name_surname[1])
    if ret[0]:
        msg = random.choice(regFailPatterns)
    else:
        msg = random.choice(regSucPatterns).format(uid)
    send_vk_msg(vk, event, msg, None)