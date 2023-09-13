from enum import Enum
import random

DEBUG = False

class UserBustException(Exception):
    "Raised when the user bust."
    pass

class DealerBustException(Exception):
    "Raised when the dealer bust."
    pass

class CardSuit(Enum):
    SPADE = "♠"
    HEART = "♥"
    CLUB = "♣"
    DIAMOND = "♦"

class Card:
    ACE_RANK: int = 0 # 1 or 11

    def __init__(self, suit: CardSuit, rank: int):
        assert 0 <= rank <= 12, f"Rank expected to be between 0-12, got {rank}."
        self.suit = suit
        self._rank = rank

    def rank_str(self) -> str:
        if self._rank == 0:
            return "A"
        elif 1 <= self._rank <= 9:
            return str(self._rank + 1)
        elif self._rank == 10:
            return "J"
        elif self._rank == 11:
            return "Q"
        elif self._rank == 12:
            return "K"
        else:
            raise ValueError(f"Rank expected to be between 0-12, got {self._rank}.")

    def rank_value(self, ace_high: bool) -> int:
        if self._rank == 0:
            # return Card.ACE_RANK
            if ace_high:
                return 11
            else:
                return 1
        elif 1 <= self._rank <= 9:
            return self._rank + 1
        elif 10 <= self._rank <= 12:
            return 10
        else:
            raise ValueError(f"Rank expected to be between 0-12, got {self._rank}.")

    def __str__(self) -> str:
        return f"{self.suit.value}{self.rank_str()}"

    def __repr__(self) -> str:
        return f"{self.suit.value}{self.rank_str()}"

class GameState:
    def __init__(self, deck: [Card], dealer_cards: [Card], user_cards: [Card]):
        self.deck = deck
        self.dealer_cards = dealer_cards
        self.user_cards = user_cards

    def _draw_card(self) -> Card:
        return random.choice(self.deck)

    def _total_cards(self, cards: [Card]) -> int:
        card_values_ace_high = [card.rank_value(ace_high=True) for card in cards]
        ace_high_sum = sum(card_values_ace_high)
        card_values_ace_low = [card.rank_value(ace_high=False) for card in cards]
        ace_low_sum = sum(card_values_ace_low)
        return min(ace_high_sum, ace_low_sum)

    def _check_did_user_bust(self) -> bool:
        return self._total_cards(self.user_cards) > 21

    def _check_did_dealer_bust(self) -> bool:
        return self._total_cards(self.dealer_cards) > 21

    def dealer_should_hit(self) -> bool:
        dealer_values = [card.rank_value(ace_high=True) for card in self.dealer_cards]
        dealer_total = sum(dealer_values)

        if dealer_total > 17:
            # Dealer does not hit on values over 17.
            return False
        elif dealer_total == 17:
            if 11 in dealer_values:
                # Dealer does hit on soft 17.
                return True
            else:
                # Dealer does not hit on hard 17.
                return False
        else:
            # Dealer always hits on values under 17.
            return True

    def draw_card_for_dealer(self):
        self.dealer_cards.append(self._draw_card())

    def draw_card_for_user(self):
        self.user_cards.append(self._draw_card())

    def check_game_state(self):
        if self._check_did_user_bust():
            raise UserBustException
        if self._check_did_dealer_bust():
            raise DealerBustException

    def print_game_state(self, reveal_dealer_cards: bool):
        print("Dealer Cards: ", end="")
        if reveal_dealer_cards:
            print(self.dealer_cards)
        else:
            print(f"[{self.dealer_cards[0]}, ??]")
        
        print("User Cards:   ", end="")
        print(self.user_cards)
        print()

    def __str__(self) -> str:
        return f"Dealer cards: {self.dealer_cards}\nUser cards: {self.user_cards}"

def create_new_deck() -> [Card]:
    deck: [Card] = []
    for suit in CardSuit:
        for rank in range(0, 13):
            card = Card(suit, rank)
            deck.append(card)
    if DEBUG:
        print(deck)
    return deck

def create_new_game_state() -> GameState:
    return GameState(create_new_deck(), [], [])

def initial_draw_phase(game_state: GameState) -> GameState:
    game_state.draw_card_for_user()
    game_state.draw_card_for_dealer()
    game_state.draw_card_for_user()
    game_state.draw_card_for_dealer()

    game_state.print_game_state(reveal_dealer_cards=False)
    
    return game_state

def user_draw_phase(game_state: GameState) -> GameState:
    continue_drawing = True
    while continue_drawing:
        user_response = input("Do you want to hit (H) or stand (S)? ")
        if user_response in {"H", "h"}:
            game_state.draw_card_for_user()
            game_state.print_game_state(reveal_dealer_cards=False)
            game_state.check_game_state()
            continue_drawing = True
        elif user_response in {"S", "s"}:
            continue_drawing = False
        else:
            print("Invalid input.")
            continue_drawing = True
    return game_state

def dealer_draw_phase(game_state: GameState) -> GameState:
    game_state.print_game_state(reveal_dealer_cards=True)
    while game_state.dealer_should_hit():
        game_state.draw_card_for_dealer()
        game_state.print_game_state(reveal_dealer_cards=True)
        game_state.check_game_state()
    return game_state

def evaluate_game_state(game_state: GameState):
    user_values = [card.rank_value(ace_high=True) for card in game_state.user_cards]
    user_sum = sum(user_values)
    if user_sum > 21:
        user_values = [card.rank_value(ace_high=False) for card in game_state.user_cards]
        user_sum = sum(user_values)

    dealer_values = [card.rank_value(ace_high=True) for card in game_state.dealer_cards]
    dealer_sum = sum(dealer_values)
    if dealer_sum > 21:
        dealer_values = [card.rank_value(ace_high=False) for card in game_state.dealer_cards]
        dealer_sum = sum(dealer_values)
        
    if user_sum > dealer_sum:
        print("You win!")
    elif dealer_sum > user_sum:
        print("You lose!")
    else:
        print("Push!")

def start_new_game():
    game_state = create_new_game_state()
    game_state = initial_draw_phase(game_state)
    game_state = user_draw_phase(game_state)
    game_state = dealer_draw_phase(game_state)
    evaluate_game_state(game_state)

def print_header():
    print("Welcome to Blackjack!")
    print("---------------------")
    print()

def play_again_prompt() -> bool:
    user_input = input("Play again (Y/n)? ")
    return user_input in {"Y", "y", ""}

def main():
    continue_playing = True
    while continue_playing:
        try:
            print_header()
            start_new_game()
        except UserBustException:
            print("You bust: game over!")
        except DealerBustException:
            print("Dealer bust: you win!")
        finally:
            continue_playing = play_again_prompt()
            if continue_playing:
                print()

if __name__ == "__main__":
    main()