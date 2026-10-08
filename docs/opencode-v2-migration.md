# Migratiestappenplan: OpenCode v1 → v2

**Eigenaar:** Thim / The Dutch Vision Group (TDVG)  
**Onderzoeksdatum:** 7 oktober 2026  
**Uitgangspunt:** OpenCode 1.18.34 en de huidige `skills/`, `opencode/` en `scripts/link.py`  
**Onderzoeksbaseline v2:** versie 2.0.24; waar relevant ook 2.0.23  
**Status:** plan; de migratie en praktijkchecks zijn nog niet uitgevoerd.

Een checkbox wordt pas afgevinkt nadat de beschreven wijziging én de relevante
verificatie zijn uitgevoerd. Bevestigde keuzes hieronder zijn uitgangspunten,
geen bewijs dat een migratieonderdeel al gereed is.

## 1. Doel, scope en bevestigde keuzes

Migreren naar een native OpenCode-v2-setup die de bestaande TDVG-werkwijze
behoudt, met expliciet geaccepteerde verschillen. De implementatie gebeurt op
een aparte branch, wordt eerst lokaal getest en wordt daarna naar de
TDVG-developmentmachines op Linux en macOS uitgerold.

| Onderwerp | Bevestigde keuze |
| --- | --- |
| Aanpak | Directe migratie op een aparte branch; lokaal verifiëren vóór rollout |
| Ondersteuning | Eindsetup is v2; geen structurele dubbele v1/v2-ondersteuning |
| Interfaces | Linux/macOS CLI; de normale terminalinterface |
| Versiebeleid | Bij uitvoering actuele v2 gebruiken; `update: notify`, geen automatische upgrades |
| Configuratie | Gedeelde configuratie en agent-frontmatter naar native v2 |
| TDVG-instellingen | Gedeelde defaults volstaan; managed afdwinging vervalt bewust |
| Agents | Orchestrator, implementer, code-reviewer, security-reviewer en tdd-expert behouden de bijgewerkte implementatie-/reviewrollen; general blijft uitgeschakeld |
| Skills | Gedeelde, harness-onafhankelijke inhoud en symlink-distributie behouden |
| Modelrouting | Eerst native modeloverrides via orchestrator en skills; modellen bij implementatie kiezen |
| Compaction | Native v2-compaction op het sessiemodel accepteren; goedkoop title-model behouden |
| LSP | Projectlint, typechecks en compilercommando's volstaan; editor verzorgt taalondersteuning |
| Server | Standaard gedeelde achtergrondserver per gebruiker |
| Persoonlijke laag | Owner-run handleiding; repo/sync overschrijft persoonlijke bestanden niet |
| CLI-voorkeuren | Persoonlijk `cli.json`; geen gedeelde CLI-config in de sync |
| Sessies | Nieuwe v2-sessies; v1-data bewaren/archiveren voor terugzoeken en rollback |
| Usage-tracking | Bestaande outputlocatie en JSON/JSONL-contracten behouden, inclusief oude data |
| MCP | Alle bestaande integraties functioneel behouden |
| Huidige opdracht | Alleen dit plan vastleggen; installatie, branch, codewijzigingen en rollout volgen later |

### Buiten deze migratie

- Windows, desktop/web-uitrol, ACP/editorintegraties en een embedded OpenCode-host.
- Een nieuwe modelrouter met subscription-first chains, automatische failover of cooldowns.
- De uitbreiding met OpenRouter-prijzen die in het usage-tracking-FTD als latere
  pluginversie wordt genoemd. Een pluginversie "V2" is iets anders dan OpenCode-product v2.
- Een nieuwe beleidsplugin, Console-workspace, dashboard of aanvullende telemetrydienst.
- Brede herziening van specialistische methoden, toestemmingseisen of agentrollen.

Het bestaande ontwerp in `docs/specs/opencode-model-router/` blijft een apart
vervolgtraject. Het is geen impliciete opdracht om die router tijdens de migratie te bouwen.

## 2. Belangrijkste onderzoeksbevindingen

Bronnen staan in §17. Gebruik officiële v2-documentatie en broncode van de
daadwerkelijk te installeren versie; een `sdk/v2`-import in een v1-package is
geen bewijs dat het over OpenCode-product v2 gaat.

| Bevinding | Gevolg voor deze setup |
| --- | --- |
| Ondersteunde v1-config en frontmatter worden in het geheugen genormaliseerd | Native conversie is onze gekozen eindvorm, niet voor ieder veld een upstream-verplichting |
| V1-pluginimplementaties draaien niet in v2 | Usage-tracking-entrypoint, subscriptions, tools en cleanup werkelijk porten |
| Server-API en clientcontracten veranderen | V1 SDK-aanroepen en eventvormen vervangen; oude fixtures bewijzen geen v2-integratie |
| De onderzochte v2-loader zoekt `opencode.json` en `opencode.jsonc` | `tdvg-standards.json` niet langer naar globaal `config.json` linken |
| De onderzochte loader heeft geen automatische `/etc/opencode/`-managed laag | Required-instellingen omzetten naar defaults; niet blijven documenteren als afgedwongen |
| `small_model` normaliseert naar het title-agentmodel | Native `agents.title.model` gebruiken; geen algemene goedkope-subagent- of compactionfallback claimen |
| Compaction gebruikt het sessiemodel | Oude compactionmodelpin niet als werkzame kostenbesparing meenemen |
| Top-level `subagent_depth` wordt genegeerd met waarschuwing | Naar `experimental.subagent_depth` verplaatsen |
| MCP-serveroverrides vervangen de volledige serverdefinitie | Persoonlijke/project-overrides moeten alle vereiste servervelden bevatten |
| MCP-tools gebruiken standaard Code Mode | Tooldiscovery, naamgebruik, permissions en telemetry expliciet controleren |
| Native subagent-tool heeft `model` en `sessionID` | Rol en model per taak scheiden; v1-dispatchvoorbeelden actualiseren |
| Modelparameter zegt standaard: alleen zetten bij expliciet modelverzoek | Autonome routing via prompts praktisch verifiëren; instructieconflict niet verbergen |
| V2 biedt momenteel geen werkende LSP-tools of diagnostics | Agentchecks aansluiten op bestaande projectcommando's |
| CLI-instellingen staan in één persoonlijk `cli.json` | Paste-voorkeur uit serverconfig halen; owner-run conversie |
| Configuratie en meerdere definities kunnen live herladen | Herstartregels actualiseren; symlink-targetwijzigingen apart verifiëren |
| Eventsubscriptions zijn live-only, zonder automatisch replay/reconnect | Telemetrycontinuïteit en herstel expliciet ontwerpen en controleren |

