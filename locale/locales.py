import re
from logger import global_log


class Locales:
    # List of languages
    langs = ["en", "pl"]

    def __init__(self):
        self.strings = {}
        self.lang = "en"

        # Load strings
        self.load_lang()

    def set_lang(self, lang):
        if lang in Locales.langs:
            self.lang = lang
            self.load_lang()
        else:
            global_log("error", "No language {} available in localization files.".format(lang))

    def load_lang(self):
        regx = re.compile("^([^#|.]*)=.*\"(.*)\".*$")
        file = "./locale/files/{}_texas.loc".format(self.lang)
        cnt = 0

        for l in open(file, "r"):
            result = regx.match(l)

            if result and len(result.groups()) == 2:
                # print(result.groups())
                self.strings[result.group(1).strip()] = result.group(2).strip()

                cnt += 1

        global_log("info", "Loaded {} strings in language <{}> from locales.".format(cnt, self.lang))

    def get_string(self, keyword):
        return self.strings[keyword]


locales = Locales()


def get_string(*args, **kwargs):
    global locales
    return locales.get_string(*args, **kwargs)
