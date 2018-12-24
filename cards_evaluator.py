import itertools


class Evaluator:
    """
        Card format:
            Tuple: (F, S)
            F - figure
            S - suit
    """

    @staticmethod
    def table_evaluate(c_players, c_table):
        """
        Evaluate best possible hands for given players and table cards.

        :param c_players: List of lists of player cards. [[c1, c1], [c2, c2], ...],
        :param c_table: List of table cards. [c1, c2, ...]
        :return: [(hand1, cards1), (hand2, cards2), ...]
        """
        players_ret = []
        for p in c_players:
            cards = p + c_table
            players_ret.append(Evaluator.player_evaluate(cards))

        return players_ret

    @staticmethod
    def player_evaluate(cards):
        """
        Return best possible hand from given cards.

        :param cards: {2 or 5 or 6 or 7} cards in list [c1, c2, ...].
        :return: Dictionary with best hand value and cards used. {cards: [], value: ()}
        """
        if len(cards) == 2:
            return Evaluator.__hand_evaluate_2(cards), cards
        else:
            best_hand, best_cards = None, None

            for cards_comb in itertools.combinations(cards, 5):
                curr_hand = Evaluator.__hand_evaluate_5(cards_comb)
                if not best_hand or curr_hand > best_hand:
                    best_hand, best_cards = curr_hand, cards_comb

            return best_hand, sorted(best_cards, key=lambda c: c[0], reverse=True)

    @staticmethod
    def __hand_evaluate_5(hand):
        """
        Returns tuple representing hand value.

        0. High card        - (0, Card0, Card1, Card2, Card3, Card4)
        1. Pair             - (1, Pair0, Card0, Card1, Card2)
        2. Two pairs        - (2, HighPair0, LowPair1, Card0)
        3. Three of a kind  - (3, Three0, Card0, Card1)
        4. Straight         - (4, HighCard0)
        5. Flush            - (5, Card0, Card1, Card2, Card3, Card4)
        6. Full house       - (6, Three0, Pair0)
        7. Four of a kind   - (7, Four0, Card0)
        8. Straight flush   - (8, HighCard0)

        :param hand: List of 5 cards (after flop)
        :return: Tuple with hand value.
        """
        if len(hand) != 5:
            raise Exception("Wrong hand size.")

        same_suit = len(set([c[1] for c in hand])) == 1

        figures = sorted([c[0] for c in hand])
        pattern = [(k, figures.count(k)) for k in set(figures)]
        pattern.sort(key=lambda x: 13 * x[1] + x[0])

        # Poker
        if same_suit and figures[4]-figures[0] == 4 and len(pattern) == 5:
            return 8, figures[4]

        # Four of a kind
        if [p[1] for p in pattern] == [1, 4]:
            return 7, pattern[1][0], pattern[0][0]

        # Full house
        if [p[1] for p in pattern] == [2, 3]:
            return 6, pattern[1][0], pattern[0][0]

        # Flush
        if same_suit:
            return (5, *figures[::-1])

        # Straight
        if figures[4]-figures[0] == 4 and len(pattern) == 5:
            return 4, figures[4]

        # Three of kind
        if [p[1] for p in pattern] == [1, 1, 3]:
            return 3, pattern[2][0], pattern[1][0], pattern[0][0]

        # Two pairs
        if [p[1] for p in pattern] == [1, 2, 2]:
            return 2, pattern[2][0], pattern[1][0], pattern[0][0]

        # Pair
        if [p[1] for p in pattern] == [1, 1, 1, 2]:
            return 1, pattern[3][0], pattern[2][0], pattern[1][0], pattern[0][0]

        # High card
        return 0,

    @staticmethod
    def __hand_evaluate_2(hand):
        """
        Returns tuple representing hand value.

        0. High card        - (0, Card0, Card1)
        1. Pair             - (1, Pair0)

        :param hand: List of 2 cards (pre-flop)
        :return: Tuple with hand value.
        """
        if len(hand) != 2:
            raise Exception("Wrong hand size.")

        if hand[0][0] == hand[1][0]:
            # Pair
            return 1, hand[0][0]
        else:
            # High card
            cards = sorted([hand[0][0], hand[1][0]], reverse=True)
            return 0, cards[0], cards[1]

#
# print(Evaluator.hand_evaluate_2([(2, 1), (3, 2)]))
#
# from card import *
# from random import shuffle
#
# deck = Card.create_deck()
#
# for i in range(0, 9):
#     for _ in range(10000):
#         shuffle(deck)
#         ev = Evaluator.hand_evaluate_5(deck[0:5])
#         if ev[0] == i:
#             print("Hand: ", '/'.join(Card.get_string(c) for c in deck[0:5]))
#             print("Value: ", ev)
