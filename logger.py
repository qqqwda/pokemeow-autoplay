import logging
from dotenv import load_dotenv

class Logger:
    _instance = None

    @staticmethod 
    def getInstance():
        """ Static access method. """
        if Logger._instance == None:
            Logger()
        return Logger._instance

    def __init__(self, name=__name__):
        """ Virtually private constructor. """
        if Logger._instance != None:
            raise Exception("This class is a singleton!")
        else:
            Logger._instance = self

            # Load environment variables
            load_dotenv()

            # Create a custom logger
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.INFO)

            # Create handlers
            c_handler = logging.StreamHandler()
            f_handler = logging.FileHandler('file.log', encoding='utf-8')

            c_handler.setLevel(logging.INFO)
            f_handler.setLevel(logging.ERROR)
            f_handler.setLevel(logging.INFO)

            # Create formatters and add it to handlers
            c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
            f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
            c_handler.setFormatter(c_format)
            f_handler.setFormatter(f_format)

            # Add handlers to the logger
            self.logger.addHandler(c_handler)
            self.logger.addHandler(f_handler)
            self.app_initialize()

    def get_logger(self):
        return self.logger
    
    def app_initialize(self):
        
        welcome_message = """
        ██████╗░░█████╗░██╗░░██╗███████╗███╗░░░███╗███████╗░█████╗░░██╗░░░░░░░██╗
        ██╔══██╗██╔══██╗██║░██╔╝██╔════╝████╗░████║██╔════╝██╔══██╗░██║░░██╗░░██║
        ██████╔╝██║░░██║█████═╝░█████╗░░██╔████╔██║█████╗░░██║░░██║░╚██╗████╗██╔╝
        ██╔═══╝░██║░░██║██╔═██╗░██╔══╝░░██║╚██╔╝██║██╔══╝░░██║░░██║░░████╔═████║░
        ██║░░░░░╚█████╔╝██║░╚██╗███████╗██║░╚═╝░██║███████╗╚█████╔╝░░╚██╔╝░╚██╔╝░
        ╚═╝░░░░░░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░░░░╚═╝╚══════╝░╚════╝░░░░╚═╝░░░╚═╝░░

        ░█████╗░██╗░░░██╗████████╗░█████╗░██████╗░██╗░░░░░░█████╗░██╗░░░██╗
        ██╔══██╗██║░░░██║╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░██╔══██╗╚██╗░██╔╝
        ███████║██║░░░██║░░░██║░░░██║░░██║██████╔╝██║░░░░░███████║░╚████╔╝░
        ██╔══██║██║░░░██║░░░██║░░░██║░░██║██╔═══╝░██║░░░░░██╔══██║░░╚██╔╝░░
        ██║░░██║╚██████╔╝░░░██║░░░╚█████╔╝██║░░░░░███████╗██║░░██║░░░██║░░░
        ╚═╝░░╚═╝░╚═════╝░░░░╚═╝░░░░╚════╝░╚═╝░░░░░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░
        """
        self.logger.info(welcome_message)