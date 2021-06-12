import random

from botFunctions.utils import send_vk_msg

# ANNUAL POTD sources
# if the annual potd has been just chosen
with open('src/annualNew.txt', 'r', encoding="utf-8") as f:
    annualNewPatterns = f.readlines()
# if the annual potd was already rolled this year
with open('src/annualResult.txt', 'r', encoding="utf-8") as f:
    annualResultPatterns = f.readlines()


def godovaliy(conn, chatid):
    sql = "SELECT * FROM pidorbot.godovaliy(%s);"
    print('кто-то рандомит годовалого...\n')
    cur = conn.cursor()
    cur.execute(sql, (chatid,))
    conn.commit()
    ret = cur.fetchone()
    cur.close()
    return ret


def doGodovaliy(conn, vk, event):
    cid = event.chat_id
    ret = godovaliy(conn, cid)
    if ret[0]:
        msg = random.choice(annualNewPatterns).format(ret[1], ret[2], ret[3])
    else:
        msg = random.choice(annualResultPatterns).format(ret[1], ret[2], ret[3])
    send_vk_msg(vk, event, msg, None)