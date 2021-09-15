from botFunctions.utils import send_vk_msg, get_name
from vk_api import tools
import random
# REMOVE sources
# line patterns for remove
with open('src/removePatterns.txt', 'r', encoding="utf-8") as f:
    removePatterns = f.readlines()


def printInitStats():
    pattern = "Remove sources:\nResult messages: {}\n"
    print(pattern.format(len(removePatterns)))


def remove(conn, cid, uid):

    print('кто-то кого-то удаляет...\n')

    cur = conn.cursor()
    sql = "SELECT amount from pidorbot.participation WHERE chatid = {0} AND userid = {1};".format(cid, uid)
    cur.execute(sql)
    row = cur.fetchone()
    conn.commit()
    isAffected = row is not None
    if isAffected:
        sql = "DELETE from pidorbot.participation WHERE chatid = {0} AND userid = {1};".format(cid, uid)
        cur.execute(sql)
        conn.commit()
    cur.close()
    return isAffected


def isAuthorised(vk, uid, peerid):
    tool = tools.VkTools(vk)
    res = tool.get_all(method="messages.getConversationMembers", max_count=1000, values={'peer_id': peerid}, key='items')
    for i in range(res.get('count')):
        currentItem = res.get('items')[i]
        if (currentItem.get('is_admin') or currentItem.get('is_owner')) and currentItem.get('member_id') == uid:
            return True
    return False


def doRemove(conn, vk, event):
    peerid = event.object.get('peer_id')
    from_uid = event.object.get('from_id')
    uid = event.object.get('text').split(' ')[1]
    cid = event.chat_id

    if isAuthorised(vk, from_uid, peerid):
        isAffected = remove(conn, cid, uid)
        if isAffected:
            msg = random.choice(removePatterns).format(from_uid, " ".join(get_name(vk, from_uid)), uid, " ".join(get_name(vk, uid)))
        else:
            #TODO REFACTOR
            msg = 'Человека с таким id в качалке нет, протри глаза.'
        send_vk_msg(vk, event, msg, None)
    else:
        # TODO REFACTOR
        msg = 'Воняешь слабостью. Проси админа выпилить человека.'
        send_vk_msg(vk, event, msg, None)

