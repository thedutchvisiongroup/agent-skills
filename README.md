<p align="center">
  <img src="assets/img/logo-dutch-white.svg" alt="TDVG Logo" width="300" />
</p>

<p align="center">
   Deze repository bevat de gedeelde skills voor de AI-gestuurde ontwikkeling binnen The Dutch Vision Group.
</p>

## Installatie

Het script `scripts/link.py` symlinkt de skills uit `skills/` naar de globale skills-mappen van de ondersteunde agent harnesses. Omdat het symlinks zijn, blijft deze repo het enige source of truth — een wijziging aan een skill is direct zichtbaar in elke gelinkte harness.

### Ondersteunde harnesses

| Harness                | Global path                              | Leest `~/.agents/skills/`? |
| ---------------------- | ---------------------------------------- | :-----------------------: |
| Universal (`.agents`)  | `~/.agents/skills/`                      | — (is zelf het pad)      |
| OpenCode               | `~/.config/opencode/skills/`             | ✅                        |
| Zed                    | `~/.agents/skills/`                      | ✅                        |
| Codex CLI              | `~/.agents/skills/`                      | ✅                        |
| GitHub Copilot (VS Code) | `~/.copilot/skills/`                   | ✅                        |
| Cursor                 | `~/.cursor/skills/`                      | ✅                        |
| Gemini CLI             | `~/.gemini/skills/`                      | ✅                        |
| Claude Code            | `~/.claude/skills/`                      | ❌                        |
| Windsurf (Cascade)     | `~/.codeium/windsurf/skills/`            | ❌                        |
| Google Antigravity     | `~/.gemini/config/skills/`               | ❌                        |

Eén symlink naar `~/.agents/skills/` dekt zes harnesses; Claude Code, Windsurf en Antigravity hebben een eigen symlink nodig.

### Vereisten

