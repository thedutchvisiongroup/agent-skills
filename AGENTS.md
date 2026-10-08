# AGENTS.md

Context voor AI-agents die in deze repository werken.

## Wat is dit?

Gedeelde AI-agent-configuratie van The Dutch Vision Group. De repo is de enige
source of truth; alles wordt via **symlinks** naar de globale mappen van agent
harnesses gesynchroniseerd, dus wijzigingen zijn direct zichtbaar in de gelinkte
bestanden. OpenCode laadt agent- en configuratiewijzigingen na een herstart.

## Structuur

| Pad | Inhoud | Sync-doel |
| --- | ------ | --------- |
| `skills/<name>/SKILL.md` | Universele agent skills | `~/.agents/skills/`, `~/.claude/skills/`, `~/.codeium/windsurf/skills/`, `~/.gemini/config/skills/` |
| `opencode/agents/*.md` | OpenCode custom agents (frontmatter + body = system prompt) | `~/.config/opencode/agents/` (per bestand) |
| `opencode/configs/tdvg-standards.json` | Overschrijfbare TDVG-defaults | `~/.config/opencode/config.json` |
| `opencode/configs/tdvg-required.json` | Afgedwongen managed settings (`plan` en `general` uitgeschakeld; `compaction`/`summary`/`title` + `small_model` op `openrouter/z-ai/glm-5.3-flash`) | `/etc/opencode/opencode.jsonc` (root vereist) |
| `opencode/plugins/usage-tracking.ts` + `opencode/plugins/usage-tracking/*` | Usage-tracking plugin (real-time gebruik/kosten-telemetrie; het platte entry-bestand is vereist voor auto-discovery) | `~/.config/opencode/plugins/` (per bestand) |
| `opencode/command/usage-status.md` | `/usage-status` slash-commando (status van de usage-tracking plugin) | `~/.config/opencode/command/` (per bestand) |

> Let op met versie-afhankelijke config-keys: OpenCode valideert streng en
> weigert te starten bij onbekende keys. Voorbeeld: `subagent_depth` bestaat
> pas sinds 1.18.2 — check `opencode debug config` na elke config-wijziging.
| `opencode/<alles anders>` | Toekomstige OpenCode-content (themes, ...) | `~/.config/opencode/` 1-op-1 per bestand |
| `scripts/link.py` | Het sync-script | — |

## Conventies

- **Skills**: elke skill is een map met een `SKILL.md` (YAML-frontmatter met
  `name` + `description`). Taal: Engels.
- **Agents**: markdown met YAML-frontmatter (`description`, `mode`,
  `temperature`, `color`, `permission`). De body is de system prompt in
  **XML-structuur** (zie skill `writing-prompts`), kort en delegerend aan een
  skill. Bestandsnaam = agent-naam. Taal: Engels.
- **`opencode/configs/` is gereserveerd**: deze submap wordt NOOIT 1-op-1 naar
  `~/.config/opencode/` gekopieerd; elk bestand heeft een vaste mapping in
  `CONFIG_FILE_MAP` in `scripts/link.py`. Nieuwe config-bestanden vereisen dus
  een regel in die map.
- **Persoonlijke laag is heilig**: `~/.config/opencode/opencode.jsonc` (en
  `plugins/`, `node_modules/`, `package*.json` aldaar) worden nooit door de
  sync aangeraakt.
- **Nooit secrets in de repo**: API-keys/tokens/MCP-credentials horen in de
  persoonlijke `opencode.jsonc`, nooit in `opencode/` of `skills/`.

## Werken met link.py

```bash
uv run scripts/link.py status   # status-tabellen (skills + OpenCode-items)
uv run scripts/link.py link     # interactief linken
uv run scripts/link.py unlink   # getrackte symlinks verwijderen
uv run scripts/link.py list     # harnesses, skills en items tonen
```

- Vereist Python ≥ 3.14 + [uv](https://docs.astral.sh/uv/).
- Non-interactive: `--skills=`, `--harnesses=`, `--opencode=` (CSV),
  `--skip-skills`, `--skip-opencode`.
- Item-keys zijn repo-relatieve paden, bv.
  `opencode/agents/code-reviewer.md` of `opencode/configs/tdvg-standards.json`.
- State staat in `scripts/.link-state.json` (v2, gitignored). Alleen getrackte
  symlinks worden ge-unlinkt; echte bestanden worden nooit verwijderd.
- Managed items (doel onder `/etc/`) vereisen root; zonder root skipt het
  script ze met een waarschuwing.

## Gedragsregels voor agents in deze repo

- Custom orchestrator blijft coordinator: alle implementaties/fixes gaan naar `implementer`, nooit naar uitgeschakelde `general`. Implementer bezit tests én broncode via Red–Green–Refactor, erft het model en start geen eigen subagents of automatische commits.
- Iedere fase/batch met Definition of Done krijgt achteraf onafhankelijke code- en TDD-review, plus security waar relevant. Afhankelijke fases wachten op vereiste verdicts/opgeloste blockers. Nieuwe-test- en TDD-reviewuitzonderingen vereisen elk afzonderlijk vooraf expliciet akkoord en alternatieve checks.
- Gedelegeerde TDD-expert is advisory-only en wijzigt tests noch broncode; fixes gaan via coordinator naar implementer. Direct aangeroepen mag hij tests schrijven/verbeteren, nooit broncode. Geplande reviewstoelen worden niet dubbel genest gestart.
- Bewijshergebruik vereist passende scope, revisie/fingerprint, commando's/resultaten, versies en omgeving. Reviewers beoordelen zelfstandig; gaps/veroudering/twijfel vragen gerichte verificatie. Iedere agent levert zijn benoemde rapport in de goedgekeurde runmap.
- Wijzig nooit iets aan de persoonlijke laag van de gebruiker buiten deze repo.
- Na het wijzigen van `scripts/link.py`: draai `uv run scripts/link.py status`
  en `uv run scripts/link.py list` ter verificatie.
- Na het wijzigen van agents/configs: valideer JSON en vermeld dat OpenCode
  herstart moet worden (config wordt alleen bij opstarten geladen).
- Houd deze AGENTS.md en de README.md synchroon met structurele wijzigingen.
