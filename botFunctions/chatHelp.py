from botFunctions.utils import send_vk_msg

# HELP sources
# help message
with open('src/helpMsg.txt', 'r', encoding="utf-8") as f:
    helpMsg = "\n".join(f.readlines())


def doHelp(vk, event):
    send_vk_msg(vk, event, helpMsg, None)
