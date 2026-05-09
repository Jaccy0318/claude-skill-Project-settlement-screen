# MVP Settlement Animation - Claude Code Skill

When you finish a project, it automatically plays a fullscreen celebration video with audio. Zero UI chrome, pure immersion.

## Demo

Say "项目完成了" (or any natural completion phrase in any language) → celebration stats panel drops in chat → your custom video pops up fullscreen with synced audio. No confirmation prompts.

## Installation

### 1. Prerequisites

```bash
pip install opencv-python pygame moviepy
```

> `moviepy` bundles `imageio-ffmpeg` (a static ffmpeg binary) — no system ffmpeg needed.

### 2. Install the Skill

Copy `SKILL.md` into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/terminal-mvp-animation
cp SKILL.md ~/.claude/skills/terminal-mvp-animation/
```

### 3. Install the Player + Video

```bash
mkdir -p ~/.pixelplay
cp pixelplay.py mvp_video.mp4 mvp_animate.py ~/.pixelplay/
```

### 4. Grant Permission (Optional but Recommended)

Add to `~/.claude/settings.json` so the video launches without prompting:

```json
{
  "permissions": {
    "allow": ["Bash(python *)"]
  }
}
```

## Usage

Just finish a project and say something like:

- "项目完成了"
- "Finally done!"
- "MVP moment"

The skill auto-detects a real milestone (not casual chat) and triggers the animation.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition — triggers, judgment logic, behavior |
| `pixelplay.py` | Fullscreen video player (OpenCV + ffmpeg audio + pygame mixer) |
| `mvp_video.mp4` | Bundled celebration video (replace with your own!) |
| `mvp_animate.py` | Fallback ASCII terminal animation (no video dependency) |

## Customizing the Video

Replace `mvp_video.mp4` with your own video. The player supports any format OpenCV can read (MP4, AVI, MOV, etc.). Keep it short (3-10 seconds recommended).

## Requirements

- Python 3.8+
- opencv-python
- pygame
- moviepy (for bundled ffmpeg)
- Windows / macOS / Linux
