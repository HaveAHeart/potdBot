from botFunctions.utils import send_vk_msg
import random

# DAILY POTD sources
# if the new potd has been just chosen
with open('src/dailyNew.txt', 'r', encoding="utf-8") as f:
    dailyNewPatterns = f.readlines()
# if the potd was already rolled today
with open('src/dailyResult.txt', 'r', encoding="utf-8") as f:
    dailyResultPatterns = f.readlines()
# random pre-result intro message
with open('src/dailyRandom.txt', 'r', encoding="utf-8") as f:
    dailyRandomMsg = f.readlines()
# other text sources for daily rolling
with open('src/dailyUtility.txt', 'r', encoding="utf-8") as f:
    dailyUtility = f.readlines()


def randomize(conn, chatid):
    sql = "SELECT * FROM pidorbot.randomize(%s);"
    print('кто-то рандомит обычного...\n')

    cur = conn.cursor()
    cur.execute(sql, (chatid,))
    conn.commit()
    ret = cur.fetchone()
    cur.close()
    return ret


def potdRequest(conn, vk, event):
    cid = event.chat_id
    ret = randomize(conn, cid)
    if ret[0]:
        msg = random.choice(dailyNewPatterns)
    else:
        msg = random.choice(dailyResultPatterns)
    if ret[1] == ret[4]:
        msg = msg + dailyUtility[0]
    msg = msg.format(ret[1], ret[2], ret[3], ret[4], ret[5], ret[6])

    send_vk_msg(vk, event, random.choice(dailyRandomMsg), None)
    send_vk_msg(vk, event, msg, None)
