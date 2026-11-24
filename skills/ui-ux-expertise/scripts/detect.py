#!/usr/bin/env python3
"""Detect common UI anti-patterns in frontend source files.

A static, heuristic scanner. Precision matters more than recall: when a
pattern is ambiguous, it is not flagged.

Usage:
  python detect.py [--json] [--ignore RULE[,RULE...]] PATH [PATH ...]

Exit codes:
  0  no findings
  1  one or more findings
  2  usage error (bad arguments, nonexistent path, unknown ignore id)

An unreadable file is reported on stderr as `path: skipped (reason)` and does
not change the exit code. A file reached twice is scanned once.

Standard library only; Python 3.9+.
"""

import argparse
import bisect
import json
import os
import re
import sys
from collections import namedtuple
from pathlib import Path

SCANNED_EXTENSIONS = {
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".vue", ".svelte",
    ".astro", ".jsx", ".tsx", ".twig", ".jinja", ".jinja2", ".j2", ".njk",
}  # fmt: skip
STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less"}
# `build` also covers `public/build`.
SKIPPED_DIRS = {
    "node_modules", "vendor", "dist", "build", ".git", "storage", ".next",
    ".nuxt", ".svelte-kit", "coverage",
}  # fmt: skip

# ---------------------------------------------------------------------------
# Matching helpers. Every check yields character offsets into the file text;
# the offset of a match start becomes the reported line.
# ---------------------------------------------------------------------------


def declarations(text, prop):
    """Yield (offset, value) for each CSS `prop: value` declaration.

    `prop` is a regex for the property name. The value stops at `;`, braces,
    angle brackets or a double quote (the end of an inline style attribute).
    """
    pattern = r"(?<![\w-])(?:%s)\s*:\s*([^;{}<>\"]*)" % prop
    for m in re.finditer(pattern, text):
        yield m.start(), m.group(1).strip()


def tailwind(text, cls, accept=None):
    """Yield offsets of the Tailwind class regex `cls` used as a whole token.

    `accept(match)`, when given, filters on the class's captured groups.
    """
    pattern = r"(?<![\w-])(?:%s)(?![\w-]|\s*:)" % cls
    for m in re.finditer(pattern, text):
        if accept is None or accept(m):
            yield m.start()


CLASS_ATTR_RE = re.compile(
    r"(?<![\w-])(?::class|v-bind:class|className|class)\s*=\s*"
    r"(?:\"([^\"]*)\"|'([^']*)'|\{((?:[^{}]|\{[^{}]*\})*)\})"
)


def class_lists(text):
    """Yield (offset, classes) for each class attribute and `@apply` rule.

    Classes are returned as a set with variant prefixes (`md:`, `hover:`)
    and `!` stripped.
    """
    found = [
        (m.start(), m.group(1) or m.group(2) or m.group(3) or "")
        for m in CLASS_ATTR_RE.finditer(text)
    ]
    found += [(m.start(), m.group(1)) for m in re.finditer(r"@apply\s+([^;{}]*)", text)]
    for offset, value in found:
        names = re.findall(r"[^\s'\"`{},]+", value)
        yield offset, {re.sub(r"^(?:[\w-]+:)+", "", n).lstrip("!") for n in names}


ATTR_VALUE = r"\"[^\"]*\"|'[^']*'|\{(?:[^{}]|\{[^{}]*\})*\}"
# The attributes of an opening tag. A bare `<` ends the match, so an
# unterminated tag fails at the next tag instead of scanning to end of file.
TAG_BODY = r"(?:%s|[^<>\"'{}])*" % ATTR_VALUE


def tags(text, name):
    """Yield (offset, attributes) for each opening tag whose name matches `name`.

    Handles multi-line tags. Attribute values are blanked, so only attribute
    names remain. Tags with spread or template syntax (`{...props}`,
    `{{ $attributes }}`) are skipped: their attributes are unknown.
    """
    pattern = r"<(?:%s)(?![\w-])(%s)>" % (name, TAG_BODY)
    for m in re.finditer(pattern, text):
        attrs = re.sub(r"=\s*(?:%s)" % ATTR_VALUE, "=", m.group(1))
        if "{" not in attrs:
            yield m.start(), attrs


