#!/usr/bin/env python3
"""
Generate a professional, hackathon-ready 7-slide presentation in 16:9 widescreen PPTX.
Designed with:
- Dark space theme matching NASA Space Apps (Deep Navy, Electric Blue/Cyan, Flame Amber, Pure White)
- Heavy emphasis on structured flowcharts, process blocks, comparison cards, and diagrams over dense text
- High-readability typography (22-26pt bold titles, 14-16pt card headers, 11-12pt clear bullet points)
- Clickable hyperlinks on every slide connecting to live dashboard, GitHub repo, and NASA datasets
- Strict 7-slide limit compliant with NASA Space Apps Challenge Global Judging rules
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ==========================================
# COLOR PALETTE (NASA Space Apps Dark Theme)
# ==========================================
BG_COLOR       = RGBColor(11, 17, 32)      # Deep Space Navy #0B1120
CARD_BG        = RGBColor(19, 29, 52)      # Slate Card Container #131D34
CARD_BORDER    = RGBColor(35, 51, 84)      # Card Border #233354

CYAN_ACCENT    = RGBColor(0, 210, 255)     # NASA Electric Cyan #00D2FF
BLUE_PRIMARY   = RGBColor(30, 144, 255)    # Dodger/Electric Blue #1E90FF
BLUE_BOX_BG    = RGBColor(13, 50, 104)     # Flow Node Blue #0D3268

AMBER_ACCENT   = RGBColor(255, 170, 0)     # Flame Gold/Amber #FFAA00
ORANGE_FLAME   = RGBColor(255, 107, 53)    # Flame Orange #FF6B35
AMBER_BOX_BG   = RGBColor(74, 46, 5)       # Flow Node Amber #4A2E05

GREEN_OK       = RGBColor(16, 185, 129)    # Emerald Green #10B981
GREEN_BOX_BG   = RGBColor(8, 56, 36)       # Flow Node Green #083824

RED_FAIL       = RGBColor(239, 68, 68)     # Crimson Red #EF4444
RED_BOX_BG     = RGBColor(69, 18, 20)      # Flow Node Red #451214

TEXT_WHITE     = RGBColor(255, 255, 255)   # Pure White
TEXT_LIGHT     = RGBColor(226, 232, 240)   # Light Slate Text #E2E8F0
TEXT_MUTED     = RGBColor(148, 163, 184)   # Slate Muted Text #94A3B8

FONT_HEADING   = "Segoe UI"
FONT_BODY      = "Segoe UI"

LIVE_DEMO_URL  = "https://parthcoep-bot.github.io/Nasa-Space-app-challenge/"
GITHUB_URL     = "https://github.com/parthcoep-bot/Nasa-Space-app-challenge"
SLIDE_DOC_URL  = "https://github.com/parthcoep-bot/Nasa-Space-app-challenge/blob/main/docs/SLIDE_DECK.md"
NASA_PSI_URL   = "https://psi.nasa.gov"
PAPER_URL      = "https://doi.org/10.1038/s41598-017-18398-4"

def create_deck(output_path="FLARE-X_NASA_Space_Apps_7Slides.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.color.rgb = BG_COLOR
        return bg

    def add_header(slide, slide_num, title, subtitle_badge):
        # Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(4.5), Inches(0.35))
        badge.fill.solid()
        badge.fill.fore_color.rgb = BLUE_BOX_BG
        badge.line.color.rgb = CYAN_ACCENT
        tf_b = badge.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = Inches(0.1)
        tf_b.margin_right = Inches(0.1)
        tf_b.margin_top = Inches(0.04)
        tf_b.margin_bottom = Inches(0.04)
        p_b = tf_b.paragraphs[0]
        p_b.text = subtitle_badge.upper()
        p_b.font.name = FONT_HEADING
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = CYAN_ACCENT

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(11.2), Inches(0.35), Inches(1.4), Inches(0.4))
        tf_n = num_box.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.text = f"SLIDE {slide_num} OF 7"
        p_n.font.name = FONT_HEADING
        p_n.font.size = Pt(11)
        p_n.font.bold = True
        p_n.font.color.rgb = TEXT_MUTED
        p_n.alignment = PP_ALIGN.RIGHT

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.8), Inches(0.65))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_top = Inches(0)
        tf_t.margin_bottom = Inches(0)
        tf_t.margin_left = Inches(0)
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

    def add_footer_link(slide):
        # Bottom hyperlink banner
        footer = slide.shapes.add_textbox(Inches(0.8), Inches(6.9), Inches(11.8), Inches(0.45))
        tf = footer.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        
        r1 = p.add_run()
        r1.text = "⚡ Explore Online: "
        r1.font.name = FONT_BODY
        r1.font.size = Pt(10)
        r1.font.bold = True
        r1.font.color.rgb = AMBER_ACCENT

        r2 = p.add_run()
        r2.text = "[Live Interactive Dashboard (Single-File WebApp)]"
        r2.font.name = FONT_BODY
        r2.font.size = Pt(10)
        r2.font.bold = True
        r2.font.color.rgb = CYAN_ACCENT
        r2.hyperlink.address = LIVE_DEMO_URL

        r3 = p.add_run()
        r3.text = "  |  "
        r3.font.name = FONT_BODY
        r3.font.size = Pt(10)
        r3.font.color.rgb = TEXT_MUTED

        r4 = p.add_run()
        r4.text = "[GitHub Open Codebase & 24/24 Verified Tests]"
        r4.font.name = FONT_BODY
        r4.font.size = Pt(10)
        r4.font.bold = True
        r4.font.color.rgb = BLUE_PRIMARY
        r4.hyperlink.address = GITHUB_URL

    # =========================================================================
    # SLIDE 1: TITLE & EXECUTIVE HOOK (The Fire You Can't Walk Away From)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Top Tagline Badge
    badge1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.55), Inches(5.8), Inches(0.4))
    badge1.fill.solid()
    badge1.fill.fore_color.rgb = BLUE_BOX_BG
    badge1.line.color.rgb = CYAN_ACCENT
    tf_b1 = badge1.text_frame
    p_b1 = tf_b1.paragraphs[0]
    p_b1.text = "NASA SPACE APPS CHALLENGE 2026 | FLAME IN FREEFALL"
    p_b1.font.size = Pt(11)
    p_b1.font.bold = True
    p_b1.font.color.rgb = CYAN_ACCENT

    # Main Project Title
    t_box1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.05), Inches(11.8), Inches(1.3))
    tf1 = t_box1.text_frame
    p1_1 = tf1.paragraphs[0]
    p1_1.text = "FLARE-X: Flame Learning, Analysis, Risk & Extinction Explorer"
    p1_1.font.name = FONT_HEADING
    p1_1.font.size = Pt(26)
    p1_1.font.bold = True
    p1_1.font.color.rgb = TEXT_WHITE

    p1_2 = tf1.add_paragraph()
    p1_2.text = "Interpretable Super Intelligence (SI) Dashboard for Microgravity Combustion & Spacecraft Fire Safety"
    p1_2.font.name = FONT_HEADING
    p1_2.font.size = Pt(14)
    p1_2.font.color.rgb = AMBER_ACCENT

    # The Human Stakes Callout Card
    quote_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.45), Inches(11.733), Inches(1.2))
    quote_card.fill.solid()
    quote_card.fill.fore_color.rgb = CARD_BG
    quote_card.line.color.rgb = ORANGE_FLAME
    quote_card.line.width = Pt(1.5)
    tf_q = quote_card.text_frame
    tf_q.word_wrap = True
    p_q1 = tf_q.paragraphs[0]
    p_q1.text = "THE ASTRONAUT'S REALITY IN DEEP SPACE:"
    p_q1.font.name = FONT_HEADING
    p_q1.font.size = Pt(12)
    p_q1.font.bold = True
    p_q1.font.color.rgb = ORANGE_FLAME
    p_q2 = tf_q.add_paragraph()
    p_q2.text = "“On Earth, fire rises. In space, it doesn't. Inside a sealed spacecraft heading to Mars, there is no window to open, no outside to evacuate to, and a finite supply of suppressant. Everything humans know about fire was learned under Earth's gravity.”"
    p_q2.font.name = FONT_BODY
    p_q2.font.size = Pt(12)
    p_q2.font.color.rgb = TEXT_LIGHT

    # Flowchart: 3-Stage High-Level Architecture Flow
    flow_y = Inches(3.9)
    flow_w = Inches(3.45)
    flow_h = Inches(2.6)

    # Box 1: Problem / Raw Data
    b1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), flow_y, flow_w, flow_h)
    b1.fill.solid()
    b1.fill.fore_color.rgb = CARD_BG
    b1.line.color.rgb = CARD_BORDER
    tf_box1 = b1.text_frame
    tf_box1.word_wrap = True
    p = tf_box1.paragraphs[0]
    p.text = "1. THE UNTAPPED ARCHIVE"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT
    items1 = [
        "Decades of ISS combustion experiments (NASA PSI).",
        "Video records trapped in qualitative scientific papers.",
        "Crucial extinction limits hard to find & compare."
    ]
    for it in items1:
        pi = tf_box1.add_paragraph()
        pi.text = "• " + it
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = TEXT_LIGHT

    # Arrow 1->2
    arr1 = s1.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.35), flow_y + Inches(1.0), Inches(0.55), Inches(0.4))
    arr1.fill.solid()
    arr1.fill.fore_color.rgb = BLUE_PRIMARY
    arr1.line.color.rgb = CYAN_ACCENT

    # Box 2: FLARE-X Innovation
    b2 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.0), flow_y, flow_w, flow_h)
    b2.fill.solid()
    b2.fill.fore_color.rgb = CARD_BG
    b2.line.color.rgb = CYAN_ACCENT
    b2.line.width = Pt(1.5)
    tf_box2 = b2.text_frame
    tf_box2.word_wrap = True
    p = tf_box2.paragraphs[0]
    p.text = "2. FLARE-X MEASUREMENT"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT
    items2 = [
        "Extreme-value noise-gated radiance proxy.",
        "Tracks dim blue flames where standard CV fails.",
        "Multivariate change-point detection with 100% recall.",
        "Extinction Proximity Index (EPI) with exact attribution."
    ]
    for it in items2:
        pi = tf_box2.add_paragraph()
        pi.text = "• " + it
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = TEXT_LIGHT

    # Arrow 2->3
    arr2 = s1.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(8.55), flow_y + Inches(1.0), Inches(0.55), Inches(0.4))
    arr2.fill.solid()
    arr2.fill.fore_color.rgb = BLUE_PRIMARY
    arr2.line.color.rgb = CYAN_ACCENT

    # Box 3: Mission Impact
    b3 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.2), flow_y, flow_w, flow_h)
    b3.fill.solid()
    b3.fill.fore_color.rgb = CARD_BG
    b3.line.color.rgb = GREEN_OK
    b3.line.width = Pt(1.5)
    tf_box3 = b3.text_frame
    tf_box3.word_wrap = True
    p = tf_box3.paragraphs[0]
    p.text = "3. EXPLORATION IMPACT"
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN_OK
    items3 = [
        "Informs Lunar Gateway, Artemis Basecamp & Mars.",
        "Upgrades 1-g flammability rules (NASA-STD-6001).",
        "Edge optical early warning before smoke alarms trigger.",
        "Protects Earth mines & subway ventilation tunnels."
    ]
    for it in items3:
        pi = tf_box3.add_paragraph()
        pi.text = "• " + it
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = TEXT_LIGHT

    add_footer_link(s1)

    # =========================================================================
    # SLIDE 2: THE CORE PHYSICS DILEMMA (Gr ∝ g)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, 2, "Why Earth Fire Safety Standards Fail in Space", "BEST USE OF SCIENCE | GALACTIC IMPACT")

    # Flowchart: Earth (1g) vs Space (Microgravity) Flowchart Comparison
    card_w = Inches(5.6)
    card_h = Inches(4.2)
    cy = Inches(1.6)

    # Left Card: Earth 1-g
    c_left = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cy, card_w, card_h)
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = CARD_BG
    c_left.line.color.rgb = CARD_BORDER
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    pl = tf_l.paragraphs[0]
    pl.text = "EARTH GRAVITY (1 g): BUOYANCY DOMINATED"
    pl.font.name = FONT_HEADING
    pl.font.size = Pt(13.5)
    pl.font.bold = True
    pl.font.color.rgb = AMBER_ACCENT

    l_items = [
        ("Grashof Number Scaling", "Gr = (g·β·ΔT·L³) / ν²  [High body force]"),
        ("Natural Buoyancy", "Hot air rises at ~30 cm/s, drawing in fresh oxygen."),
        ("Flame Morphology", "Classic tall teardrop shape; soot glows bright yellow."),
        ("Extinction Limit", "Quenches when heat loss exceeds buoyant fuel generation."),
        ("Standard Flammability", "NASA-STD-6001 Test 1 tests upward spread in 1 g.")
    ]
    for h, b in l_items:
        p_h = tf_l.add_paragraph()
        p_h.text = f"• {h}: "
        p_h.font.bold = True
        p_h.font.size = Pt(11)
        p_h.font.color.rgb = TEXT_WHITE
        r = p_h.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(10.5)
        r.font.color.rgb = TEXT_LIGHT

    # Right Card: Microgravity
    c_right = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), cy, card_w, card_h)
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = CARD_BG
    c_right.line.color.rgb = CYAN_ACCENT
    c_right.line.width = Pt(1.5)
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    pr = tf_r.paragraphs[0]
    pr.text = "MICROGRAVITY (10⁻⁶ g): DIFFUSION & DRIFT"
    pr.font.name = FONT_HEADING
    pr.font.size = Pt(13.5)
    pr.font.bold = True
    pr.font.color.rgb = CYAN_ACCENT

    r_items = [
        ("Grashof Number Collapse", "Gr falls by 1,000,000×; buoyant velocity drops to 0."),
        ("Forced Ventilation Only", "Cabin air circulation (0.4–8 cm/s) controls oxygen."),
        ("The Low-Flow Paradox", "Flames survive at oxygen levels BELOW Earth limits!"),
        ("Near-Limit Appearance", "Soot vanishes; flame becomes dim, blue, spherical."),
        ("The Critical Safety Gap", "1-g certification misjudges microgravity fire risk!")
    ]
    for h, b in r_items:
        p_h = tf_r.add_paragraph()
        p_h.text = f"• {h}: "
        p_h.font.bold = True
        p_h.font.size = Pt(11)
        p_h.font.color.rgb = TEXT_WHITE
        r = p_h.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(10.5)
        r.font.color.rgb = TEXT_LIGHT

    # Bottom Equation Callout Box
    eq_box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.75))
    eq_box.fill.solid()
    eq_box.fill.fore_color.rgb = BLUE_BOX_BG
    eq_box.line.color.rgb = CYAN_ACCENT
    tf_eq = eq_box.text_frame
    tf_eq.word_wrap = True
    pe = tf_eq.paragraphs[0]
    pe.text = "SCIENTIFIC HYPOTHESIS: Link et al. (Nature 2018) published that flames become 'longer, dimmer, and bluer' near extinction. FLARE-X transforms this qualitative observation into an auditable, frame-by-frame quantitative measurement."
    pe.font.size = Pt(11)
    pe.font.color.rgb = TEXT_WHITE
    pe.font.bold = True

    add_footer_link(s2)

    # =========================================================================
    # SLIDE 3: DATA CURATION & RIGOROUS REJECTIONS
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, 3, "Curating NASA PSI: Selecting BASS-II with Scientific Integrity", "BEST USE OF DATA | GLOBAL CONNECTION")

    # Flowchart Container: 4 Step Process Tree
    pw = Inches(2.7)
    ph = Inches(4.0)
    py = Inches(1.6)

    # Step 1: NASA PSI Review
    p1 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), py, pw, ph)
    p1.fill.solid()
    p1.fill.fore_color.rgb = CARD_BG
    p1.line.color.rgb = CARD_BORDER
    tf = p1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "NASA PSI AUDIT"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT
    t_items = [
        "17 Combustion investigations examined in NASA PSI.",
        "Disciplines: Solid spread, gaseous jets, droplet burning.",
        "Goal: Falsifiable solid material extinction physics."
    ]
    for it in t_items:
        pi = tf.add_paragraph()
        pi.text = "• " + it
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = TEXT_LIGHT

    # Step 2: Principled Rejections
    p2 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.8), py, pw, ph)
    p2.fill.solid()
    p2.fill.fore_color.rgb = CARD_BG
    p2.line.color.rgb = RED_FAIL
    p2.line.width = Pt(1.5)
    tf = p2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "REJECTED (WHY?)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RED_FAIL
    rej_items = [
        ("FLEX Droplets", "No solid fuel, no spread front. Incommensurate."),
        ("ACME Gas Jets", "No pyrolysis substrate dynamics."),
        ("Saffire Burns", "15× larger scale, concurrent flow, different optics.")
    ]
    for r_title, r_desc in rej_items:
        pi = tf.add_paragraph()
        pi.text = f"✕ {r_title}: "
        pi.font.size = Pt(10.5)
        pi.font.bold = True
        pi.font.color.rgb = TEXT_WHITE
        r = pi.add_run()
        r.text = r_desc
        r.font.bold = False
        r.font.color.rgb = TEXT_LIGHT

    # Step 3: Selected BASS-II
    p3 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), py, pw, ph)
    p3.fill.solid()
    p3.fill.fore_color.rgb = CARD_BG
    p3.line.color.rgb = GREEN_OK
    p3.line.width = Pt(1.5)
    tf = p3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "SELECTED: BASS-II"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN_OK
    sel_items = [
        ("Fuel Type", "PMMA rods in Microgravity Science Glovebox (ISS)."),
        ("Staircase Flow", "Opposed flow stepped down until extinction."),
        ("Built-In Reference", "Camera burned-in telemetry displays anemometer & fan voltage!")
    ]
    for s_title, s_desc in sel_items:
        pi = tf.add_paragraph()
        pi.text = f"✓ {s_title}: "
        pi.font.size = Pt(10.5)
        pi.font.bold = True
        pi.font.color.rgb = TEXT_WHITE
        r = pi.add_run()
        r.text = s_desc
        r.font.bold = False
        r.font.color.rgb = TEXT_LIGHT

    # Step 4: Provenance Chain
    p4 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.8), py, pw, ph)
    p4.fill.solid()
    p4.fill.fore_color.rgb = CARD_BG
    p4.line.color.rgb = AMBER_ACCENT
    p4.line.width = Pt(1.5)
    tf = p4.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "PROVENANCE CHAIN"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT
    chain_items = [
        "Cryptographic SHA-256 hash attached to source file.",
        "Zero data drift: numbers bound to frame byte hashes.",
        "Transparent claim levels: L1 NASA Fact to L5 Concept.",
        "Uncalibrated values labelled NOT_VERIFIED, never faked."
    ]
    for it in chain_items:
        pi = tf.add_paragraph()
        pi.text = "• " + it
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = TEXT_LIGHT

    # Bottom Links Box
    b_link_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.9), Inches(11.733), Inches(0.8))
    b_link_box.fill.solid()
    b_link_box.fill.fore_color.rgb = BLUE_BOX_BG
    b_link_box.line.color.rgb = CYAN_ACCENT
    tf_bl = b_link_box.text_frame
    tf_bl.word_wrap = True
    p_bl = tf_bl.paragraphs[0]
    r = p_bl.add_run()
    r.text = "EXPLORE DATA SOURCES: "
    r.font.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = AMBER_ACCENT
    r2 = p_bl.add_run()
    r2.text = "[NASA PSI Portal]"
    r2.font.bold = True
    r2.font.size = Pt(11)
    r2.font.color.rgb = CYAN_ACCENT
    r2.hyperlink.address = NASA_PSI_URL
    r3 = p_bl.add_run()
    r3.text = "  •  "
    r3.font.color.rgb = TEXT_MUTED
    r4 = p_bl.add_run()
    r4.text = "[Nature Scientific Reports Link et al. (2018) Paper]"
    r4.font.bold = True
    r4.font.size = Pt(11)
    r4.font.color.rgb = BLUE_PRIMARY
    r4.hyperlink.address = PAPER_URL

    add_footer_link(s3)

    # =========================================================================
    # SLIDE 4: CV INNOVATION: SURVIVING THE DIM BLUE FLAME
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, 4, "Innovation: Surviving the Dim Blue Near-Limit Flame", "BEST USE OF TECHNOLOGY | ART & TECHNOLOGY")

    # Flow Diagram: Problem vs Solution Architecture
    card_w4 = Inches(5.6)
    card_h4 = Inches(4.1)

    # Left: Commercial CV Failure
    c_cv_fail = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), card_w4, card_h4)
    c_cv_fail.fill.solid()
    c_cv_fail.fill.fore_color.rgb = CARD_BG
    c_cv_fail.line.color.rgb = RED_FAIL
    c_cv_fail.line.width = Pt(1.5)
    tf_fail = c_cv_fail.text_frame
    tf_fail.word_wrap = True
    p = tf_fail.paragraphs[0]
    p.text = "OFF-THE-SHELF FIRE DETECTOR FAILURE"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = RED_FAIL

    fail_items = [
        ("The Fatal Assumption", "Standard detectors filter for red/yellow soot glow."),
        ("The Microgravity Reality", "Near extinction, flames emit dim chemiluminescent blue (CH*/C₂ radicals)."),
        ("Catastrophic Result", "Red-channel mask is completely EMPTY: reports 0 flame exactly where critical science occurs!"),
        ("Otsu Noise Trap", "Thresholding pure sensor noise creates 25 false-positive frames after flame has extinguished.")
    ]
    for h, b in fail_items:
        pi = tf_fail.add_paragraph()
        pi.text = f"✕ {h}: "
        pi.font.bold = True
        pi.font.size = Pt(11)
        pi.font.color.rgb = TEXT_WHITE
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(10.5)
        r.font.color.rgb = TEXT_LIGHT

    # Right: FLARE-X Architecture
    c_fx_sol = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.933), Inches(1.6), card_w4, card_h4)
    c_fx_sol.fill.solid()
    c_fx_sol.fill.fore_color.rgb = CARD_BG
    c_fx_sol.line.color.rgb = GREEN_OK
    c_fx_sol.line.width = Pt(1.5)
    tf_sol = c_fx_sol.text_frame
    tf_sol.word_wrap = True
    p = tf_sol.paragraphs[0]
    p.text = "FLARE-X RADIANCE PROXY INNOVATION"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = GREEN_OK

    sol_items = [
        ("Radiance Proxy V = max(R,G,B)", "Soot-independent intensity detects soot incandescence AND blue chemiluminescence."),
        ("Extreme-Value Noise Floor", "Gated at σ√(2 ln N) (~5σ ceiling). Prevents noise flooding; achieves 0 false positives!"),
        ("Decoupled Sootiness Index χ", "χ = (R-B)/(R+B) quantifies the yellow→blue shift as an independent physical observable."),
        ("Flow-Axis Morphology", "Resolves flame length, width, and standoff against fuel rod axis, invariant to camera angle.")
    ]
    for h, b in sol_items:
        pi = tf_sol.add_paragraph()
        pi.text = f"✓ {h}: "
        pi.font.bold = True
        pi.font.size = Pt(11)
        pi.font.color.rgb = TEXT_WHITE
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(10.5)
        r.font.color.rgb = TEXT_LIGHT

    # Telemetry Masking Callout Box
    tel_callout = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.95), Inches(11.733), Inches(0.8))
    tel_callout.fill.solid()
    tel_callout.fill.fore_color.rgb = BLUE_BOX_BG
    tel_callout.line.color.rgb = CYAN_ACCENT
    tf_tc = tel_callout.text_frame
    tf_tc.word_wrap = True
    ptc = tf_tc.paragraphs[0]
    ptc.text = "TELEMETRY OVERLAY ABLATION: Masking the camera's burned-in digital display increased segmentation IoU from 0.654 to 0.843 (+22.4% relative gain)—proving software robustness against real NASA flight video artifacts."
    ptc.font.size = Pt(11)
    ptc.font.bold = True
    ptc.font.color.rgb = TEXT_WHITE

    add_footer_link(s4)

    # =========================================================================
    # SLIDE 5: INTERACTIVE DASHBOARD & EXTINCTION PROXIMITY INDEX
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, 5, "FLARE-X Dashboard: Zero-Latency, Zero Black-Box Opacity", "ART & TECHNOLOGY | BEST USE OF TECHNOLOGY")

    # Flowchart: 5 Physical Terms -> Closed-Form Extinction Proximity Index
    box_w5 = Inches(2.15)
    box_h5 = Inches(3.8)
    box_y5 = Inches(1.6)

    terms = [
        ("1. ELONGATION", "Weight: 25%", "Length / Width ratio increases along flow axis as flame stretches.", CYAN_ACCENT),
        ("2. STANDOFF", "Weight: 25%", "Flame lifts off surface behind thickened boundary layer.", CYAN_ACCENT),
        ("3. BLUENESS", "Weight: 20%", "Sootiness index χ drops; flame shifts from yellow to blue.", AMBER_ACCENT),
        ("4. DIMNESS", "Weight: 15%", "Mean relative radiance falls as reaction zone cools.", AMBER_ACCENT),
        ("5. CONTRACTION", "Weight: 15%", "Projected flame area shrinks prior to thermal quenching.", GREEN_OK),
    ]

    for idx, (t_name, t_wt, t_desc, t_col) in enumerate(terms):
        bx = Inches(0.8 + idx * 2.4)
        c_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, box_y5, box_w5, box_h5)
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = CARD_BG
        c_box.line.color.rgb = t_col
        c_box.line.width = Pt(1.5)
        tf_t = c_box.text_frame
        tf_t.word_wrap = True
        
        p = tf_t.paragraphs[0]
        p.text = t_name
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = t_col

        p2 = tf_t.add_paragraph()
        p2.text = t_wt
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_WHITE

        p3 = tf_t.add_paragraph()
        p3.text = "\n" + t_desc
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = TEXT_LIGHT

    # Closed-Form Mathematical Box
    cf_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.65), Inches(11.733), Inches(1.1))
    cf_box.fill.solid()
    cf_box.fill.fore_color.rgb = BLUE_BOX_BG
    cf_box.line.color.rgb = CYAN_ACCENT
    tf_cf = cf_box.text_frame
    tf_cf.word_wrap = True
    p = tf_cf.paragraphs[0]
    p.text = "EXACT CLOSED-FORM PER-FRAME ATTRIBUTION:"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT

    p_eq = tf_cf.add_paragraph()
    p_eq.text = "EPI(t) = 0.25·(Elongation) + 0.25·(Standoff) + 0.20·(Blueness) + 0.15·(Dimness) + 0.15·(Area Contraction)"
    p_eq.font.size = Pt(12)
    p_eq.font.bold = True
    p_eq.font.color.rgb = TEXT_WHITE

    p_note = tf_cf.add_paragraph()
    p_note.text = "• Zero Black-Box: Linear combination of bounded observables provides exact attribution bars on every frame."
    p_note.font.size = Pt(10.5)
    p_note.font.color.rgb = TEXT_LIGHT

    add_footer_link(s5)

    # =========================================================================
    # SLIDE 6: FALSIFICATION TESTING & VERIFIED BENCHMARKS
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, 6, "Built-In Falsification: Ground Truth Proved by Telemetry", "BEST USE OF SCIENCE | BEST USE OF DATA")

    # 4 Metric Cards Across
    mc_w = Inches(2.7)
    mc_h = Inches(4.2)
    mc_y = Inches(1.6)

    metrics_data = [
        ("CHANGE-POINT RECALL", "1.000 (100%)", "Commanded Flow Steps", [
            "All 6 commanded flow step transitions detected.",
            "Scored against burned-in camera anemometer data.",
            "Sub-frame temporal accuracy: Mean offset = 0.125 frames!"
        ], CYAN_ACCENT),
        ("SEGMENTATION ACCURACY", "0.843 IoU", "0.915 Mean Dice Score", [
            "Scored on 332 individual video frames.",
            "5th percentile IoU: 0.829 (rock-solid).",
            "Zero false positives on empty or post-extinction frames."
        ], GREEN_OK),
        ("EPI MONOTONICITY", "ρ = -0.989", "Spearman Rank Correlation", [
            "Tracks approach to extinction monotonically (p < 10⁻⁵).",
            "Initial dwell EPI: 0.111 → Final live frame EPI: 0.850.",
            "Built-in falsification rule: ρ > -0.3 returns NOT_SUPPORTED."
        ], AMBER_ACCENT),
        ("TEST SUITE COVERAGE", "24 / 24 PASSED", "100% Automated Testing", [
            "Physics equations (Gr ∝ g) verified.",
            "Extreme-value noise floor tests verified.",
            "Zero false positives post-extinction verified.",
            "Reproducible with seed 20261114."
        ], BLUE_PRIMARY)
    ]

    for idx, (m_title, m_big, m_sub, m_bullets, m_col) in enumerate(metrics_data):
        bx = Inches(0.8 + idx * 3.0)
        c_m = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, mc_y, mc_w, mc_h)
        c_m.fill.solid()
        c_m.fill.fore_color.rgb = CARD_BG
        c_m.line.color.rgb = m_col
        c_m.line.width = Pt(1.5)
        tf_m = c_m.text_frame
        tf_m.word_wrap = True

        p = tf_m.paragraphs[0]
        p.text = m_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = m_col

        p_big = tf_m.add_paragraph()
        p_big.text = m_big
        p_big.font.size = Pt(20)
        p_big.font.bold = True
        p_big.font.color.rgb = TEXT_WHITE

        p_sub = tf_m.add_paragraph()
        p_sub.text = m_sub
        p_sub.font.size = Pt(10)
        p_sub.font.bold = True
        p_sub.font.color.rgb = AMBER_ACCENT

        for b in m_bullets:
            pi = tf_m.add_paragraph()
            pi.text = "• " + b
            pi.font.size = Pt(10)
            pi.font.color.rgb = TEXT_LIGHT

    # Bottom Falsification Rule Banner
    f_bar = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.75))
    f_bar.fill.solid()
    f_bar.fill.fore_color.rgb = BLUE_BOX_BG
    f_bar.line.color.rgb = GREEN_OK
    tf_fb = f_bar.text_frame
    tf_fb.word_wrap = True
    pf = tf_fb.paragraphs[0]
    pf.text = "FALSIFICATION DISCIPLINE: If detected change points did not land on the commanded flow schedule, the method has failed. Our 0.125-frame alignment proves the image features directly measure the physical flow regime shifts."
    pf.font.size = Pt(11)
    pf.font.bold = True
    pf.font.color.rgb = TEXT_WHITE

    add_footer_link(s6)

    # =========================================================================
    # SLIDE 7: MISSION IMPACT & FORWARD HORIZONS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, 7, "Mission Impact: Moon, Mars, Earth Infrastructure & Beyond", "GALACTIC IMPACT | BEST MISSION CONCEPT | LOCAL IMPACT")

    # 3 Large Pillars: Spacecraft Flight, Earth Infrastructure, Global Open Science
    p_w7 = Inches(3.7)
    p_h7 = Inches(4.2)
    p_y7 = Inches(1.6)

    # Pillar 1: Spaceflight (Artemis / Mars)
    pil1 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), p_y7, p_w7, p_h7)
    pil1.fill.solid()
    pil1.fill.fore_color.rgb = CARD_BG
    pil1.line.color.rgb = CYAN_ACCENT
    pil1.line.width = Pt(1.5)
    tf1 = pil1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "1. DEEP-SPACE HABITATION"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CYAN_ACCENT
    pil1_items = [
        ("Lunar Gateway & Artemis", "Protects crewed lunar habitats by identifying non-buoyant extinction margins."),
        ("Mars Transit Vehicles", "Multi-year missions cannot afford false alarms or unquenched smoldering."),
        ("Next-Gen NASA SoFIE", "Built as a drop-in analytical harness for NASA's active SoFIE payload on the ISS."),
        ("Modernizing Standards", "Provides empirical low-g data to upgrade NASA-STD-6001 Test 1.")
    ]
    for h, b in pil1_items:
        pi = tf1.add_paragraph()
        pi.text = f"• {h}: "
        pi.font.bold = True
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = TEXT_WHITE
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(10)
        r.font.color.rgb = TEXT_LIGHT

    # Pillar 2: Edge Flight Concept (Level 5)
    pil2 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), p_y7, p_w7, p_h7)
    pil2.fill.solid()
    pil2.fill.fore_color.rgb = CARD_BG
    pil2.line.color.rgb = AMBER_ACCENT
    pil2.line.width = Pt(1.5)
    tf2 = pil2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "2. LEVEL-5 FLIGHT CONCEPT"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT
    pil2_items = [
        ("Optical Edge Sensors", "Runs rule-based Tier-1 morphology on low-SWaP radiation-tolerant flight computers."),
        ("Pre-Smoke Early Warning", "Detects boundary layer standoff and blueness drift BEFORE smoke enters detectors."),
        ("ECLSS Integration", "Automated ventilation throttling and targeted N₂/CO₂ suppressant release."),
        ("Honest TRL Label", "Clearly demarcated as Level 5 Mission Concept (TRL 3-4).")
    ]
    for h, b in pil2_items:
        pi = tf2.add_paragraph()
        pi.text = f"• {h}: "
        pi.font.bold = True
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = TEXT_WHITE
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(10)
        r.font.color.rgb = TEXT_LIGHT

    # Pillar 3: Terrestrial Impact (Mines, Tunnels, Education)
    pil3 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), p_y7, p_w7, p_h7)
    pil3.fill.solid()
    pil3.fill.fore_color.rgb = CARD_BG
    pil3.line.color.rgb = GREEN_OK
    pil3.line.width = Pt(1.5)
    tf3 = pil3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "3. EARTH SPIN-OFFS & STEM"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GREEN_OK
    pil3_items = [
        ("Subway & Mine Tunnels", "Forced horizontal low-speed air in low-ceiling shafts mirrors microgravity flame spread."),
        ("Aircraft Cargo Holds", "Low-pressure, constrained convection fire detection."),
        ("Global STEM Education", "Free MIT-licensed simulator for universities and fire academies worldwide without GPUs."),
        ("Democratizing Space", "Turns locked NASA archives into interactive open science for all.")
    ]
    for h, b in pil3_items:
        pi = tf3.add_paragraph()
        pi.text = f"• {h}: "
        pi.font.bold = True
        pi.font.size = Pt(10.5)
        pi.font.color.rgb = TEXT_WHITE
        r = pi.add_run()
        r.text = b
        r.font.bold = False
        r.font.size = Pt(10)
        r.font.color.rgb = TEXT_LIGHT

    # Bottom Call to Action
    cta_box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.75))
    cta_box.fill.solid()
    cta_box.fill.fore_color.rgb = BLUE_BOX_BG
    cta_box.line.color.rgb = CYAN_ACCENT
    tf_cta = cta_box.text_frame
    tf_cta.word_wrap = True
    p_cta = tf_cta.paragraphs[0]
    p_cta.text = "THE MISSION CONCLUSION: NASA measured this. FLARE-X makes it measurable, auditable, and actionable. From the International Space Station to the Moon, Mars, and Earth's deepest tunnels—making fire safety an exact science."
    p_cta.font.size = Pt(11)
    p_cta.font.bold = True
    p_cta.font.color.rgb = TEXT_WHITE

    add_footer_link(s7)

    # Save presentation
    prs.save(output_path)
    print(f"Successfully generated {output_path} (7 slides, 16:9 widescreen, fully hyperlinked)")

if __name__ == "__main__":
    create_deck()
