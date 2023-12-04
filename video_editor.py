from moviepy.editor import VideoFileClip, clips_array, CompositeVideoClip
from moviepy.video.fx.all import crop, resize
from skimage.filters import gaussian
from proglog import ProgressBarLogger
from game_hud import game_health_bar
from hud_compositor import hud_selector
import configparser
import re


class MyBarLogger(ProgressBarLogger):
    def __init__(self, window):
        super().__init__()
        self.last_message = ''
        self.previous_percentage = 0
        self.window = window

    def callback(self, **changes):
        for (parameter, value) in changes.items():
            self.last_message = value

    def bars_callback(self, bar, attr, value, old_value=None):
        if 'Writing video' in self.last_message:
            percentage = (value / self.bars[bar]['total']) * 100
            if 0 < percentage < 100 and int(percentage) != self.previous_percentage:
                self.previous_percentage = int(percentage)
                self.window.write_event_value('-UPDATE_PROGRESS-', self.previous_percentage)

    def get_previous_percentage(self):
        return self.previous_percentage

    def update_gui_with_percentage(self):
        pass


# Import config values for facecam placement
config = configparser.ConfigParser()
config.read('config.ini')


# Parse string from configparser and return coordinates as a tuple
def get_coordinates(text):
    pattern = r'(\d+), (\d+), (\d+), (\d+)'
    match = re.match(pattern, text)

    if match:
        coords = tuple(int(x) for x in match.groups())
        return coords
    else:
        return None


facecamxy = get_coordinates(config['Settings']['facecamxy'])


# Returns a blurred version of the video for background canvas
def blur(image):
    return gaussian(image.astype(float), sigma=4.5)


def format_clip(input_video, output_video,
                selected_game,
                health_hud, placement_hud, killsdmg_hud, weapon_hud,
                facecam_enabled,
                logger=None):

    # Load original video clip
    og_clip = VideoFileClip(input_video)

    # Resize to 1920x1080 for cross resolution compatibility
    og_clip_resized = og_clip.resize(width=1920, height=1080)

    # Crop POV clip
    pov_clip = crop(og_clip_resized, x_center=960, y_center=540, width=889, height=1080)
    pov_clip_resized = pov_clip.resize(width=1080, height=1312)

    if facecam_enabled is True:
        # Crop Facecam clip using tuple extracted from config, then resize
        facecam_clip = crop(og_clip_resized, x1=facecamxy[0], y1=facecamxy[1], x2=facecamxy[2], y2=facecamxy[3])
        facecam_clip_resized = facecam_clip.resize(width=1080, height=608)
        # Create a clips array with Facecam and POV clips, Facecam on top
        base_video = clips_array([[facecam_clip_resized], [pov_clip_resized]])
    else:
        # Crop clip for background canvas
        bg_clip = crop(og_clip_resized, x_center=960, y_center=540, width=608, height=1080)
        # Blur and resize background clip
        bg_clip_blurred = bg_clip.fl_image(blur)
        final_bg = bg_clip_blurred.resize(width=1080, height=1920)
        # Composite pov clip on top of blurred background
        base_video = CompositeVideoClip([final_bg, pov_clip_resized.set_position("center")])

    # Determine which HUD mask to use from GUI input
    hud = game_health_bar(selected_game, og_clip_resized)
    health, squads, dmg, weapon = hud

    # Default export without game HUD
    final_video = base_video

    # Check if HUD components exist and are enabled, and include it in the final composition
    final_video = hud_selector(health, squads, dmg, weapon,
                               health_hud, placement_hud, killsdmg_hud, weapon_hud,
                               selected_game, facecam_enabled,
                               final_video)

    # Confirm video is in correct resolution after compositing
    final_video_resized = final_video.resize((1080, 1920))

    # Export the final video
    final_video_resized.write_videofile(output_video, codec="libx264", audio_codec="aac", logger=logger)
