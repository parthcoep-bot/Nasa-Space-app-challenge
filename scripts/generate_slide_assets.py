#!/usr/bin/env python3
"""
Generate high-resolution visual diagrams and assets for the FLARE-X presentation slides.
Uses matplotlib and PIL with a clean NASA Space Apps light theme:
- Clean white background (#FFFFFF)
- Electric Royal Blue (#0B47D9 / #0052FF)
- Neon Lime Accent (#D4FF00)
- Crisp dark typography (#0F172A)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT_DIR = Path("slide_assets")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Earth 1-g vs Space Microgravity Flame Comparison
def make_flame_compare():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3.2), dpi=200, facecolor='#FFFFFF')
    
    # Earth 1-g
    ax1.set_facecolor('#F8FAFC')
    y = np.linspace(0, 1.5, 200)
    # Teardrop flame contour
    x_right = 0.5 * (1 - y/1.5)**0.5 * np.sin(np.pi * y / 1.5)
    x_left = -x_right
    ax1.fill_betweenx(y, x_left, x_right, color='#FFAA00', alpha=0.9, label='Soot Glow (Yellow)')
    ax1.fill_betweenx(y*0.7, x_left*0.5, x_right*0.5, color='#FF5500', alpha=0.9)
    # Upward buoyant flow arrows
    for arr_x in [-0.35, 0.35]:
        ax1.annotate('', xy=(arr_x, 1.4), xytext=(arr_x, 0.2),
                     arrowprops=dict(arrowstyle="->", color='#0052FF', lw=2))
    ax1.text(0, -0.25, "Earth (1 g): Buoyancy ~30 cm/s\nNatural Updraft Feeds Flame", 
             ha='center', fontsize=9, fontweight='bold', color='#0F172A')
    ax1.set_xlim(-0.6, 0.6)
    ax1.set_ylim(-0.35, 1.6)
    ax1.axis('off')
    ax1.set_title("EARTH FLAME (1 g)", fontsize=11, fontweight='bold', color='#D97706')

    # Space Microgravity
    ax2.set_facecolor('#F8FAFC')
    # Spherical dim blue flame
    theta = np.linspace(0, 2*np.pi, 200)
    r = 0.55
    x_circ = r * np.cos(theta)
    y_circ = r * np.sin(theta) + 0.6
    ax2.fill(x_circ, y_circ, color='#38BDF8', alpha=0.4, label='Chemiluminescence')
    ax2.plot(x_circ, y_circ, color='#0284C7', lw=2.5)
    # Fuel rod
    ax2.fill_between([-0.6, 0.6], [0.1, 0.1], [0.25, 0.25], color='#475569')
    # Diffusive radial arrows
    for angle in [np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4]:
        dx, dy = 0.35 * np.cos(angle), 0.35 * np.sin(angle)
        ax2.annotate('', xy=(dx, 0.6+dy), xytext=(dx*0.3, 0.6+dy*0.3),
                     arrowprops=dict(arrowstyle="->", color='#D97706', lw=1.5))
    ax2.text(0, -0.25, "Space (μg): Gr drops 1,000,000×\nSpherical, Dim Blue, Boundary Layer Thickens", 
             ha='center', fontsize=9, fontweight='bold', color='#0F172A')
    ax2.set_xlim(-0.6, 0.6)
    ax2.set_ylim(-0.35, 1.6)
    ax2.axis('off')
    ax2.set_title("SPACE FLAME (μg)", fontsize=11, fontweight='bold', color='#0284C7')

    plt.tight_layout()
    out_file = OUT_DIR / "diagram_flame_compare.png"
    fig.savefig(out_file, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)
    print(f"Generated {out_file}")

# 2. Red-Channel Failure vs Radiance Proxy Success
def make_segmentation_compare():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 2.8), dpi=200, facecolor='#FFFFFF')
    
    # Standard Red Filter Failure
    ax1.set_facecolor('#0F172A')
    # Draw blank box with cross
    ax1.plot([-0.5, 0.5], [-0.5, 0.5], color='#EF4444', lw=3)
    ax1.plot([-0.5, 0.5], [0.5, -0.5], color='#EF4444', lw=3)
    ax1.set_xlim(-0.6, 0.6)
    ax1.set_ylim(-0.6, 0.6)
    ax1.axis('off')
    ax1.set_title("STANDARD RED-CHANNEL FILTER\nMask: EMPTY (0 px flame detected!)", 
                  fontsize=10, fontweight='bold', color='#DC2626')

    # FLARE-X Radiance Proxy Success
    ax2.set_facecolor('#0F172A')
    # Draw segmented dim blue flame contour
    theta = np.linspace(0, 2*np.pi, 100)
    rx, ry = 0.45 * np.cos(theta), 0.3 * np.sin(theta)
    ax2.fill(rx, ry, color='#38BDF8', alpha=0.6)
    ax2.plot(rx, ry, color='#38BDF8', lw=2.5)
    # Flow vector
    ax2.annotate('', xy=(-0.4, -0.45), xytext=(-0.1, -0.45),
                 arrowprops=dict(arrowstyle="->", color='#D4FF00', lw=2))
    ax2.text(0, -0.5, "FLOW AXIS ALIGNED", ha='center', fontsize=8, color='#D4FF00', fontweight='bold')
    ax2.set_xlim(-0.6, 0.6)
    ax2.set_ylim(-0.6, 0.6)
    ax2.axis('off')
    ax2.set_title("FLARE-X V = max(R,G,B) PROXY\nMask: DETECTED (Dim blue flame tracked!)", 
                  fontsize=10, fontweight='bold', color='#0284C7')

    plt.tight_layout()
    out_file = OUT_DIR / "diagram_segmentation.png"
    fig.savefig(out_file, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)
    print(f"Generated {out_file}")

# 3. Flow Staircase & Change-Point Flags
def make_staircase_plot():
    fig, ax = plt.subplots(figsize=(7, 2.6), dpi=200, facecolor='#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Commanded flow steps
    time = np.array([0, 50, 50, 110, 110, 170, 170, 230, 230, 290, 290, 335, 335, 360])
    flow = np.array([4.2, 4.2, 3.5, 3.5, 2.8, 2.8, 2.1, 2.1, 1.4, 1.4, 0.7, 0.7, 0.0, 0.0])
    ax.step(time, flow, where='post', color='#0052FF', lw=2.5, label='Commanded Flow (cm/s)')
    
    # Detected change points (red/amber dashed lines)
    cps = [50, 110, 170, 230, 290, 335]
    for cp in cps:
        ax.axvline(x=cp, color='#EF4444', linestyle='--', lw=1.5, alpha=0.8)
        ax.scatter([cp], [4.4], color='#EF4444', s=35, zorder=5)
    
    ax.set_ylabel("Flow (cm/s)", fontsize=9, fontweight='bold', color='#0F172A')
    ax.set_xlabel("Video Frame Index", fontsize=9, fontweight='bold', color='#0F172A')
    ax.set_title("FLARE-X CHANGE POINTS vs COMMANDED FLOW SCHEDULE (100% RECALL)", 
                 fontsize=10, fontweight='bold', color='#0052FF')
    ax.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1')
    ax.set_ylim(-0.2, 4.8)
    ax.set_xlim(0, 360)
    
    out_file = OUT_DIR / "diagram_staircase.png"
    fig.savefig(out_file, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)
    print(f"Generated {out_file}")

# 4. EPI Attribution Bars
def make_epi_bars():
    fig, ax = plt.subplots(figsize=(7, 2.6), dpi=200, facecolor='#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    terms = ['Area Shrink', 'Dimness', 'Blueness (-χ)', 'Standoff', 'Elongation']
    weights = [0.15, 0.15, 0.20, 0.25, 0.25]
    colors = ['#10B981', '#F59E0B', '#0284C7', '#0052FF', '#6366F1']
    
    bars = ax.barh(terms, weights, color=colors, height=0.55, edgecolor='#0F172A', lw=1)
    for bar, wt in zip(bars, weights):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                f"{int(wt*100)}%", va='center', fontsize=9, fontweight='bold', color='#0F172A')
        
    ax.set_xlim(0, 0.35)
    ax.set_xlabel("Linear Contribution Weight", fontsize=9, fontweight='bold', color='#0F172A')
    ax.set_title("EXTINCTION PROXIMITY INDEX (EPI) EXACT ATTRIBUTION", 
                 fontsize=10, fontweight='bold', color='#0052FF')
    ax.grid(True, axis='x', linestyle=':', alpha=0.6, color='#CBD5E1')
    
    out_file = OUT_DIR / "diagram_epi_bars.png"
    fig.savefig(out_file, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)
    print(f"Generated {out_file}")

if __name__ == "__main__":
    make_flame_compare()
    make_segmentation_compare()
    make_staircase_plot()
    make_epi_bars()