def has_attr(attrs, name):
    """True if `attrs` (from tags()) has attribute `name`, plain or bound."""
    return re.search(r"(?<![\w-])(?:%s)(?![\w-])" % name, attrs) is not None


def blocks(text):
    """Yield (offset, body) for innermost `{...}` blocks and style attributes."""
    for m in re.finditer(r"\{([^{}]*)\}", text):
        yield m.start(1), m.group(1)
    for m in re.finditer(r"(?<![\w-])style\s*=\s*\"([^\"]*)\"", text):
        yield m.start(1), m.group(1)


def is_markup(path):
    """True unless the file is a stylesheet."""
    return os.path.splitext(path.lower())[1] not in STYLE_EXTENSIONS


def matches(pattern, flags=0):
    """Build a check that flags every match of `pattern`."""
    compiled = re.compile(pattern, flags)
    return lambda text, path: (m.start() for m in compiled.finditer(text))


def length(value):
    """Return (number, unit) for a leading px/rem/em length, else None."""
    m = re.match(r"(-?\d*\.?\d+)(px|rem|em)(?![\w-])", value.strip())
    return (float(m.group(1)), m.group(2)) if m else None


def to_px(value):
    """Return a leading `px`/`rem` length in px (1rem = 16px), else None."""
    parsed = length(value)
    if parsed is None or parsed[1] == "em":
        return None
    number, unit = parsed
    return number * 16 if unit == "rem" else number


def to_em(value):
    """Return a leading `em` length as a number, else None."""
    parsed = length(value)
    return parsed[0] if parsed and parsed[1] == "em" else None


def tokens(value):
    """Split a CSS value on whitespace, keeping function calls whole."""
    return re.findall(r"[\w-]+\((?:[^()]|\([^()]*\))*\)|[^\s,]+", value)


NEUTRAL_NAME_RE = re.compile(
    r"(?:black|white|transparent|currentcolor|inherit|initial|unset|silver"
    r"|gainsboro|whitesmoke|(?:light|dark|dim)?gr[ae]y)$"
)


def is_neutral_color(color):
    """True for black, white, grays and low-chroma colors.

    A `var()` is neutral only when its name says so (gray, neutral, border,
    muted); other custom properties count as colored.
    """
    c = color.strip().lower()
    if NEUTRAL_NAME_RE.match(c):
        return True
    if c.startswith("var("):
        return bool(re.search(r"gr[ae]y|neutral|border|muted", c))
    hex_match = re.fullmatch(r"#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})", c)
    if hex_match:
        digits = hex_match.group(1)
        if len(digits) <= 4:
            digits = "".join(d * 2 for d in digits)
        channels = [int(digits[i : i + 2], 16) for i in (0, 2, 4)]
        return max(channels) - min(channels) <= 24
    rgb_match = re.match(r"rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)", c)
    if rgb_match:
        channels = [int(v) for v in rgb_match.groups()]
        return max(channels) - min(channels) <= 24
    hsl_match = re.match(r"hsla?\(\s*[^,\s]+[\s,]+(\d*\.?\d+)%", c)
    return bool(hsl_match) and float(hsl_match.group(1)) <= 10


def split_layers(value):
    """Split a CSS value on top-level commas (not inside parentheses)."""
    layers, depth, start = [], 0, 0
    for i, char in enumerate(value):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            layers.append(value[start:i].strip())
            start = i + 1
    layers.append(value[start:].strip())
    return layers


# ---------------------------------------------------------------------------
# Rule checks, in registry order
# ---------------------------------------------------------------------------


