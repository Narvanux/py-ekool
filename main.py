from prompt.ekool_prompt import EkoolPrompt
import configparser
import sys
import os

def parse_config():
    cfg = configparser.ConfigParser()
    cfg.read(os.environ['HOME'] + '/.config/py-ekool/config.ini')
    if cfg.sections() == []:
        print('Copy default config file to $HOME/.config/py-ekool/')
        sys.exit()
    auth = cfg['AUTH']
    if auth == None:
        print('AUTH is empty')
        sys.exit()
    username = auth.get('username', '')
    password = auth.get('password', '')
    return {
            'username': username,
            'password': password
            }

def main():
    cfg = parse_config()
    ep = EkoolPrompt(cfg)
    ep.prompt_cycle()

if __name__ == "__main__":
    main()
