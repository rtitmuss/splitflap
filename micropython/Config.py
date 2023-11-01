# element order when displaying alphabet
# display_order = 'abcdefghijklmnopqrst'
display_order = 'rqnmjifebatspolkhgdc'

# flap offsets in display order from calibration
display_offsets = [0, 0, 0, 0, 5, 22, 11, 0, 0, 0,
                   0, 0, 0, 0, 32, 0, 0, 0, 0, 0]

_alphabet = 'abcdefghijklmnopqrstuvwxyz'
_display_len = len(display_order)

test_words = [
    _alphabet,
    _alphabet[3:],
    _alphabet[6:],
    "A" * _display_len,
    "B" * _display_len,
    "Y" * _display_len,
    "Z" * _display_len,
    "Hello  World", "Spirit", "Purple", "Marvel", "Garden", "Elephant", "Football", "Birthday", "Rainbow",
    "Keyboard", "Necklace", "Positive", "Mountain", "Campaign", "Hospital", "Orbit", "Pepper",
    "7849501273", "2398756104", "5476928310", "1062547983", "3987165420",
    "$" * _display_len,
    "&" * _display_len,
    "$#$#$#$#$##$#$#$#$#$",
]
