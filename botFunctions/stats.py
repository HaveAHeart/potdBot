import random
from botFunctions.utils import send_vk_msg

# STATS sources
# line patterns for result
with open('src/statPatterns.txt', 'r', encoding="utf-8") as f:
    statPatterns = f.readlines()
# other text sources for stats
with open('src/statUtility.txt', 'r', encoding="utf-8") as f:
    statUtility = f.readlines()


def printInitStats():
    pattern = "Stats sources:\nResult messages: {}\n"
    print(pattern.format(len(statPatterns)))


def stats(conn, chatid):
    sql = "SELECT * FROM pidorbot.stats(%s);"
    print('кто-то просит стату...\n')

    cur = conn.cursor()
    cur.execute(sql, (chatid,))
    conn.commit()
    ret = []
    row = cur.fetchone()
    while row is not None:
        ret.append(row)
        row = cur.fetchone()
    cur.close()
    return ret


def doStats(conn, vk, event):
    cid = event.chat_id
    ret = stats(conn, cid)
    msg = statUtility[0] + '\n\n'
    ptrn = random.choice(statPatterns)
    for row in ret:
        msg = msg + ptrn.format(row[0], row[1], row[2], row[3])
    send_vk_msg(vk, event, msg, None)