def check_gradient_text(text, path):
    for start, body in blocks(text):
        clips = [
            offset
            for offset, value in declarations(
                body, "-webkit-background-clip|background-clip"
            )
            if value.startswith("text")
        ]
        gradient = any(
            "gradient(" in value
            for _, value in declarations(body, "background|background-image")
        )
        if clips and gradient:
            yield start + clips[0]
    for offset, classes in class_lists(text):
        if "bg-clip-text" in classes and any(
            re.match(r"bg-(?:gradient-to-|linear-|radial|conic)", c) for c in classes
        ):
            yield offset


BORDER_STYLES = {
    "none", "hidden", "solid", "dashed", "dotted", "double", "groove", "ridge",
    "inset", "outset", "!important",
}  # fmt: skip


def check_side_stripe_border(text, path):
    side = r"border-(?:left|right|inline-start|inline-end)"
    for offset, value in declarations(text, side + "-width"):
        px = to_px(value)
        if px is not None and px > 1:
            yield offset
    for offset, value in declarations(text, side):
        parts = tokens(value)
        widths = [px for px in map(to_px, parts) if px is not None]
        colors = [t for t in parts if to_px(t) is None and t not in BORDER_STYLES]
        if widths and widths[0] > 1 and colors and not is_neutral_color(colors[0]):
            yield offset

    def is_thick(m):
        px = int(m.group(1)) if m.group(1) else to_px(m.group(2))
        return px is not None and px >= 2

    yield from tailwind(text, r"border-[lrse]-(?:(\d+)|\[([^\]]+)\])", is_thick)


def shadows(text):
    """Yield (offset, layers) for CSS box-shadow and Tailwind shadow-[...].

    Each layer is (lengths in px, color or None); `inset` is ignored.
    """
    values = list(declarations(text, "box-shadow"))
    for m in re.finditer(r"(?<![\w-])shadow-\[([^\]\s]+)\]", text):
        values.append((m.start(), m.group(1).replace("_", " ")))
    for offset, value in values:
        layers = []
        for layer in split_layers(value):
            lengths, colors = [], []
            for token in tokens(layer):
                px = 0.0 if token == "0" else to_px(token)
                if px is not None:
                    lengths.append(px)
                elif token not in ("inset", "!important"):
                    colors.append(token)
            layers.append((lengths, colors[0] if colors else None))
        yield offset, layers


def check_hard_offset_shadow(text, path):
    for offset, layers in shadows(text):
        lengths = layers[0][0]
        # Offsets up to 1px are hairline dividers/highlights, not block shadows.
        has_offset = len(lengths) >= 2 and max(abs(lengths[0]), abs(lengths[1])) > 1
        if has_offset and (len(lengths) == 2 or lengths[2] == 0):
            yield offset


def check_glow_halo(text, path):
    for offset, layers in shadows(text):
        for lengths, color in layers:
            centered = len(lengths) >= 3 and lengths[0] == 0 and lengths[1] == 0
            if centered and lengths[2] >= 8 and color and not is_neutral_color(color):
                yield offset
                break


def check_glass_default(text, path):
    for offset, value in declarations(text, "-webkit-backdrop-filter|backdrop-filter"):
        if re.search(r"blur\(\s*(?!0(?:px)?\s*\))", value):
            yield offset
    yield from tailwind(
        text,
        r"backdrop-blur(?:-[\w.\[\]]+)?",
        lambda m: m.group() != "backdrop-blur-none",
    )


def is_wide_tracking_class(name):
    if name in ("tracking-wide", "tracking-wider", "tracking-widest"):
        return True
    m = re.fullmatch(r"tracking-\[(.+)\]", name)
    em = to_em(m.group(1)) if m else None
    return em is not None and em >= 0.1


def is_small_text_class(name):
    if name in ("text-xs", "text-sm"):
        return True
    m = re.fullmatch(r"text-\[(.+)\]", name)
    px = to_px(m.group(1)) if m else None
    return px is not None and px <= 14


