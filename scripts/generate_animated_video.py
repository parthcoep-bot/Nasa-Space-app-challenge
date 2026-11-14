#!/usr/bin/env python3
"""
Generate a high-quality, motion-graphics style 24.5-second explainer video.
Features:
- Animated Earth vs Microgravity flames (pulsing convection, spherical chemiluminescent glow)
- Animated physics vectors (boundary layer thickening, Grashof number collapse)
- Side-by-side computer vision demonstration (Red channel failure vs Radiance proxy lock-on)
- Animated telemetry staircase and dynamic EPI attribution gauge
- Artemis Moon base, Mars transit, and Earth tunnel icons
- Muxed with voiceover_30s.wav using ffmpeg (H.264 Baseline, AAC) for native PowerPoint playback.
"""

import cv2
import numpy as np
import subprocess
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG_EXE = r"C:\Users\Admin\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v9.0.2.exe"
AUDIO_WAV = "voiceover_30s.wav"
TEMP_VIDEO = "temp_animated.mp4"
FINAL_VIDEO = "flarex_30s_presentation.mp4"
POSTER_PNG = Path("slide_assets") / "video_poster.png"

WIDTH, HEIGHT = 1280, 720
FPS = 30
DURATION = 24.5
TOTAL_FRAMES = int(FPS * DURATION)

# Try loading standard Windows system fonts, fallback to default
try:
    font_title = ImageFont.truetype("arialbd.ttf", 36)
    font_subtitle = ImageFont.truetype("arialbd.ttf", 24)
    font_header = ImageFont.truetype("arialbd.ttf", 26)
    font_body = ImageFont.truetype("arial.ttf", 20)
    font_body_bold = ImageFont.truetype("arialbd.ttf", 20)
    font_badge = ImageFont.truetype("arialbd.ttf", 16)
    font_mono = ImageFont.truetype("courbd.ttf", 22)
except Exception:
    font_title = font_subtitle = font_header = font_body = font_body_bold = font_badge = font_mono = ImageFont.load_default()

def draw_top_nav(draw, t, scene_title):
    # Top bar
    draw.rectangle([0, 0, WIDTH, 80], fill='#0052FF')
    draw.rectangle([0, 75, WIDTH, 80], fill='#D4FF00') # Lime stripe
    draw.text((30, 20), "FLARE-X: 30-SECOND MISSION DEMO", fill='#FFFFFF', font=font_subtitle)
    draw.text((WIDTH - 420, 26), f"SCENE: {scene_title.upper()}", fill='#D4FF00', font=font_badge)
    
    # Bottom progress timeline
    draw.rectangle([0, HEIGHT - 14, WIDTH, HEIGHT], fill='#1E293B')
    prog_w = int((t / DURATION) * WIDTH)
    draw.rectangle([0, HEIGHT - 14, prog_w, HEIGHT], fill='#00D2FF')

