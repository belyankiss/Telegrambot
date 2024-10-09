from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_NAME: str
    ADMIN: int
    CODER: int
    URL_RULES: str
    ABOUT_ADV: int
    CHAT_SUB_ID: int
    CHAT_SUB_LINK: str
    CHAT_NAME: str
    CRYPTOBOT_TOKEN: str
    HREF_REF: str
    PERCENTAGE_FROM_REF: float
    NAME_BOT: str

    PRICE_PROXY: int
    COUNTRY_PRICE_PROXY: int
    PERCENTAGE: float

    API_KEY_PROXY_LINE: str

    @property
    def DATABASE_URL_aiosqlite(self):
        return f"sqlite+aiosqlite:///{self.DB_NAME}"

    @property
    def PARAMS(self):
        return {self.BOT_TOKEN,
                self.DB_NAME,
                self.ADMIN,
                self.CODER,
                self.URL_RULES,
                self.ABOUT_ADV,
                self.CHAT_SUB_ID,
                self.CHAT_SUB_LINK,
                self.CHAT_NAME,
                self.CRYPTOBOT_TOKEN,
                self.HREF_REF,
                self.PERCENTAGE_FROM_REF,
                self.NAME_BOT,
                self.PRICE_PROXY,
                self.COUNTRY_PRICE_PROXY,
                self.PERCENTAGE,
                self.API_KEY_PROXY_LINE
                }

    model_config = SettingsConfigDict(env_file='C:/Users/Eldorado/PycharmProjects/UProxy08102024/proxy_bot/configs.env')


settings = Settings()