**Versiegevoelig:** de online documentatie kan verder zijn dan de geïnstalleerde
release. Bijvoorbeeld: de onderzochte 2.0.23-pluginloader weigert expliciet
geconfigureerde lokale bestandsplugins, terwijl online voorbeelden die vorm
wel noemen. Gebruik voor deze port één native plugin-directory en controleer
de exacte package/API-contracten bij uitvoering.

## 3. Uitvoeringsvolgorde en afhankelijkheden

| Fase | Werk | Gereed voordat |
| --- | --- | --- |
| A | Baseline, branch, backup en symlink-overgang voorbereiden (§4) | Native bestanden aan actieve symlinks veranderen |
| B | Configuratie, defaults, sync en owner-run instellingen (§5–6, §11) | V2 normaal wordt gebruikt |
| C | Agents, skills, permissions en dispatch porten (§7–8) | Gedragschecks/modelrouting |
| D | Usage-tracking, tools, dependencies en scripts porten (§9–10) | Migratie als functioneel gereed wordt beschouwd |
| E | Persoonlijke providers/MCP en lokale runtime controleren (§11–12) | End-to-end acceptatie |
| F | Lokale acceptatie en documentatie afronden (§13–14) | Merge en rollout |
| G | Rollout per machine en rollbackbaarheid bevestigen (§15–16) | Migratie afsluiten |

Dezelfde checkout wisselen van branch verandert direct de doelen van bestaande
symlinks. Een aparte branch is daarom op zichzelf geen geïsoleerde testomgeving.
Voer geen gelijktijdige v1- en v2-processen uit tegen een checkout die naar
native v2 wordt omgezet. Leg vooraf vast welke checkout de links tijdens de
lokale migratie gebruiken; een aparte worktree kan nuttig zijn als isolatie nodig is.

## 4. Voorbereiding, versie en herstelpunt

- [ ] Inventariseer repo-, globale en projectgebonden configuratie op de lokale pilotmachine; de eigenaar inventariseert persoonlijke bestanden.
- [ ] Noteer huidige v1-versie, installatiebron, binarypad, OS/architectuur en actieve symlinkdoelen.
- [ ] Leg de aparte migratiebranch en het v1-herstelcommit vast; behandel bestaande ongecommitte wijzigingen als mogelijk gebruikerswerk.
- [ ] Kies bij uitvoering de actuele v2-release en leg de exact lokaal geteste versie vast voor de rollout.
- [ ] Stop v1-processen vóór de actieve symlinktargets native v2-inhoud krijgen.
- [ ] Maak owner-run backups van persoonlijke configuratie, auth/data, link-state en bestaande usage-tracking-output; sla geheimen niet in de repo op.
- [ ] Leg vast hoe v1-sessies later worden teruggevonden; converteer of hervat ze niet als onderdeel van deze scope.
- [ ] Houd rekening met gedeelde OpenCode-data/configpaden: nieuwe sessies betekenen niet automatisch een nieuwe database.
- [ ] Bepaal of de pilot een afzonderlijke v2-database via `OPENCODE_DB` nodig heeft; maak de keuze expliciet vóór eerste startup.
- [ ] Leg een restore-route voor de v1-database vast voordat v2 migraties op de bestaande database uitvoert; terugzetten van alleen de binary is geen volledige rollback.

**Acceptatie:** branch, versie, linkdoelen en backups zijn bekend; v1 kan terug
zonder afhankelijk te zijn van geconverteerde config of een gewijzigde database.

## 5. Configuratie: native v2 en gedeelde defaults

### 5.1 Nieuwe laagindeling

| Rol | Repo-bron / eigenaar | V2-doel |
| --- | --- | --- |
| Gedeelde, overschrijfbare defaults | `opencode/configs/tdvg-standards.json` | `~/.config/opencode/opencode.json` |
| Persoonlijke instellingen en secrets | Eigenaar; buiten repo | `~/.config/opencode/opencode.jsonc` |
| Projectinstellingen | Eigenaar van betreffende project | `opencode.json(c)` en/of `.opencode/opencode.json(c)` |
| CLI- en servicevoorkeuren | Eigenaar; buiten repo | Persoonlijk `cli.json` en `service.json` |

De globale `.json` wordt vóór `.jsonc` geladen. Projectconfiguratie kan de
defaults eveneens wijzigen. De huidige required-laag vervalt als afdwinging;
haar ondersteunde instellingen worden opgenomen in `tdvg-standards.json`.
Behoud het gereserveerde `opencode/configs/`-mechanisme met expliciete mapping.

### 5.2 Concrete conversies

| Huidig | Native v2 / actie |
| --- | --- |
| `subagent_depth: 3` | `experimental.subagent_depth: 3` |
| `experimental.disable_paste_summary: true` | Uit serverconfig; persoonlijk `cli.json` met `prompt.paste: full` |
| `mcp.<server>` | `mcp.servers.<server>` |
| `agent.plan.disable: true` | Default `agents.plan.disabled: true` |
| `agent.title.model` en `small_model` | Eén expliciete default `agents.title.model` |
| Pins voor `compaction` en `summary` | Werkzame v2-paden controleren; niet als goedkope algemene onderhoudsmodelpins blijven presenteren |
| `permission.bash` | Geordende `permissions`-regels met `action: shell` |
| `share: disabled` | Default behouden; v2-sharing is momenteel niet beschikbaar |
| Updatebeleid | Expliciet globaal `update: notify` |

- [ ] Zet `tdvg-standards.json` om naar native v2 en maak het tevens strikt geldige JSON; het huidige bestand bevat een trailing comma.
- [ ] Neem de ondersteunde defaults uit `tdvg-required.json` over: Plan uit, goedkoop title-model, sharing uit en vragen vóór `rm *` / `git push *`.
- [ ] Verwijder `small_model` als native veld; gebruik `agents.title.model: openrouter/z-ai/glm-5.3-flash` zolang dat model beschikbaar is.
- [ ] Leg het geaccepteerde compactionverschil vast; gebruik native compaction en vermijd een custom implementatie.
- [ ] Controleer het gebruik van de verborgen `summary`-agent in de doelrelease; verwijder een pin zonder werkzaam onderhoudspad of documenteer het echte gebruik.
- [ ] Verplaats nesting naar `experimental.subagent_depth` en behoud runtimewaarde 3.
- [ ] Verwijder de paste-instelling uit de gedeelde serverconfig en beschrijf de persoonlijke equivalent.
- [ ] Controleer de actuele server- en CLI-schemas; verwissel `https://opencode.ai/config.json` en `https://opencode.ai/v2/cli.json` niet.
- [ ] Verwijder de required-bron/mapping pas wanneer ondersteunde instellingen en cleanup-instructies zijn overgenomen.
- [ ] Controleer `opencode debug config` én de effectief geladen agents/MCP/modellen; in v2 is debug-output niet per definitie één v1-achtige merged JSON.
- [ ] Controleer startup/reload-logs op verworpen documenten, onbekende velden en genegeerde legacy-instellingen; alleen een succesvolle startup is onvoldoende.
- [ ] Bewijs met onschuldige verschillen dat persoonlijke en projectinstellingen defaults kunnen overschrijven; schrijf in documentatie nergens meer "afgedwongen" voor deze laag.