- Python ≥ 3.14
- [uv](https://docs.astral.sh/uv/) (installeert automatisch dependencies bij de eerste run)

### Gebruik

**Status bekijken** — toont per (skill × harness) of er al een symlink staat:

```bash
uv run scripts/link.py status
```

**Interactief linken** — kies eerst welke skills, dan welke OpenCode-items, dan welke harnesses (alleen relevant voor skills). Het script detecteert aanwezige harnesses automatisch en pre-selecteert ze. Bestaande echte bestanden in de doelmap worden interactief afgehandeld (backup / overschrijven / skip):

```bash
uv run scripts/link.py link
```

**Non-interactive linken** — voor scripting of CI:

```bash
uv run scripts/link.py link --skills=excel-spreadsheets,writing-skills --harnesses=agents,claude
uv run scripts/link.py link --skip-skills --opencode=opencode/agents/code-reviewer.md,opencode/configs/tdvg-standards.json
```

Met `--skip-skills` of `--skip-opencode` beperk je een run tot één categorie.

**Unlinken** — verwijdert eerder aangemaakte symlinks (geen echte bestanden):

```bash
uv run scripts/link.py unlink
uv run scripts/link.py unlink --skills=excel-spreadsheets --harnesses=agents
uv run scripts/link.py unlink --opencode=opencode/configs/tdvg-required.json
```

**Overzicht van harnesses en skills in de repo:**

```bash
uv run scripts/link.py list
```

### Status tabel

| Symbool | Betekenis                               |
| ------- | --------------------------------------- |
| `✓`     | Symlink naar deze repo (correct)        |
| `·`     | Niets aanwezig                          |
| `↗`     | Symlink naar een andere locatie         |
| `✗`     | Broken symlink                          |
| `D`     | Echte map (wordt interactief afgehandeld) |
| `F`     | Echt bestand (wordt interactief afgehandeld) |
| `*`     | Trackt in `.link-state.json`           |

### Wat doet het script?

1. Ontdekt alle skills in `skills/` (elke map met een `SKILL.md`) én alle OpenCode-items in `opencode/` (zie hieronder).
2. Detecteert geïnstalleerde harnesses op basis van hun config-mappen.
3. Per geselecteerde skill × harness en per OpenCode-item: controleert de doel-locatie.
4. Bij een conflict (echte map/bestand) vraagt het interactief om backup, overschrijven of skip — backups krijgen de suffix `.bak-<timestamp>`.
5. Maakt de symlink aan en houdt de link bij in `scripts/.link-state.json`.
6. Items met een managed target (`/etc/opencode/`) vereisen root; zonder root worden ze netjes overgeslagen met een waarschuwing.

## OpenCode-configuratie

Naast skills synchroniseert de repo ook OpenCode-specifieke configuratie. De map `opencode/` wordt **per bestand** gesymlinkt naar `~/.config/opencode/` — met één uitzondering: de gereserveerde submap `opencode/configs/` wordt niet 1-op-1 gekopieerd, maar heeft een vaste doel-mapping.

### Drie-lagen config-model

OpenCode laadt en merget meerdere config-bestanden (later wint bij conflicten; niet-conflicterende keys blijven behouden). De repo gebruikt dat voor een drie-lagen-model:

| Laag | Repo-bron | Symlink-doel | Rol |
| ---- | --------- | ------------ | --- |
| TDVG-standards | `opencode/configs/tdvg-standards.json` | `~/.config/opencode/config.json` | Gedeelde defaults. Persoonlijke config mag dit overriden. |
| Persoonlijk | — (niet in repo) | `~/.config/opencode/opencode.jsonc` | **Wordt nooit door de sync aangeraakt.** Persoonlijke overwrites, aanvullingen, MCP-servers en secrets. |
| TDVG-required | `opencode/configs/tdvg-required.json` | `/etc/opencode/opencode.jsonc` | Managed laag (hoogste precedentie, deep-merge per key): afgedwongen, niet te overriden. Vereist root om te linken. |

> ⚠️ **`subagent_depth` vereist OpenCode ≥ 1.18.2** — Deze key is geïntroduceerd in 1.18.2; oudere versies weigeren te starten met een onbekende key. Voeg `"subagent_depth": 3` toe aan `tdvg-standards.json` zodra je geminimumde versie ≥ 1.18.2 is. Tot die tijd werkt de handoff-fallback in de agents (zie hieronder).

> ⚠️ **Nooit secrets committen** — API-keys, tokens en MCP-credentials horen uitsluitend thuis in je persoonlijke `~/.config/opencode/opencode.jsonc`, nooit in `opencode/configs/` of ergens anders in deze repo.

### Agents

De map `opencode/agents/` bevat custom agents (markdown met YAML-frontmatter; de body is de system prompt):

| Agent | Skill (verplicht) | Rol |
| ----- | ----------------- | --- |
| `code-reviewer` | `code-review` | Advisory-only code review (lint/types/format/tests, testkwaliteit, logica, design). Edit nooit code. Security-vermoedens → `security-reviewer`. |
| `security-reviewer` | `security-review` | Advisory-only security review (dataflow, 11 vulnerability classes, verplicht online onderzoek). Fixt nooit. Kwaliteitsissues → `code-reviewer`. |

Beide agents: `mode: all` (primary én subagent), `temperature: 0.1`, enige tool-restrictie is `edit: deny`. Hun system prompts zijn kort en delegeren alle methodiek aan de bijbehorende skill, die ze als eerste actie laden en stap voor stap volgen. Elke agent probeert de ander bij twijfel als subagent aan te roepen; lukt dat niet (bijv. `subagent_depth: 1` op OpenCode < 1.18.2), dan eindigt het rapport met een expliciete handoff-aanbeveling.

Na het linken van nieuwe/gewijzigde agent- of config-bestanden: **herstart OpenCode** — config wordt alleen bij opstarten geladen.

### Usage-tracking plugin

De plugin `opencode/plugins/usage-tracking/` legt real-time gebruik en kosten van elke OpenCode-sessie vast (modellen, tokens, kosten, tools, active time, subagents — recursief), als append-only event stream plus afgeleide sessie-aggregaten. Data landt standaard in `~/.local/share/opencode-usage/<hash>/` (per project een deterministische hash-submap met `events.jsonl`, `sessions/` en `overview.json`, buiten de werkrepo's); de hash is deterministisch per device+project en merge-safe over devices — er is geen register nodig. Er worden nooit berichtteksten, prompts of tool-output weggeschreven.

**Activeren** — de plugin laadt via auto-discovery met het platte entry-bestand `opencode/plugins/usage-tracking.ts` (OpenCode scant alleen bestanden direct in de plugins-map):

```bash
uv run scripts/link.py link --skip-skills --opencode=opencode/plugins/usage-tracking.ts,opencode/plugins/usage-tracking/,opencode/command/usage-status.md
```

…gevolgd door een **herstart van OpenCode** (plugins laden bij opstarten). Schrijfgezondheid en actuele sessietotallen zijn daarna in elke sessie op te vragen met het commando `/usage-status`.

**Verificatie** — statisch (offline):

```bash
devbox run -- scripts/smoke_usage_tracking.sh --check
```

Live smoke-test (provider-backed, draaien terwijl er geen andere OpenCode-sessies actief zijn):

```bash
devbox run -- scripts/smoke_usage_tracking.sh --run --model PROVIDER/MODEL
```

**Rollback** — `uv run scripts/link.py unlink` met dezelfde item-keys als hierboven, daarna OpenCode herstarten. Verzamelde data is afgeleid en disposabel; het event stream blijft bij als bron van herstel staan.
