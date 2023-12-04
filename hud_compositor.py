from moviepy.editor import CompositeVideoClip
import configparser
import re


# Import config values for hud placement
config = configparser.ConfigParser()
config.read('config.ini')


# Parse string from configparser and return coordinates as a tuple
def getCoordinates(text):
    pattern = r'(\d+), (\d+)'
    match = re.match(pattern, text)
    if match:
        coords = tuple(int(x) for x in match.groups())
        return coords

# Any future HUD elements will be imported here from the ini

apexhealth = getCoordinates(config['Settings']['apexhealth'])
apexplacement = getCoordinates(config['Settings']['apexplacement'])
apexkills = getCoordinates(config['Settings']['apexkills'])
apexweapon = getCoordinates(config['Settings']['apexweapon'])


def hud_selector(
        health, squads, dmg, weapon,
        health_hud, placement_hud, killsdmg_hud, weapon_hud,
        selected_game, facecam_enabled,
        final_video):
    if facecam_enabled is True:
        if health is not None and health_hud is True:
            if selected_game == "Apex":
                final_video = CompositeVideoClip(
                    [final_video, health.set_position((apexhealth))])
            elif selected_game == "Warzone":
                final_video = CompositeVideoClip(
                    [final_video, health.set_position((apexhealth))]) # fill this in with wz health when you figure it out

        if squads is not None and placement_hud is True:
            if selected_game == "Apex":
                final_video = CompositeVideoClip(
                    [final_video, squads.set_position((apexplacement))])

        if dmg is not None and killsdmg_hud is True:
            if selected_game == "Apex":
                final_video = CompositeVideoClip(
                    [final_video, dmg.set_position((apexkills))])

        if weapon is not None and weapon_hud is True:
            if selected_game == "Apex":
                final_video = CompositeVideoClip(
                    [final_video, weapon.set_position((apexweapon))])
    else:
        # This is not elegant but it works for me currently
        if health is not None and health_hud is True:
            if selected_game == "Apex":
                final_video = CompositeVideoClip(
                    [final_video, health.set_position((apexhealth[0], apexhealth[1] + 1000))])
            elif selected_game == "Warzone":
                final_video = CompositeVideoClip(
                    [final_video,
                     health.set_position((apexhealth[0], apexhealth[1] + 1000))])

        if squads is not None and placement_hud is True:
            if selected_game == "Apex":
                final_video = CompositeVideoClip(
                    [final_video, squads.set_position((apexplacement[0], apexplacement[1] + 1000))])

        if dmg is not None and killsdmg_hud is True:
            if selected_game == "Apex":
                final_video = CompositeVideoClip(
                    [final_video, dmg.set_position((apexkills[0], apexkills[1] + 1000))])

        if weapon is not None and weapon_hud is True:
            if selected_game == "Apex":
                final_video = CompositeVideoClip(
                    [final_video, weapon.set_position((apexweapon[0], apexweapon[1] + 1000))])

    return final_video