Gebruik geen nieuwe policies om bestaande `ask`-regels in harde `deny`-regels te
veranderen. Dat zou het bevestigde gedrag wijzigen.

**Acceptatie:** alle bedoelde defaults werken, persoonlijke overrides blijven
mogelijk, er is geen afhankelijkheid van globaal `config.json` of `/etc/`-loading.

## 6. Symlinks en `scripts/link.py`

### 6.1 Bestandsmapping

| Huidig | Beoogd |
| --- | --- |
| Standards → globaal `config.json` | Standards → globaal `opencode.json` |
| `tdvg-required.json` → `/etc/opencode/opencode.jsonc` | Required-bron vervalt; oud getrackt linkdoel gecontroleerd opruimen |
| `opencode/agents/*.md` | Zelfde bron- en doelpaden |
| Flat `plugins/usage-tracking.ts` + pluginmap | Alleen native plugin-directory `plugins/usage-tracking/` als laadroute |
| `opencode/command/usage-status.md` | `opencode/commands/usage-status.md` |
| `skills/<id>/` | Bestaande volledige-directorylinks behouden |

De bestaande link-state reconstrueert itemtargets via de actuele
`CONFIG_FILE_MAP`. Na een mappingwijziging kan het oude target daardoor niet
meer correct worden afgeleid. Cleanup moet de oude mapping kennen.

- [ ] Documenteer vóór de wijziging de oude getrackte targets en itemkeys per machine.
- [ ] Kies één expliciete overgang: oude geselecteerde links met de oude scriptversie unlinken vóór update, of een eenmalige migratie die de oude mappings bewaart.
- [ ] Controleer bij cleanup dat het om de bedoelde symlink gaat; verwijder geen echte bestanden of persoonlijke config.
- [ ] Wijzig `CONFIG_FILE_MAP` voor standards naar globaal `opencode.json`; verwijder de required-mapping na gecontroleerde overgang.
- [ ] Verwijder oude `config.json`-, required-, singular-command- en flat-pluginlinks uitsluitend via de afgesproken owner-run cleanup.
- [ ] Behoud overige harnesslinks, bestaande echte bestanden, backupprocedure en niet-geselecteerde items.
- [ ] Zorg dat de native pluginmap eenmaal wordt geladen; laat niet tegelijk het flat entry-bestand en het directory-entrypoint actief.
- [ ] Houd ondersteunende pluginbestanden samen; deploy geen repo-only `*.test.ts`-bestanden.
- [ ] Behoud bescherming van persoonlijke `opencode.jsonc`, `cli.json`, `service.json`, packagebestanden, auth en persoonlijke plugins.
- [ ] Controleer op Linux én macOS padresolutie, herhaald linken, stale state, unlinken en het gedrag bij bestaande echte targets.
- [ ] Voer na scriptwijzigingen `uv run scripts/link.py status` en `uv run scripts/link.py list` uit.
- [ ] Controleer na linken de daadwerkelijke bronnen die v2 ontdekt; een groene symlinkstatus bewijst op zichzelf geen OpenCode-loading.

**Acceptatie:** deze repo blijft source of truth; nieuwe links kloppen, oude
laadroutes zijn weg en opnieuw linken is idempotent.

## 7. Custom agents en permissions

### 7.1 Frontmatter en toolnamen

| V1 | V2 |
| --- | --- |
| `permission`-map | `permissions`-array van `{action, resource, effect}` |
| `temperature: 0.1` | `request.body.temperature: 0.1`, providerondersteuning verifiëren |
| `color: primary/accent/warning/success` | Expliciete zes-cijferige hexkleur |
| `bash` | `shell` |
| `task` | `subagent` |
| `list` | Directorylisting via `read` |
| `skill({name: ...})` | `skill({id: ...})` |
| `task.subagent_type` | `subagent.agent` |
| `task.task_id` | `subagent.sessionID` |

V2's legacy-conversie zet niet-hex agentkleuren op een grijze fallback. Kies
tijdens implementatie passende expliciete kleuren; kopieer de oude semantische
kleurnamen niet als native kleurwaarden.

- [ ] Converteer alle vijf agent-frontmatters naar native v2; meng geen legacy/native velden.
- [ ] Behoud orchestrator primary, implementer subagent en specialisten all; converteer general-disablement mee.
- [ ] Behoud XML-body, rolverdeling, toestemming voor werkplan/runmap, rapportcontracten en onafhankelijke review.
- [ ] Behoud laadvolgorde: eerst rolskill, daarna `writing-simple-code` bij technisch werk; gebruik de v2-skill-ID.
- [ ] Actualiseer expliciete v1-toolnamen en dispatchvoorbeelden in de agentbodies.
- [ ] Verwijder de niet-werkzame LSP-toolverwachting; verwijs voor verificatie naar beschikbare projectlint/typecheck/compilercommando's.
- [ ] Controleer tasktracking: v2 documenteert geen ingebouwde `todowrite`; behoud het duurzame runplan/ledger en maak de workflow niet afhankelijk van een ontbrekende tool.
- [ ] Houd de bestaande shelltoestemmingseffecten aan; controleer matching van samengestelde commando's en patronen zonder argumenten.
- [ ] Behoud advisory-only code/security en gedelegeerde TDD-review; direct TDD-gebruik is tests-only en implementer bezit tests/broncode.
- [ ] Behoud rapportpermissions voor root-relatieve én geprefixte `.agents/runs/**/*.md`-paden; verifieer de v2 whole-value-wildcards met echte doelpaden.
- [ ] Controleer dat rapporttoestemming geen productiecode of andere run-artifacts toestaat; bestaande `ask`-rechten blijven `ask`.
- [ ] Verifieer shellgedrag apart: `edit`-permissions zijn geen filesystem-sandbox voor shellcommando's.
- [ ] Controleer nested specialist-handoffs: custom children gebruiken hun eigen permissions, niet automatisch een restrictieve subset van de parent.
- [ ] Controleer modelinheritance: de rol blijft herbruikbaar zonder verplicht model in elk agentbestand; een expliciete dispatchoverride werkt daadwerkelijk.

### 7.2 Praktijkcheck per agent