def check_eyebrow_kicker(text, path):
    def wide(value):
        em, px = to_em(value), to_px(value)
        return (em is not None and em >= 0.08) or (px is not None and px >= 1)

    def small(value):
        px = to_px(value)
        return px is not None and px <= 14

    for start, body in blocks(text):
        upper = [o for o, v in declarations(body, "text-transform") if v == "uppercase"]
        if (
            upper
            and any(wide(v) for _, v in declarations(body, "letter-spacing"))
            and any(small(v) for _, v in declarations(body, "font-size"))
        ):
            yield start + upper[0]
    for offset, classes in class_lists(text):
        if (
            "uppercase" in classes
            and any(is_wide_tracking_class(c) for c in classes)
            and any(is_small_text_class(c) for c in classes)
        ):
            yield offset


# An element whose text is only `01`, optionally followed by a separator and
# a short label (`01 /`, `01.`, `01 - About`).
SECTION_NUMBER_RE = re.compile(
    r"<[a-zA-Z][\w-]*%s>\s*"
    r"(0[1-9](?:\s*[./|:\u00b7\u2013\u2014-](?:\s*[^\W\d][^<>.!?]{0,30})?)?)\s*<"
    % TAG_BODY
)
LIST_OR_TABLE_OPEN_RE = re.compile(r"<(?:li|td|th|option)(?![\w-])")
LIST_OR_TABLE_CLOSE_RE = re.compile(r"</(?:li|td|th|option)>")


def check_numbered_section_label(text, path):
    if not is_markup(path):
        return
    opens = [m.start() for m in LIST_OR_TABLE_OPEN_RE.finditer(text)]
    closes = [m.start() for m in LIST_OR_TABLE_CLOSE_RE.finditer(text)]
    for m in SECTION_NUMBER_RE.finditer(text):
        offset = m.start(1)
        # Not inside a list item, table cell or option: the last such opening
        # tag before the number is already closed.
        if last_before(opens, offset) <= last_before(closes, offset):
            yield offset


def last_before(positions, offset):
    """Return the last of the sorted `positions` before `offset`, else -1."""
    i = bisect.bisect_left(positions, offset)
    return positions[i - 1] if i else -1


NUMBER = r"(-?\d*\.?\d+)"
CUBIC_BEZIER_RE = re.compile(
    r"cubic-bezier\(\s*" + r"[\s_]*,[\s_]*".join([NUMBER] * 4) + r"\s*\)"
)


def check_bounce_easing(text, path):
    for m in CUBIC_BEZIER_RE.finditer(text):
        y1, y2 = float(m.group(2)), float(m.group(4))
        if not (0 <= y1 <= 1 and 0 <= y2 <= 1):
            yield m.start()
    for offset, value in declarations(text, "animation|animation-name"):
        if re.search(r"bounce|elastic", value, re.IGNORECASE):
            yield offset
    yield from tailwind(text, "animate-bounce")


def check_transition_all(text, path):
    for offset, value in declarations(text, "transition|transition-property"):
        if any(re.match(r"all(?![\w-])", layer) for layer in split_layers(value)):
            yield offset
    yield from tailwind(text, "transition-all")


LAYOUT_PROPERTY = (
    r"width|height|top|left|right|bottom|margin(?:-[\w-]+)?|padding(?:-[\w-]+)?"
)
LAYOUT_PROPERTY_RE = re.compile(r"(?:%s)$" % LAYOUT_PROPERTY)
# `@keyframes name {`, vendor-prefixed (`@-webkit-keyframes`) included.
KEYFRAMES_RE = re.compile(r"@(?:-[a-z]+-)?keyframes\s+[\w-]+\s*\{")
BRACE_RE = re.compile(r"[{}]")


def keyframes(text):
    """Yield (offset, body) for each `@keyframes` block, nested braces included.

    An unterminated block runs to the end of the text.
    """
    m = KEYFRAMES_RE.search(text)
    while m:
        depth, end = 1, len(text)
        for brace in BRACE_RE.finditer(text, m.end()):
            depth += 1 if brace.group() == "{" else -1
            if depth == 0:
                end = brace.start()
                break
        yield m.end(), text[m.end() : end]
        m = KEYFRAMES_RE.search(text, end)


