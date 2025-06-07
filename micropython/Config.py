from provider.ProviderArt import ProviderArt
from provider.ProviderClock import ProviderClock
from provider.ProviderDadJoke import ProviderDadJoke
from provider.ProviderMotion import ProviderMotion
from provider.ProviderNewYearCountdown import ProviderNewYearCountdown
from provider.ProviderLetters import ProviderLetters
from provider.ProviderWordClock import ProviderWordClock

# default timezone for the application
default_timezone = "Europe/Stockholm"

# element order when displaying alphabet
# display_order = ['abcdefghij','klmnopqrst']
display_order = ['vurqnmjifeba',
                 'xwtspolkhgdc']

# flap offsets in display order for calibration
display_offsets = [11, 5, -12, -8, -21, 4, 18, 17, 11, 5, 0, -3,
                   -6, 2, 15, -18, -18, -22, 22, -2, -4, -5, 1, 2]

providers = {
    "{CLOCK_STO}": ProviderClock("STO  %H:%M    %d.%m.%Y", "Europe/Stockholm"),
    "{CLOCK_ADL}": ProviderClock("ADL  %H:%M    %d.%m.%Y", "Australia/Adelaide"),
    "{CLOCK_NYC}": ProviderClock("NYC  %H:%M    %d.%m.%Y", "America/New_York"),
    "{WORD_CLOCK_STO_EN}": ProviderWordClock("en", "Europe/Stockholm"),
    "{WORD_CLOCK_STO_SV}": ProviderWordClock("sv", "Europe/Stockholm"),
    "{NEW_YEAR_STO}": ProviderNewYearCountdown("Europe/Stockholm"),
    "{ART}": ProviderArt(),
    "{MOTION}": ProviderMotion(),
    "{DAD_JOKE}": ProviderDadJoke(),
    "{LETTERS}": ProviderLetters(),
}

_alphabet = 'abcdefghijklmnopqrstuvwxyz'
_display_len = len(display_order)

test_words = [
    # display length words
    _alphabet[:_display_len],
    _alphabet[3:3 + _display_len],
    _alphabet[6:6 + _display_len],
    "A" * _display_len,
    "B" * _display_len,
    "Y" * _display_len,
    "Z" * _display_len,
    "$" * _display_len,
    "&" * _display_len,
    "$#" * int(_display_len / 2) + "#$" * int(_display_len / 2),
    # short words
    "Hello", "World", "Spirit", "Purple", "Marvel", "Garden", "Elephant", "Football", "Birthday", "Rainbow",
    "Keyboard", "Necklace", "Positive", "Mountain", "Campaign", "Hospital", "Orbit", "Pepper",
    "7849501273", "2398756104", "5476928310", "1062547983", "3987165420",
]