- [ ] Orchestrator onderzoekt scope, vraagt noodzakelijke verduidelijking en start geen dispatch vóór expliciet plan-/runmapakkoord.
- [ ] Orchestrator implementeert geen projectbestanden; uitvoering/fixes gaan naar implementer met bevestigde grenzen.
- [ ] Implementer doet Red–Green–Refactor, tests/broncode en bewijsrapport zonder eigen subagents, gebruikersvragen of automatische commits.
- [ ] Elke fase/batch wacht op code- en achteraf-testreview, plus relevante security; test- en reviewuitzonderingen zijn vooraf afzonderlijk goedgekeurd.
- [ ] Code-reviewer rapporteert bevindingen zonder gereviewde code te wijzigen; testkwaliteit/security wordt correct overgedragen.
- [ ] Security-reviewer doet de verplichte onderbouwde analyse/online research en schrijft alleen het benoemde rapport.
- [ ] Gedelegeerde TDD-expert beoordeelt in B en schrijft alleen het benoemde rapport; fixes gaan naar implementer. Direct gebruik mag tests wijzigen, nooit broncode.
- [ ] Specialisten retourneren ontbrekende context naar de coordinator en starten geen eigen gebruikersvragen in gedelegeerd werk.

**Acceptatie:** alle vijf agents worden ontdekt en volgen de bijgewerkte rolgrenzen;
toestemmingen werken ook bij daadwerkelijk uitvoeren en nested handoffs.

## 8. Skills, instructies en promptgestuurde modelrouting

### 8.1 Gedeelde skills

- [ ] Inventariseer alle huidige skillmappen, inclusief `writing-simple-code`, references, scripts en templates.
- [ ] Behoud IDs, Engelse skillinhoud en volledige-directorysymlinks voor alle huidige harnesses.
- [ ] Controleer v2-discovery onder `~/.agents/skills/` en `~/.claude/skills/`; controleer bij dubbele IDs welke bron werkelijk wint.
- [ ] Controleer path-derived skill-ID, exacte casing en toegang tot relatieve supporting files.
- [ ] Werk `skills/using-subagents/references/harness-notes.md` bij voor v2-dispatch, resume, skillinput, permissions en achtergrondgedrag.
- [ ] Werk v1-voorbeelden in discovery/templates/control bij zonder andere harnesssecties naar v2 te herschrijven.
- [ ] Behoud runtime nesting 3 en de bestaande skillgrens maximaal 2 niveaus met alleen goedgekeurde advisory-handoffs; de hogere runtimewaarde verruimt het beleid niet.
- [ ] Behoud standaard foreground-waves; background dispatch alleen gebruiken waar het bestaande/expliciet goedgekeurde plan dat toestaat.
- [ ] Controleer overige harnessspecifieke paden, bijvoorbeeld `.opencode/skills/impeccable/scripts/`; gebruik de werkelijk geladen skill-base als dat pad niet bestaat.
- [ ] Inventariseer projectgebruik van `CLAUDE.md` en `instructions`; v2 laadt momenteel alleen `AGENTS.md` en resolveert de `instructions`-array niet.
- [ ] Laat de eigenaar noodzakelijke projectinstructies in de juiste `AGENTS.md` opnemen; de repo migreert geen andere projecten stilzwijgend.
- [ ] Controleer geladen instructies na reload/compaction; reeds ontdekte nested instructies kunnen een nieuwe sessie vereisen voor gewijzigde inhoud.

### 8.2 Native modelrouting

Een nieuwe v2-child kiest `model` uit de aanroep, daarna het agentmodel,
daarna het parentmodel. Een expliciete override kan ook bij resume het model
wijzigen. Ontdek modellen/varianten via de daadwerkelijke catalogus; raad
geen IDs uit geheugen en behandel beschikbaarheid als projectgebonden.

- [ ] Bepaal bij implementatie de beschikbare providers/modellen en hun relevante varianten, kosten en taakgeschiktheid.
- [ ] Leg compacte routingcriteria in de orchestrator/skill vast: goedkoop geschikt voor eenvoudige taken, voldoende capaciteit voor complexe taken en reviews.
- [ ] Leg toestemming voor autonome modelselectie expliciet vast en neem modelkeuze en escalatie in het goedgekeurde werkplan/delegatiecontract op.
- [ ] Behoud één rolprofiel per agent; maak geen gekopieerde rolprompts enkel om verschillende modellen te gebruiken.
- [ ] Verifieer eenvoudige en complexe dispatches, een dispatch zonder override en resume met expliciete override tegen werkelijke childmetadata/telemetry.
- [ ] Controleer het instructieconflict rond `model`: de standaard tooltekst staat het alleen toe bij expliciet gebruikersverzoek; een skilltekst is geen gegarandeerde override daarvan.
- [ ] Beoordeel meerdere representatieve runs; alleen een belofte van de parent of één gelukte call is onvoldoende.
- [ ] Als prompts-first onvoldoende betrouwbaar blijkt, leg bevindingen aan Thim voor en vraag een afzonderlijke beslissing over een kleine routing-plugin.
- [ ] Bouw geen router/failover uit het bestaande FTD en voeg geen ongedocumenteerde `model_tiers`-config toe.

**Acceptatie:** alle benodigde skills laden onder hun huidige ID; agentrollen
blijven intact en modelrouting wordt door werkelijk gebruikte modellen bewezen.
Een noodzakelijke uitbreiding of afwijking wordt eerst expliciet besloten.

## 9. Plugins: usage-tracking porten

### 9.1 Entry, registratie en dependencies

- [ ] Gebruik één native directory-entrypoint `opencode/plugins/usage-tracking/index.ts`; verwijder de oude flat laadroute na linkcleanup.
- [ ] Vervang de v1-function-export door `Plugin.define({id, setup})` met een stabiele plugin-ID.
- [ ] Vervang `@opencode-ai/plugin` door de bij de doelrelease passende `@opencode/plugin`-dependency en werk `package.json`/`bun.lock` bij.
- [ ] Controleer `tsconfig.json` en module/runtime-resolutie ook via de symlink-deploy; vertrouw niet alleen op imports vanuit de repo.
- [ ] Lees opties via `ctx.options`; vervang v1-tuples in owner-run configuratie door `{package, options}`.
- [ ] Gebruik `ctx.location` voor de pluginlocatie; bepaal event-/sessielocatie afzonderlijk om projectscheiding te behouden.
- [ ] Vervang de `$` Bun-shellhelper door expliciet beheerde processaanroepen waar nodig; behoud fail-open gedrag.
- [ ] Gebruik `ctx.app.version` voor de werkelijke hostversie in plaats van een mogelijk andere `opencode` op `PATH` te proben.
- [ ] Maak device-/OS-metadata ook op macOS bruikbaar; `/etc/os-release` is Linux-specifiek en mag geen harde afhankelijkheid zijn.
- [ ] Behoud de bestaande hostname/project-hash, remote/pathfallback en non-git-projectscheiding.
- [ ] Pas logging aan de actuele plugin-API aan; log geen volledige events, prompts, toolinput/-output of secrets.

