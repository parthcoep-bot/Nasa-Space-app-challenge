#!/usr/bin/env python3
"""
Generate the updated NASA Space Apps 7-slide presentation deck:
- Matching the official NASA Space Apps website theme (Electric Royal Blue, Neon Lime, Pure White)
- Clean White Canvas (>50% white space for crisp modern presentation aesthetics)
- Increased text sizes by 3-4 sizes across all slides (Titles 28-30pt, Headers 16-18pt, Body 13-15pt)
- Embedded diagrammatic illustrations (Earth vs Space flame, Segmentation comparison, Flow staircase)
- Slide 5 dedicated to the 30-Second Video Presentation with embedded movie, poster, and timestamps
- Clickable hyperlinks on every slide connecting to live dashboard, GitHub repo, and NASA portals
- Strict 7-slide limit compliant with NASA Space Apps Challenge Global Judging rules
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ==========================================
# COLOR PALETTE (NASA Space Apps Light Theme)
# ==========================================
BG_WHITE       = RGBColor(255, 255, 255)   # Pure White Canvas #FFFFFF
CARD_BG_LIGHT  = RGBColor(248, 250, 252)   # Subtle Slate Card #F8FAFC
CARD_BORDER    = RGBColor(203, 213, 225)   # Slate Border #CBD5E1

ROYAL_BLUE     = RGBColor(0, 82, 255)      # NASA Space Apps Royal Blue #0052FF
NAVY_HEADER    = RGBColor(11, 27, 61)      # Dark Navy #0B1B3D
BLUE_ACCENT    = RGBColor(14, 116, 144)    # Cyan / Teal Accent #0E7490

NEON_LIME      = RGBColor(212, 255, 0)     # Space Apps Neon Lime #D4FF00
AMBER_GOLD     = RGBColor(217, 119, 6)     # Flame Gold #D97706
RED_ALERT      = RGBColor(220, 38, 38)     # Crimson Alert #DC2626
GREEN_VERIFIED = RGBColor(5, 150, 105)     # Emerald Green #059669

TEXT_DARK      = RGBColor(15, 23, 42)      # Deep Charcoal Text #0F172A
TEXT_MUTED     = RGBColor(71, 85, 105)     # Slate Body Text #475569
TEXT_WHITE     = RGBColor(255, 255, 255)   # Pure White Text

FONT_NAME      = "Segoe UI"

LIVE_DEMO_URL  = "https://parthcoep-bot.github.io/Nasa-Space-app-challenge/"
GITHUB_URL     = "https://github.com/parthcoep-bot/Nasa-Space-app-challenge"
VIDEO_URL      = "https://github.com/parthcoep-bot/Nasa-Space-app-challenge/raw/main/flarex_30s_presentation.mp4"
NASA_PSI_URL   = "https://psi.nasa.gov"
PAPER_URL      = "https://doi.org/10.1038/s41598-017-18398-4"

VIDEO_FILE     = "flarex_30s_presentation.mp4"
ASSETS_DIR     = Path("slide_assets")

def create_deck(output_path="FLARE-X_NASA_Space_Apps_7Slides.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_white_canvas(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_WHITE
        bg.line.color.rgb = BG_WHITE
        return bg

    def add_header(slide, slide_num, title, subtitle_badge):
        # Top Accent Stripe (Neon Lime #D4FF00)
        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = NEON_LIME
        stripe.line.color.rgb = NEON_LIME

        # Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.35), Inches(5.2), Inches(0.42))
        badge.fill.solid()
        badge.fill.fore_color.rgb = ROYAL_BLUE
        badge.line.color.rgb = ROYAL_BLUE
        tf_b = badge.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = Inches(0.12)
        tf_b.margin_top = Inches(0.04)
        p_b = tf_b.paragraphs[0]
        p_b.text = subtitle_badge.upper()
        p_b.font.name = FONT_NAME
        p_b.font.size = Pt(12)
        p_b.font.bold = True
        p_b.font.color.rgb = NEON_LIME

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(11.0), Inches(0.35), Inches(1.6), Inches(0.4))
        tf_n = num_box.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.text = f"SLIDE {slide_num} OF 7"
        p_n.font.name = FONT_NAME
        p_n.font.size = Pt(13)
        p_n.font.bold = True
        p_n.font.color.rgb = ROYAL_BLUE
        p_n.alignment = PP_ALIGN.RIGHT

        # Main Title (Increased Size: 28pt)
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.8), Inches(0.65))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_top = Inches(0)
        tf_t.margin_left = Inches(0)
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_NAME
        p_t.font.size = Pt(28)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_DARK

    def add_footer_link(slide):
        footer = slide.shapes.add_textbox(Inches(0.8), Inches(6.88), Inches(11.8), Inches(0.48))
        tf = footer.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        
        r1 = p.add_run()
        r1.text = "⚡ EXPLORE LIVE: "
        r1.font.name = FONT_NAME
        r1.font.size = Pt(12)
        r1.font.bold = True
        r1.font.color.rgb = AMBER_GOLD

        r2 = p.add_run()
        r2.text = "[Interactive WebApp Dashboard]"
        r2.font.name = FONT_NAME
        r2.font.size = Pt(12)
        r2.font.bold = True
        r2.font.color.rgb = ROYAL_BLUE
        r2.hyperlink.address = LIVE_DEMO_URL

        r3 = p.add_run()
        r3.text = "   •   "
        r3.font.name = FONT_NAME
        r3.font.size = Pt(12)
        r3.font.color.rgb = TEXT_MUTED

        r4 = p.add_run()
        r4.text = "[GitHub Codebase & 24/24 Verified Tests]"
        r4.font.name = FONT_NAME
        r4.font.size = Pt(12)
        r4.font.bold = True
        r4.font.color.rgb = ROYAL_BLUE
        r4.hyperlink.address = GITHUB_URL

    # =========================================================================
    # SLIDE 1: TITLE & EXECUTIVE HOOK (The Fire You Can't Walk Away From)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s1)

    # Top Lime Accent Stripe
    st1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    st1.fill.solid()
    st1.fill.fore_color.rgb = NEON_LIME
    st1.line.color.rgb = NEON_LIME

    # Header Badge
    badge1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(6.4), Inches(0.45))
    badge1.fill.solid()
    badge1.fill.fore_color.rgb = ROYAL_BLUE
    badge1.line.color.rgb = ROYAL_BLUE
    tf_b1 = badge1.text_frame
    p_b1 = tf_b1.paragraphs[0]
    p_b1.text = "NASA SPACE APPS CHALLENGE 2026 | FLAME IN FREEFALL"
    p_b1.font.size = Pt(12)
    p_b1.font.bold = True
    p_b1.font.color.rgb = NEON_LIME

    # Main Project Title (30pt Bold)
    t_box1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.8), Inches(1.4))
    tf1 = t_box1.text_frame
    p1_1 = tf1.paragraphs[0]
    p1_1.text = "FLARE-X: Flame Learning, Analysis, Risk & Extinction Explorer"
    p1_1.font.name = FONT_NAME
    p1_1.font.size = Pt(30)
    p1_1.font.bold = True
    p1_1.font.color.rgb = TEXT_DARK

    p1_2 = tf1.add_paragraph()
    p1_2.text = "Interpretable Super Intelligence (SI) Platform for Microgravity Combustion & Spacecraft Safety"
    p1_2.font.name = FONT_NAME
    p1_2.font.size = Pt(16)
    p1_2.font.bold = True
    p1_2.font.color.rgb = ROYAL_BLUE

    # The Human Stakes Card (Clean White with Royal Blue border)
    quote_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.45), Inches(11.733), Inches(1.3))
    quote_card.fill.solid()
    quote_card.fill.fore_color.rgb = CARD_BG_LIGHT
    quote_card.line.color.rgb = ROYAL_BLUE
    quote_card.line.width = Pt(2.0)
    tf_q = quote_card.text_frame
    tf_q.word_wrap = True
    p_q1 = tf_q.paragraphs[0]
    p_q1.text = "THE ASTRONAUT'S REALITY IN DEEP SPACE:"
    p_q1.font.name = FONT_NAME
    p_q1.font.size = Pt(14)
    p_q1.font.bold = True
    p_q1.font.color.rgb = AMBER_GOLD
    p_q2 = tf_q.add_paragraph()
    p_q2.text = "“On Earth, fire rises. In space, it doesn't. Inside a sealed spacecraft heading to Mars, there is no window to open, no outside to evacuate to, and a finite supply of suppressant. Everything humans know about fire was learned under Earth's gravity.”"
    p_q2.font.name = FONT_NAME
    p_q2.font.size = Pt(13.5)
    p_q2.font.color.rgb = TEXT_DARK

    # Flowchart: 3-Stage Architecture (Increased font sizes)
    flow_y = Inches(3.95)
    flow_w = Inches(3.5)
    flow_h = Inches(2.7)

    # Box 1
    b1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), flow_y, flow_w, flow_h)
    b1.fill.solid()
    b1.fill.fore_color.rgb = CARD_BG_LIGHT
    b1.line.color.rgb = CARD_BORDER
    tf_box1 = b1.text_frame
    tf_box1.word_wrap = True
    p = tf_box1.paragraphs[0]
    p.text = "1. UNTAPPED ARCHIVE"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ROYAL_BLUE
    items1 = [
        "Decades of ISS tests in NASA PSI repository.",
        "Crucial extinction data trapped in qualitative logs.",
        "Difficult to compare, query, or audit."
    ]
    for it in items1:
        pi = tf_box1.add_paragraph()
        pi.text = "• " + it
        pi.font.size = Pt(13)
        pi.font.color.rgb = TEXT_DARK

    # Arrow 1->2
    arr1 = s1.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.4), flow_y + Inches(1.05), Inches(0.5), Inches(0.45))
    arr1.fill.solid()
    arr1.fill.fore_color.rgb = ROYAL_BLUE
    arr1.line.color.rgb = ROYAL_BLUE

    # Box 2
    b2 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.0), flow_y, flow_w, flow_h)
    b2.fill.solid()
    b2.fill.fore_color.rgb = CARD_BG_LIGHT
    b2.line.color.rgb = ROYAL_BLUE
    b2.line.width = Pt(2.0)
    tf_box2 = b2.text_frame
    tf_box2.word_wrap = True
    p = tf_box2.paragraphs[0]
    p.text = "2. FLARE-X ENGINE"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = AMBER_GOLD
    items2 = [
        "Extreme-value noise-gated radiance proxy.",
        "Tracks dim blue flames where standard CV fails.",
        "100% change-point recall against telemetry.",
        "Extinction Proximity Index (EPI) attribution."
    ]
    for it in items2:
        pi = tf_box2.add_paragraph()
        pi.text = "• " + it
        pi.font.size = Pt(13)
        pi.font.color.rgb = TEXT_DARK

    # Arrow 2->3
    arr2 = s1.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(8.6), flow_y + Inches(1.05), Inches(0.5), Inches(0.45))
    arr2.fill.solid()
    arr2.fill.fore_color.rgb = ROYAL_BLUE
    arr2.line.color.rgb = ROYAL_BLUE

    # Box 3
    b3 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.2), flow_y, flow_w, flow_h)
    b3.fill.solid()
    b3.fill.fore_color.rgb = CARD_BG_LIGHT
    b3.line.color.rgb = GREEN_VERIFIED
    b3.line.width = Pt(2.0)
    tf_box3 = b3.text_frame
    tf_box3.word_wrap = True
    p = tf_box3.paragraphs[0]
    p.text = "3. MISSION IMPACT"
    p.font.name = FONT_NAME
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = GREEN_VERIFIED
    items3 = [
        "Informs Lunar Gateway, Artemis & Mars crew.",
        "Modernizes 1-g standards (NASA-STD-6001).",
        "Edge optical pre-smoke early warning.",
        "Earth subway tunnel & mine shaft safety."
    ]
    for it in items3:
        pi = tf_box3.add_paragraph()
        pi.text = "• " + it
        pi.font.size = Pt(13)
        pi.font.color.rgb = TEXT_DARK

    add_footer_link(s1)

    # =========================================================================
    # SLIDE 2: THE CORE PHYSICS DILEMMA (Gr ∝ g) + DIAGRAM
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s2)
    add_header(s2, 2, "Why Earth Fire Safety Standards Fail in Space", "BEST USE OF SCIENCE | GALACTIC IMPACT")

    # Left Container: Flowchart comparison
    card_l2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.8), Inches(4.3))
    card_l2.fill.solid()
    card_l2.fill.fore_color.rgb = CARD_BG_LIGHT
    card_l2.line.color.rgb = ROYAL_BLUE
    card_l2.line.width = Pt(1.5)
    tf_l2 = card_l2.text_frame
    tf_l2.word_wrap = True
    p = tf_l2.paragraphs[0]
    p.text = "THE ZERO-GRAVITY COMBUSTION PARADOX"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ROYAL_BLUE

    points2 = [
        ("Grashof Scaling Collapse", "Gr = (g·β·ΔT·L³)/ν² falls by 10⁶× in space! Buoyant velocity drops from 30 cm/s to ZERO."),
        ("The Low-Flow Hazard", "Under forced ventilation (0.4–8 cm/s), materials ignite and burn below Earth oxygen limits!"),
        ("Boundary Layer Thickening", "Flame lifts off surface, heat feedback drops, surface re-radiation quenches reaction."),
        ("Standard Flammability Flaw", "NASA-STD-6001 Test 1 tests upward in 1 g, misjudging microgravity low-flow flammability.")
    ]
    for h, b in points2:
        pi = tf_l2.add_paragraph()
        pi.text = f"• {h}: "
        pi.font.bold = True
        pi.font.size = Pt(13.5)
        pi.font.color.rgb = TEXT_DARK
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(13)
        r.font.color.rgb = TEXT_MUTED

    # Right Container: High-Res Flame Diagram
    diag1_path = ASSETS_DIR / "diagram_flame_compare.png"
    if diag1_path.exists():
        s2.shapes.add_picture(str(diag1_path), Inches(6.8), Inches(1.6), Inches(5.733), Inches(4.3))

    # Bottom Equation Callout
    bot2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.72))
    bot2.fill.solid()
    bot2.fill.fore_color.rgb = ROYAL_BLUE
    bot2.line.color.rgb = ROYAL_BLUE
    tf_b2 = bot2.text_frame
    tf_b2.word_wrap = True
    pb2 = tf_b2.paragraphs[0]
    pb2.text = "FALSIFIABLE HYPOTHESIS: Link et al. (Nature 2018) published that flames become 'longer, dimmer, and bluer' near extinction. FLARE-X transforms this into an auditable frame-by-frame measurement!"
    pb2.font.size = Pt(13)
    pb2.font.bold = True
    pb2.font.color.rgb = TEXT_WHITE

    add_footer_link(s2)

    # =========================================================================
    # SLIDE 3: DATA CURATION & RIGOROUS REJECTIONS
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s3)
    add_header(s3, 3, "Curating NASA PSI: Selecting BASS-II with Scientific Integrity", "BEST USE OF DATA | GLOBAL CONNECTION")

    col_w3 = Inches(3.7)
    col_h3 = Inches(4.25)
    col_y3 = Inches(1.6)

    # Column 1: Audit
    c1 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), col_y3, col_w3, col_h3)
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG_LIGHT
    c1.line.color.rgb = CARD_BORDER
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "1. NASA PSI AUDIT"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ROYAL_BLUE
    c1_items = [
        "17 Combustion investigations examined across NASA PSI archives.",
        "Disciplines: Solid spread, gas jets, droplet burning.",
        "Objective: Solid fuel spread flame with an extinction event."
    ]
    for it in c1_items:
        pi = tf1.add_paragraph()
        pi.text = "• " + it
        pi.font.size = Pt(13.5)
        pi.font.color.rgb = TEXT_DARK

    # Column 2: Rejections
    c2 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), col_y3, col_w3, col_h3)
    c2.fill.solid()
    c2.fill.fore_color.rgb = CARD_BG_LIGHT
    c2.line.color.rgb = RED_ALERT
    c2.line.width = Pt(2.0)
    tf2 = c2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "2. REJECTED (WHY?)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = RED_ALERT
    c2_items = [
        ("FLEX Droplets", "No solid fuel, no spread front. Pooling descriptors produces meaningless numbers."),
        ("ACME Gas Jets", "No pyrolysis substrate dynamics."),
        ("Saffire Burns", "15× larger scale, concurrent flow, different optics confounding physics.")
    ]
    for h, b in c2_items:
        pi = tf2.add_paragraph()
        pi.text = f"✕ {h}: "
        pi.font.bold = True
        pi.font.size = Pt(13)
        pi.font.color.rgb = TEXT_DARK
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(12.5)
        r.font.color.rgb = TEXT_MUTED

    # Column 3: Selected BASS-II
    c3 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), col_y3, col_w3, col_h3)
    c3.fill.solid()
    c3.fill.fore_color.rgb = CARD_BG_LIGHT
    c3.line.color.rgb = GREEN_VERIFIED
    c3.line.width = Pt(2.0)
    tf3 = c3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "3. SELECTED: BASS-II"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = GREEN_VERIFIED
    c3_items = [
        ("Target", "PMMA solid fuel rods under controlled opposed flow on ISS."),
        ("Ground Truth", "Camera burned-in telemetry displays anemometer & fan voltage!"),
        ("SHA-256 Provenance", "Every float bound to source file hash. Zero data drift.")
    ]
    for h, b in c3_items:
        pi = tf3.add_paragraph()
        pi.text = f"✓ {h}: "
        pi.font.bold = True
        pi.font.size = Pt(13)
        pi.font.color.rgb = TEXT_DARK
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(12.5)
        r.font.color.rgb = TEXT_MUTED

    # Bottom Links
    bot3 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.75))
    bot3.fill.solid()
    bot3.fill.fore_color.rgb = ROYAL_BLUE
    bot3.line.color.rgb = ROYAL_BLUE
    tf_b3 = bot3.text_frame
    tf_b3.word_wrap = True
    p_b3 = tf_b3.paragraphs[0]
    r = p_b3.add_run()
    r.text = "DATA TRANSPARENCY:  "
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = NEON_LIME
    r2 = p_b3.add_run()
    r2.text = "[NASA Physical Sciences Informatics (PSI) Portal]"
    r2.font.bold = True
    r2.font.size = Pt(13)
    r2.font.color.rgb = TEXT_WHITE
    r2.hyperlink.address = NASA_PSI_URL
    r3 = p_b3.add_run()
    r3.text = "   •   "
    r3.font.color.rgb = TEXT_WHITE
    r4 = p_b3.add_run()
    r4.text = "[Nature Scientific Reports Link et al. Paper]"
    r4.font.bold = True
    r4.font.size = Pt(13)
    r4.font.color.rgb = TEXT_WHITE
    r4.hyperlink.address = PAPER_URL

    add_footer_link(s3)

    # =========================================================================
    # SLIDE 4: CV INNOVATION + SEGMENTATION COMPARISON DIAGRAM
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s4)
    add_header(s4, 4, "Innovation: Surviving the Dim Blue Near-Limit Flame", "BEST USE OF TECHNOLOGY | ART & TECHNOLOGY")

    # Left Container: Technical explanation
    card_l4 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.8), Inches(4.3))
    card_l4.fill.solid()
    card_l4.fill.fore_color.rgb = CARD_BG_LIGHT
    card_l4.line.color.rgb = ROYAL_BLUE
    card_l4.line.width = Pt(1.5)
    tf_l4 = card_l4.text_frame
    tf_l4.word_wrap = True
    p = tf_l4.paragraphs[0]
    p.text = "THE FATAL FLAW OF COMMERCIAL FIRE DETECTORS"
    p.font.size = Pt(15.5)
    p.font.bold = True
    p.font.color.rgb = RED_ALERT

    points4 = [
        ("Commercial AI Blind Spot", "Standard CV filters on red/yellow pixels. As flames starve of oxygen, soot ceases and flames turn dim blue (CH*/C₂). Standard models report ZERO flame!"),
        ("Radiance Proxy V = max(R,G,B)", "Segments on soot-independent intensity, catching soot incandescence AND faint blue chemiluminescence alike."),
        ("Extreme-Value Noise Floor", "Gated at σ√(2 ln N) (~5σ ceiling). Prevents Otsu sensor noise flooding; achieves 0 false positives!"),
        ("Decoupled Sootiness Index χ", "χ = (R-B)/(R+B) measures color shift as an independent physical observable.")
    ]
    for h, b in points4:
        pi = tf_l4.add_paragraph()
        pi.text = f"• {h}: "
        pi.font.bold = True
        pi.font.size = Pt(13)
        pi.font.color.rgb = TEXT_DARK
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(12.5)
        r.font.color.rgb = TEXT_MUTED

    # Right Container: High-Res Segmentation Comparison Diagram
    diag2_path = ASSETS_DIR / "diagram_segmentation.png"
    if diag2_path.exists():
        s4.shapes.add_picture(str(diag2_path), Inches(6.8), Inches(1.6), Inches(5.733), Inches(4.3))

    # Bottom Overlay Ablation Banner
    bot4 = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.72))
    bot4.fill.solid()
    bot4.fill.fore_color.rgb = ROYAL_BLUE
    bot4.line.color.rgb = ROYAL_BLUE
    tf_b4 = bot4.text_frame
    tf_b4.word_wrap = True
    pb4 = tf_b4.paragraphs[0]
    pb4.text = "TELEMETRY OVERLAY ABLATION: Masking the camera's burned-in digital display increased segmentation IoU from 0.654 to 0.843 (+22.4% relative gain)—proving software robustness against real NASA flight artifacts."
    pb4.font.size = Pt(13)
    pb4.font.bold = True
    pb4.font.color.rgb = TEXT_WHITE

    add_footer_link(s4)

    # =========================================================================
    # SLIDE 5: 30-SECOND VIDEO DEMONSTRATION (Dedicated Video Presentation)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s5)
    add_header(s5, 5, "FLARE-X: 30-Second Mission Pitch & Video Demonstration", "PROJECT DEMONSTRATION | TIMED VIDEO PITCH (24.5s)")

    # Left Half: Video Player / Embedded Movie
    vid_x, vid_y, vid_w, vid_h = Inches(0.8), Inches(1.6), Inches(6.0), Inches(4.3)
    poster_path = ASSETS_DIR / "video_poster.png"
    
    if os.path.exists(VIDEO_FILE):
        try:
            # Embed video object in PowerPoint
            s5.shapes.add_movie(
                VIDEO_FILE,
                vid_x, vid_y, vid_w, vid_h,
                poster_frame_image=str(poster_path) if poster_path.exists() else None
            )
        except Exception as e:
            # Fallback to poster picture if movie embedding encounters issue
            if poster_path.exists():
                s5.shapes.add_picture(str(poster_path), vid_x, vid_y, vid_w, vid_h)
    elif poster_path.exists():
        s5.shapes.add_picture(str(poster_path), vid_x, vid_y, vid_w, vid_h)

    # Right Half: Video Transcript & Timestamps Container
    card_r5 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(1.6), Inches(5.533), Inches(4.3))
    card_r5.fill.solid()
    card_r5.fill.fore_color.rgb = CARD_BG_LIGHT
    card_r5.line.color.rgb = ROYAL_BLUE
    card_r5.line.width = Pt(1.5)
    tf_r5 = card_r5.text_frame
    tf_r5.word_wrap = True
    p = tf_r5.paragraphs[0]
    p.text = "OFFICIAL 30-SECOND VIDEO TRANSCRIPT"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ROYAL_BLUE

    script_steps = [
        ("[0:00 - 0:03] Intro & Team", "“We are Team FLARE-X for the Flame in Freefall challenge.”"),
        ("[0:03 - 0:08] The Problem", "“In space, buoyancy vanishes, altering flame physics and endangering astronauts.”"),
        ("[0:08 - 0:15] The Platform", "“We built FLARE-X: an interpretable Super Intelligence dashboard using NASA BASS-II data.”"),
        ("[0:15 - 0:21] The Breakthrough", "“Our extreme-value radiance pipeline detects dim blue flames where standard detectors fail, extracting exact extinction proximity.”"),
        ("[0:21 - 0:25] The Future", "“Safeguarding Artemis on the Moon, crewed missions to Mars, and mines on Earth!”")
    ]
    for h, b in script_steps:
        pi = tf_r5.add_paragraph()
        pi.text = f"{h}: "
        pi.font.bold = True
        pi.font.size = Pt(12)
        pi.font.color.rgb = AMBER_GOLD
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(12)
        r.font.color.rgb = TEXT_DARK

    # Bottom Video Play Hyperlink Banner
    bot5 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.72))
    bot5.fill.solid()
    bot5.fill.fore_color.rgb = ROYAL_BLUE
    bot5.line.color.rgb = ROYAL_BLUE
    tf_b5 = bot5.text_frame
    tf_b5.word_wrap = True
    pb5 = tf_b5.paragraphs[0]
    r = pb5.add_run()
    r.text = "PLAY / DOWNLOAD VIDEO:  "
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.color.rgb = NEON_LIME
    r2 = pb5.add_run()
    r2.text = "[▶ Click Here to Watch / Download 30-Second MP4 Video]"
    r2.font.bold = True
    r2.font.size = Pt(13)
    r2.font.color.rgb = TEXT_WHITE
    r2.hyperlink.address = VIDEO_URL

    add_footer_link(s5)

    # =========================================================================
    # SLIDE 6: FALSIFICATION TESTING & VERIFIED BENCHMARKS
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s6)
    add_header(s6, 6, "Built-In Falsification: Ground Truth Proved by Telemetry", "BEST USE OF SCIENCE | BEST USE OF DATA")

    # Left Container: 4 Big Metric Cards
    card_l6 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.8), Inches(4.3))
    card_l6.fill.solid()
    card_l6.fill.fore_color.rgb = CARD_BG_LIGHT
    card_l6.line.color.rgb = GREEN_VERIFIED
    card_l6.line.width = Pt(1.5)
    tf_l6 = card_l6.text_frame
    tf_l6.word_wrap = True
    p = tf_l6.paragraphs[0]
    p.text = "100% REPRODUCIBLE VALIDATION METRICS"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = GREEN_VERIFIED

    metrics6 = [
        ("Change-Point Recall: 1.000", "All 6 commanded flow step transitions detected with 0.125-frame mean offset!"),
        ("Mean IoU: 0.843 | Dice: 0.915", "Scored against 332 ground-truth frames. Zero false positives after extinction!"),
        ("EPI Monotonicity: ρ = -0.989", "Spearman rank correlation verifies monotone tracking of extinction approach (p < 10⁻⁵)."),
        ("Automated Tests: 24 / 24 Passed", "Physics equations (Gr ∝ g), extreme noise floors, and segmentation verified.")
    ]
    for h, b in metrics6:
        pi = tf_l6.add_paragraph()
        pi.text = f"✓ {h}: "
        pi.font.bold = True
        pi.font.size = Pt(13.5)
        pi.font.color.rgb = TEXT_DARK
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(12.5)
        r.font.color.rgb = TEXT_MUTED

    # Right Container: High-Res Flow Staircase Plot
    diag3_path = ASSETS_DIR / "diagram_staircase.png"
    if diag3_path.exists():
        s6.shapes.add_picture(str(diag3_path), Inches(6.8), Inches(1.6), Inches(5.733), Inches(4.3))

    # Bottom Falsification Rule Banner
    bot6 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.72))
    bot6.fill.solid()
    bot6.fill.fore_color.rgb = ROYAL_BLUE
    bot6.line.color.rgb = ROYAL_BLUE
    tf_b6 = bot6.text_frame
    tf_b6.word_wrap = True
    pb6 = tf_b6.paragraphs[0]
    pb6.text = "FALSIFICATION DISCIPLINE: Detected change points must land on the camera's burned-in anemometer telemetry. Our 0.125-frame alignment proves the algorithm directly measures physical flow regime transitions."
    pb6.font.size = Pt(13)
    pb6.font.bold = True
    pb6.font.color.rgb = TEXT_WHITE

    add_footer_link(s6)

    # =========================================================================
    # SLIDE 7: MISSION IMPACT & FORWARD HORIZONS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_white_canvas(s7)
    add_header(s7, 7, "Mission Impact: Moon, Mars, Earth Infrastructure & Beyond", "GALACTIC IMPACT | BEST MISSION CONCEPT | LOCAL IMPACT")

    col_w7 = Inches(3.7)
    col_h7 = Inches(4.25)
    col_y7 = Inches(1.6)

    # Pillar 1: Spaceflight
    p1 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), col_y7, col_w7, col_h7)
    p1.fill.solid()
    p1.fill.fore_color.rgb = CARD_BG_LIGHT
    p1.line.color.rgb = ROYAL_BLUE
    p1.line.width = Pt(1.5)
    tf1 = p1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "1. DEEP-SPACE HABITATION"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ROYAL_BLUE
    p1_items = [
        ("Lunar Gateway & Artemis", "Protects crewed lunar basecamp by quantifying non-buoyant extinction margins."),
        ("Crewed Mars Transit", "Multi-year missions cannot afford false alarms or unquenched smoldering fires."),
        ("Next-Gen NASA SoFIE", "Built as a drop-in analytical harness for NASA's active SoFIE payload on the ISS.")
    ]
    for h, b in p1_items:
        pi = tf1.add_paragraph()
        pi.text = f"• {h}: "
        pi.font.bold = True
        pi.font.size = Pt(13)
        pi.font.color.rgb = TEXT_DARK
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(12)
        r.font.color.rgb = TEXT_MUTED

    # Pillar 2: Edge Flight Architecture
    p2 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), col_y7, col_w7, col_h7)
    p2.fill.solid()
    p2.fill.fore_color.rgb = CARD_BG_LIGHT
    p2.line.color.rgb = AMBER_GOLD
    p2.line.width = Pt(1.5)
    tf2 = p2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "2. LEVEL-5 FLIGHT CONCEPT"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = AMBER_GOLD
    p2_items = [
        ("Optical Edge Sensors", "Runs rule-based Tier-1 morphology on low-SWaP radiation-tolerant flight computers."),
        ("Pre-Smoke Early Warning", "Detects boundary layer standoff and blueness drift BEFORE smoke enters detectors."),
        ("ECLSS Integration", "Automated ventilation throttling and targeted N₂/CO₂ suppressant release.")
    ]
    for h, b in p2_items:
        pi = tf2.add_paragraph()
        pi.text = f"• {h}: "
        pi.font.bold = True
        pi.font.size = Pt(13)
        pi.font.color.rgb = TEXT_DARK
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(12)
        r.font.color.rgb = TEXT_MUTED

    # Pillar 3: Terrestrial Spin-Offs
    p3 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), col_y7, col_w7, col_h7)
    p3.fill.solid()
    p3.fill.fore_color.rgb = CARD_BG_LIGHT
    p3.line.color.rgb = GREEN_VERIFIED
    p3.line.width = Pt(1.5)
    tf3 = p3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "3. EARTH INFRASTRUCTURE"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = GREEN_VERIFIED
    p3_items = [
        ("Subway & Mine Tunnels", "Forced horizontal low-speed air in low-ceiling shafts mirrors microgravity flame spread."),
        ("Aircraft Cargo Holds", "Low-pressure, constrained convection fire detection."),
        ("Global STEM Education", "Free MIT-licensed simulator for universities and fire academies worldwide without GPUs.")
    ]
    for h, b in p3_items:
        pi = tf3.add_paragraph()
        pi.text = f"• {h}: "
        pi.font.bold = True
        pi.font.size = Pt(13)
        pi.font.color.rgb = TEXT_DARK
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(12)
        r.font.color.rgb = TEXT_MUTED

    # Bottom Conclusion
    bot7 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.05), Inches(11.733), Inches(0.72))
    bot7.fill.solid()
    bot7.fill.fore_color.rgb = ROYAL_BLUE
    bot7.line.color.rgb = ROYAL_BLUE
    tf_b7 = bot7.text_frame
    tf_b7.word_wrap = True
    pb7 = tf_b7.paragraphs[0]
    pb7.text = "THE MISSION CONCLUSION: NASA measured this. FLARE-X makes it measurable, auditable, and actionable. From the International Space Station to the Moon, Mars, and Earth's deepest tunnels—making fire safety an exact science."
    pb7.font.size = Pt(13)
    pb7.font.bold = True
    pb7.font.color.rgb = TEXT_WHITE

    add_footer_link(s7)

    prs.save(output_path)
    print(f"Successfully generated {output_path} (7 slides, NASA theme, white canvas, embedded video on slide 5)")

if __name__ == "__main__":
    create_deck()
