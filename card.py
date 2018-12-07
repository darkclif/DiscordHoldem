class Card:
    colors = ['♠', '♥', '♦', '♣']
    figures = list(str(range(2, 11))) + ['J', 'Q', 'K', 'A']

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
        return [Card(c, f) for c in range(4) for f in range(13)]

    def get(self):
        return Card.figures[self._figure], Card.colors[self._color]

    def get_ascii(self):
        return Card.ascii_cards[self._color][self._figure]

    def __init__(self, color, figure):
        self._color = color
        self._figure = figure

    def __str__(self):
        return '%s %s'.format(Card.figures[self._figure], Card.colors[self._color])

