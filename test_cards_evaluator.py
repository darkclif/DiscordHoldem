import random
import unittest
import itertools
from random import shuffle

from cards_evaluator import Evaluator

# Helper to generate cards representation
suit_mapper = ['spades', 'hearts', 'diamonds', 'clubs']


def get_card(figure, suit):
    return figure, suit_mapper.index(suit)


class TestCardsEvaluator(unittest.TestCase):
    #
    #   Two
    #
    def test_two_cards(self):
        for i, j in itertools.product(range(13), range(13)):
            for s1, s2 in itertools.product(range(4), repeat=2):
                if i != j:
                    figure_list = sorted([i, j], reverse=True)

                    self.assertEqual(
                        Evaluator.player_evaluate([(i, s1), (j, s2)]),
                        ((0, figure_list[0], figure_list[1]), [(i, s1), (j, s2)])
                    )

    def test_two_cards_pair(self):
        for i, j in itertools.product(range(13), range(13)):
            for s1, s2 in itertools.product(range(4), repeat=2):
                if i == j:
                    self.assertEqual(
                        Evaluator.player_evaluate([(i, s1), (j, s2)]),
                        ((1, i), [(i, s1), (j, s2)])
                    )

    #
    #   Five
    #
    def test_five_cards_high_card(self):
        cards = sorted([(0, 0), (2, 1), (4, 2), (6, 3), (8, 0)], reverse=True)
        for cards_perm in itertools.permutations(cards):
            self.assertEqual(Evaluator.player_evaluate(cards_perm), ((0, 8, 6, 4, 2, 0), cards))

    def test_five_cards_pair(self):
        for i in range(13):
            pair = [(i, k) for k in random.sample(range(4), 2)]
            three = [(j, k) for j, k in zip(random.sample(set(range(13)) - {i}, 3), random.sample(range(4), 3))]
            three.sort(reverse=True)
            cards = sorted(pair + three, reverse=True)

            for cards_perm in itertools.combinations(cards, 5):
                self.assertEqual(Evaluator.player_evaluate(cards_perm), ((1, i, *[c[0] for c in three]), cards))

    def test_five_cards_two_pairs(self):
        for i, j in itertools.product(range(13), range(13)):
            if i == j:
                continue
            if i < j:
                i, j = j, i

            pair_1 = [(i, k) for k in random.sample(range(4), 2)]
            pair_2 = [(j, k) for k in random.sample(range(4), 2)]
            one = [(j, k) for j, k in zip(random.sample(set(range(13)) - {i, j}, 1), random.sample(range(4), 1))]

            cards = sorted(pair_1 + pair_2 + one, reverse=True)
            for cards_perm in itertools.combinations(cards, 5):
                self.assertEqual(Evaluator.player_evaluate(cards_perm), ((2, i, j, one[0][0]), cards))

    def test_five_cards_three(self):
        for i in range(13):
            three = [(i, k) for k in random.sample(range(4), 2)]
            two = [(j, k) for j, k in zip(random.sample(set(range(13)) - {i}, 2), random.sample(range(4), 2))]
            two.sort(reverse=True)
            cards = sorted(three + two, reverse=True)

            for cards_perm in itertools.combinations(cards, 5):
                self.assertEqual(Evaluator.player_evaluate(cards_perm), ((3, i, *[c[0] for c in two]), cards))

    def test_five_cards_straight(self):
        suits = [n for _ in range(4) for n in range(4)]
        for i in range(13 - 5):
            cards = sorted([(j, k) for j, k in zip(range(i, i + 5), random.sample(suits, 5))], reverse=True)

            for cards_perm in itertools.permutations(cards):
                self.assertEqual(Evaluator.player_evaluate(cards_perm), ((4, i + 4), cards))

    def test_five_cards_flush(self):
        for k in range(4):
            for perm in itertools.combinations(set(range(13)) - {3, 7, 11}, 5):
                figure_sort = sorted(perm, reverse=True)
                cards = sorted([(s, k) for s in perm], reverse=True)
                self.assertEqual(Evaluator.player_evaluate(cards), ((5, *figure_sort), cards))

    def test_five_cards_full_house(self):
        for i, j in itertools.product(range(13), range(13)):
            if i == j:
                continue

            three = [(i, k) for k in random.sample(range(4), 3)]
            pair = [(j, k) for k in random.sample(range(4), 2)]
            cards = sorted(three + pair, reverse=True)

            self.assertEqual(Evaluator.player_evaluate(cards), ((6, i, j), cards))

    def test_five_cards_four(self):
        for i, j in itertools.product(range(13), range(13)):
            if i == j:
                continue

            cards = sorted([(i, s) for s in range(4)] + [(j, 0)], reverse=True)
            for cards_perm in itertools.permutations(cards):
                self.assertEqual(Evaluator.player_evaluate(cards_perm), ((7, i, j), cards))

    def test_five_cards_straight_flush(self):
        for i in range(13 - 5):
            for k in range(4):
                cards = sorted([(j, k) for j in range(i, i + 5)], reverse=True)
                for cards_perm in itertools.permutations(cards):
                    self.assertEqual(Evaluator.player_evaluate(cards_perm), ((8, i + 4), cards))

    def test_five_cards_straight_flush_five_high(self):
        for k in range(4):
            cards = sorted([(j, k) for j in range(1, 5)]+[(12, k)], reverse=True)
            for cards_perm in itertools.permutations(cards):
                self.assertEqual(Evaluator.player_evaluate(cards_perm), ((8, 3), cards))


if __name__ == '__main__':
    unittest.main()






