import configparser

config = configparser.ConfigParser()
config['VK_MSG'] = {'Token': 'filler', 'Session': 'filler', 'Key': 'filler', 'Server': 'filler', 'ts': 'filler'}
config['DB'] = {'Host': 'filler', 'Database': 'filler', 'User': 'filler', 'Password': 'filler'}

with open('params.ini', 'w') as configfile:
    config.write(configfile)



