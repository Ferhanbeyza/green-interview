import argparse
import time

import cv2

from common import analyze_frame, find_videos, make_tracker, save_labels, warm_up

THUMB = (160, 90)


def thumbnail(frame):
    small = cv2.resize(frame, THUMB, interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)


def shrink(frame, height):
    h, w = frame.shape[:2]
    if h <= height:
        return frame
    return cv2.resize(frame, (int(w * height / h), height), interpolation=cv2.INTER_AREA)


def process_video(video, threshold, max_gap, height):
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    max_gap_frames = max(1, int(round(max_gap * fps)))

    labels, analyzed = [], []
    last_thumb, last_label, since = None, None, 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        thumb = thumbnail(frame)
        changed = (
            last_thumb is None
            or since >= max_gap_frames
            or float(cv2.absdiff(thumb, last_thumb).mean()) > threshold
        )
        if changed:
            last_label = analyze_frame(shrink(frame, height))
            last_thumb, since = thumb, 0
        else:
            since += 1
        labels.append(last_label)
        analyzed.append(changed)
    cap.release()
    return labels, analyzed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path", nargs="?", default="data")
    p.add_argument("--threshold", type=float, default=5.0,
                   help="kareler arasi ortalama piksel farki esigi (0-255)")
    p.add_argument("--max-gap", type=float, default=1.0,
                   help="model calistirilmadan gecebilecek en uzun sure (sn)")
    p.add_argument("--height", type=int, default=480,
                   help="modele verilecek karenin yuksekligi (piksel)")
    args = p.parse_args()

    videos = find_videos(args.path)
    warm_up()

    tracker = make_tracker("optimized")
    tracker.start()
    t0 = time.time()
    total = calls = 0
    for video in videos:
        labels, analyzed = process_video(video, args.threshold, args.max_gap, args.height)
        total += len(labels)
        calls += sum(analyzed)
        save_labels("optimized", video, labels, analyzed)
        print(f"{video}: {len(labels)} kare, {sum(analyzed)} model cagrisi")
    emissions = tracker.stop()

    print(f"\nOPTIMIZE  kare={total}  model cagrisi={calls}  "
          f"sure={time.time() - t0:.1f} sn  CO2={emissions * 1000:.4f} g")


if __name__ == "__main__":
    main()
