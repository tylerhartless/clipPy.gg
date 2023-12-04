from moviepy.editor import ImageClip
from moviepy.video.fx.all import crop, resize


def game_health_bar(game, og_clip):
    match game:
        case "Apex":
            # Load health bar mask as an ImageClip
            apex_mask = ImageClip("./masks/apex/apex_hud.png", ismask=True)
            # Set the health bar mask as a mask for the original clip
            og_clip_apex = og_clip.set_mask(apex_mask)
            # Crop out health bar
            health = crop(og_clip_apex, x1=50, y1=950, x2=441, y2=1033)
            # Squads remaining/current place
            squads = crop(og_clip_apex, x1=1618, y1=46, x2=1880, y2=86)
            # Kills/Damage
            dmg = crop(og_clip_apex, x1=1595, y1=87, x2=1854, y2=129)
            # Weapon
            weapon = crop(og_clip_apex, x1=1500, y1=950, x2=1877, y2=1060)
            # Resize elements
            health = health.resize(1.75)
            weapon = weapon.resize(.75)
            dmg = dmg.resize(1.35)
            return health, squads, dmg, weapon
        case "Warzone":
            wz_mask = ImageClip("./masks/warzone/health_bar_wz.png", ismask=True)
            og_clip_wz = og_clip.set_mask(wz_mask)
            health = crop(og_clip_wz, x1=32, y1=977, x2=236, y2=1035)
            health = health.resize(2)
            return health, None, None, None
        case _:
            return None, None, None, None
