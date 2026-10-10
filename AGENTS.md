# AGENTS.md

Context voor AI-agents die in deze repository werken.

## Wat is dit?

Gedeelde AI-agent-configuratie van The Dutch Vision Group. De repo is de enige
source of truth; alles wordt via **symlinks** naar de globale mappen van agent
harnesses gesynchroniseerd (Claude-configuratie in `claude/configs/` via een
JSON-merge), dus wijzigingen zijn direct zichtbaar in de gelinkte bestanden.
OpenCode laadt agent- en configuratiewijzigingen na een herstart; Claude Code
na een nieuwe sessie.

## Structuur

| Pad | Inhoud | Sync-doel |
| --- | ------ | --------- |
| `skills/<name>/SKILL.md` | Universele agent skills | `~/.agents/skills/`, `~/.claude/skills/`, `~/.codeium/windsurf/skills/`, `~/.gemini/config/skills/` |
| `opencode/agents/*.md` | OpenCode custom agents (frontmatter + body = system prompt) | `~/.config/opencode/agents/` (per bestand) |
| `opencode/configs/tdvg-standards.json` | Overschrijfbare TDVG-defaults | `~/.config/opencode/config.json` |
| `opencode/configs/tdvg-required.json` | Afgedwongen managed settings (`plan` en `general` uitgeschakeld; `compaction`/`summary`/`title` + `small_model` op `openrouter/z-ai/glm-5.3-flash`) | `/etc/opencode/opencode.jsonc` (root vereist) |
| `opencode/plugins/usage-tracking.ts` + `opencode/plugins/usage-tracking/*` | Usage-tracking plugin (real-time gebruik/kosten-telemetrie; het platte entry-bestand is vereist voor auto-discovery) | `~/.config/opencode/plugins/` (per bestand) |
| `opencode/command/usage-status.md` | `/usage-status` slash-commando (status van de usage-tracking plugin) | `~/.config/opencode/command/` (per bestand) |
| `opencode/<alles anders>` | Toekomstige OpenCode-content (themes, ...) | `~/.config/opencode/` 1-op-1 per bestand |
| `claude/CLAUDE.md` | Claude Code user-instructies | `~/.claude/CLAUDE.md` (symlink) |
| `claude/agents/*.md` | Claude Code subagents (frontmatter + body = system prompt) | `~/.claude/agents/` (per bestand) |
| `claude/hooks/tdvg-write-guard.py` | PreToolUse write guard voor reviewers/tdd-expert (`test_*.py` is repo-only) | `~/.claude/hooks/` (per bestand) |
| `claude/configs/tdvg-settings.json` | Claude Code permissies (ask/deny, TDVG-keys) | `~/.claude/settings.json` (JSON-merge) |
| `claude/configs/tdvg-mcp.json` | Claude Code MCP-servers (context7, deepwiki) | `~/.claude.json` → `mcpServers` (JSON-merge) |
| `scripts/link.py` | Het sync-script | — |

> Let op met versie-afhankelijke config-keys: OpenCode valideert streng en
> weigert te starten bij onbekende keys. Voorbeeld: `subagent_depth` bestaat
> pas sinds 1.18.2 — check `opencode debug config` na elke config-wijziging.

## Conventies

- **Skills**: elke skill is een map met een `SKILL.md` (YAML-frontmatter met
  `name` + `description`). Taal: Engels.
- **Agents**: markdown met YAML-frontmatter (`description`, `mode`,
  `temperature`, `color`, `permission`). De body is de system prompt in
  **XML-structuur** (zie skill `writing-prompts`), kort en delegerend aan een
  skill. Bestandsnaam = agent-naam. Taal: Engels. Claude-agents
  (`claude/agents/`) gebruiken andere frontmatter (`skills`, `model`, `effort`,
  `disallowedTools`); zie de README.
- **`opencode/configs/` is gereserveerd**: deze submap wordt NOOIT 1-op-1 naar
  `~/.config/opencode/` gekopieerd; elk bestand heeft een vaste mapping in
  `CONFIG_FILE_MAP` in `scripts/link.py`. Nieuwe config-bestanden vereisen dus
  een regel in die map.
