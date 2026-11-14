import csv
import glob
import os

import cv2
import numpy as np
from codecarbon import OfflineEmissionsTracker
from deepface import DeepFace

RESULTS_DIR = "results"
VIDEO_EXTS = (".mp4", ".mov", ".avi", ".mkv", ".webm")


def find_videos(path):
    if os.path.isfile(path):
        return [path]
    videos = sorted(
        f for f in glob.glob(os.path.join(path, "*")) if f.lower().endswith(VIDEO_EXTS)
    )
    if not videos:
        raise SystemExit(f"'{path}' icinde video bulunamadi. data/ klasorune bir mulakat videosu koyun.")
    return videos


def analyze_frame(frame):
    result = DeepFace.analyze(
        img_path=frame,
        actions=["emotion"],
        enforce_detection=False,
        silent=True,
    )
    if isinstance(result, list):
        result = result[0]
    return result["dominant_emotion"]


def warm_up():
    analyze_frame(np.zeros((224, 224, 3), dtype=np.uint8))


def make_tracker(name):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    return OfflineEmissionsTracker(
        country_iso_code="TUR",
        project_name=name,
        output_dir=RESULTS_DIR,
        output_file=f"emissions_{name}.csv",
        log_level="error",
    )


def save_labels(name, video, labels, analyzed):
    stem = os.path.splitext(os.path.basename(video))[0]
    out = os.path.join(RESULTS_DIR, f"labels_{name}_{stem}.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frame", "emotion", "analyzed"])
        for i, (label, a) in enumerate(zip(labels, analyzed)):
            w.writerow([i, label, int(a)])
    return out
