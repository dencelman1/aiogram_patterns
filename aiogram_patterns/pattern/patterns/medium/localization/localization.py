from translate import Translator
import json
from typing import List
from os.path import isdir, splitext, dirname, exists, join
from os import makedirs




class Localization:


    @classmethod
    async def localize(
            cls,
            text_list:List[str],
            lang_codes:List[str],
            export_path:str = None,
        ) -> str:

        translations = [
            {
                "origin": text,
                **{
                    lang_code: await cls.from_text(text, lang_code)
                    for lang_code in lang_codes
                }
            }
            for text in text_list
        ]

        translated_dict = {
            "translations": translations
        }

        dict_str = json.dumps(translated_dict, indent=4, ensure_ascii=False)

        if export_path:
            await cls.path_checks(export_path)
            with open(export_path, 'w', encoding='utf-8') as file:
                file.write(dict_str)

        return dict_str
        
        
    @classmethod
    async def path_checks(cls, export_path:str):
        if isdir(export_path):
            export_path = join(export_path, "translation.json")
        
        if splitext(export_path)[-1] != ".json":
            raise ValueError("Translation must be exported to JSON file")
        
        dir = dirname(export_path)
        if not exists(dir):
            makedirs(dir)



    @classmethod
    async def from_dict(cls, from_dict:dict, lang_code='en') -> dict:
        keys = [str(i) for i in list(from_dict.keys())]
        values = [str(i) for i in list(from_dict.values())]

        trans_keys = await cls.from_list(keys, lang_code)
        trans_values = await cls.from_list(values, lang_code)

        return dict(zip(trans_keys, trans_values))


    @classmethod
    async def from_list(cls, text_list, lang_code="en"):
        t = Translator(to_lang=lang_code)

        return [
            t.translate(item_text) for item_text in text_list
        ]


    @classmethod
    async def from_text(cls, text, lang_code = "en"):
        t = Translator(to_lang=lang_code)
        return t.translate(text)

        
