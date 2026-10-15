"""Tests for detect.py (stdlib unittest; temp dirs only).

Run from the repo root:
    python3 -m unittest discover -s skills/ui-ux-expertise/scripts -p 'test_*.py' -v
"""

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("detect.py")
_spec = importlib.util.spec_from_file_location("detect_under_test", SCRIPT)
detect = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = detect
_spec.loader.exec_module(detect)


class DetectTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def write(self, rel, text=""):
        path = self.tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_cli(self, *args):
        """Run main() and return (exit code, stdout, stderr)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = detect.main([str(a) for a in args])
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def lines_for(self, rule, text, name="x.html"):
        """Line numbers at which `rule` fires on `text` saved as `name`."""
        findings = detect.scan_text(text, name)
        return [f["line"] for f in findings if f["rule"] == rule]

    def assertFlags(self, rule, text, name="x.html", lines=None):
        found = self.lines_for(rule, text, name)
        if lines is None:
            self.assertTrue(found, f"{rule} not flagged in {name}: {text!r}")
        else:
            self.assertEqual(found, lines)

    def assertNotFlags(self, rule, text, name="x.html"):
        self.assertEqual(self.lines_for(rule, text, name), [], f"{rule}: {text!r}")


class CliTests(DetectTestCase):
    def test_clean_file_prints_no_findings_and_exits_0(self):
        path = self.write("clean.html", "<p>Hello</p>\n")
        code, out, _ = self.run_cli(path)
        self.assertEqual(code, 0)
        self.assertEqual(out, "No findings.\n")

    def test_findings_print_one_line_each_plus_summary_and_exit_1(self):
        path = self.write("a.css", "p {\n  text-align: justify;\n}\n")
        code, out, _ = self.run_cli(path)
        self.assertEqual(code, 1)
        lines = out.splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith(f"{path}:2  [W] justified-text  "))
        self.assertGreater(len(lines[0]), len(f"{path}:2  [W] justified-text  "))
        self.assertEqual(lines[1], "1 finding (0 errors, 1 warning)")

    def test_json_output_shape(self):
        path = self.write("a.css", "p {\n  text-align: justify;\n}\n")
        code, out, _ = self.run_cli("--json", path)
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["findings"]), 1)
        finding = data["findings"][0]
        self.assertEqual(set(finding), {"file", "line", "rule", "severity", "message"})
        self.assertEqual(finding["file"], str(path))
        self.assertEqual(finding["line"], 2)
        self.assertEqual(finding["rule"], "justified-text")
        self.assertEqual(finding["severity"], "warning")
        self.assertIsInstance(finding["message"], str)

    def test_json_output_without_findings(self):
        path = self.write("clean.css", "p { color: red; }\n")
        code, out, _ = self.run_cli("--json", path)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"findings": [], "count": 0})

    def test_ignore_suppresses_listed_rules(self):
        path = self.write("a.css", "p { text-align: justify; transition: all 1s; }\n")
        code, out, _ = self.run_cli("--ignore", "justified-text,transition-all", path)
        self.assertEqual(code, 0)
        self.assertEqual(out, "No findings.\n")

    def test_unknown_ignore_id_is_usage_error(self):
        path = self.write("a.css", "p { color: red; }\n")
        code, _, err = self.run_cli("--ignore", "no-such-rule", path)
        self.assertEqual(code, 2)
        self.assertIn("no-such-rule", err)

    def test_nonexistent_path_is_usage_error(self):
        code, _, err = self.run_cli(self.tmp / "missing.css")
        self.assertEqual(code, 2)
        self.assertIn("missing.css", err)

    def test_missing_path_argument_is_usage_error(self):
        code, _, _ = self.run_cli()
        self.assertEqual(code, 2)

    def test_invalid_utf8_is_read_with_replacement(self):
        path = self.tmp / "bad.css"
        path.write_bytes(b"/* \xff\xfe */\np { text-align: justify; }\n")
        code, out, _ = self.run_cli(path)
        self.assertEqual(code, 1)
        self.assertIn(f"{path}:2  [W] justified-text", out)


class RegistryTests(unittest.TestCase):
    def test_rule_ids_and_severities_match_the_contract(self):
        expected = {
            "gradient-text": "error",
            "side-stripe-border": "error",
            "hard-offset-shadow": "warning",
            "glow-halo": "warning",
            "glass-default": "warning",
            "eyebrow-kicker": "error",
            "numbered-section-label": "warning",
            "bounce-easing": "warning",
            "transition-all": "warning",
            "layout-transition": "warning",
            "arbitrary-z-index": "warning",
            "outline-removed": "error",
            "zoom-disabled": "error",
            "extreme-tracking": "warning",
            "tiny-text": "warning",
            "justified-text": "warning",
            "reflex-font": "warning",
            "cream-tokens": "warning",
            "stripes-background": "warning",
            "img-missing-alt": "error",
            "img-missing-dimensions": "warning",
            "clickable-div": "error",
            "positive-tabindex": "warning",
            "emoji-icon": "warning",
            "marketing-buzzword": "warning",
        }
        self.assertEqual({r.id: r.severity for r in detect.RULES}, expected)
        self.assertEqual(len(detect.RULES), len(expected))
        for rule in detect.RULES:
            self.assertTrue(rule.message.strip(), rule.id)


class WalkTests(DetectTestCase):
    BAD = "p { text-align: justify; }\n"

    def files_flagged(self, *args):
        code, out, _ = self.run_cli("--json", *args)
        return code, sorted({f["file"] for f in json.loads(out)["findings"]})

    def test_directory_is_walked_recursively_with_extension_filter(self):
        root = self.tmp / "app"
        for rel in (
            "app/a.css",
            "app/deep/nested/b.vue",
            "app/views/page.blade.php",
            "app/other.php",
            "app/notes.txt",
            "app/script.js",
        ):
            self.write(rel, self.BAD)
        code, files = self.files_flagged(root)
        self.assertEqual(code, 1)
        self.assertEqual(
            files,
            [
                str(root / "a.css"),
                str(root / "deep" / "nested" / "b.vue"),
                str(root / "views" / "page.blade.php"),
            ],
        )

    def test_all_listed_extensions_are_scanned(self):
        exts = (
            ".html .htm .css .scss .sass .less .vue .svelte .astro .jsx .tsx "
            ".twig .jinja .jinja2 .j2 .njk"
        ).split()
        for ext in exts:
            self.write(f"app/f{ext}", self.BAD)
        _, files = self.files_flagged(self.tmp / "app")
        self.assertEqual(len(files), len(exts))

    def test_skipped_directories_are_not_walked(self):
        skipped = (
            "node_modules vendor dist build .git storage .next .nuxt "
            ".svelte-kit coverage public/build"
        ).split()
        for name in skipped:
            self.write(f"app/{name}/x.css", self.BAD)
        self.write("app/public/ok.css", self.BAD)
        _, files = self.files_flagged(self.tmp / "app")
        self.assertEqual(files, [str(self.tmp / "app" / "public" / "ok.css")])

    def test_explicit_file_with_other_extension_is_scanned(self):
        path = self.write("styles.txt", self.BAD)
        code, files = self.files_flagged(path)
        self.assertEqual(code, 1)
        self.assertEqual(files, [str(path)])

    def test_text_output_is_sorted_by_path_then_line(self):
        b = self.write("b.css", "p {}\n" + self.BAD + self.BAD)
        a = self.write("a.css", self.BAD)
        _, out, _ = self.run_cli(b, a)
        locations = [line.split("  ")[0] for line in out.splitlines()[:-1]]
        self.assertEqual(locations, [f"{a}:1", f"{b}:2", f"{b}:3"])


class JustifiedTextTests(DetectTestCase):
    def test_flags_css_and_tailwind(self):
        self.assertFlags("justified-text", "p { text-align: justify; }", "a.css")
        self.assertFlags("justified-text", '<p class="mt-2 text-justify">x</p>')

    def test_ignores_other_alignment_and_text_justify_property(self):
        self.assertNotFlags("justified-text", "p { text-align: left; }", "a.css")
        self.assertNotFlags(
            "justified-text", "p { text-justify: inter-word; }", "a.css"
        )


class TransitionAllTests(DetectTestCase):
    def test_flags_css_and_tailwind(self):
        self.assertFlags("transition-all", "a { transition: all 0.3s ease; }", "a.css")
        self.assertFlags("transition-all", "a { transition-property: all; }", "a.css")
        self.assertFlags("transition-all", '<a class="transition-all duration-200">')
        self.assertFlags("transition-all", '<a style="transition: all .2s">x</a>')

    def test_ignores_named_properties(self):
        self.assertNotFlags(
            "transition-all", "a { transition: opacity 0.3s; }", "a.css"
        )
        self.assertNotFlags("transition-all", '<a class="transition-colors">x</a>')
        self.assertNotFlags("transition-all", "<p>Transition: all teams moved</p>")


class LayoutTransitionTests(DetectTestCase):
    def test_flags_layout_properties(self):
        for value in (
            "width 0.3s",
            "height .2s ease-out",
            "opacity 1s, top 1s",
            "margin-left 200ms",
            "padding 1s cubic-bezier(0.4, 0, 0.2, 1)",
        ):
            self.assertFlags(
                "layout-transition", f"a {{ transition: {value}; }}", "a.css"
            )
        self.assertFlags(
            "layout-transition", "a { transition-property: left, opacity; }", "a.css"
        )

    def test_ignores_compositor_properties_and_lookalikes(self):
        for value in (
            "opacity 0.3s",
            "transform .2s ease-in-out",
            "all 1s",
            "max-height 1s",
        ):
            self.assertNotFlags(
                "layout-transition", f"a {{ transition: {value}; }}", "a.css"
            )
        self.assertNotFlags(
            "layout-transition",
            '<a style="transition: opacity 1s" class="top-0 left-0">',
        )


class ArbitraryZIndexTests(DetectTestCase):
    def test_flags_large_values(self):
        self.assertFlags("arbitrary-z-index", ".m { z-index: 999; }", "a.css")
        self.assertFlags(
            "arbitrary-z-index", ".m { z-index: 99999 !important; }", "a.css"
        )
        self.assertFlags("arbitrary-z-index", '<div class="fixed z-[9999]">')

    def test_ignores_scale_values(self):
        self.assertNotFlags("arbitrary-z-index", ".m { z-index: 998; }", "a.css")
        self.assertNotFlags("arbitrary-z-index", ".m { z-index: 50; }", "a.css")
        self.assertNotFlags("arbitrary-z-index", '<div class="z-50 z-[100]">')


class TinyTextTests(DetectTestCase):
    def test_flags_sizes_below_12px(self):
        self.assertFlags("tiny-text", "small { font-size: 11px; }", "a.css")
        self.assertFlags("tiny-text", "small { font-size: 0.7rem; }", "a.css")
        self.assertFlags("tiny-text", '<span class="text-[10px]">x</span>')
        self.assertFlags("tiny-text", '<span class="text-[11.5px]">x</span>')

    def test_ignores_12px_and_up(self):
        self.assertNotFlags("tiny-text", "small { font-size: 12px; }", "a.css")
        self.assertNotFlags("tiny-text", "small { font-size: 0.75rem; }", "a.css")
        self.assertNotFlags("tiny-text", "small { font-size: 0.8em; }", "a.css")
        self.assertNotFlags("tiny-text", '<span class="text-xs text-[12px]">x</span>')


class ExtremeTrackingTests(DetectTestCase):
    def test_flags_tracking_tighter_than_minus_004em(self):
        self.assertFlags("extreme-tracking", "h1 { letter-spacing: -0.05em; }", "a.css")
        self.assertFlags("extreme-tracking", "h1 { letter-spacing: -.06em; }", "a.css")
        self.assertFlags("extreme-tracking", '<h1 class="tracking-tighter">x</h1>')
        self.assertFlags("extreme-tracking", '<h1 class="tracking-[-0.05em]">x</h1>')
        self.assertFlags("extreme-tracking", '<h1 class="tracking-[-0.08em]">x</h1>')

    def test_ignores_moderate_tracking(self):
        for value in ("-0.02em", "-0.04em", "0.1em", "normal"):
            self.assertNotFlags(
                "extreme-tracking", f"h1 {{ letter-spacing: {value}; }}", "a.css"
            )
        self.assertNotFlags("extreme-tracking", '<h1 class="tracking-tight">x</h1>')
        self.assertNotFlags("extreme-tracking", '<h1 class="tracking-[-0.04em]">x</h1>')


class GlassDefaultTests(DetectTestCase):
    def test_flags_backdrop_blur(self):
        css = ".card {\n  -webkit-backdrop-filter: blur(10px);\n  backdrop-filter: blur(10px);\n}"
        self.assertFlags("glass-default", css, "a.css", lines=[2, 3])
        self.assertFlags("glass-default", '<div class="backdrop-blur">x</div>')
        self.assertFlags("glass-default", '<div class="md:backdrop-blur-md">x</div>')

    def test_ignores_other_filters_and_no_blur(self):
        self.assertNotFlags(
            "glass-default", ".c { backdrop-filter: saturate(2); }", "a.css"
        )
        self.assertNotFlags(
            "glass-default", ".c { backdrop-filter: blur(0); }", "a.css"
        )
        self.assertNotFlags("glass-default", ".c { filter: blur(4px); }", "a.css")
        self.assertNotFlags("glass-default", '<div class="backdrop-blur-none blur-sm">')


class StripesBackgroundTests(DetectTestCase):
    def test_flags_repeating_gradients(self):
        css = ".s { background: repeating-linear-gradient(45deg, #000 0 2px, #fff 0 8px); }"
        self.assertFlags("stripes-background", css, "a.css")
        self.assertFlags(
            "stripes-background",
            '<div style="background-image: repeating-radial-gradient(circle, red, blue 10%)">',
        )
        self.assertFlags(
            "stripes-background",
            '<div class="bg-[repeating-linear-gradient(45deg,red_0_2px,blue_0_8px)]">',
        )

    def test_ignores_plain_gradients(self):
        css = ".s { background: linear-gradient(45deg, red, blue); }"
        self.assertNotFlags("stripes-background", css, "a.css")


class CreamTokensTests(DetectTestCase):
    def test_flags_cream_token_definitions(self):
        for name in (
            "--cream", "--paper", "--sand", "--bone", "--flour", "--linen",
            "--parchment", "--wheat", "--biscuit", "--ivory",
            "--color-cream", "--paper-2", "--bg-ivory-light",
        ):  # fmt: skip
            self.assertFlags("cream-tokens", f":root {{ {name}: #f5f0e6; }}", "a.css")

    def test_ignores_usages_and_lookalike_names(self):
        self.assertNotFlags("cream-tokens", ".a { color: var(--cream); }", "a.css")
        for name in ("--sandbox", "--thousand", "--background", "--paperclip"):
            self.assertNotFlags("cream-tokens", f":root {{ {name}: #fff; }}", "a.css")


class PositiveTabindexTests(DetectTestCase):
    def test_flags_positive_values(self):
        self.assertFlags("positive-tabindex", '<div tabindex="1">x</div>')
        self.assertFlags("positive-tabindex", "<div tabindex='3'>x</div>")
        self.assertFlags("positive-tabindex", "<div tabIndex={2}>x</div>", "a.jsx")
        self.assertFlags("positive-tabindex", '<div :tabindex="5">x</div>', "a.vue")

    def test_ignores_zero_and_negative(self):
        self.assertNotFlags("positive-tabindex", '<div tabindex="0">x</div>')
        self.assertNotFlags("positive-tabindex", '<div tabindex="-1">x</div>')
        self.assertNotFlags("positive-tabindex", "<div tabIndex={-1}>x</div>", "a.jsx")


class ZoomDisabledTests(DetectTestCase):
    def test_flags_disabled_zoom(self):
        for content in (
            "width=device-width, user-scalable=no",
            "width=device-width, user-scalable=0",
            "width=device-width, initial-scale=1, maximum-scale=1",
            "width=device-width, maximum-scale=1.0",
        ):
            html = f'<meta name="viewport" content="{content}">'
            self.assertFlags("zoom-disabled", html)
        multi = '<head>\n<meta\n  content="maximum-scale=1"\n  name="viewport"\n/>'
        self.assertFlags("zoom-disabled", multi, lines=[2])

    def test_ignores_zoomable_viewports(self):
        for content in (
            "width=device-width, initial-scale=1",
            "width=device-width, maximum-scale=5",
            "width=device-width, maximum-scale=1.5",
            "width=device-width, user-scalable=yes",
        ):
            html = f'<meta name="viewport" content="{content}">'
            self.assertNotFlags("zoom-disabled", html)


class BounceEasingTests(DetectTestCase):
    def test_flags_overshoot_curves_and_bounce_animations(self):
        for css in (
            ".a { transition: transform .3s cubic-bezier(0.68, -0.55, 0.27, 1.55); }",
            ".a { transition-timing-function: cubic-bezier(.34,1.56,.64,1); }",
            ".a { animation: bounceIn 1s; }",
            ".a { animation-name: elastic-pop; }",
        ):
            self.assertFlags("bounce-easing", css, "a.css")
        self.assertFlags("bounce-easing", '<span class="animate-bounce">x</span>')
        self.assertFlags(
            "bounce-easing",
            '<a class="ease-[cubic-bezier(0.68,-0.55,0.27,1.55)]">x</a>',
        )

    def test_ignores_standard_curves_and_other_animations(self):
        for css in (
            ".a { transition: opacity .2s cubic-bezier(0.4, 0, 0.2, 1); }",
            ".a { transition: opacity .2s cubic-bezier(0, 0, 1, 1); }",
            ".a { animation: fade-in 1s ease-out; }",
        ):
            self.assertNotFlags("bounce-easing", css, "a.css")
        self.assertNotFlags("bounce-easing", '<span class="animate-spin">x</span>')


class OutlineRemovedTests(DetectTestCase):
    def test_flags_every_occurrence_without_focus_replacement(self):
        css = "a { outline: none; }\nbutton:focus {\n  outline: 0;\n}\n"
        self.assertFlags("outline-removed", css, "a.css", lines=[1, 3])
        self.assertFlags("outline-removed", '<input class="outline-none">')
        self.assertFlags("outline-removed", '<input class="focus:outline-none">')

    def test_ignores_files_with_a_focus_visible_replacement(self):
        for extra in (
            "a:focus-visible { outline: 2px solid blue; }",
            '<a class="focus-visible:ring-2">',
            '<a class="focus:ring-2">',
            '<a class="focus:outline-2 focus:outline-blue-500">',
        ):
            text = "a { outline: none; }\n" + extra
            self.assertNotFlags("outline-removed", text, "a.vue")

    def test_focus_outline_none_is_not_a_replacement(self):
        text = '<input class="outline-none focus:outline-none">'
        self.assertFlags("outline-removed", text)

    def test_ignores_visible_outlines(self):
        self.assertNotFlags("outline-removed", "a { outline: 2px solid; }", "a.css")
        self.assertNotFlags("outline-removed", "a { outline: 0.2rem solid; }", "a.css")
        self.assertNotFlags("outline-removed", "a { outline-offset: 0; }", "a.css")


class SideStripeBorderTests(DetectTestCase):
    def test_flags_thick_colored_side_borders(self):
        for decl in (
            "border-left: 4px solid #3b82f6",
            "border-right: 2px solid var(--accent)",
            "border-inline-start: 0.25rem solid rgb(59, 130, 246)",
            "border-inline-end: 3px dashed hsl(220, 90%, 50%)",
            "border-left-width: 3px",
            "border-inline-start-width: 0.125rem",
        ):
            self.assertFlags("side-stripe-border", f".c {{ {decl}; }}", "a.css")
        for cls in (
            "border-l-4",
            "border-r-2",
            "border-s-8",
            "border-e-2",
            "border-l-[3px]",
        ):
            self.assertFlags(
                "side-stripe-border", f'<div class="{cls} border-blue-500">'
            )

    def test_ignores_thin_neutral_or_absent_borders(self):
        for decl in (
            "border-left: 1px solid red",
            "border-left: 0",
            "border-left: none",
            "border-left: 4px solid #e5e7eb",
            "border-left: 4px solid #ccc",
            "border-right: 3px solid rgba(0, 0, 0, 0.1)",
            "border-left: 2px solid transparent",
            "border-left: 2px solid gray",
            "border-left: 4px solid",
            "border-left: 4px solid var(--border)",
            "border-left-width: 1px",
            "border-left: 0.0625rem solid red",
            "border-top: 4px solid red",
        ):
            self.assertNotFlags("side-stripe-border", f".c {{ {decl}; }}", "a.css")
        for cls in (
            "border-l",
            "border-l-0",
            "border-r-[1px]",
            "border-x-4",
            "border-t-4",
        ):
            self.assertNotFlags("side-stripe-border", f'<div class="{cls}">')


class HardOffsetShadowTests(DetectTestCase):
    def test_flags_zero_blur_offset_shadows(self):
        for value in (
            "4px 4px 0 #000",
            "4px 4px 0px black",
            "-3px 0 0 rgba(0, 0, 0, 1)",
            "0 6px 0 0 var(--ink)",
            "8px 8px #111",
            "4px 4px 0 #000, 0 1px 2px rgba(0,0,0,.1)",
        ):
            self.assertFlags(
                "hard-offset-shadow", f".c {{ box-shadow: {value}; }}", "a.css"
            )
        self.assertFlags("hard-offset-shadow", '<div class="shadow-[4px_4px_0_#000]">')
        self.assertFlags(
            "hard-offset-shadow", '<div class="shadow-[4px_4px_0px_0px_black]">'
        )

    def test_ignores_rings_blurred_and_layered_soft_shadows(self):
        for value in (
            "0 0 0 1px #e5e7eb",
            "0 0 0 2px var(--ring)",
            "4px 4px 8px #000",
            "0 1px 2px rgba(0, 0, 0, 0.05)",
            "0 1px 2px rgba(0,0,0,.1), 4px 4px 0 #000",
            "none",
            "var(--shadow-md)",
        ):
            self.assertNotFlags(
                "hard-offset-shadow", f".c {{ box-shadow: {value}; }}", "a.css"
            )
        self.assertNotFlags(
            "hard-offset-shadow", '<div class="shadow-[0_0_0_1px_#000]">'
        )
        self.assertNotFlags(
            "hard-offset-shadow", '<div class="shadow-[0_4px_12px_#000]">'
        )


class GlowHaloTests(DetectTestCase):
    def test_flags_colored_centered_glows(self):
        for value in (
            "0 0 20px rgba(99, 102, 241, 0.6)",
            "0 0 8px #3b82f6",
            "0 0 1rem 4px hsl(260, 80%, 60%)",
            "0 1px 2px rgba(0,0,0,.1), 0 0 30px var(--accent)",
        ):
            self.assertFlags("glow-halo", f".c {{ box-shadow: {value}; }}", "a.css")
        self.assertFlags(
            "glow-halo", '<div class="shadow-[0_0_20px_rgba(99,102,241,0.5)]">'
        )

    def test_ignores_neutral_small_or_offset_shadows(self):
        for value in (
            "0 0 20px rgba(0, 0, 0, 0.3)",
            "0 0 20px #000",
            "0 0 20px black",
            "0 0 12px hsl(0, 0%, 50%)",
            "0 0 6px #3b82f6",
            "0 4px 20px #3b82f6",
            "0 0 0 3px #3b82f6",
            "0 0 20px",
        ):
            self.assertNotFlags("glow-halo", f".c {{ box-shadow: {value}; }}", "a.css")
        self.assertNotFlags(
            "glow-halo", '<div class="shadow-[0_0_20px_rgba(0,0,0,0.2)]">'
        )


class GradientTextTests(DetectTestCase):
    def test_flags_css_gradient_text(self):
        css = (
            ".title {\n"
            "  background: linear-gradient(90deg, #6366f1, #ec4899);\n"
            "  -webkit-background-clip: text;\n"
            "  background-clip: text;\n"
            "  color: transparent;\n"
            "}\n"
        )
        self.assertFlags("gradient-text", css, "a.scss", lines=[3])
        inline = (
            '<h1 style="background-image: radial-gradient(red, blue); '
            'background-clip: text">x</h1>'
        )
        self.assertFlags("gradient-text", inline)

    def test_flags_tailwind_gradient_text(self):
        for gradient in (
            "bg-gradient-to-r",
            "bg-linear-to-r",
            "bg-radial",
            "bg-conic-180",
        ):
            html = f'<h1 class="{gradient} from-pink-500 to-violet-500 bg-clip-text">'
            self.assertFlags("gradient-text", html)
        jsx = '<h1 className="bg-clip-text text-transparent bg-gradient-to-br">x</h1>'
        self.assertFlags("gradient-text", jsx, "a.tsx")

    def test_ignores_clip_text_without_gradient_and_gradient_without_clip(self):
        css = ".a { background: url(x.png); background-clip: text; }\n"
        css += ".b { background: linear-gradient(red, blue); }\n"
        css += ".c { background-clip: text; }\n.d { background: linear-gradient(red, blue); }\n"
        self.assertNotFlags("gradient-text", css, "a.css")
        self.assertNotFlags("gradient-text", '<h1 class="bg-clip-text bg-blue-500">')
        self.assertNotFlags(
            "gradient-text", '<div class="bg-gradient-to-r from-a to-b">'
        )
        self.assertNotFlags(
            "gradient-text",
            '<h1 class="bg-clip-text">x</h1>\n<div class="bg-gradient-to-r">y</div>',
        )


class EyebrowKickerTests(DetectTestCase):
    def test_flags_tailwind_eyebrow(self):
        for classes in (
            "text-xs uppercase tracking-widest text-indigo-600",
            "text-sm font-semibold uppercase tracking-wide",
            "uppercase tracking-[0.2em] text-[11px]",
            "md:text-sm uppercase tracking-wider",
        ):
            self.assertFlags("eyebrow-kicker", f'<p class="{classes}">Features</p>')
        self.assertFlags(
            "eyebrow-kicker",
            '<p className="uppercase tracking-wider text-xs">',
            "a.jsx",
        )
        self.assertFlags(
            "eyebrow-kicker",
            "<p :class=\"'uppercase tracking-wide text-xs'\">",
            "a.vue",
        )

    def test_flags_css_eyebrow(self):
        css = (
            ".kicker {\n  font-size: 12px;\n  text-transform: uppercase;\n"
            "  letter-spacing: 0.1em;\n}\n"
        )
        self.assertFlags("eyebrow-kicker", css, "a.css", lines=[3])
        css = ".k { text-transform: uppercase; letter-spacing: 2px; font-size: 0.875rem; }"
        self.assertFlags("eyebrow-kicker", css, "a.css")

    def test_ignores_partial_combinations(self):
        for classes in (
            "text-xs uppercase",
            "text-xs tracking-widest",
            "uppercase tracking-widest text-lg",
            "uppercase tracking-tight text-xs",
            "uppercase tracking-[0.05em] text-xs",
            "uppercase tracking-wide text-[16px]",
        ):
            self.assertNotFlags("eyebrow-kicker", f'<p class="{classes}">x</p>')
        self.assertNotFlags(
            "eyebrow-kicker",
            '<p class="uppercase tracking-wide">a</p><span class="text-xs">b</span>',
        )
        for css in (
            ".k { text-transform: uppercase; letter-spacing: 0.05em; font-size: 12px; }",
            ".k { text-transform: uppercase; letter-spacing: 0.1em; font-size: 16px; }",
            ".k { text-transform: uppercase; letter-spacing: 0.1em; }",
            ".k { letter-spacing: 0.1em; font-size: 12px; }",
        ):
            self.assertNotFlags("eyebrow-kicker", css, "a.css")


class ReflexFontTests(DetectTestCase):
    def test_flags_reflex_fonts_in_declarations_links_imports_and_classes(self):
        for css in (
            'h1 { font-family: "Playfair Display", serif; }',
            "body { font-family: 'DM Sans', sans-serif; }",
            "body { font: 16px/1.5 Inter, 'Space Grotesk'; }",
            "@theme { --font-display: 'Fraunces', serif; }",
            "@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans&display=swap');",
        ):
            self.assertFlags("reflex-font", css, "a.css")
        link = (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Plus+Jakarta+Sans:wght@400;700" rel="stylesheet">'
        )
        self.assertFlags("reflex-font", link)
        self.assertFlags("reflex-font", "<h1 class=\"font-['Instrument_Sans']\">x</h1>")
        self.assertFlags("reflex-font", "body { font-family: 'crimson pro'; }", "a.css")

    def test_ignores_other_fonts_and_names_outside_font_contexts(self):
        for css in (
            "body { font-family: Inter, system-ui, sans-serif; }",
            "body { font-family: 'Loraine Sans'; }",
            ".outfit-card { color: red; }",
        ):
            self.assertNotFlags("reflex-font", css, "a.css")
        self.assertNotFlags("reflex-font", "<p>We love Playfair Display and Lora.</p>")


class ImgMissingAltTests(DetectTestCase):
    def test_flags_img_without_alt(self):
        self.assertFlags("img-missing-alt", '<img src="alt.png" width="1" height="1">')
        self.assertFlags(
            "img-missing-alt", '<img src="a.png" data-alt="x" title="alt">'
        )
        self.assertFlags(
            "img-missing-alt",
            "<p>x</p>\n<img\n  src={logo}\n  onLoad={() => setReady(true)}\n/>",
            "a.jsx",
            lines=[2],
        )

    def test_accepts_alt_in_all_forms(self):
        for tag in (
            '<img src="a.png" alt="">',
            '<img src="a.png" alt="Team photo">',
            '<img src="a.png" :alt="photo.caption">',
            '<img src="a.png" v-bind:alt="caption">',
            "<img src={a} alt={caption} />",
            '<img\n  src="a.png"\n  alt="Multi-line"\n>',
        ):
            self.assertNotFlags("img-missing-alt", tag, "a.vue")

    def test_skips_tags_with_spread_or_template_attributes(self):
        self.assertNotFlags("img-missing-alt", "<img {...props} />", "a.tsx")
        self.assertNotFlags(
            "img-missing-alt", '<img src="a.png" {{ $attributes }}>', "a.blade.php"
        )

    def test_ignores_components_named_like_img(self):
        self.assertNotFlags("img-missing-alt", '<Img src="a.png" />', "a.jsx")
        self.assertNotFlags("img-missing-alt", '<image href="a.png" />', "a.svelte")


class ImgMissingDimensionsTests(DetectTestCase):
    def test_flags_img_without_width_and_height(self):
        for tag in (
            '<img src="a.png" alt="">',
            '<img src="a.png" alt="" width="40">',
            '<img src="a.png" alt="" style="width: 40px; height: 40px">',
            '<img src="a.png" alt="" data-width="40" data-height="40">',
        ):
            self.assertFlags("img-missing-dimensions", tag)
        multi = (
            '<div>\n  <img\n    src="a.png"\n    alt=""\n    height="20"\n  >\n</div>'
        )
        self.assertFlags("img-missing-dimensions", multi, lines=[2])

    def test_accepts_plain_and_bound_dimensions(self):
        for tag in (
            '<img src="a.png" alt="" width="40" height="40">',
            '<img src="a.png" alt="" :width="w" :height="h">',
            "<img src={a} alt='' width={40} height={40} />",
            '<img\n  src="a.png"\n  alt=""\n  width="40"\n  height="40"\n/>',
        ):
            self.assertNotFlags("img-missing-dimensions", tag, "a.vue")


class ClickableDivTests(DetectTestCase):
    def test_flags_click_handlers_on_div_and_span(self):
        for tag, name in (
            ('<div onclick="go()">x</div>', "a.html"),
            ('<span @click="open = !open">x</span>', "a.vue"),
            ('<div v-on:click="go">x</div>', "a.vue"),
            ("<div onClick={() => setOpen(true)}>x</div>", "a.tsx"),
            ('<div wire:click="save">x</div>', "a.blade.php"),
            ('<div x-on:click="open = true">x</div>', "a.html"),
            ("<div on:click={toggle}>x</div>", "a.svelte"),
            ('<div @click.prevent="go">x</div>', "a.vue"),
        ):
            self.assertFlags("clickable-div", tag, name)
        multi = '<ul>\n<div\n  class="card"\n  @click="select(item)"\n>'
        self.assertFlags("clickable-div", multi, "a.vue", lines=[2])

    def test_accepts_role_or_tabindex_and_other_elements(self):
        for tag in (
            '<div role="button" onclick="go()">x</div>',
            '<div tabindex="0" @click="go">x</div>',
            "<div onClick={go} role='button' tabIndex={0}>x</div>",
            '<button onclick="go()">x</button>',
            '<div class="onclick-target" data-onclick="x">x</div>',
            '<divider onclick="go()">x</divider>',
        ):
            self.assertNotFlags("clickable-div", tag, "a.vue")


class EmojiIconTests(DetectTestCase):
    def test_flags_emoji_text_in_buttons_and_links(self):
        self.assertFlags("emoji-icon", '<button class="btn">\U0001f680 Launch</button>')
        self.assertFlags("emoji-icon", '<a href="/settings">\u2699 Settings</a>')
        self.assertFlags(
            "emoji-icon",
            "<button onClick={() => go()}>\n  <span>\U0001f525</span> Hot\n</button>",
            "a.tsx",
            lines=[2],
        )

    def test_ignores_emoji_outside_controls_or_in_attributes(self):
        self.assertNotFlags("emoji-icon", "<p>We \u2764 design \U0001f680</p>")
        self.assertNotFlags(
            "emoji-icon", '<button aria-label="\U0001f680">Launch</button>'
        )
        self.assertNotFlags(
            "emoji-icon", '<a href="/"><img src="a.png" alt="\U0001f680"> Home</a>'
        )
        self.assertNotFlags("emoji-icon", "<button>Next \u2192</button>")
        self.assertNotFlags(
            "emoji-icon", "<abbr>\U0001f680</abbr><article>\U0001f680</article>"
        )


class NumberedSectionLabelTests(DetectTestCase):
    def test_flags_standalone_section_numbers(self):
        for label in (
            "01",
            "02 /",
            "03 \u00b7",
            "04.",
            "05 \u2014",
            "06 - About",
            " 07 ",
        ):
            self.assertFlags(
                "numbered-section-label", f'<span class="label">{label}</span>'
            )
        html = '<section>\n  <p class="eyebrow">\n    01 / Services\n  </p>'
        self.assertFlags("numbered-section-label", html, lines=[3])

    def test_ignores_sentences_tables_lists_and_other_numbers(self):
        for html in (
            "<p>01 apples were picked today</p>",
            "<p>04. This is the start of a much longer sentence about the work.</p>",
            "<p>Call 01 23 45</p>",
            "<td>01</td>",
            "<li>02 - Setup</li>",
            "<table><tr><td><span>03</span></td></tr></table>",
            "<ol><li><span>04</span> Step</li></ol>",
            '<option value="01">01</option>',
            "<span>10</span><span>00</span><span>1</span>",
        ):
            self.assertNotFlags("numbered-section-label", html)

    def test_only_in_markup_files(self):
        css = '.a::before { content: "x"; }\n/* <span>01</span> */'
        self.assertNotFlags("numbered-section-label", css, "a.css")


class MarketingBuzzwordTests(DetectTestCase):
    PHRASES = (
        "streamline your", "empower your", "supercharge your", "unleash your",
        "unleash the power", "leverage the power", "harness the power",
        "built for the modern", "trusted by leading", "trusted by the world",
        "best-in-class", "industry-leading", "world-class", "enterprise-grade",
        "next-generation", "cutting-edge", "transform your business", "revolutionize",
        "game-changer", "game changing", "mission-critical", "best of breed",
        "future-proof", "future proof", "seamless experience", "seamlessly integrate",
        "drive engagement", "drive growth", "drive results",
    )  # fmt: skip

    def test_flags_every_phrase_in_visible_text(self):
        for phrase in self.PHRASES:
            self.assertFlags(
                "marketing-buzzword", f"<h1>We {phrase.upper()} teams</h1>"
            )

    def test_flags_phrases_wrapped_across_lines(self):
        html = "<p>\n  Supercharge\n  your workflow\n</p>"
        self.assertFlags("marketing-buzzword", html, "a.astro", lines=[2])

    def test_ignores_scripts_styles_comments_and_stylesheets(self):
        for html in (
            "<script>const s = 'best-in-class';</script>",
            "<style>/* world-class */ .a { color: red; }</style>",
            "<!-- industry-leading copy goes here -->",
            '<div class="cutting-edge-card">x</div>',
            "<p>We build tools for teams.</p>",
        ):
            self.assertNotFlags("marketing-buzzword", html)
        self.assertNotFlags(
            "marketing-buzzword", '.a::after { content: "world-class"; }', "a.css"
        )


if __name__ == "__main__":
    unittest.main()