### 9.2 Events naar het bestaande opslagcontract

Het bestaande `mapping.ts` verwacht `{id, type, properties}` en v1-messageparts.
V2 gebruikt onder meer `{id, type, created, data, location, durable?}`.
Behoud de genormaliseerde opslagrecords en vertaal aan de inputkant.

| Bestaande betekenis | V2-bron om te koppelen/verifiëren |
| --- | --- |
| Session identity / parent / project / model | `session.created` en zo nodig publieke sessiemetadata |
| Titelupdate | `session.renamed` |
| Actief agent/model en stepstart | `session.step.started`, model-/agentselectie-events |
| Tokens, cost en stepeinde | `session.step.ended`; failed-step usage indien beschikbaar |
| Toolnaam en terminal resultaat | Tool input/start + `session.tool.success` / `session.tool.failed` via call-ID |
| Turn afgerond / idle | Publieke execution/status/idle-events van de doelrelease |
| Verwijderd | `session.deleted` |
| Compactionkosten | Publieke compaction-ended/failed en usageprojectie zonder dubbel tellen |

`session.usage.recorded` is in de onderzochte schema's een intern event, geen
garantie voor publieke subscriptions. Cumulatieve usage-updates en stepkosten
zijn evenmin twee onafhankelijke kostenbronnen die mogen worden opgeteld.

- [ ] Maak eerst een kleine metadata-only runtime-inventarisatie van de echte events en IDs op de gekozen v2-versie.
- [ ] Port `mapping.ts` en eventuele nodige adapters; behoud genormaliseerde types en bestaande JSON/JSONL-veldnamen.
- [ ] Correlateer model, agent en steps via `assistantMessageID`; definieer een stabiele mapping voor legacy `messageID`/`partID`-velden.
- [ ] Controleer ontbrekende en dubbele terminal events, retries, failures, interrupt en modelwissels.
- [ ] Behoud input/output/reasoning/cache-read/cache-write counters en numerieke USD-costs; registreer nul en ontbrekende bedragen correct.
- [ ] Controleer aparte onderhoudsusage en voorkomen van dubbel tellen; `cost > 0` is geen universele succesvoorwaarde voor subscription/free-modellen.
- [ ] Behoud recursive childrollup via `parentID`, ook bij meerdere turns en nested handoffs.
- [ ] Behoud event-ID-dedup over live ingest, overlappende instanties, restart en eigen JSONL-replay.
- [ ] Behoud de huidige betekenis en bekende replaybeperking van `activeMs`; presenteer geen gereconstrueerde duur die niet uit opgeslagen records volgt.
- [ ] Behoud `~/.local/share/opencode-usage/<hash>/events.jsonl`, `sessions/<id>.json` en de bestaande elf-key `overview.json`.
- [ ] Verifieer verwerking van bestaande v1-telemetry en nieuwe v2-records zonder in-place datareset of stille schemawijziging.
- [ ] Behoud metadata-only, serial writequeue, error health en fail-open opslaggedrag.

### 9.3 Gedeelde-serverlifecycle

- [ ] Start `ctx.event.subscribe()` als beheerde achtergrondtaak; blokkeer `setup` niet op een oneindige stream.
- [ ] Filter events op de juiste session/location/project; een plugininstance-locatie is niet automatisch de locatie van elk event.
- [ ] Houd verwerking licht en buffer writes; een trage subscriber kan de gedeelde eventbron ophouden.
- [ ] Leg de herstelroute bij stream-EOF/fout expliciet vast: nieuwe subscription en waar nodig metadata/usage-reconciliatie via publieke API.
- [ ] Ga niet uit van automatisch eventreplay of reconnect; maak detecteerbare gaten niet onzichtbaar als geslaagde ingest.
- [ ] Stop subscriptions/timers/processen bij cleanup en drain de queue voordat de instance sluit.
- [ ] Verifieer dat reload geen dubbele consumers of verloren writes veroorzaakt.
- [ ] Verifieer meerdere gelijktijdige projecten/clients tegen één gedeelde server, inclusief childsessions.
- [ ] Behoud bestaande store/aggregate/overview-logica waar het contract al voldoet; geen algemene herschrijving zonder noodzaak.

**Acceptatie:** de plugin laadt eenmaal, bestaande telemetry blijft bruikbaar,
nieuwe parent-/childusage klopt en pluginfouten breken OpenCode niet.

## 10. Commands, status-tool en verificatiescripts

- [ ] Verplaats `opencode/command/usage-status.md` naar `opencode/commands/usage-status.md` met behoud van commandnaam en bodycontract.
- [ ] Registreer `usage_status` via `ctx.tool.transform`; gebruik native JSON Schema voor de lege input en de actuele structured content-returnvorm.
- [ ] Controleer toolzichtbaarheid: als de tool via Code Mode wordt aangeboden, moet het command nog steeds dezelfde tool kunnen vinden en exact de JSON-tekst teruggeven.
- [ ] Behoud sessiongebonden status, outputpad, aantallen, laatste write, errors en lopende tokens/costs.
- [ ] Houd `/usage-status` in de huidige sessie; maak er geen background-childcommand van.
- [ ] Actualiseer `scripts/smoke_usage_tracking.sh` voor `subagent`, native directoryloading, nieuwe commandpaden en v2-runtime.
- [ ] Vervang Linux-only shellhulpmiddelen zoals GNU `readlink -f` en `find -printf` waar macOS geen equivalent gedrag biedt.
- [ ] Behoud CLI-contracten `--check` en `--run --model PROVIDER/MODEL`, en de offline/live scheiding.
- [ ] Controleer `opencode run --format json` op de doelrelease; neem geen v1-eventoutputvorm aan.
- [ ] Verifieer het normale gedeelde-serverpad; gebruik standalone aanvullend voor gecontroleerde diagnose wanneer process-environmentisolatie nodig is.
- [ ] Behoud privacyvriendelijke diagnostiek met paden/tellingen/booleans; maak live falen wel bruikbaar te diagnosticeren.
- [ ] Stem cost-asserties af op het gekozen model: niet-negatief/geldig voor alle modellen; positief alleen als een betaald model dat behoort te rapporteren.
- [ ] Port bestaande pluginchecks/fixtures naar v2 en behoud betekenisvolle regressiechecks van opslag, rollup, fail-open en cleanup.
- [ ] Laat implementer tests én broncode porten/schrijven/verifiëren; laat de TDD-specialist na iedere fase/batch onafhankelijk in advisory Mode B beoordelen. Deze planning is geen bewijs dat checks al groen zijn.