def check_layout_transition(text, path):
    for offset, value in declarations(text, "transition|transition-property"):
        words = re.sub(r"\([^()]*\)", "", value).replace(",", " ").split()
        if any(LAYOUT_PROPERTY_RE.match(word) for word in words):
            yield offset
    for start, body in keyframes(text):
        for offset, _ in declarations(body, LAYOUT_PROPERTY):
            yield start + offset


def check_arbitrary_z_index(text, path):
    for offset, value in declarations(text, "z-index"):
        digits = re.match(r"\d+", value)
        if digits and int(digits.group()) >= 999:
            yield offset
    yield from tailwind(text, r"z-\[(\d+)\]", lambda m: int(m.group(1)) >= 999)


FOCUS_STYLE_RE = re.compile(r"focus-visible|focus:ring|focus:outline-(?!none(?![\w-]))")


def check_outline_removed(text, path):
    if FOCUS_STYLE_RE.search(text):
        return
    for offset, value in declarations(text, "outline"):
        if re.match(r"(?:none|0)(?![\w.])", value):
            yield offset
    yield from tailwind(text, "outline-none")


ZOOM_LOCK_RE = re.compile(
    r"user-scalable\s*=\s*(?:no|0)(?![\w.])|maximum-scale\s*=\s*1(?:\.0+)?(?![\d.])"
)


def check_zoom_disabled(text, path):
    for m in re.finditer(r"<meta\b[^>]*>", text, re.IGNORECASE):
        tag = m.group()
        if "viewport" in tag.lower() and ZOOM_LOCK_RE.search(tag):
            yield m.start()


def check_extreme_tracking(text, path):
    def is_extreme(value):
        em = to_em(value)
        return em is not None and em < -0.04

    for offset, value in declarations(text, "letter-spacing"):
        if is_extreme(value):
            yield offset
    yield from tailwind(text, "tracking-tighter")
    yield from tailwind(
        text, r"tracking-\[([^\]]+)\]", lambda m: is_extreme(m.group(1))
    )


def check_tiny_text(text, path):
    def is_tiny(value):
        px = to_px(value)
        return px is not None and 0 < px < 12

    for offset, value in declarations(text, "font-size"):
        if is_tiny(value):
            yield offset
    yield from tailwind(text, r"text-\[([^\]]+)\]", lambda m: is_tiny(m.group(1)))


def check_justified_text(text, path):
    for offset, value in declarations(text, "text-align"):
        if re.match(r"justify(?![\w-])", value):
            yield offset
    yield from tailwind(text, "text-justify")


REFLEX_FONTS = (
    "Fraunces", "Playfair Display", "Cormorant", "Lora", "Crimson", "Newsreader",
    "Syne", "Space Grotesk", "Space Mono", "IBM Plex", "DM Sans", "DM Serif",
    "Outfit", "Plus Jakarta Sans", "Instrument Sans",
)  # fmt: skip
REFLEX_FONT_RE = re.compile(
    r"\b(?:%s)\b" % "|".join(name.replace(" ", r"[\s+_]") for name in REFLEX_FONTS),
    re.IGNORECASE,
)
# Places where a font is named: declarations, @import, Google Fonts URLs and
# Tailwind font-[...] classes.
FONT_CONTEXT_RE = re.compile(
    r"(?<![\w-])(?:font-family|font|--font[\w-]*)\s*:[^;{}<>\n]*"
    r"|@import[^;\n]*"
    r"|fonts\.googleapis\.com/[^\s\"'<>)]*"
    r"|(?<![\w-])font-\[[^\]]*\]"
)


def check_reflex_font(text, path):
    for m in FONT_CONTEXT_RE.finditer(text):
        font = REFLEX_FONT_RE.search(m.group())
        if font:
            yield m.start() + font.start()


