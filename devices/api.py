import configparser

def main():
    config = configparser.ConfigParser()		
    config.read("config.ini")
    print(config)


if __name__ == '__main__':
    main()