- **`claude/configs/` is gereserveerd**: deze submap wordt NOOIT gesymlinkt;
  elk bestand wordt JSON-merged naar het doel uit `MERGE_FILE_MAP` in
  `scripts/link.py`. Nieuwe config-bestanden vereisen dus een regel in die map.
- **Persoonlijke laag is heilig**: `~/.config/opencode/opencode.jsonc` (en
  `plugins/`, `node_modules/`, `package*.json` aldaar) worden nooit door de
  sync aangeraakt. **Uitzondering (Claude Code):** `link.py` merget alleen de
  TDVG-keys uit `claude/configs/` additief in `~/.claude/settings.json` en
  `~/.claude.json` (backup, interactieve conflicten, omkeerbaar via `unlink`)
  en raakt verder niets in die bestanden aan.
- **Nooit secrets in de repo**: API-keys/tokens/MCP-credentials horen in de
  persoonlijke `opencode.jsonc`, nooit in `opencode/` of `skills/`.

## Werken met link.py

```bash
uv run scripts/link.py status   # status-tabellen (skills + OpenCode- + Claude-items)
uv run scripts/link.py link     # interactief linken
uv run scripts/link.py unlink   # getrackte symlinks verwijderen
uv run scripts/link.py list     # harnesses, skills en items tonen
```

- Vereist Python ≥ 3.14 + [uv](https://docs.astral.sh/uv/).
- Non-interactive: `--skills=`, `--harnesses=`, `--opencode=` en `--claude=`
  (CSV), `--skip-skills`, `--skip-opencode`, `--skip-claude`.
- Item-keys zijn repo-relatieve paden, bv.
  `opencode/agents/code-reviewer.md` of `opencode/configs/tdvg-standards.json`.
- State staat in `scripts/.link-state.json` (v3, gitignored). Alleen getrackte
  symlinks worden ge-unlinkt; echte bestanden worden nooit verwijderd. Claude-
  merges worden alleen teruggedraaid voor wat `link.py` zelf heeft toegevoegd
  of overschreven.
- Managed items (doel onder `/etc/`) vereisen root; zonder root skipt het
  script ze met een waarschuwing.

## Gedragsregels voor agents in deze repo

- Custom orchestrator blijft coordinator: alle implementaties/fixes gaan naar `implementer`, nooit naar uitgeschakelde `general`. Implementer bezit tests én broncode via Red–Green–Refactor, erft het model en start geen eigen subagents of automatische commits.
- In Claude Code is het hoofdgesprek de coordinator (de orchestrator is daar nog niet geporteerd); dezelfde regels gelden: implementatie via `implementer`, reviews onafhankelijk en achteraf.
- Iedere fase/batch met Definition of Done krijgt achteraf onafhankelijke code- en TDD-review, plus security waar relevant. Afhankelijke fases wachten op vereiste verdicts/opgeloste blockers. Nieuwe-test- en TDD-reviewuitzonderingen vereisen elk afzonderlijk vooraf expliciet akkoord en alternatieve checks.
- Gedelegeerde TDD-expert is advisory-only en wijzigt tests noch broncode; fixes gaan via coordinator naar implementer. Direct aangeroepen mag hij tests schrijven/verbeteren, nooit broncode. Geplande reviewstoelen worden niet dubbel genest gestart.
- Bewijshergebruik vereist passende scope, revisie/fingerprint, commando's/resultaten, versies en omgeving. Reviewers beoordelen zelfstandig; gaps/veroudering/twijfel vragen gerichte verificatie. Iedere agent levert zijn benoemde rapport in de goedgekeurde runmap.
- Wijzig nooit iets aan de persoonlijke laag van de gebruiker buiten deze repo, behalve de gedocumenteerde Claude-merge hierboven.
- Na het wijzigen van `scripts/link.py`: draai `uv run scripts/link.py status`
  en `uv run scripts/link.py list` ter verificatie.
- Na het wijzigen van agents/configs: valideer JSON en vermeld dat OpenCode
  herstart moet worden (config wordt alleen bij opstarten geladen). Voor Claude
  Code: vermeld dat een nieuwe sessie nodig is (CLAUDE.md, agents en settings
  worden bij sessiestart gelezen).
- Houd deze AGENTS.md en de README.md synchroon met structurele wijzigingen.
