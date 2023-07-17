



class Emoji:

    COUNTRY_FLAGS = {
        'kz': '\U0001F1F0\U0001F1FF',
        'by': '\U0001F1E7\U0001F1FE',
        'ua': '\U0001F1FA\U0001F1E6',
        'ru': '\U0001F1F7\U0001F1FA',
        'us': '\U0001F1FA\U0001F1F8',
        'de': '\U0001F1E9\U0001F1EA',
        "global": "🌐"
    }

    @staticmethod
    def get_country_emoji(country_code:str) -> str:
        
        try:
            return Emoji.COUNTRY_FLAGS[country_code.lower()]
        
        except KeyError:
            return Emoji.COUNTRY_FLAGS['global']
            
    