def check_img_missing_alt(text, path):
    for offset, attrs in tags(text, "img"):
        if not has_attr(attrs, "alt"):
            yield offset


def check_img_missing_dimensions(text, path):
    for offset, attrs in tags(text, "img"):
        if not (has_attr(attrs, "width") and has_attr(attrs, "height")):
            yield offset


CLICK_HANDLER = r"on[cC]lick|@click|v-on:click|x-on:click|wire:click|on:click"


def check_clickable_div(text, path):
    for offset, attrs in tags(text, "div|span"):
        if has_attr(attrs, CLICK_HANDLER) and not has_attr(attrs, "role|tab[iI]ndex"):
            yield offset


EMOJI_RE = re.compile("[\U0001f300-\U0001faff\u2600-\u27bf]")
CONTROL_TAG_RE = re.compile(r"<(button|a)(?![\w-])%s>" % TAG_BODY)


def check_emoji_icon(text, path):
    for m in CONTROL_TAG_RE.finditer(text):
        end = text.find("</%s>" % m.group(1), m.end())
        content = text[m.end() : end] if end != -1 else ""
        for emoji in EMOJI_RE.finditer(content):
            before = content[: emoji.start()]
            if before.rfind("<") <= before.rfind(">"):  # text, not inside a tag
                yield m.end() + emoji.start()
                break


BUZZWORDS = (
    "streamline your", "empower your", "supercharge your", "unleash your",
    "unleash the power", "leverage the power", "harness the power",
    "built for the modern", "trusted by leading", "trusted by the world",
    "best-in-class", "industry-leading", "world-class", "enterprise-grade",
    "next-generation", "cutting-edge", "transform your business", "revolutionize",
    "game-changer", "game changing", "mission-critical", "best of breed",
    "future-proof", "future proof", "seamless experience", "seamlessly integrate",
    "drive engagement", "drive growth", "drive results",
)  # fmt: skip
BUZZWORD_RE = re.compile(
    r"\b(?:%s)"
    % "|".join(r"\s+".join(re.escape(word) for word in p.split()) for p in BUZZWORDS),
    re.IGNORECASE,
)
# Scripts, styles, comments and tags: everything that is not visible text.
NOT_VISIBLE_RE = re.compile(
    r"<script\b.*?</script\s*>|<style\b.*?</style\s*>|<!--.*?-->"
    r"|</?[a-zA-Z][\w:.-]*%s>" % TAG_BODY,
    re.DOTALL | re.IGNORECASE,
)


def check_marketing_buzzword(text, path):
    if not is_markup(path):
        return
    # Blank hidden parts with spaces, keeping newlines so offsets stay valid.
    visible = NOT_VISIBLE_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), text)
    for m in BUZZWORD_RE.finditer(visible):
        yield m.start()


# prefers-reduced-motion, motion-safe:/motion-reduce:, and JS names such as
# useReducedMotion, prefersReducedMotion or reducedMotion.
REDUCED_MOTION_RE = re.compile(r"reduced-?motion|motion-(?:safe|reduce):", re.I)


def has_reduced_motion(text):
    return REDUCED_MOTION_RE.search(text) is not None


def check_missing_reduced_motion(text, path):
    """Yield the file's first animation unless the file handles reduced motion.

    The verdict spans all scanned files: main() drops these findings when any
    of them has_reduced_motion().
    """
    if has_reduced_motion(text):
        return
    animations = [m.start() for m in KEYFRAMES_RE.finditer(text)]
    animations += [
        offset
        for offset, value in declarations(text, "animation|animation-name")
        # `true`/`false` are JS options (e.g. a chart config), not CSS animations.
        if value and not re.match(r"['`]?(?:none|false|true)(?![\w-])", value)
    ]
    animations += [
        offset
        for offset, classes in class_lists(text)
        if any(c.startswith("animate-") and c != "animate-none" for c in classes)
    ]
    if animations:
        yield min(animations)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

