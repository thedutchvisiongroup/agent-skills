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

**Interactief linken** — kies eerst welke skills, dan welke harnesses. Het script detecteert aanwezige harnesses automatisch en pre-selecteert ze. Bestaande echte bestanden in de doelmap worden interactief afgehandeld (backup / overschrijven / skip):

```bash
uv run scripts/link.py link
```

**Non-interactive linken** — voor scripting of CI:

```bash
uv run scripts/link.py link --skills=excel-spreadsheets,writing-skills --harnesses=agents,claude
```

**Unlinken** — verwijdert eerder aangemaakte symlinks (geen echte bestanden):

```bash
uv run scripts/link.py unlink
uv run scripts/link.py unlink --skills=excel-spreadsheets --harnesses=agents
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

1. Ontdekt alle skills in `skills/` (elke map met een `SKILL.md`).
2. Detecteert geïnstalleerde harnesses op basis van hun config-mappen.
3. Per geselecteerde (skill, harness): controleert de doel-locatie.
4. Bij een conflict (echte map/bestand) vraagt het interactief om backup, overschrijven of skip — backups krijgen de suffix `.bak-<timestamp>`.
5. Maakt de symlink aan en houdt de link bij in `scripts/.link-state.json`.
