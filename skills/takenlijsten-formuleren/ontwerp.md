---
type: ontwerp
status: concept
aangemaakt: 2026-09-23
bijgewerkt: 2026-09-23
---

# Ontwerpnotitie — takenlijsten-formuleren

## Doel

Deze notitie legt vast hoe de skill `takenlijsten-formuleren` is ontworpen en
waarom hij er zo uitziet. Het is een ontwerpdocument bij de skill: het beschrijft
de keuzes, de redenering erachter en de weg ernaartoe. Het is geen gebruikshandleiding —
die staat in `SKILL.md` en de `references/`.

## Aanleiding en scope

De vraag was: wat maakt een goede takenlijst voor software development, en hoe
formuleer je die zodat het juiste eindresultaat ontstaat? Dat liep uiteen in
twee delen: onderzoek naar wat een goede takenlijst is, en een skill die
takenlijsten formuleert voor uitvoering door zowel medewerkers als
georchestreerde AI-agents.

De scope van de skill is het **formuleren** van takenlijsten. Wat bewust buiten
de lijst valt: wijzigingsbeleid, faalmodi, eigenaarschap, samenwerkingsafspraken,
schatfilosofie, en gedeelde projectstatus. Dat zijn processuele afspraken, geen
lijstinhoud.

## Structuur

```
takenlijsten-formuleren/
├── SKILL.md                      # kern, < 500 regels, Engels
├── ontwerp.md                    # dit bestand
└── references/
    ├── task-examples.md          # vijf voorbeelden: goed, zwak, human,
    │                             #   agent-human, edge case
    ├── splitting-rules.md        # beslisboom + signalen + terminal test
    └── nfr-landing.md            # drie landingsplekken voor NFR's
```

`SKILL.md` draagt het contract en de werkstroom. De references zijn
progressive disclosure: ze worden alleen geladen wanneer ze nodig zijn en
staan één niveau diep onder `SKILL.md`. `ontwerp.md` staat bewust in de root
en wordt niet door de skill gerefereerd — het is documentatie voor de lezer,
niet uitvoeringsmateriaal.

De inhoud van de skill is Engels omdat Engels de contracttaal is; deze notitie
is Nederlands omdat die voor jou is.

## Kernkeuzes

### Owner = Executor

Een taak heeft één eigenaar, en die eigenaar ís de partij in `Executor`. Er is
geen apart eigenaarveld. Reden: eigenaarschapsafspraken vielen eerder buiten
scope, maar de terminal test toetste wél op "one owner" — je kunt niet toetsen
wat je niet vastlegt. Door owner te definiëren als de executorpartij wordt het
toetsbaar via een bestaand veld, zonder verantwoordelijkheidsafspraken de lijst
in te trekken.

### Vier velden per agent-taak

Zodra een agent uitvoert, zijn verificatie, bewijs, grenzen (Limits) en
terugdraaien verplicht. Bewijs is geen samenwerkingsding maar een taakeigenschap:
het is wat je oplevert zodat een mens kan vaststellen dat het klopt zonder het
werk over te doen. Voor taken met tests hoort het bewijs de **rode** run én de
groene run te bevatten — de rode run is het bewijs dat de test iets toetst.

`agent-human` is één taak in twee fasen: de agent doet wat hij kan, een mens de
stappen die een persoon vragen (review, externe instellingen, oordeel). Nog
altijd één deliverable, één eigenaar, één afsluitmoment.

### Limits is een allowlist

Limits noemt wat er wél aangeraakt mag worden. Alles wat er niet staat, is
verboden. Dat is veiliger dan een verbodslijst, en het dwingt tot nadenken over
de scope van de taak. Samen met de stappen moet de allowlist elk
acceptatiecriterium kunnen bereiken: staat er een criterium dat de allowlist
verbiedt, dan wordt de taak aangepast en niet de grens stilletjes verruimd.

### NFR's op drie plekken

Een NFR telt pas als gedekt wanneer hij landt op precies één plek:

1. een eigen taak;
2. een acceptatiecriterium van een taak;
3. een groepsbrede afsluitregel, getoetst vóór het sluiten van de groep.

Een NFR benoemen zonder verificatiepunt telt niet. Een NFR wordt nooit over
meerdere plekken uitgesmeerd — zo glipt hij ertussenuit.

### Groepsregels gelden automatisch