**Acceptatie:** dezelfde slash command en scriptinterfaces werken op Linux en
macOS; de live smoke bewijst één echte parent→child-run met correcte outputdata.

## 11. Owner-run migratie van persoonlijke instellingen

Deze stappen gebeuren door de eigenaar op iedere machine. `link.py` schrijft
niet naar persoonlijke `opencode.jsonc`, `cli.json`, `service.json`, auth of
persoonlijke package-/pluginbestanden.

- [ ] Inventariseer persoonlijke providers, modelaliases/varianten, MCP-servers, plugins, env-substituties en CLI-voorkeuren zonder secrets naar de repo te kopiëren.
- [ ] Converteer persoonlijke `provider` naar `providers`, packages/settings/headers/body en model-/variantvormen volgens de v2-guide.
- [ ] Converteer eventuele persoonlijke agent-/command-overrides als gehele nested entries; native/legacy niet binnen zo'n entry mengen.
- [ ] Controleer provider-ID-renames als ze voorkomen: `azure-cognitive-services`→`azure`, `google-vertex-anthropic`→`google-vertex`.
- [ ] Controleer providerauth na startup; v2 kan ondersteunde legacy `auth.json`-credentials naar SQLite importeren en schrijft nieuwe credentials niet terug naar dat bestand.
- [ ] Gebruik `/connect` of de auth-CLI voor benodigde herauthenticatie; beheer credentials niet door de database rechtstreeks te wijzigen.
- [ ] Controleer alle persoonlijke plugins op echte v2-ondersteuning; alleen een package-entry hernoemen is onvoldoende.
- [ ] Migreer persoonlijke terminalinstellingen naar `~/.config/opencode/cli.json`; bekijk ook automatisch geïmporteerde globale `tui.json`-voorkeuren.
- [ ] Zet de eerdere paste-voorkeur op `prompt.paste: full` als die behouden moet blijven.
- [ ] Controleer thema, agentkleuren, model/agentselectie, keybinds en toestemmingdialogen; behoud expliciete prompts, geen automatische acceptatie als migratieshortcut.
- [ ] Controleer server-environment, `PATH`, projecttooling en eventuele proxy/CA-variabelen; een gedeelde server krijgt latere shell/direnv-wijzigingen niet vanzelf.
- [ ] Gebruik de servicecommando's om noodzakelijke environmentwijzigingen en restart te beheren; zet geen secretwaarden in dit plan of gedeelde voorbeelden.
- [ ] Behoud `update: notify` in de globale serverconfig; controleer dat een persoonlijke override niet onbedoeld automatische updates activeert.

**Acceptatie:** benodigde accounts/modellen/tools zijn beschikbaar op de machine
en persoonlijke instellingen blijven van de eigenaar.

## 12. MCP en overige runtimefunctionaliteit

### 12.1 MCP

De gedeelde repo definieert Context7 en DeepWiki. Firecrawl, Tavily en andere
integraties kunnen uit de persoonlijke laag komen; de eigenaar inventariseert
hun precieze transport, headers en credentials.

- [ ] Behoud gedeelde servernamen/URLs en converteer naar `mcp.servers`.
- [ ] Controleer complete persoonlijke overrides: `type`, `url`/`command` en andere vereiste velden moeten aanwezig blijven.
- [ ] Converteer `enabled` naar inverse `disabled`, scalar timeout naar de toepasselijke timeoutvelden en OAuth-fields naar snake_case.
- [ ] Controleer remote OAuth versus API-keyheaders; gebruik `oauth: false` uitsluitend voor servers waarvoor dat passend is.
- [ ] Controleer startup/catalog/execution-timeouts; verhoog die alleen wanneer bestaande researchwerkzaamheden dat nodig hebben.
- [ ] Controleer default Code Mode en de effectieve namen/permissions; behoud directe exposure via `codemode: false` alleen als het bestaande gebruik dat nodig maakt.
- [ ] Verifieer Context7 met resolve + query, DeepWiki met een codebasevraag en Firecrawl/Tavily met een kleine succesvolle research/retrieval-call.
- [ ] Maak quota-/creditproblemen zichtbaar als externe blokkade, niet als bewijs dat de OpenCode-port stuk is of geslaagd is.
- [ ] Verifieer dezelfde benodigde tools vanuit custom subagents; MCP-verbinding alleen bewijst nog geen bruikbaarheid in de agentworkflow.
- [ ] Behoud researchbeleid en naamverwijzingen waar discovery die kan oplossen; voorkom harde v1-namen die niet meer bestaan.

### 12.2 Overige v2-oppervlakken

- [ ] Leg bestaande lint/typecheck/compilercommando's per relevant project vast als LSP-vervanging; installeer niet ongemerkt nieuwe tooling.
- [ ] Controleer formatterinstellingen waar ze gebruikt worden: v2-built-in formatters zijn opt-in via `formatter: true`; behoud bestaand doelgedrag.
- [ ] Controleer snapshots/undo in een wegwerpfixture; snapshots zijn geen rollback van externe shellbijwerkingen of een vervanging voor de migratiebackup.
- [ ] Controleer eventuele references en externe-directorytoestemmingen; references zijn geen algemene permission-bypass.
- [ ] Controleer relevante attachmentflows: PDF lezen via `read` en PDF als promptattachment hebben niet dezelfde ondersteuning.
- [ ] Houd warming uit zoals de v2-default; activeer geen extra betaalde achtergrondrequests tijdens deze behoudende migratie.
- [ ] Behoud huidige onderzoeks-MCP's; vervang ze niet automatisch door v2's optionele hosted websearch/Console.
- [ ] Controleer noodzakelijke netwerk/proxy-instellingen met loopback in `NO_PROXY` als er een proxy is.

**Acceptatie:** dagelijkse agent- en researchflows werken en geaccepteerde
verschillen hebben concrete vervangende commando's of een vastgelegde beperking.

## 13. Lokale acceptatie en go/no-go

Bewaar resultaten per geteste versie/platform zonder prompts, secrets of volledige
tool-output aan de gedeelde documentatie toe te voegen. Test native v2-config
en de echte symlink-deploy, niet alleen repo-imports of losse bestanden.

### 13.1 Statische en discoverychecks

