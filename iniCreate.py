import configparser


def iniCreate(fileName, token, session, key, server, ts, host, database, user, password):
    config = configparser.ConfigParser()
    config['VK_MSG'] = {'Token': token, 'Session': session, 'Key': key, 'Server': server, 'ts': ts}
    config['DB'] = {'Host': host, 'Database': database, 'User': user, 'Password': password}

    with open(fileName, 'w') as configfile:
        config.write(configfile)
