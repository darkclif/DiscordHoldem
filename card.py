class Card:
    char_suits = ['♠', '♥', '♦', '♣']
    char_figures = list(str(i) for i in range(2, 11)) + ['J', 'Q', 'K', 'A']

    # ASCII
    ascii_cards = [
        ['🂡', '🂢', '🂣', '🂤', '🂥', '🂦', '🂧', '🂨', '🂩', '🂪', '🂫', '🂬', '🂭', '🂮'],
        ['🂱', '🂲', '🂳', '🂴', '🂵', '🂶', '🂷', '🂸', '🂹', '🂺', '🂻', '🂼', '🂽', '🂾'],
        ['🃁', '🃂', '🃃', '🃄', '🃅', '🃆', '🃇', '🃈', '🃉', '🃊', '🃋', '🃌', '🃍', '🃎'],
        ['🃑', '🃒', '🃓', '🃔', '🃕', '🃖', '🃗', '🃘', '🃙', '🃚', '🃛', '🃜', '🃝', '🃞'],
    ]

    ascii_back = "🂠"

    @staticmethod
    def create_deck():
        return [(f, s) for s in range(4) for f in range(13)]

    @staticmethod
    def get_string(card):
        return '{}{}'.format(Card.char_figures[card[0]], Card.char_suits[card[1]])

    @staticmethod
    def get_ascii(card):
        return Card.ascii_cards[card[0]][card[1]]
