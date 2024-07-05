To prepare unity : 
Remove:
Breed
CharacteristicCategory
Characteristic
Effect
SpellVariant
SpellLevelEffect
SpellLevel
Spell

New structure :

Elem

ElemSpell

Spell
index
character_id
is_disenchantment
is_boost
is_healing
on_enemy
elem_spells

Spell
ap_cost
max_cast
min_range
range
duration_boost
range_can_be_boosted
min_player_level