Groepsregels gelden voor élke taak in de groep. Taken verwijzen er daarom
niet naar in het `NFR`-veld. Dat veld kent nog maar twee vormen: `own criterion`
en `none`. Dit is bewust gekozen boven een lijst met verwijzingen per taak:
zo'n lijst is ofwel onvolledig (een taak noemt één groepsregel maar valt onder
alle), ofwel ruis (elke taak draagt alle ids).

Afsluitregels in `Group rules` dragen een id `GR1`, `GR2`, … en worden als
checkbox geschreven, want ze worden bij het sluiten afgevinkt. Die ids dienen
de leesbaarheid van `Group rules` zelf en de dekkingstabel, niet het NFR-veld.

### Eén lijst is één groep

Eén lijst draagt precies één thema, en dat thema ís de groep. Er is geen
subgroepslidmaatschap om vast te leggen, en dus ook geen tweede niveau om af te
sluiten. Dit is de consequentie van "groepsregels gelden automatisch": zou een
lijst meerdere groepen dragen, dan bepaalt het lidmaatschap welke regels op een
taak van toepassing zijn — en daarvoor bood de structuur geen veld. Meerdere
thema's worden losse lijsten, elk met eigen header, preflight en afsluiting.

### Traceability en dekking

Elke taak verwijst naar bron met versie of paragraaf. Diepte over wat en waarom
staat in het bronbestand; de taak zelf blijft kort — geen lappen tekst, geen
dubbele waarheid.

De 100%-regel heeft twee kanten: elk bronelement hangt aan minstens één taak
óf staat expliciet onder Out, en geen twee taken leveren dezelfde oplevering.
"Mist niks" en "doet niks dubbel" zijn allebei nodig. Elementen die bewust
buiten scope vallen, komen in de dekkingstabel als `Out` — anders ziet een
bewuste uitsluiting eruit als een gat.

De dekkingstabel (bron-element → T-ids, `GR<n>` of `Out`) is verplicht en maakt
de toetsing aantoonbaar. Zonder tabel is de 100%-check een vinkje zonder bewijs.

### Afsluiting per niveau

Twee lagen, elk met eigen afsluitregel: taak (acceptatiecriteria afgevinkt,
verificatie groen, bewijs aanwezig) en lijst, wat tegelijk de groep is
(groeps-DoD inclusief NFR-toetsen, preflight nog geldig, anti-goals
gerespecteerd, dekkingstabel compleet). Zonder afsluitregel blijft "af" een
gevoel.

### Taken: SMART en INVEST

SMART met een bewuste weging: Specific, Measurable, Achievable en Relevant zijn
verplicht; Time-boxed is het minst belangrijk, want de omvang zit al in de
story en de scope. Voor agent-taken geldt één maatregel in plaats daarvan: de
taak past in één executor session — één executor rondt hem af zonder de scope
te heronderhandelen of naar een andere deliverable over te schakelen.

INVEST geldt volledig. Bij Independent is er een grens aan samenvoegen: alleen
als het resultaat de terminal test haalt én in één executor session past.

### Splitsen: beslisboom en terminal test

De beslisboom is bewust sequentieel — drie vragen op vaste volgorde, stoppen bij
het eerste beslissende antwoord. Parallelle takken gaven tegenstrijdige
uitkomsten: een deel met zelfstandige waarde én zonder inhoudsverlies
splitsbaar, eindigde in twee verschillende antwoorden.

De terminal test sluit daarop aan: regels 2 en 4 moeten gelden, en daarnaast
minstens één van de regels 1 of 3. Alle vier verplicht stellen zou de boom
tegenspreken: vraag 2 "Yes" en vraag 3 "No" leveren elk een terminal taak op,
en die tweede haalt regel 1 per definitie niet.

Taken zijn werkpackages: één deliverable, één eigenaar, niet verder te splitsen
zonder de inhoud te veranderen. Stappen binnen een taak zijn uitvoeringsvolgorde
en tellen niet mee voor de afsluitregel.

### Omschrijving en taal

Taken worden kort en resultaatgericht geformuleerd, met verwijzing naar bron.
Eén regel wat, waarom en hoe alleen waar nodig.

