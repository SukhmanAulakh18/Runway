"""Colours, CSS and small display helpers. Change the look here, not in the pages."""
import streamlit as st

INK, ORANGE, SLATE, PAPER = "#1d2433", "#e86f00", "#8a94a6", "#fbf7f2"   # orange = ours, slate = standard formula

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&display=swap');
html, body, [class*="css"], .stMarkdown, .stText {{ font-family: 'DM Sans', system-ui, sans-serif; }}
h1, h2, h3 {{ font-family: 'DM Sans', system-ui, sans-serif; font-weight: 700; color: {INK}; letter-spacing: -0.01em; }}
.big {{ font-family: 'DM Serif Display', Georgia, serif; font-size: 3.2rem; line-height: 1; }}
.key {{ color: {SLATE}; }} .real {{ color: {ORANGE}; }}
.card {{ border: 1px solid #e7e1d8; border-radius: 14px; padding: 18px 20px; background: white; }}
.chip {{ display: inline-block; padding: 3px 10px; margin: 2px 4px 2px 0; border-radius: 999px;
        background: #fff1e4; color: #8a4200; font-size: 0.85rem; }}
.flag {{ display: inline-block; padding: 3px 10px; margin: 2px 4px 2px 0; border-radius: 999px;
        background: #eef1f6; color: #3b4459; font-size: 0.85rem; }}
.muted {{ color: #6b7385; font-size: 0.9rem; }}
</style>"""


def apply():
    st.markdown(CSS, unsafe_allow_html=True)


def flags_html(flags: list[str]) -> str:
    return "".join(f"<span class='flag'>{f}</span>" for f in flags)
