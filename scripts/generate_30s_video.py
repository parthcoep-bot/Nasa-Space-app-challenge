#!/usr/bin/env python3
"""
Generate a 25-second animated presentation video with synchronized voiceover.
Muxes animated frames with voiceover_30s.wav using imageio-ffmpeg.
Produces:
- flarex_30s_presentation.mp4
- slide_assets/video_poster.png (high-res thumbnail for Slide 5)
"""

import cv2
import numpy as np
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG_EXE = r"C:\Users\Admin\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v9.0.2.exe"
AUDIO_WAV = "voiceover_30s.wav"
TEMP_VIDEO = "temp_silent.mp4"
FINAL_VIDEO = "flarex_30s_presentation.mp4"
POSTER_PNG = Path("slide_assets") / "video_poster.png"

WIDTH, HEIGHT = 1280, 720
FPS = 24
DURATION = 24.5
TOTAL_FRAMES = int(FPS * DURATION)

def create_frame(t):
    # Base background: Clean NASA Space Apps theme (Clean White / Royal Blue header)
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#FFFFFF')
    draw = ImageDraw.Draw(img)
    
    # Top Header Banner (Electric Royal Blue #0052FF)
    draw.rectangle([0, 0, WIDTH, 110], fill='#0052FF')
    # Neon Lime Accent line
    draw.rectangle([0, 105, WIDTH, 110], fill='#D4FF00')
    
    # Header text
    draw.text((40, 25), "FLARE-X: 30-SECOND MISSION DEMO", fill='#FFFFFF')
    draw.text((40, 65), "NASA Space Apps Challenge 2026 | Flame in Freefall", fill='#D4FF00')
    
    # Bottom Progress Bar
    prog_w = int((t / DURATION) * WIDTH)
    draw.rectangle([0, HEIGHT - 12, WIDTH, HEIGHT], fill='#E2E8F0')
    draw.rectangle([0, HEIGHT - 12, prog_w, HEIGHT], fill='#0052FF')
    
    # Scenes
    if t < 4.5:
        # Scene 1: Introduction
        draw.rectangle([60, 160, WIDTH-60, HEIGHT-60], fill='#F8FAFC', outline='#CBD5E1', width=2)
        draw.text((100, 200), "PROJECT INTRODUCTION", fill='#0052FF')
        draw.text((100, 260), "FLARE-X: Flame Learning, Analysis, Risk & Extinction Explorer", fill='#0F172A')
        draw.text((100, 320), "Challenge: Flame in Freefall — Microgravity Combustion Data", fill='#D97706')
        draw.text((100, 400), "• Team: FLARE-X Space Exploration Safety Group", fill='#334155')
        draw.text((100, 460), "• Core Data: NASA Physical Sciences Informatics (PSI) BASS-II", fill='#334155')
        draw.text((100, 520), "• Mission: Safeguard Artemis Moon Basecamp & Crewed Mars Transit", fill='#059669')

    elif t < 9.5:
        # Scene 2: The Core Physics
        draw.rectangle([60, 160, WIDTH-60, HEIGHT-60], fill='#F8FAFC', outline='#0052FF', width=2)
        draw.text((100, 190), "THE PHYSICS OF MICROGRAVITY COMBUSTION (Gr ∝ g)", fill='#0052FF')
        draw.text((100, 250), "Why Earth Fire Rules Fail in Space:", fill='#D97706')
        draw.text((100, 310), "1. Buoyancy Collapses: Grashof number drops 1,000,000× (u_b → 0)", fill='#0F172A')
        draw.text((100, 370), "2. Low-Speed Paradox: Flames survive in 0.4–8 cm/s ventilation below 1-g limits", fill='#0F172A')
        draw.text((100, 430), "3. Thickened Boundary Layer: Reduces solid heat feedback, driving extinction", fill='#0F172A')
        draw.text((100, 500), "Qualitative NASA findings now made frame-by-frame quantitative!", fill='#059669')

    elif t < 15.5:
        # Scene 3: The Dim Blue Flame Problem
        draw.rectangle([60, 160, WIDTH-60, HEIGHT-60], fill='#F8FAFC', outline='#DC2626', width=2)
        draw.text((100, 190), "THE FATAL BLIND SPOT OF CONVENTIONAL FIRE CV", fill='#DC2626')
        draw.text((100, 250), "Standard detectors filter on red/yellow pixels. Near extinction, flames turn BLUE!", fill='#0F172A')
        draw.text((100, 320), "✕ Off-The-Shelf AI: Mask is EMPTY (Misses the flame completely!)", fill='#DC2626')
        draw.text((100, 390), "✓ FLARE-X Solution: Radiance Proxy V = max(R,G,B) + Extreme-Value Noise Gate", fill='#059669')
        draw.text((100, 460), "✓ Sootiness Index: χ = (R-B)/(R+B) measures the yellow→blue transition", fill='#0284C7')
        draw.text((100, 530), "✓ Overlay Masking: Prevents a 22.4% accuracy degradation from telemetry display", fill='#0052FF')

    elif t < 20.5:
        # Scene 4: Verification & EPI
        draw.rectangle([60, 160, WIDTH-60, HEIGHT-60], fill='#F8FAFC', outline='#059669', width=2)
        draw.text((100, 190), "BUILT-IN FALSIFICATION & EXTINCTION PROXIMITY INDEX", fill='#059669')
        draw.text((100, 250), "• Change-Point Recall: 1.000 (100% of all commanded steps detected)", fill='#0052FF')
        draw.text((100, 310), "• Sub-frame Alignment: Mean temporal offset = 0.125 frames", fill='#0052FF')
        draw.text((100, 370), "• Mean IoU: 0.843 | Dice: 0.915 | Zero False Positives on empty frames", fill='#059669')
        draw.text((100, 440), "• Exact EPI Attribution: Elongation + Standoff + Blueness + Dimness + Contraction", fill='#D97706')
        draw.text((100, 510), "• Monotonic Response: Spearman ρ = -0.989 (p < 10⁻⁵)", fill='#059669')

    else:
        # Scene 5: Mission Horizons & Conclusion
        draw.rectangle([60, 160, WIDTH-60, HEIGHT-60], fill='#F8FAFC', outline='#0052FF', width=2)
        draw.text((100, 190), "GALACTIC IMPACT & TERRESTRIAL SPIN-OFFS", fill='#0052FF')
        draw.text((100, 260), "• Space Exploration: Lunar Gateway, Artemis Basecamp & Crewed Mars Transit", fill='#0F172A')
        draw.text((100, 330), "• Drop-in analytical harness for NASA SoFIE (Active ISS CIR Payload)", fill='#0284C7')
        draw.text((100, 400), "• Terrestrial Safety: Subway tunnels, mine shafts, and aircraft cargo compartments", fill='#D97706')
        draw.text((100, 480), "• Interactive Dashboard: https://parthcoep-bot.github.io/Nasa-Space-app-challenge/", fill='#0052FF')
        draw.text((100, 540), "NASA measured this. FLARE-X makes it measurable, auditable, and actionable.", fill='#059669')

    # Convert to OpenCV BGR
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def build_video():
    print(f"Rendering {TOTAL_FRAMES} frames...")
    writer = cv2.VideoWriter(TEMP_VIDEO, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
    
    for i in range(TOTAL_FRAMES):
        t = i / FPS
        frame = create_frame(t)
        writer.write(frame)
        if i % 60 == 0:
            print(f"  Rendered {i}/{TOTAL_FRAMES} frames ({t:.1f}s)")
            
    writer.release()
    print("Silent video written.")

    # Save a high-res poster frame at t=1.0s
    poster = create_frame(1.0)
    # Add a prominent play button circle
    cv2.circle(poster, (WIDTH//2, HEIGHT//2), 60, (0, 82, 255), -1)
    pts = np.array([[WIDTH//2 - 15, HEIGHT//2 - 25], [WIDTH//2 - 15, HEIGHT//2 + 25], [WIDTH//2 + 25, HEIGHT//2]], np.int32)
    cv2.fillPoly(poster, [pts], (212, 255, 0)) # Lime triangle
    cv2.imwrite(str(POSTER_PNG), poster)
    print(f"Saved poster: {POSTER_PNG}")

    # Mux with audio using imageio-ffmpeg
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", TEMP_VIDEO,
        "-i", AUDIO_WAV,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        FINAL_VIDEO
    ]
    print("Muxing audio and video with ffmpeg...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"SUCCESS: Generated {FINAL_VIDEO} (24.5s with audio and animation)")
    else:
        print("FFmpeg error:", res.stderr)

if __name__ == "__main__":
    build_video()

