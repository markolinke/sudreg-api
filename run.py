from config import Config
from use_cases import CompanyLoop

config = Config()
loop = CompanyLoop(config)
loop.start_main_loop()