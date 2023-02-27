from mtga import *

mtga = mtga_reader('~/Games/magic-the-gathering-arena/drive_c/Program Files/Wizards of the Coast/MTGA/', lang='enUS')

card = mtga.get_card_by_name("captain sisay", get_art=False)[0]
print(card)

art = mtga.get_card_art_by_id(card['art'])
print(art)