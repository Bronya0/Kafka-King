#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json

with open('language/lang.json', encoding='utf-8') as f:
    lang_dict: dict = json.load(f)


class Lang(object):
    def __init__(self, language):
        self.language = language

    def i18n(self, default_str: str):
        if self.language is None:
            return default_str
        res = lang_dict.get(default_str, {}).get(self.language)
        if res == "":
            return default_str


lang = Lang(language=None)
