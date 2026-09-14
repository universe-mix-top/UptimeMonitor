from configparser import ConfigParser, ExtendedInterpolation, SectionProxy
from pathlib import Path


class Config:
    def __init__(self):
        config_ini = ConfigParser(interpolation=ExtendedInterpolation())
        config_ini_path = Path(__file__).parent / 'config.ini'
        config_ini.read(config_ini_path)

        self.config = config_ini

    def __getitem__(self, key: str) -> SectionProxy:
        if isinstance(key, slice):
            raise IndexError('к config нельзя использовать срезы')
        else:
            return self.config[key]


config = Config()

if __name__ == '__main__':
    print(config.info())