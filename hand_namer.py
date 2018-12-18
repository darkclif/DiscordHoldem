class HandNamer:
    mapper = {
        0: "High Card",
        1: "Pair",
        2: "Two pairs",
        3: "Three of a kind	",
        4: "Straight",
        5: "Flush",
        6: "Full house",
        7: "Four of a kind",
        8: "Straight flush"
    }

    @staticmethod
    def name_hand(hand):
        return HandNamer.mapper[hand[0]]
