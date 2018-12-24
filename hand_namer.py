from locale import locales


class HandNamer:
    locale_template_mapper = {
        0: "HIGH_CARD",
        1: "PAIR",
        2: "TWO_PAIRS",
        3: "THREE_OF_A_KIND",
        4: "STRAIGHT",
        5: "FLUSH",
        6: "FULL_HOUSE",
        7: "FOUR_OF_A_KIND",
        8: "STRAIGHT_FLUSH"
    }

    @staticmethod
    def name_hand(hand):
        return locales.get_string(HandNamer.locale_template_mapper[hand[0]])
