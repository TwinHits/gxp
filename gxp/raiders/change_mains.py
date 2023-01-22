import datetime

from gxp.raiders.constants import MainChangeErrors

from gxp.experience.serializers import ExperienceGainSerializer

def change_mains(old_main, new_main):
    print(f"old_main {old_main}")
    print(f"new_main {new_main}")
    main_change_event_id = "MAIN_CHANGE"

    # check if alt is actually alt
    old_main_alts = old_main.alts
    if new_main not in old_main_alts:
        raise Exception(MainChangeErrors.NOT_ALT)

    # merge aliases
    old_main_aliases = old_main.aliases.all()
    for alias in old_main_aliases:
        alias.raider = new_main
        alias.save()

    # merge alts
    for alt in old_main_alts:
        alt.main = new_main
        alt.save()

    # set main
    old_main.main = new_main
    new_main.main = None
    new_main.save()

    # set experience event on main with tokens
    ExperienceGainSerializer.create_experience_gain(
        main_change_event_id,
        new_main.id,
        raid_id=None,
        tokens={
            "old_main": old_main.name,
            "new_main": new_main.name
        },
    )