import os
import shutil
import cv2
from yt_dlp import YoutubeDL

def download_video(youtube_url: str, output_path: str) -> str:
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "outtmpl": output_path,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        filename = ydl.prepare_filename(info)
    return filename


def on_trackbar(pos: int):
    """Trackbar callback to seek to the selected frame."""
    global seek_frame
    seek_frame = pos


if __name__ == "__main__":
    # 1. Set your YouTube link here:
    YT_LINK = "https://www.youtube.com/watch?v=TIF3xiap60U&ab_channel=YNOTStudios"

    # 2. Define a local temporary filename in working dir
    temp_video_path = "temp_video.mp4"

    # 3. Reset or create frames directory
    frames_dir = "frames"
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    try:
        # 4. Download the video into the same directory
        print("Downloading video...")
        video_file = download_video(YT_LINK, output_path=temp_video_path)
        print(f"Downloaded to: {video_file}")

        # 5. Open the video
        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video file {video_file}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Total frames: {total_frames}")

        # 6. Create window and trackbar
        window_name = "Video Player (a/d to step, s to save, q to quit)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.createTrackbar("Frame", window_name, 0, total_frames - 1, on_trackbar)

        seek_frame = 0
        saved_count = 0

        while True:
            # Seek to the selected frame and grab it
            cap.set(cv2.CAP_PROP_POS_FRAMES, seek_frame)
            ret, frame = cap.read()
            if not ret:
                print("Reached end of video or failed to read frame.")
                break

            # Reflect the seek in the trackbar
            cv2.setTrackbarPos("Frame", window_name, seek_frame)
            cv2.imshow(window_name, frame)

            # Wait indefinitely for a key press
            key = cv2.waitKey(0) & 0xFF

            if key == ord("q"):
                # Quit
                break
            elif key == ord("s"):
                # Save current frame into the frames directory
                save_name = os.path.join(frames_dir, f"frame_{seek_frame:06d}.jpg")
                cv2.imwrite(save_name, frame)
                print(f"Saved {save_name}")
                saved_count += 1
            elif key == ord("d"):
                # Step one frame forward
                seek_frame = min(seek_frame + 1, total_frames - 1)
            elif key == ord("a"):
                # Step one frame backward
                seek_frame = max(seek_frame - 1, 0)
            else:
                # Ignore other keys, stay on same frame
                continue

        cap.release()
        cv2.destroyAllWindows()
        print(f"Done. Total frames saved: {saved_count}")

    finally:
        # Remove the downloaded video file when done
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
