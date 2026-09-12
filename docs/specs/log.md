# Directory Update Log

## 2026-09-11
* **OKF v0.2 migration**: Migrated the bundle to OKF v0.2 — this index now declares `okf_version: "0.2"` and the concept frontmatter in [opencode-model-router](opencode-model-router/) and [opencode-usage-tracking](opencode-usage-tracking/) replaces legacy `timestamp` with `generated` (values preserved as `generated.at`; actor `opencode/glm-5.3-flash` as house default, original authoring agents unknown) plus `status`, with only truthful `sources` entries added.
* **Migration**: Migrated the bundle to per-directory scaffolding — [opencode-model-router](opencode-model-router/) and [opencode-usage-tracking](opencode-usage-tracking/) now carry their own `index.md` and `log.md`; nested references moved out of this directory's index and log (writing-okf same-level house rules).

## 2026-08-19
* **Initialization**: Created foundational directory structure.
