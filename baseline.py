import sys
import time

import cv2

from common import analyze_frame, find_videos, make_tracker, save_labels, warm_up


def process_video(video):
    cap = cv2.VideoCapture(video)
    labels = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        labels.append(analyze_frame(frame))
    cap.release()
    return labels


def main():
    videos = find_videos(sys.argv[1] if len(sys.argv) > 1 else "data")
    warm_up()

    tracker = make_tracker("baseline")
    tracker.start()
    t0 = time.time()
    total = 0
    for video in videos:
        labels = process_video(video)
        total += len(labels)
        save_labels("baseline", video, labels, [True] * len(labels))
        print(f"{video}: {len(labels)} kare, {len(labels)} model cagrisi")
    emissions = tracker.stop()

    print(f"\nBASELINE  kare={total}  model cagrisi={total}  "
          f"sure={time.time() - t0:.1f} sn  CO2={emissions * 1000:.4f} g")


if __name__ == "__main__":
    main()