def render_scene_1(t):
    # 0.0s to 5.0s: The Fire in Freefall (Earth 1g vs Space ug)
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#070E20')
    draw = ImageDraw.Draw(img)
    draw_top_nav(draw, t, "1. The Fire in Freefall")

    # Center challenge badge
    draw.rectangle([WIDTH//2 - 280, 105, WIDTH//2 + 280, 145], fill='#0052FF', outline='#D4FF00', width=2)
    draw.text((WIDTH//2 - 250, 114), "NASA SPACE APPS CHALLENGE 2026", fill='#D4FF00', font=font_badge)

    # Left Container: Earth 1g
    draw.rectangle([80, 170, 580, 640], fill='#0F172A', outline='#FFAA00', width=2)
    draw.text((120, 195), "EARTH (1 g): BUOYANCY DRIVEN", fill='#FFAA00', font=font_header)
    draw.text((120, 235), "• Natural buoyant updraft: ~30 cm/s", fill='#E2E8F0', font=font_body)
    draw.text((120, 265), "• Soot continuum: Bright yellow incandescence", fill='#E2E8F0', font=font_body)
    draw.text((120, 295), "• Standard flammability tests assume 1 g", fill='#E2E8F0', font=font_body)

    # Animate Earth Flame
    pulse = math.sin(t * 8) * 6
    flame_cx, flame_base_y = 330, 560
    # Yellow outer
    flame_pts = [
        (flame_cx, flame_base_y - 180 + pulse),
        (flame_cx + 55 + pulse*0.5, flame_base_y - 70),
        (flame_cx + 40, flame_base_y),
        (flame_cx - 40, flame_base_y),
        (flame_cx - 55 - pulse*0.5, flame_base_y - 70)
    ]
    draw.polygon(flame_pts, fill='#FFAA00')
    # Orange inner
    inner_pts = [
        (flame_cx, flame_base_y - 130 + pulse*0.7),
        (flame_cx + 30, flame_base_y - 50),
        (flame_cx + 20, flame_base_y),
        (flame_cx - 20, flame_base_y),
        (flame_cx - 30, flame_base_y - 50)
    ]
    draw.polygon(inner_pts, fill='#FF4500')

    # Right Container: Microgravity Space Flame
    draw.rectangle([700, 170, 1200, 640], fill='#0F172A', outline='#00D2FF', width=2)
    draw.text((740, 195), "SPACE (μg): BUOYANCY REMOVED", fill='#00D2FF', font=font_header)
    draw.text((740, 235), "• Grashof Number drops 1,000,000× (u_b → 0)", fill='#E2E8F0', font=font_body)
    draw.text((740, 265), "• Flame is spherical, creeping, and DIM BLUE", fill='#E2E8F0', font=font_body)
    draw.text((740, 295), "• Flames linger at low speed below 1-g limits!", fill='#D4FF00', font=font_body_bold)

    # Animate Microgravity Flame (Expanding dim blue sphere around fuel rod)
    sp_cx, sp_cy = 950, 480
    r_sphere = 65 + math.sin(t * 5) * 4
    # Fuel rod
    draw.rectangle([sp_cx - 180, sp_cy - 12, sp_cx + 180, sp_cy + 12], fill='#64748B')
    draw.text((sp_cx - 80, sp_cy + 25), "PMMA FUEL ROD", fill='#94A3B8', font=font_badge)
    # Blue chemiluminescent glow circles
    draw.ellipse([sp_cx - r_sphere - 15, sp_cy - r_sphere - 15, sp_cx + r_sphere + 15, sp_cy + r_sphere + 15], 
                 outline='#0052FF', width=2)
    draw.ellipse([sp_cx - r_sphere, sp_cy - r_sphere, sp_cx + r_sphere, sp_cy + r_sphere], 
                 fill='#0284C7', outline='#38BDF8', width=3)
    
    return img

def render_scene_2(t):
    # 5.0s to 10.0s: The Physics & Low-Flow Paradox
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#070E20')
    draw = ImageDraw.Draw(img)
    draw_top_nav(draw, t, "2. The Zero-g Combustion Paradox")

    # Large Equation Header Card
    draw.rectangle([80, 110, 1200, 230], fill='#0F172A', outline='#0052FF', width=2)
    draw.text((110, 125), "THE GOVERNING FLUID DYNAMICS EQUATION:", fill='#D4FF00', font=font_header)
    draw.text((110, 165), "Grashof Number:  Gr = (g · β · ΔT · L³) / ν²   ∝  g", fill='#FFFFFF', font=font_title)

    # Visual Flow Diagram
    draw.rectangle([80, 260, 620, 640], fill='#0F172A', outline='#CBD5E1', width=1)
    draw.text((110, 285), "PHYSICAL MECHANISM IN SPACE", fill='#00D2FF', font=font_header)
    draw.text((110, 335), "1. Buoyant draft collapses from 30 cm/s to ZERO.", fill='#E2E8F0', font=font_body)
    draw.text((110, 385), "2. Low forced flow (0.4–8 cm/s) controls oxidizer.", fill='#E2E8F0', font=font_body)
    draw.text((110, 435), "3. Boundary layer thickens, flame stands off.", fill='#E2E8F0', font=font_body)
    draw.text((110, 485), "4. Heat feedback falls; surface re-radiation quenches.", fill='#E2E8F0', font=font_body)
    draw.text((110, 545), "⚠️ Terrestrial NASA-STD-6001 Test 1 tests upward", fill='#FFAA00', font=font_body_bold)
    draw.text((110, 575), "    in 1 g, misjudging low-velocity space danger!", fill='#FFAA00', font=font_body_bold)

    # Right Animation: Thickening Boundary Layer
    draw.rectangle([660, 260, 1200, 640], fill='#0F172A', outline='#00D2FF', width=2)
    draw.text((690, 285), "BOUNDARY LAYER LIFTOFF MODEL", fill='#00D2FF', font=font_header)
    
    # Rod
    rod_y = 500
    draw.rectangle([720, rod_y, 1140, rod_y + 20], fill='#64748B')
    draw.text((730, rod_y + 30), "SOLID FUEL SURFACE", fill='#94A3B8', font=font_badge)

    # Flow arrows
    flow_x = 730 + int((t * 80) % 200)
    draw.text((730, rod_y - 120), "FORCED OXIDIZER FLOW (0.4 – 8 cm/s)  →→→", fill='#00D2FF', font=font_body_bold)
    
    # Thickened boundary envelope (grows with time in scene)
    prog = (t - 5.0) / 5.0
    envelope_h = int(40 + prog * 60)
    draw.arc([750, rod_y - envelope_h * 2, 1100, rod_y], start=180, end=0, fill='#0284C7', width=3)
    # Flame sitting at standoff distance
    draw.ellipse([860, rod_y - envelope_h - 20, 980, rod_y - envelope_h + 15], fill='#38BDF8', outline='#00D2FF', width=2)
    draw.text((860, rod_y - envelope_h - 45), f"STANDOFF: {4.5 + prog*3.2:.1f} mm ↑", fill='#D4FF00', font=font_badge)

    return img

def render_scene_3(t):
    # 10.0s to 15.5s: The Dim Blue Flame Problem & CV Solution
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#070E20')
    draw = ImageDraw.Draw(img)
    draw_top_nav(draw, t, "3. Overcoming the Dim Blue Flame Failure")

    # Split Screen Comparison
    # Left: Commercial CV Failure
    draw.rectangle([80, 110, 620, 640], fill='#0F172A', outline='#DC2626', width=3)
    draw.rectangle([80, 110, 620, 160], fill='#DC2626')
    draw.text((100, 120), "OFF-THE-SHELF FIRE DETECTOR (RED FILTER)", fill='#FFFFFF', font=font_header)
    
    # Empty camera box
    draw.rectangle([130, 190, 570, 460], fill='#000000', outline='#EF4444', width=2)
    # Red crosshair scanning
    scan_y = 200 + int((t * 120) % 240)
    draw.line([140, scan_y, 560, scan_y], fill='#EF4444', width=2)
    draw.text((220, 310), "MASK: 0 PIXELS", fill='#EF4444', font=font_title)
    draw.text((180, 360), "NO FLAME DETECTED!", fill='#EF4444', font=font_header)

    draw.text((100, 480), "✕ Fatal Blindspot: Filters on red/yellow soot.", fill='#EF4444', font=font_body_bold)
    draw.text((100, 520), "✕ Near extinction, soot ceases; flame turns blue.", fill='#E2E8F0', font=font_body)
    draw.text((100, 560), "✕ Detector reports zero flame at critical moment!", fill='#EF4444', font=font_body_bold)

    # Right: FLARE-X Radiance Proxy
    draw.rectangle([660, 110, 1200, 640], fill='#0F172A', outline='#059669', width=3)
    draw.rectangle([660, 110, 1200, 160], fill='#059669')
    draw.text((680, 120), "FLARE-X RADIANCE PROXY: V = max(R,G,B)", fill='#FFFFFF', font=font_header)

    # Clean tracked camera box
    draw.rectangle([710, 190, 1150, 460], fill='#000000', outline='#00D2FF', width=2)
    # Dim blue flame detected
    draw.ellipse([860, 280, 1000, 370], fill='#0284C7', outline='#38BDF8', width=3)
    # Bounding contour tracking box
    draw.rectangle([840, 260, 1020, 390], outline='#D4FF00', width=2)
    draw.text((845, 235), "✓ FLAME DETECTED [2485 px]", fill='#D4FF00', font=font_badge)

    draw.text((680, 480), "✓ Extreme-Value Noise Gate: σ√(2 ln N) floor", fill='#00D2FF', font=font_body_bold)
    draw.text((680, 520), "✓ Decoupled Sootiness Index: χ = (R-B)/(R+B)", fill='#E2E8F0', font=font_body)
    draw.text((680, 560), "✓ Telemetry Masking: Recovers +22.4% accuracy", fill='#10B981', font=font_body_bold)

    return img

def render_scene_4(t):
    # 15.5s to 20.5s: Falsification Testing & Extinction Proximity Index
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#070E20')
    draw = ImageDraw.Draw(img)
    draw_top_nav(draw, t, "4. Telemetry Falsification & EPI Attribution")

    # Left: The Staircase Flow Graph
    draw.rectangle([80, 110, 620, 640], fill='#0F172A', outline='#0052FF', width=2)
    draw.text((100, 130), "COMMANDED FLOW STAIRCASE", fill='#00D2FF', font=font_header)
    draw.text((100, 165), "Scored against in-frame hot-wire anemometer overlay:", fill='#94A3B8', font=font_body)

    # Draw staircase
    gx0, gy0, gw, gh = 120, 220, 460, 240
    draw.rectangle([gx0, gy0, gx0+gw, gy0+gh], fill='#020617', outline='#334155', width=1)
    
    # 5 Flow steps
    steps = [(0, 4.2), (80, 3.5), (160, 2.8), (240, 2.1), (320, 1.4), (400, 0.7), (450, 0.0)]
    pts = []
    for i in range(len(steps)-1):
        x1 = gx0 + steps[i][0]
        y1 = gy0 + int((4.5 - steps[i][1]) / 4.5 * gh)
        x2 = gx0 + steps[i+1][0]
        y2 = gy0 + int((4.5 - steps[i+1][1]) / 4.5 * gh)
        pts.extend([(x1, y1), (x2, y1)])
        # Detected change point marker
        draw.line([x2, gy0, x2, gy0+gh], fill='#EF4444', width=2)
        draw.text((x2 - 12, gy0 + 10), "CP", fill='#EF4444', font=font_badge)
    pts.append((gx0 + 460, gy0 + gh))
    draw.line(pts, fill='#00D2FF', width=3)

    draw.text((100, 490), "• CHANGE-POINT RECALL: 1.000 (100%)", fill='#10B981', font=font_body_bold)
    draw.text((100, 530), "• MEAN TEMPORAL OFFSET: 0.125 FRAMES", fill='#10B981', font=font_body_bold)
    draw.text((100, 570), "• ZERO FALSE POSITIVES AFTER EXTINCTION", fill='#D4FF00', font=font_body_bold)

    # Right: Dynamic Extinction Proximity Index (EPI)
    draw.rectangle([660, 110, 1200, 640], fill='#0F172A', outline='#FFAA00', width=2)
    draw.text((690, 130), "EXTINCTION PROXIMITY INDEX (EPI)", fill='#FFAA00', font=font_header)
    draw.text((690, 165), "Exact linear attribution — 100% zero black-box:", fill='#94A3B8', font=font_body)

    # Dynamic animated bars
    prog = min(1.0, (t - 15.5) / 5.0)
    bar_y = 230
    terms_info = [
        ("Elongation", 0.25, '#00D2FF'),
        ("Standoff Distance", 0.25, '#38BDF8'),
        ("Blueness (-χ)", 0.20, '#D4FF00'),
        ("Dimness", 0.15, '#FFAA00'),
        ("Area Contraction", 0.15, '#10B981')
    ]
    for name, wt, col in terms_info:
        draw.text((700, bar_y), f"{name} ({int(wt*100)}%)", fill='#FFFFFF', font=font_body)
        bw = int(wt * 1200 * prog)
        draw.rectangle([700, bar_y + 30, 700 + bw, bar_y + 50], fill=col)
        bar_y += 65

    # Composite indicator gauge
    draw.rectangle([690, 560, 1170, 620], fill='#0052FF', outline='#D4FF00', width=2)
    epi_val = 0.11 + prog * 0.74
    draw.text((710, 575), f"COMPOSITE EPI: {epi_val:.3f}   |   MONOTONIC ρ = -0.989", fill='#FFFFFF', font=font_header)

    return img

def render_scene_5(t):
    # 20.5s to 24.5s: Mission Horizons & Conclusion
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#070E20')
    draw = ImageDraw.Draw(img)
    draw_top_nav(draw, t, "5. Galactic Impact & Mission Horizons")

    # 3 Glowing Impact Cards
    cw = 340
    # Card 1: Moon Artemis
    draw.rectangle([80, 120, 80 + cw, 550], fill='#0F172A', outline='#00D2FF', width=2)
    draw.text((105, 145), "LUNAR GATEWAY", fill='#00D2FF', font=font_header)
    draw.text((105, 180), "& ARTEMIS BASECAMP", fill='#00D2FF', font=font_header)
    draw.text((105, 230), "• Low-g boundary layer", fill='#E2E8F0', font=font_body)
    draw.text((105, 260), "  extinction margins.", fill='#E2E8F0', font=font_body)
    draw.text((105, 300), "• Modernizes NASA-STD-6001", fill='#E2E8F0', font=font_body)
    draw.text((105, 330), "  materials standards.", fill='#E2E8F0', font=font_body)
    draw.text((105, 370), "• Tested against BASS-II,", fill='#E2E8F0', font=font_body)
    draw.text((105, 400), "  ready for NASA SoFIE!", fill='#D4FF00', font=font_body_bold)

    # Card 2: Mars Transit
    draw.rectangle([470, 120, 470 + cw, 550], fill='#0F172A', outline='#FFAA00', width=2)
    draw.text((495, 145), "CREWED MARS", fill='#FFAA00', font=font_header)
    draw.text((495, 180), "TRANSIT HABITATS", fill='#FFAA00', font=font_header)
    draw.text((495, 230), "• Multi-year missions", fill='#E2E8F0', font=font_body)
    draw.text((495, 260), "  with zero resupply.", fill='#E2E8F0', font=font_body)
    draw.text((495, 300), "• Edge optical monitoring", fill='#E2E8F0', font=font_body)
    draw.text((495, 330), "  on low-SWaP flight chips.", fill='#E2E8F0', font=font_body)
    draw.text((495, 370), "• Pre-smoke early warning", fill='#E2E8F0', font=font_body)
    draw.text((495, 400), "  before alarms trigger!", fill='#D4FF00', font=font_body_bold)

    # Card 3: Earth Infrastructure
    draw.rectangle([860, 120, 860 + cw, 550], fill='#0F172A', outline='#10B981', width=2)
    draw.text((885, 145), "EARTH TUNNELS", fill='#10B981', font=font_header)
    draw.text((885, 180), "& MINING SHAFTS", fill='#10B981', font=font_header)
    draw.text((885, 230), "• Subways and mines with", fill='#E2E8F0', font=font_body)
    draw.text((885, 260), "  horizontal forced flow.", fill='#E2E8F0', font=font_body)
    draw.text((885, 300), "• Ceiling constraints", fill='#E2E8F0', font=font_body)
    draw.text((885, 330), "  mimic microgravity spread.", fill='#E2E8F0', font=font_body)
    draw.text((885, 370), "• Free open STEM simulator", fill='#E2E8F0', font=font_body)
    draw.text((885, 400), "  for global universities!", fill='#D4FF00', font=font_body_bold)

    # Bottom Callout: Explore Live
    draw.rectangle([80, 580, 1200, 640], fill='#0052FF', outline='#D4FF00', width=2)
    draw.text((120, 595), "EXPLORE LIVE: https://parthcoep-bot.github.io/Nasa-Space-app-challenge/", fill='#FFFFFF', font=font_header)

    return img

def create_video():
    print(f"Generating {TOTAL_FRAMES} motion graphic frames...")
    writer = cv2.VideoWriter(TEMP_VIDEO, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
    
    for i in range(TOTAL_FRAMES):
        t = i / FPS
        if t < 5.0:
            frame = render_scene_1(t)
        elif t < 10.0:
            frame = render_scene_2(t)
        elif t < 15.5:
            frame = render_scene_3(t)
        elif t < 20.5:
            frame = render_scene_4(t)
        else:
            frame = render_scene_5(t)
            
        # Convert PIL to OpenCV BGR
        cv_frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        writer.write(cv_frame)
        if i % 90 == 0:
            print(f"  Frame {i}/{TOTAL_FRAMES} rendered ({t:.1f}s)")
            
    writer.release()
    print("Temporary video rendered.")

    # Save high-res poster thumbnail
    poster = render_scene_1(2.5)
    poster_cv = cv2.cvtColor(np.array(poster), cv2.COLOR_RGB2BGR)
    # Draw play button
    cv2.circle(poster_cv, (WIDTH//2, HEIGHT//2 + 40), 65, (0, 82, 255), -1)
    pts = np.array([[WIDTH//2 - 15, HEIGHT//2 + 15], [WIDTH//2 - 15, HEIGHT//2 + 65], [WIDTH//2 + 25, HEIGHT//2 + 40]], np.int32)
    cv2.fillPoly(poster_cv, [pts], (212, 255, 0)) # Lime triangle
    cv2.imwrite(str(POSTER_PNG), poster_cv)
    print(f"Generated poster: {POSTER_PNG}")

    # Mux with audio using ffmpeg with standard high-compatibility H.264 profile
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", TEMP_VIDEO,
        "-i", AUDIO_WAV,
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-shortest",
        FINAL_VIDEO
    ]
    print("Muxing audio and video with ffmpeg...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"SUCCESS: Generated {FINAL_VIDEO} (high-quality animation with synchronized voiceover)")
    else:
        print("FFmpeg error:", res.stderr)

if __name__ == "__main__":
    create_video()