Rule = namedtuple("Rule", "id severity message check")

RULES = [
    Rule(
        "gradient-text",
        "error",
        "gradient text hurts legibility and reads as generic; use a solid text color",
        check_gradient_text,
    ),
    Rule(
        "side-stripe-border",
        "error",
        "thick colored side stripe is a dated accent; use a full border or background tint",
        check_side_stripe_border,
    ),
    Rule(
        "hard-offset-shadow",
        "warning",
        "hard offset shadow (no blur) is a neo-brutalist reflex; use a soft shadow",
        check_hard_offset_shadow,
    ),
    Rule(
        "glow-halo",
        "warning",
        "colored glow halo is a generic AI look; use a subtle neutral shadow",
        check_glow_halo,
    ),
    Rule(
        "glass-default",
        "warning",
        "glassmorphism by default; use a solid surface unless blur has a purpose",
        check_glass_default,
    ),
    Rule(
        "eyebrow-kicker",
        "error",
        "small uppercase tracked eyebrow label is a template reflex; let the heading lead",
        check_eyebrow_kicker,
    ),
    Rule(
        "numbered-section-label",
        "warning",
        "numbered section label (01, 02, ...) is decorative filler; use a real heading",
        check_numbered_section_label,
    ),
    Rule(
        "bounce-easing",
        "warning",
        "bounce/elastic easing feels dated; use a smooth ease-out curve",
        check_bounce_easing,
    ),
    Rule(
        "transition-all",
        "warning",
        "transition: all animates unintended properties; name the properties",
        check_transition_all,
    ),
    Rule(
        "layout-transition",
        "warning",
        "transitioning or animating layout properties causes reflow; "
        "animate transform/opacity",
        check_layout_transition,
    ),
    Rule(
        "arbitrary-z-index",
        "warning",
        "arbitrary z-index escalation; use a small layered z-index scale",
        check_arbitrary_z_index,
    ),
    Rule(
        "outline-removed",
        "error",
        "focus outline removed without a :focus-visible replacement; add one",
        check_outline_removed,
    ),
    Rule(
        "zoom-disabled",
        "error",
        "viewport blocks pinch zoom; remove user-scalable/maximum-scale limits",
        check_zoom_disabled,
    ),
    Rule(
        "extreme-tracking",
        "warning",
        "letter-spacing tighter than -0.04em makes glyphs collide; loosen it",
        check_extreme_tracking,
    ),
    Rule(
        "tiny-text",
        "warning",
        "text below 12px is hard to read; use at least 12px",
        check_tiny_text,
    ),
    Rule(
        "justified-text",
        "warning",
        "justified text creates uneven word gaps; align left",
        check_justified_text,
    ),
    Rule(
        "reflex-font",
        "warning",
        "overused training-data default font on expressive surfaces; "
        "needs a reason no other face satisfies",
        check_reflex_font,
    ),
    Rule(
        "cream-tokens",
        "warning",
        "cream/paper palette token is a reflex default; derive colors from the brand",
        matches(
            r"(?<![\w-])--(?:[\w-]*-)?"
            r"(?:cream|paper|sand|bone|flour|linen|parchment|wheat|biscuit|ivory)"
            r"(?:-[\w-]*)?\s*:"
        ),
    ),
    Rule(
        "stripes-background",
        "warning",
        "decorative stripe background adds noise; use a plain surface",
        matches(r"repeating-(?:linear|radial)-gradient\("),
    ),
    Rule(
        "img-missing-alt",
        "error",
        'image without alt attribute; describe it, or use alt="" if decorative',
        check_img_missing_alt,
    ),
    Rule(
        "img-missing-dimensions",
        "warning",
        "image without width and height causes layout shift; set both attributes",
        check_img_missing_dimensions,
    ),
    Rule(
        "clickable-div",
        "error",
        "click handler on a div/span is not keyboard accessible; use a <button>",
        check_clickable_div,
    ),
    Rule(
        "positive-tabindex",
        "warning",
        "positive tabindex breaks the natural focus order; use 0 or DOM order",
        matches(r"(?<![\w-])tab[iI]ndex\s*=\s*[\"'{]?\s*0*[1-9]"),
    ),
    Rule(
        "emoji-icon",
        "warning",
        "emoji used as an icon renders inconsistently; use an SVG icon",
        check_emoji_icon,
    ),
    Rule(
        "marketing-buzzword",
        "warning",
        "generic marketing buzzword; say concretely what the product does",
        check_marketing_buzzword,
    ),
    Rule(
        "missing-reduced-motion",
        "warning",
        "animations without a prefers-reduced-motion alternative in the scanned "
        "files; add a reduced-motion path",
        check_missing_reduced_motion,
    ),
]


