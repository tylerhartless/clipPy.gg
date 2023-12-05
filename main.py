import os
import sys
import PySimpleGUI as sg
import re
from video_editor import format_clip, MyBarLogger
from facecam_selector import map_facecam
from configparser import ConfigParser


sg.theme('dark grey 9')


class VideoEditorGUI:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = ConfigParser()
        self.load_config()
        self.layout = [
            [sg.Text("Select Game (or N/A if game is not listed):"),
             sg.Combo(['Apex', 'Warzone', 'N/A'], default_value='Apex', key='selected_game')],
            [sg.Text("Select Elements To Include:")],
            [sg.Checkbox("Facecam", True, key='facecam'),
             sg.Checkbox("Health", True, key='health'),
             sg.Checkbox("Kills/Dmg", False, key='killsdmg'),
             sg.Checkbox("Placement", False, key='placement'),
             sg.Checkbox("Weapon", False, key='weapon')],
            [sg.Text("Output Directory:")],
            [sg.Input(size=(43, 1), key="output_dir", default_text=self.last_output_dir), sg.FolderBrowse()],
            [sg.Text("Add Clip to Queue:")],
            [sg.Input(size=(43, 1), key="input_file", enable_events=True), sg.FileBrowse()],
            [sg.Listbox(values=[], size=(50, 3), key="queue_display", select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED)],
            [sg.Button("Remove from Queue"), sg.Button("Process Queue")],
            [sg.Text("Processing:"), sg.Text("", key="current_clip")],
            [sg.ProgressBar(100, orientation='h', size=(33.5, 20), key='progress_bar'),
             sg.Text("", key='progress_percent')],
        ]

        self.window = sg.Window("clipPy.gg", self.layout)
        self.my_bar_logger = MyBarLogger(window=self.window)

    def load_config(self):
        config = ConfigParser()
        config.read(self.config_file)
        self.last_output_dir = config.get('Settings', 'LastOutputDir', fallback='')
        self.video_queue = []

    def save_config(self):
        config = ConfigParser()
        config.read(self.config_file)

        config['Settings']['LastOutputDir'] = self.last_output_dir
        config['Settings']['facecamxy'] = self.coords

        # Manually write the updated configuration back to the file
        with open(self.config_file, 'w') as configfile:
            for section in config.sections():
                configfile.write(f'[{section}]\n')
                for key, value in config.items(section):
                    configfile.write(f'{key} = {value}\n')

    def update_queue_display(self):
        filenames = [os.path.basename(item) for item in self.video_queue]
        self.window["queue_display"].update(values=filenames)

    def add_to_queue(self, file_path):
        self.video_queue.append(file_path)
        self.update_queue_display()

    def remove_from_queue(self, values):
        selected_items = values.get("queue_display", [])
        if selected_items:
            updated_queue = [item for item in self.video_queue if os.path.basename(item) not in selected_items]
            self.video_queue = updated_queue
            self.update_queue_display()

    def process_queue(self):
        output_dir = self.window["output_dir"].get()
        selected_game = self.window["selected_game"].get()
        facecam_enabled = self.window["facecam"].get()
        health_hud = self.window["health"].get()
        placement_hud = self.window["placement"].get()
        killsdmg_hud = self.window["killsdmg"].get()
        weapon_hud = self.window["weapon"].get()

        if facecam_enabled and self.get_facecamxy() is None:
            self.window.write_event_value('-FACECAM_LOCATION_NEEDED-', '')
            return

        if output_dir and self.video_queue:
            total_clips = len(self.video_queue)

            # Create a thread to process the queue
            def process_queue_thread():
                for i, input_file in enumerate(self.video_queue):
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    output_video = f"{output_dir}/{base_name}-clipPy.gg.mp4"

                    # Update the "current_clip" text element using an event
                    self.window.write_event_value('-UPDATE_CURRENT_CLIP-', (i + 1, total_clips, base_name))

                    format_clip(
                        input_file, output_video,
                        selected_game,
                        health_hud, placement_hud, killsdmg_hud, weapon_hud,
                        facecam_enabled,
                        logger=self.my_bar_logger
                    )
                # Send an event to signal the end of processing
                self.window.write_event_value('-PROCESSING_COMPLETED-', '')

            # Start the thread
            import threading
            threading.Thread(target=process_queue_thread, daemon=True).start()

    def restart_program(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)
    def get_facecamxy(self):
        config = ConfigParser()
        config.read(self.config_file)
        facecamxy = config.get('Settings', 'facecamxy', fallback='')
        if facecamxy:
            value = self.get_coordinates(facecamxy)
            return value
        else:
            return None

    def get_coordinates(self, text):
        pattern = r'(\d+), (\d+), (\d+), (\d+)'
        match = re.match(pattern, text)

        if match:
            coords = tuple(int(x) for x in match.groups())
            return coords
        else:
            return None

    def run(self):
        processing_event_triggered = False

        while True:
            event, values = self.window.read(timeout=100)

            if if (event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT) and 
                sg.popup_yes_no('Process queue is running. Are you sure?') == 'Yes':
                self.save_config()
                break

            current_output_dir = values.get("output_dir", "")
            if current_output_dir != self.last_output_dir:
                self.last_output_dir = current_output_dir

            elif event == "Process Queue" and not processing_event_triggered and len(self.video_queue) != 0:
                self.process_queue()
                processing_event_triggered = True  # Set the flag to avoid repeated event triggers

            elif event == "Process Queue" and len(self.video_queue) == 0:
                sg.popup_ok("Please add files to queue before processing.", background_color="firebrick4", no_titlebar=True)

            elif event == "Process Queue" and processing_event_triggered:
                sg.popup_ok("Please wait until current queue is done processing.", background_color="firebrick4", no_titlebar=True)

            elif event == "Remove from Queue" and not processing_event_triggered:
                self.remove_from_queue(values)

            elif event == "Remove from Queue" and processing_event_triggered:
                sg.popup_ok("Please wait until current queue is done processing.", background_color="firebrick4", no_titlebar=True)

            elif event == "input_file" and not processing_event_triggered:
                input_file = values["input_file"]
                if input_file:
                    self.add_to_queue(input_file)

            elif event == "input_file" and processing_event_triggered:
                sg.popup_ok("Please wait until current queue is done processing.", background_color="firebrick4", no_titlebar=True)

            elif event == '-FACECAM_LOCATION_NEEDED-':
                processing_event_triggered = False  # Reset the flag so user can process after mapping facecam
                facecam_warning = sg.popup_yes_no("Do you have a Facecam?", "(if yes, program will restart once Facecam is selected)", no_titlebar=True, background_color="DarkOrchid4")

                if facecam_warning == 'Yes':
                    input_file = values["input_file"]
                    coords_arr = map_facecam(input_file)

                    if coords_arr is not None:
                        self.coords = ', '.join(str(x) for x in coords_arr)
                        self.save_config()
                        sg.popup_auto_close("clipPy.gg will now restart", no_titlebar=True,
                                            background_color="DarkOrchid4", auto_close_duration=5)
                        self.restart_program()

                    elif coords_arr is None:
                        self.window.Refresh()


                elif facecam_warning == 'No':
                    self.window['facecam'].update(False)
                    self.process_queue()
                    processing_event_triggered = True


            elif event == '-UPDATE_CURRENT_CLIP-':
                i, total, base_name = values[event]
                self.window["current_clip"].update(f"{i}/{total} - {base_name}")
                self.window.Refresh()

            elif event == '-UPDATE_PROGRESS-':
                percentage = values[event]
                self.window["progress_bar"].update(current_count=percentage)
                self.window["progress_percent"].update(f"{percentage}{'%'}")
                self.window.Refresh()

            elif event == '-PROCESSING_COMPLETED-':
                sg.popup("Video processing completed!", title="Success")
                self.video_queue = []
                self.update_queue_display()
                processing_event_triggered = False  # Reset the flag after processing

        self.window.close()


if __name__ == "__main__":
    gui = VideoEditorGUI()
    gui.run()