- [ ] Native JSON/YAML en schemas geldig; geen relevante normalizationwarnings.
- [ ] `uv run scripts/link.py status` en `uv run scripts/link.py list` tonen de bedoelde nieuwe targets.
- [ ] `opencode --version` en de serverversie komen overeen met de geteste release.
- [ ] `opencode service status`, `opencode api GET /api/info` en `opencode debug config` geven de verwachte runtime/bronnen.
- [ ] `opencode debug agents`, `opencode models`, `opencode mcp list` en `opencode plugin list` bewijzen effectieve discovery.
- [ ] Beschikbare offline plugin-/typechecks en de aangepaste `scripts/smoke_usage_tracking.sh --check` slagen.

### 13.2 Gedrag en telemetry

- [ ] Alle vijf agentpraktijkchecks uit §7 slagen, inclusief skilllaadvolgorde en general-disablement.
- [ ] Toestemming voor werkplan/runmap en onafhankelijke review blijven onderdeel van de workflow.
- [ ] Toegestane rapport-/testwrites en niet-toegestane productie-edits worden correct behandeld.
- [ ] Runtime nesting en de strengere skillgrens zijn beide bewezen.
- [ ] Promptgestuurde modelrouting en hervatten zijn gecontroleerd met de echte childmodellen.
- [ ] Live smoke met parent en child slaagt; `/usage-status` toont actuele, plausibele totals.
- [ ] Meerdere turns, nested children, modelwissels, interrupt en relevante onderhoudsusage blijven correct geteld.
- [ ] Bestaande v1-telemetry blijft leesbaar; nieuwe output houdt het afgesproken contract.
- [ ] Reload/restart en twee gelijktijdige projecten veroorzaken geen dubbele counting, projectscheidingfouten of pluginlekken.
- [ ] Een gecontroleerde opslagfout laat OpenCode werken en wordt zichtbaar in status/logging.
- [ ] Wijziging van een symlinktarget wordt geladen via watch/reload of de vastgelegde service-restartprocedure.
- [ ] Persoonlijke CLI-voorkeuren, MCP-auth en projectverificatiecommando's werken.

### 13.3 Vrijgavevoorwaarden

- [ ] Thim accepteert het lokale resultaat op Linux en bevestigt welke macOS-machine vóór/bij rollout wordt geverifieerd.
- [ ] Geen open migratieblokkers: onwerkzame plugin, verloren telemetrycontract, ontbrekende verplichte skill of niet-functionele hoofdworkflow.
- [ ] Bij structureel onbetrouwbare prompt-routing wordt eerst een expliciete beslissing genomen; geen stille uitbreiding met routercode.
- [ ] Onafhankelijke implementatiereview en de relevante security-/testspecialistchecks zijn afgerond volgens het bestaande agentbeleid.
- [ ] Rollback is aantoonbaar uitvoerbaar met de bewaarde v1-bestanden, links, binary en data.

## 14. Repo-documentatie bijwerken

- [ ] Werk `README.md` en `AGENTS.md` synchroon bij voor v2-bestandsmapping, overschrijfbare defaults, native frontmatter, tools en lifecycle.
- [ ] Verwijder claims dat `config.json` en `/etc/` nog de bedoelde laadroute/afdwinging leveren.
- [ ] Vervang de algemene startup-only-herstartclaim door v2 watch/reloadgedrag plus een betrouwbare service-restartfallback voor symlink/dependencywijzigingen.
- [ ] Werk commandpaden en plugin-directoryloading bij; beschrijf geen verplicht flat entry-bestand meer.
- [ ] Werk het usage-tracking-FTD en relevante taak-/statusdocumentatie bij voor de port, events en behouden outputcontract.
- [ ] Houd de model-router-FTD herkenbaar als afzonderlijk v1-gebaseerd vervolgontwerp; corrigeer relevante verwijzingen zonder het alsnog in scope te trekken.
- [ ] Beschrijf geaccepteerde verschillen: geen managed afdwinging, sessiemodel voor compaction, CLI-checks in plaats van LSP en persoonlijke `cli.json`.
- [ ] Noteer de exact geteste v2-versie en OS/architecturen; actualiseer bij een volgende bewuste update.

## 15. Rollout naar TDVG-developmentmachines

- [ ] Laat de migratiebranch pas na lokale go/no-go integreren; laat de eigenaar/het afgesproken Git-proces merge en push uitvoeren.
- [ ] Gebruik dezelfde lokaal geteste v2-release voor de initiële uitrol; als een nieuwere release wordt gekozen, verifieer die eerst opnieuw.
- [ ] Geef per machine een korte owner-run instructie met backup, oude-linkcleanup vóór mappingwissel, repo-update, v2-installatie, nieuwe links en controles.
- [ ] Verwijder/vervang package-managed v1 volgens de installatiebron; v1/v2 gebruiken beide `opencode` en delen configuratiepaden.
- [ ] Gebruik passende v2-installatie voor Linux/macOS; controleer `PATH` en voorkom dat een oude package of shellalias alsnog v1 start.
- [ ] Voer owner-run conversie van persoonlijke config/auth/CLI/MCP uit zonder secrets te distribueren.
- [ ] Voer `link.py link` voor de nieuwe itemkeys uit en controleer achtergebleven legacy-links.
- [ ] Herstart de gedeelde service na de installatie/omschakeling en controleer `/api/info`; alleen de TUI sluiten activeert geen nieuwe serverbinary.
- [ ] Controleer de korte discovery-, agent-, MCP- en usage-smoke op iedere machine; documenteer resultaat en eventuele externe quota-/authblokkades.
- [ ] Bevestig macOS-portabiliteit van scripts/device-informatie vóór macOS als geslaagd te markeren.
- [ ] Laat updates daarna alleen melden en voer relevante regressiechecks uit vóór een bewuste upgrade.

## 16. Rollback

Rollback is herstel van de complete v1-setup, niet alleen het unlinken van de
usage-plugin. Nieuwe v2-sessies/telemetry blijven apart bewaard wanneer terugrollen nodig is.

- [ ] Stop de gedeelde v2-service en alle betrokken clients vóór restore.
- [ ] Bewaar nieuwe v2-data die later nodig kan zijn; laat rollback geen bestaande usage-output verwijderen.
- [ ] Verwijder uitsluitend de v2-links die voor de overgang zijn aangemaakt en gecontroleerd zijn.
- [ ] Herstel repo/checkout naar het v1-herstelpunt en herstel de oude `CONFIG_FILE_MAP`/link-state waar nodig.
- [ ] Herstel oude standards-, required-, command- en pluginlaadroutes met de v1-scriptversie; required-linkherstel kan root vereisen.
- [ ] Laat de eigenaar persoonlijke configuratie en v1-auth/data uit backup herstellen als die gewijzigd/gemigreerd zijn.
- [ ] Installeer de bewaarde v1-versie en controleer binarypad; start v1 niet met native v2-config of ongecontroleerd geconverteerde database.
- [ ] Controleer v1-agentdiscovery, MCP en `/usage-status`; leg de aanleiding en open blocker vast vóór een nieuwe poging.

