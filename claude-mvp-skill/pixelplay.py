#!/usr/bin/env python3
"""全屏沉浸式MVP结算动画 — 音画同步，无UI铬，纯全屏。

用法:
    python pixelplay.py <视频路径>
    python pixelplay.py <视频路径> --loop
"""

import sys
import os
import time
import tempfile
import subprocess
import threading
import cv2
import pygame.mixer
import imageio_ffmpeg


def extract_audio(video_path):
    """用 imageio-ffmpeg 从视频中提取音频到临时 WAV 文件。"""
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp.close()

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg, '-y', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', tmp.name],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        check=True
    )
    return tmp.name


def play_fullscreen(video_path, loop=False):
    """OpenCV 纯全屏视频 + pygame 音频同步播放。"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30
    frame_delay = 1.0 / fps

    # ── 音频 ──
    audio_file = None
    has_audio = False
    try:
        audio_file = extract_audio(video_path)
        pygame.mixer.init(frequency=44100)
        sound = pygame.mixer.Sound(audio_file)
        has_audio = True
    except Exception:
        pass  # 无音频轨道或提取失败，静默播放

    # ── 全屏窗口 ──
    window_name = 'MVP'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # ── 同步播放 ──
    if has_audio:
        sound.play()

    start_time = time.time()
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            if loop:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                if has_audio:
                    sound.play()
                start_time = time.time()
                frame_idx = 0
                continue
            else:
                break

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q') or key == ord(' '):
            break

        # 帧率控制（相对于开始时间，避免累积漂移）
        frame_idx += 1
        target_time = start_time + frame_idx * frame_delay
        sleep_time = target_time - time.time()
        if sleep_time > 0:
            time.sleep(min(sleep_time, 0.05))

    # ── 清理 ──
    if has_audio:
        sound.stop()
        pygame.mixer.quit()
    cap.release()
    cv2.destroyAllWindows()

    if audio_file and os.path.exists(audio_file):
        try:
            os.unlink(audio_file)
        except Exception:
            pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python pixelplay.py <video_path> [--loop]")
        sys.exit(1)

    path = os.path.abspath(sys.argv[1])
    loop = '--loop' in sys.argv

    if not os.path.exists(path):
        print(f"[ERROR] Video not found: {path}")
        sys.exit(1)

    play_fullscreen(path, loop=loop)