De lijst heeft één taal: die van het verzoek, want dat is de lezer. Drie dingen
blijven Engels omdat ze contract zijn, wat de lijsttaal ook is: veldnamen,
sectienamen, en alle backticked contractwaarden (executor-waarden, `Out`,
`none`, `GR<n>`, NFR-vormen). Brontermen en citaten blijven onvertaald. Dit is
expliciet gemaakt omdat "nooit mengen" zonder die uitzonderingen zichzelf
tegensprak: veldnamen Engels en inhoud in de lijsttaal ís mengen.

### Header en preflight

De lijst begint met een `Header` (source, audience, ceiling) — de antwoorden op
de drie vragen die je verplicht stelt vóór je schrijft. Zonder plek voor die
antwoorden in de output verdwenen audience en ceiling simpelweg.

Daaronder `Preflight`: dependencies, tools, groeps-DoD gelezen. Geen taak start
zolang preflight niet afgevinkt is. Dat is DoR op lijstniveau.

## Besluitgeschiedenis

De skill is in vier feedbackrondes aangescherpt. Per rondje: wat er speelde en
wat er is besloten.

### Ronde 0 — het begin (2026-09-23)

Samen vastgelegd wat een goede takenlijst moet hebben: SMART met time-boxed als
laagste prioriteit, INVEST volledig, taken die niet verder te splitsen zijn,
traceability met afsluitregels (DoR, acceptatiecriteria, DoD), publiek mens
én georchestreerde agents, per niveau een eigen afsluitregel, heldere scope met
wél en niet, NFR's bij groeperingen, documentatie en tests op het juiste moment
(rode tests → code → tests opnieuw), en korte omschrijvingen die verwijzen naar
de oorspronkelijke documentatie.

Aanvullend die we eerder over het hoofd zagen en die wel in het ontwerp kwamen:
preflight op dependencies en tools, terugdraaibaarheid bij agentic werk (git),
en de classificatie van uitvoerbaarheid met criteria en bewijs per klasse.

Bewust geschrapt op jouw oordeel: wijzigingsbeleid, faalmodi, spikes,
eigenaarschap, levensduur van de lijst, wijzigrecht, schatfilosofie. Die horen
bij samenwerking en overleg, niet bij de lijst. Statuscontract en onafhankelijke
review alleen laten gelden wanneer agents uitvoeren.

### Ronde 1 — structuur volgens writing-skills

Gekozen: skill-directory met progressive disclosure, Engelse inhoud, middelste
vrijheidsgraad (format verplicht, invulling vrij), en alleen in `concepten/`
nog niet installeren. Resultaat: `SKILL.md` plus drie references.

### Ronde 2 — fouten in de voorbeelden en open posten

Wat er bovenkwam: het CI-voorbeeld haalde zijn eigen acceptatiecriterium niet
(branch protection is een repo-instelling, niet iets in `.github/workflows/`);
een validatie-voorbeeld noemde client-side validatie terwijl de allowlist alleen
server-side toeliet; NFR-verwijzingen liepen uiteen in naam en taal; een
voorbeeld liet reviewen door een bij naam genoemd persoon; de beslisboom gaf
tegenstrijdige uitkomsten; "exactly once" was te streng voor bronelementen; de
dekstingscheck liet geen bewijs achter; de outputtaal was niet vastgelegd.

Daarnaast het eigenaarvraagstuk: "one owner" zat in de terminal test, er was
geen veld voor, en eigenaarschap was tegelijk uitgesloten van de scope.

**Besloten:** owner wordt de partij in `Executor` — geen nieuw veld, wel
toetsbaar. Verder: beslisboom sequentieel, dekkingstabel als verplicht bewijs,
één taal per lijst, Limits als allowlist, rode run als bewijs, `agent-human`
uitgelegd, één executor session als maat, en een vaste sectie voor open vragen.

### Ronde 3 — consequenties doortrekken

Wat er bovenkwam: een voorbeeldtaak gebruikte nog een verbodslijst bij Limits;
diezelfde taak zakte voor zijn eigen terminal test, wat met de "alle vier"
formulering een lus met de beslisboom opleverde; er stond een kapotte link in
de werkstroom; "list owner" sloop als nieuw begrip binnen terwijl owner net
uitgesloten was; de eerste tak van de beslisboom stuurde bij twee deliverables
niet naar splitsen; samenvoegen bij een harde keten had geen grens; de
dekkingstabel kende `Out` nog niet als waarde en mengde "section" met
"element"; de taalregel sprak zichzelf tegen; de controle op agent-taken miste
rollback en de bereikbaarheid van criteria.