def scan_text(text, path):
    """Return the findings for one file's text."""
    newlines = [m.start() for m in re.finditer("\n", text)]
    findings = []
    for rule in RULES:
        # A set: overlapping matchers (e.g. nested blocks) may yield one spot twice.
        for offset in sorted(set(rule.check(text, path))):
            findings.append(
                {
                    "file": path,
                    "line": bisect.bisect_left(newlines, offset) + 1,
                    "rule": rule.id,
                    "severity": rule.severity,
                    "message": rule.message,
                }
            )
    return findings


def is_scanned(name):
    name = name.lower()
    return (
        name.endswith(".blade.php") or os.path.splitext(name)[1] in SCANNED_EXTENSIONS
    )


def iter_files(path):
    """Yield `path` itself, or the scannable files below a directory."""
    if not os.path.isdir(path):
        yield path
        return
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIPPED_DIRS]
        for name in files:
            if is_scanned(name):
                yield os.path.join(root, name)


def plural(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="detect.py",
        description="Detect common UI anti-patterns in frontend source files.",
    )
    parser.add_argument("--json", action="store_true", help="print JSON output")
    parser.add_argument(
        "--ignore",
        default="",
        metavar="RULE[,RULE...]",
        help="comma-separated rule ids to suppress",
    )
    parser.add_argument("paths", nargs="+", metavar="PATH", help="file or directory")
    args = parser.parse_args(argv)

    ignored = {rule_id for rule_id in args.ignore.split(",") if rule_id}
    unknown = ignored - {rule.id for rule in RULES}
    if unknown:
        parser.error("unknown rule id(s) for --ignore: " + ", ".join(sorted(unknown)))
    for path in args.paths:
        if not Path(path).exists():
            parser.error(f"path does not exist: {path}")

    findings = []
    seen = set()  # real paths, so a file reached twice is scanned once
    reduced_motion = False
    for path in args.paths:
        for file in iter_files(path):
            real = os.path.realpath(file)
            if real in seen:
                continue
            seen.add(real)
            try:
                text = Path(file).read_text(encoding="utf-8", errors="replace")
            except OSError as exc:  # unreadable file or dangling symlink
                print(f"{file}: skipped ({exc.strerror or exc})", file=sys.stderr)
                continue
            reduced_motion = reduced_motion or has_reduced_motion(text)
            findings.extend(scan_text(text, file))

    if reduced_motion:  # one scanned file handling it covers them all
        ignored.add("missing-reduced-motion")
    findings = [f for f in findings if f["rule"] not in ignored]
    findings.sort(key=lambda f: (f["file"], f["line"], f["rule"]))
    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, indent=2))
        return 1 if findings else 0
    if not findings:
        print("No findings.")
        return 0
    for f in findings:
        letter = "E" if f["severity"] == "error" else "W"
        print(f"{f['file']}:{f['line']}  [{letter}] {f['rule']}  {f['message']}")
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = len(findings) - errors
    print(
        f"{plural(len(findings), 'finding')} "
        f"({plural(errors, 'error')}, {plural(warnings, 'warning')})"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
