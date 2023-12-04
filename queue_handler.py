import os

def update_queue_display(window, video_queue):
    filenames = [os.path.basename(item) for item in video_queue]
    window["queue_display"].update(values=filenames)

def add_to_queue(video_queue, file_path, window):
    video_queue.append(file_path)
    update_queue_display(window, video_queue)

def remove_from_queue(video_queue, values, window):
    selected_items = values.get("queue_display", [])
    if selected_items:
        updated_queue = [item for item in self.video_queue if os.path.basename(item) not in selected_items]
        video_queue = updated_queue
        update_queue_display(window, video_queue)