## 17. Onderzoeksdekking, bronnen en versiecontrole

De v2-documentatie is geïnventariseerd via de volledige Engelstalige
documentatieboom `services/www/src/docs/content/` (54 MDX-bronnen in de
2.0.23-baseline), de algemene docs, CLI, Build, Console en de gegenereerde API.
Relevante gedragclaims zijn nader gecontroleerd in getagde v2-broncode.

| Documentatiegebied | Relevantie voor dit plan |
| --- | --- |
| Intro, migratie, config, troubleshooting | Installatie, discovery, compatibiliteit, diagnose |
| Agents, skills, instructies, permissions, policies, tools | Rollen, dispatch, nesting, skillloading en permissiongedrag |
| Plugins + Build/Plugins/porting | Entry, lifecycle, tools, context, hooks en dependencies |
| Build/Client, Effect-varianten, RPC, SDK, Cloudflare | Client/eventcontracten onderzocht; RPC/embedded/cloudhosting is geen migratieonderdeel |
| CLI intro/commands/config/TUI/providers/keybinds/themes/plugins | Service, persoonlijke instellingen, auth, commands en UX |
| Providers, models, compaction, warming | Modelkeuze, varianten, onderhoudskosten en extra requests |
| MCP, websearch, network | Researchtools, transport/auth, Code Mode en environment |
| Formatters, references, attachments, snapshots, sharing | Aanvullende dagelijkse functionaliteit en beperkingen |
| CLI ACP/web, Console intro/BYOK/budgets/Go/inference/models/websearch | Bekeken voor raakvlakken; geen nieuwe integratie/dienst in scope |
| API en event-/usage-schema's | Input/outputvormen en telemetrymapping voor de echte pluginport |

**MCP-onderzoek:** Context7 is geprobeerd maar had zijn maandquotum bereikt;
Firecrawl kon door onvoldoende credits geen nieuwe documentatie ophalen.
Tavily leverde discovery/retrieval/research en DeepWiki codebasecontext. Waar
die resultaten v1 en v2 vermengden of verouderde details gaven, zijn officiële
pagina's en getagde broncode doorslaggevend gebruikt. Symlinkwatching,
modelrouting en het telemetryherstelpad blijven praktijkchecks; ze zijn niet
als reeds bewezen gemarkeerd.

### Officiële documentatie

- [V2 intro/installatie](https://opencode.ai/v2/docs/)
- [Migreren vanaf v1](https://opencode.ai/v2/docs/migrate-v1)
- [Configuratie](https://opencode.ai/v2/docs/config) · [Server-schema](https://opencode.ai/config.json)
- [Agents](https://opencode.ai/v2/docs/agents) · [Permissions](https://opencode.ai/v2/docs/permissions) · [Policies](https://opencode.ai/v2/docs/policies)
- [Skills](https://opencode.ai/v2/docs/skills) · [Instructions](https://opencode.ai/v2/docs/instructions) · [Tools](https://opencode.ai/v2/docs/tools)
- [Plugins laden](https://opencode.ai/v2/docs/plugins) · [Plugin-API](https://opencode.ai/v2/docs/build/plugins) · [V1-pluginport](https://opencode.ai/v2/docs/build/plugins/migrate-v1)
- [Client/eventsubscriptions](https://opencode.ai/v2/docs/build/client) · [API](https://opencode.ai/v2/docs/api)
- [CLI/service](https://opencode.ai/v2/docs/cli) · [CLI-commando's](https://opencode.ai/v2/docs/cli/commands) · [Troubleshooting](https://opencode.ai/v2/docs/troubleshooting)
- [CLI-config](https://opencode.ai/v2/docs/cli/config) · [CLI-schema](https://opencode.ai/v2/cli.json) · [Provideraccounts](https://opencode.ai/v2/docs/cli/providers)
- [Commands](https://opencode.ai/v2/docs/commands) · [MCP](https://opencode.ai/v2/docs/mcp-servers)
- [Providers](https://opencode.ai/v2/docs/providers) · [Models](https://opencode.ai/v2/docs/models) · [Compaction](https://opencode.ai/v2/docs/compaction)
- [Formatters](https://opencode.ai/v2/docs/formatters) · [Network](https://opencode.ai/v2/docs/network) · [Warming](https://opencode.ai/v2/docs/warming)
- [References](https://opencode.ai/v2/docs/references) · [Attachments](https://opencode.ai/v2/docs/attachments) · [Snapshots](https://opencode.ai/v2/docs/snapshots) · [Sharing](https://opencode.ai/v2/docs/sharing)

### Broncode voor cruciale versiegebonden claims

- [V2.0.24 config-discovery](https://github.com/anomalyco/opencode/blob/v2.0.24/packages/core/src/config/discovery.ts) en [config-loader](https://github.com/anomalyco/opencode/blob/v2.0.24/packages/core/src/config.ts): bestandsnamen, documentvolgorde en ontbreken van de huidige managed-laadroute.
- [Serverprocess-config](https://github.com/anomalyco/opencode/blob/v2.0.24/packages/cli/src/server-process.ts): service-environment en expliciete configopties.
- [Agentmigratie](https://github.com/anomalyco/opencode/blob/v2.0.24/packages/core/src/v1/config/migrate.ts): requestvelden, actions en legacykleurfallback.
- [Subagent-tool](https://github.com/anomalyco/opencode/blob/v2.0.24/packages/core/src/tool/plugin/subagent.ts): modeloverride, resume, toolinstructie en `experimental.subagent_depth`.
- [Plugindiscovery](https://github.com/anomalyco/opencode/blob/v2.0.24/packages/core/src/plugin/source-directory.ts): directe files, directories en symlinks.
- [Session-eventschema](https://github.com/anomalyco/opencode/blob/v2.0.24/packages/schema/src/session-event.ts), [eventenvelope](https://github.com/anomalyco/opencode/blob/v2.0.24/packages/schema/src/event.ts), [tokenusage](https://github.com/anomalyco/opencode/blob/v2.0.24/packages/schema/src/token-usage.ts): telemetry-inputcontract.
- [Documentatieboom](https://github.com/anomalyco/opencode/tree/v2.0.23/services/www/src/docs/content): onderzoeksinventaris; bij uitvoering vergelijken met de gekozen release.

**Voor uitvoering:** controleer deze claims tegen de actuele release en noteer
afwijkingen. Wijzig een bevestigde scopekeuze niet stilzwijgend omdat een
nieuwere release een andere API of default heeft.
