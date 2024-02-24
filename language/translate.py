#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json

with open('language/lang.json', encoding='utf-8') as f:
    lang_dict: dict = json.load(f)


class Lang(object):
    def __init__(self, language):
        self.language = language

    def i18n(self, default_str: str):
        print(default_str, self.language)
        if self.language is None:
            return default_str
        res = lang_dict.get(default_str, {}).get(self.language, default_str)
        return res


lang = Lang(language=None)
i18n = lang.i18n
