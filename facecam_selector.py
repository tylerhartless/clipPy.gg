from moviepy.editor import VideoFileClip
from matplotlib.widgets import RectangleSelector, Button
import matplotlib.pyplot as plt
import matplotlib as mpl

coords = None
confirmed = False

def map_facecam(input_video):
    mpl.rcParams['toolbar'] = 'None'
    og_clip = VideoFileClip(input_video)
    screenshot = og_clip.get_frame(2)

    def line_select_callback(eclick, erelease):
        # eclick and erelease are the press and release events
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        x1 = round(x1)
        y1 = round(y1)
        x2 = round(x2)
        y2 = round(y2)
        global coords
        coords = [x1, y1, x2, y2]

    def toggle_selector(event):
        print(' Key pressed.')
        if event.key in ['Q', 'q'] and toggle_selector.RS.active:
            print(' RectangleSelector deactivated.')
            toggle_selector.RS.set_active(False)
        if event.key in ['A', 'a'] and not toggle_selector.RS.active:
            print(' RectangleSelector activated.')
            toggle_selector.RS.set_active(True)

    def on_confirm_button_clicked(event):
        global coords, confirmed
        confirmed = True
        plt.close()  # Close the window
        return coords  # Return the coordinates

    def on_close(event):
        global coords, confirmed
        if confirmed is False:
            coords = None
        plt.close()  # Close the window
        return coords  # Return None when the window is closed without confirming


    fig, current_ax = plt.subplots()

    plt.imshow(screenshot)

    # drawtype is 'box' or 'line' or 'none'
    toggle_selector.RS = RectangleSelector(current_ax, line_select_callback,
                                           useblit=True,
                                           button=[1, 3],  # don't use middle button
                                           minspanx=5, minspany=5,
                                           spancoords='pixels',
                                           interactive=True)
    plt.connect('key_press_event', toggle_selector)
    plt.connect('close_event', on_close)

    plt.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    current_ax.set_title('Click and Drag to highlight Facecam')

    # Add Confirm and Cancel buttons
    confirm_button_ax = plt.axes([0.81, 0.01, 0.1, 0.05])  # [left, bottom, width, height]
    confirm_button = Button(confirm_button_ax, 'Confirm')
    confirm_button.on_clicked(on_confirm_button_clicked)

    cancel_button_ax = plt.axes([0.7, 0.01, 0.1, 0.05])  # [left, bottom, width, height]
    cancel_button = Button(cancel_button_ax, 'Cancel')
    cancel_button.on_clicked(on_close)

    plt.tight_layout()
    plt.show()

    return coords