**Besloten:** terminal test als (1 of 3) en 2 en 4; `Out` als dekkingswaarde;
element als eenheid; taalregel met expliciete contract-uitzonderingen; en het
NFR-referentieformaat vastgelegd omdat het anders per lijst zou verschillen.

### Ronde 4 — het NFR-veld en het netwerkcriterium

Wat er bovenkwam: het NFR-veld kon maar één groepsregel dragen terwijl
groepsregels per definitie voor alle taken gelden — een verwijzing per taak is
dan ofwel onvolledig, ofwel ruis. Het landingsvoorbeeld benoemde een
deelverzameling en schond daarmee de eigen definitie van landing 3. Audience en
ceiling hadden geen plek in de output. Er stond nog een restant oude notatie. De
taalregel miste de contractwaarden zelf. En het netwerkcriterium in het
CI-voorbeeld was onhaalbaar: `pip install` en `actions/checkout` gaan over het
netwerk.

**Besloten:** groepsregels gelden automatisch en worden niet per taak benoemd;
het `NFR`-veld kent nog `own criterion` en `none`; landing 3 wordt één toets
over de hele groep; er komt een `Header`-sectie; de taalregel noemt alle
backticked contractwaarden; en het netwerkcriterium wordt beperkt tot de
teststap. Eigen aanvulling: de dekkingstabel accepteert `GR<n>` als waarde,
anders ziet een element dat als groepsregel landt eruit als een gat.

### Ronde 5 — groepsmodel en restanten

Wat er bovenkwam: de output kon maar één groep bevatten terwijl de
lijstafsluiting van "alle groepen" sprak — en nu groepsregels automatisch
gelden, bepaalde groepslidmaatschap wél welke regels op een taak van
toepassing zijn. Er was geen veld om dat vast te leggen. Verder: de lijst opende
niet meer met preflight terwijl de tekst dat nog eiste; workflowstap 2 noemde
nog "source version" terwijl de bron naar de header was verhuisd; groepsregels
werden in twee notaties geschreven; en het netwerkcriterium hing nog deels af
van testcode die buiten de allowlist van de taak viel.

**Besloten:** één lijst is één groep — de ceiling is één thema en het
groepsniveau valt samen met het lijstniveau, met twee sluitniveaus in plaats van
drie. Preflight volgt op de header. Groepsregels worden consequent als checkbox
geschreven, want ze worden afgevinkt. En het netwerkcriterium wordt een
eigenschap van de workflow zelf ("the test step runs without outbound network
access"), zodat allowlist en stappen samen het criterium kunnen halen.

## Bewust niet gedaan

- **Het testartefact bijwerken.** `takenlijst-ftd-exam-checker-v1-3.md` is niet
  conform de huidige regels. Dat is bewust zo gelaten: het is een test, geen
  doel op zich.
- **Signaleren dat een bron al (deels) geïmplementeerd lijkt.** Afgewezen: niet
  gewenst in de skill.
- **Een nieuwe takenlijst uit de laatste FTD.** Als test mogelijk, nu niet nodig.

## Openstaand

- De skill is na de laatste wijzigingen niet meer op een verse takenlijst
  beproefd. De vier feedbackrondes toetsten het ontwerp, niet het gedrag bij
  uitvoering.
- De vijf voorbeelden dekken goed, zwak, human, agent-human en een edge case,
  maar geen voorbeeld met meerdere groepsregels in `GR`-vorm naast een
  `own criterion` — de combinatie komt dus niet in beeld.

## Bronnen

Grondslag voor het ontwerp (eerder onderzocht, 2026-09-23):

- Anthropic, *Equipping agents for the real world with Agent Skills* (2025) en
  *Skill authoring best practices* — progressive disclosure, degrees of
  freedom, evals-first, feedback loops.
- Agent Skills-specificatie (agentskills.io, 2025) — formaat `SKILL.md`,
  `scripts/`, `references/`, `assets/`.
- Bill Wake, *INVEST in Good Stories, and SMART Tasks* (2003) — INVEST en
  SMART; de weging van Time-boxed komt van de observatie dat omvang al in de
  story zit.
- PMBOK / WBS-praktijk — 100%-regel, mutually exclusive, work packages,
  terminal elementen.
- Cucumber / Gherkin — waarneembare uitkomsten in `Then`-stappen.
- Cialdini (2021) en Meincke e.a. (2025) — commitment via checklists en
  bright-line rules.
