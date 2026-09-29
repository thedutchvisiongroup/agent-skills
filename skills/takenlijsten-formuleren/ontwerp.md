---
type: ontwerp
status: concept
aangemaakt: 2026-09-23
bijgewerkt: 2026-09-29
---

# Ontwerpnotitie — takenlijsten-formuleren

## Doel

Deze notitie legt vast hoe de skill `takenlijsten-formuleren` is ontworpen en
waarom hij er zo uitziet. Het is een ontwerpdocument bij de skill: het beschrijft
de keuzes, de redenering erachter en de weg ernaartoe. Het is geen
gebruikshandleiding. Die staat in `SKILL.md` en de `references/`.

## Aanleiding en scope

De vraag was: wat maakt een goede takenlijst voor software development, en hoe
formuleer je die zodat het juiste eindresultaat ontstaat? Dat liep uiteen in
twee delen: onderzoek naar wat een goede takenlijst is, en een skill die
takenlijsten formuleert voor uitvoering door mensen en door georchestreerde
AI-agents.

Sinds ronde 6 ligt de lat concreter. Een lijst moet werkbaar zijn voor een
beginnend programmeur die zijn eerste programma schrijft. Hij moet elke actie
kunnen terugvoeren op de juiste plek in de bron. En hij moet bestaan in drie
vormen: voor één persoon, voor een team, of voor een persoon met een agent.

De scope blijft het **formuleren** van takenlijsten. Wijzigingsbeleid,
faalmodi, samenwerkingsafspraken, schatfilosofie en gedeelde projectstatus
vallen erbuiten. Dat zijn processuele afspraken, geen lijstinhoud.

## Structuur

```
takenlijsten-formuleren/
├── SKILL.md                      # kern, < 500 regels, Engels
├── ontwerp.md                    # dit bestand, niet mee in de upload
└── references/
    ├── list-variants.md          # solo, team, human-agent
    ├── splitting-rules.md        # phases, items, beslisboom
    ├── nfr-landing.md            # vier landingsplekken voor NFR's
    └── task-examples.md          # goede en zwakke phase, timing,
                                  #   human-agent- en teamfragment
```

`SKILL.md` draagt de werkstroom en de regels. De references zijn progressive
disclosure: ze worden alleen geladen wanneer ze nodig zijn en staan één
niveau diep onder `SKILL.md`. De map heet verplicht `references/`, want
`SKILL.md` linkt ernaar. Bij de eerste upload stonden de bestanden los naast
`SKILL.md`, en toen wezen alle vier de links naar niets.

`ontwerp.md` staat in de root en wordt niet door de skill gerefereerd. Het is
documentatie voor de lezer, geen uitvoeringsmateriaal. Het staat lokaal in de
bronmap en gaat niet mee in de upload.

De skill is Engels. De lijsten die hij maakt, zijn in de taal van het verzoek.
Deze notitie is Nederlands, want die is voor mij.

## Kernkeuzes

### Phases met een to-do en een DoD

Een lijst bestaat uit phases. Een phase is een use case uit de bron, of een
doorsnijdende fase: voorbereiding, integratie en review, release, observatie.
Elke phase heeft een to-do met de acties en een DoD met de controles. Phase 0
bestaat altijd. Daarin staan de controles uit de verificatiestap.

Dit vervangt "één lijst is één groep" uit ronde 5. Die keuze was nodig omdat
groepsregels automatisch voor elke taak golden, en er geen veld was om vast te
leggen bij welke groep een taak hoorde. Met phases is dat opgelost. Een item
hoort bij de phase waar het in staat. Meer administratie is niet nodig.

### Items: één actie of één controle

Een to-do-item is één handeling, met het volledige pad en, als het bekend is,
het exacte commando. Een DoD-item is één controle die je met ja of nee
beantwoordt, met het bewijs erbij. Er zijn geen subtaken. Een item dat
sub-items nodig heeft, is een phase of meerdere items.

Het oude taakcontract met dertien velden per taak is weg. Bij de test in
ronde 6 verdween de inhoud tussen de veldnamen. Bovendien herhaalden de
stappen de acceptatiecriteria, omdat de skill voorschreef dat het *hoe* open
moest blijven. Nu is het omgekeerd. Het hoe staat erin, tot op het commando.
Alleen ontwerpkeuzes die de bron openlaat, blijven open.

SMART en INVEST hebben geen eigen sectie meer, maar zitten in de itemregels.
Specific en Measurable zitten in "één actie" en "ja of nee met bewijs".
Achievable zit in de verificatiestap en de regel over de toolchain. Relevant
zit in de verplichte bronlink. Valuable en Small werken op phaseniveau: een
phase is een verticale plak van een use case die zelfstandig kan sluiten.

### Beginnersniveau

De lezer kent de basis van de programmeertaal, maar niet het project, de tools
of de bron. Daarom is geen stap impliciet. Wat vooraf waar moet zijn, zoals
geïnstalleerde dependencies of draaiende services, staat in "Voordat je
begint", met het commando dat het controleert. Elk commando krijgt één regel
uitleg. Een stap die op een bekende manier mis kan gaan, krijgt "Als het
misgaat". Een verwijdering zegt ook wat er moet blijven staan.

Dit komt rechtstreeks uit de praktijk. Bij het uitvoeren van de eerste phase
bleek vrijwel elk item een vervolgvraag op te leveren: waar staat het script,
wat haal ik precies weg, waarom werkt `vitest` niet? Dat laatste kwam door een
ontbrekende `npm ci`, iets wat CI wel doet en de lijst niet noemde. Eén keer
scheelde het weinig of de hele teststap was verwijderd in plaats van alleen
de coverage.

### Drie varianten

Er zijn drie varianten: `solo`, `team` en `human-agent`. De variant bepaalt
de bestanden en de labels, niet de regels.

`solo` is één lijst zonder uitvoerderslabels. Een stap van iemand anders,
zoals een goedkeuring, noemt de rol uit de bron.

`team` is één algemene lijst plus één lijst per persoon. De algemene lijst is
de enige plek waar een phase sluit. Daarin staan de DoD's, de gedeelde acties
en de overdrachten. De persoonlijke lijsten bevatten alleen de eigen acties.
Ze linken terug naar de algemene lijst en houden per item hun bronlink.

`human-agent` is één lijst waarin elk item begint met `(mens)` of `(agent)`.
Per phase staan de grenzen van de agent, het bewijs dat hij vastlegt en de
rollback. Een mensstap is voor oordeel, beslissingen, goedkeuringen en externe
instellingen. Iets controleren wat een run al laat zien, is geen mensstap.

Hiermee verandert ook de keuze "owner = executor". In `team` wordt vastgelegd
wie wat doet, anders bestaan er geen persoonlijke lijsten. Dat is bewust. Wie
wat doet, is wat anders dan eigenaarschap of verantwoordelijkheid. Die blijven
buiten de lijst. De verdeling komt van de gebruiker. De skill mag een voorstel
doen, maar beslist niet.

### Herleidbaarheid per item

Elk to-do- en DoD-item eindigt met precies één markering. Dat is een wikilink
naar de kop in de bron die het item uitvoert, of de markering "aanvulling" met
een link naar de reden. De aanvullingen staan in een eigen sectie, met wat de
bron niet zegt, waarom de lijst het nodig heeft en wie het bevestigt.

Vroeger stond de bron per taak. Daardoor zagen mijn eigen toevoegingen er in
ronde 6 uit alsof ze uit de FTD kwamen. Actionlint installeren stond er
bijvoorbeeld als taak, terwijl de FTD het alleen als optie noemt. Per item
markeren maakt dat verschil zichtbaar. Na het schrijven controleert de skill
zelf dat elk item een markering heeft en dat elke wikilink naar een bestaande
kop wijst.

### Verifiëren, niet aannemen

Alles waar de lijst op leunt, wordt gecontroleerd voordat een phase start. Een
verwijzing in de bron wordt geopend en nagelezen. Een tool moet beschikbaar
zijn via de toolchain van het project, niet alleen installeerbaar.

In ronde 6 ging dat twee keer mis op één punt. De DoD van de FTD eiste
YAML-validatie "per ADR-0008 convention". Eerst leek ADR-0008 niet te bestaan.
Daarna bleek dat het PyYAML alleen noemt als eenmalige controle, niet als
afspraak. En PyYAML zat niet in Devbox. Een conventie die je niet hebt
nagelezen, is een gerucht met een ADR-nummer.

Dit is iets anders dan signaleren of een bron al geïmplementeerd is. Dat
blijft afgewezen (zie Bewust niet gedaan). Hier gaat het alleen om wat de
lijst zelf nodig heeft om uitvoerbaar te zijn.

### Toetsbaar op het moment van sluiten

Elk DoD-item moet af te vinken zijn op het moment dat de phase sluit, met de
triggers, branches en omgeving die er dan zijn. Lukt dat niet, dan komt er een
to-do bij die het mogelijk maakt, of het item verhuist naar de phase waar het
wel kan.

Dit was de grootste fout in de eerste lijst. De test-workflows werden
push-only op `main` en `dev`. Daardoor kon niets vóór de merge bewezen worden,
terwijl de DoD dat wel vroeg. De oplossing in de referentielijst is een
tijdelijke validatiebranch, plus een item dat die weer opruimt.

### Rood vóór groen, ook buiten tests

Een controle die nooit gefaald heeft, bewijst niets. Dat gold al voor tests en
geldt nu ook voor gedragscontroles in CI. Voor een wijziging in configuratie of
toolchain gelden drie vragen. Is weg wat weg moest? Is er niets anders
veranderd? Merk je het in het gedrag? Bij Xdebug stond eerst alleen de eerste
vraag in de DoD. De diff van `devbox.lock` en `php -v` bleken nodig om het echt
te weten.

### Toolchain en uitvoeringsstrategie volgen de bron

Een aanvulling voegt geen tools of dependencies toe buiten de toolchain die de
bron vastlegt. Is iets toch nodig, dan wordt het een open vraag voor degene
die beslist. Branches, het aantal pull requests en rollback volgen de rollout
van de bron. De eerste lijst gaf elke taak een eigen branch, terwijl de FTD
één PR voorschreef. "Git revert van de taakcommit" had daarmee geen betekenis.

### Dekking vanuit de bron

De 100%-regel blijft: elk bronelement landt ergens, en niets wordt dubbel
gedaan. Nieuw is waar de dekkingstabel vandaan komt. Die wordt opgebouwd door
alle secties van de bron op te sommen, niet alleen de user stories: DoD,
success criteria, NFR's, constraints, risico's, quality scenarios, rollout en
open vragen. De eerste lijst bouwde de tabel vanuit zijn eigen taken en claimde
daarmee volledigheid. Een tabel die de lijst naast zichzelf legt, bewijst
alleen dat de lijst zichzelf dekt.

Daarbij hoort een tweede regel: elk DoD-item en elke review uit de bron heeft
een to-do die hem uitvoert. De eerste lijst eiste een review door
`code-reviewer`, maar geen enkele taak voerde die uit.

### NFR's op vier plekken

Een NFR telt pas als gedekt wanneer hij op precies één plek landt en daar een
controle heeft:

1. eigen to-dos met een DoD-item, binnen de phase waar hij bij hoort;
2. een DoD-item van de phase waarvan de uitkomst hem waarmaakt;
3. de DoD van de hele lijst, als het één controle over alles is;
4. een DoD-item van de observatiephase, als hij over tijd gemeten wordt.

Plek 4 is nieuw. De eerste lijst zette NFR's die over een week gemeten worden
onder Out. Daardoor kon de DoD van de FTD nooit op done komen. Een NFR die je
niet kunt meten bij het sluiten van een phase, verdwijnt niet. Hij verhuist.

### Limits als allowlist

Dit blijft, maar nu op phaseniveau in de variant `human-agent`. De allowlist
noemt wat de agent mag aanraken. Alles wat er niet op staat, is verboden. Nieuw
is dat lock-bestanden en gegenereerde bestanden die een tool als bijwerking
aanpast, er ook op moeten staan. `devbox.lock` ontbrak in de eerste lijst.

### Vragen, maar niet te veel

De skill vraagt alleen wat het verzoek en de bron niet beantwoorden. Het oude
"Do not proceed without answers" liet een agent zelf de ceiling invullen, en
die sloot de observatie uit. Nu mag de ceiling de DoD, de success criteria en
de rollout van de bron nooit uitsluiten. Wil de gebruiker dat toch, dan komt
het onder open vragen.

Nieuw is ook de vraag naar werkmateriaal. Is de repository beschikbaar, dan
leest de skill de echte bestanden, zodat items echte paden en commando's
noemen. Is hij er niet, dan begint een item dat een plek nodig heeft met een
zoekactie, niet met een gok.

### Taal

De hele lijst is in de taal van het verzoek, inclusief koppen en labels. Een
vaste tabel regelt de Nederlandse en Engelse labels. Programmeertermen,
commando's, identifiers en brontermen blijven zoals ze zijn.

Dit vervangt de oude regel dat veldnamen en contractwaarden altijd Engels
bleven. Die regel was nodig voor het dertien-veldencontract. Nu dat contract
weg is, leverde hij alleen nog een lijst op die half Engels was.

### Afsluiting per niveau

Er zijn drie niveaus. Een item is af als het is afgevinkt met bewijs. Een phase
is af als alle items zijn afgevinkt. De lijst is af als alle phases gesloten
zijn, de DoD van de lijst gehaald is, de dekking compleet is en de open vragen
opgelost of bewust geaccepteerd zijn. Zonder afsluitregel blijft "af" een
gevoel.

## Besluitgeschiedenis

De skill is in zes rondes aangescherpt. Per ronde: wat er speelde en wat er is
besloten.

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

Bewust geschrapt op mijn oordeel: wijzigingsbeleid, faalmodi, spikes,
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
een validatievoorbeeld noemde client-side validatie terwijl de allowlist alleen
server-side toeliet; NFR-verwijzingen liepen uiteen in naam en taal; een
voorbeeld liet reviewen door een bij naam genoemd persoon; de beslisboom gaf
tegenstrijdige uitkomsten; "exactly once" was te streng voor bronelementen; de
dekkingscheck liet geen bewijs achter; de outputtaal was niet vastgelegd.

Daarnaast het eigenaarvraagstuk: "one owner" zat in de terminal test, er was
geen veld voor, en eigenaarschap was tegelijk uitgesloten van de scope.

**Besloten:** owner wordt de partij in `Executor`. Geen nieuw veld, wel
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
element als eenheid; taalregel met expliciete contractuitzonderingen; en het
NFR-referentieformaat vastgelegd, omdat het anders per lijst zou verschillen.

### Ronde 4 — het NFR-veld en het netwerkcriterium

Wat er bovenkwam: het NFR-veld kon maar één groepsregel dragen, terwijl
groepsregels per definitie voor alle taken gelden. Een verwijzing per taak is
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

Wat er bovenkwam: de output kon maar één groep bevatten, terwijl de
lijstafsluiting van "alle groepen" sprak. En nu groepsregels automatisch
gelden, bepaalde groepslidmaatschap wél welke regels op een taak van
toepassing zijn. Er was geen veld om dat vast te leggen. Verder: de lijst opende
niet meer met preflight terwijl de tekst dat nog eiste; workflowstap 2 noemde
nog "source version" terwijl de bron naar de header was verhuisd; groepsregels
werden in twee notaties geschreven; en het netwerkcriterium hing nog deels af
van testcode die buiten de allowlist van de taak viel.

**Besloten:** één lijst is één groep. De ceiling is één thema, het groepsniveau
valt samen met het lijstniveau, en er zijn twee sluitniveaus in plaats van
drie. Preflight volgt op de header. Groepsregels worden consequent als checkbox
geschreven, want ze worden afgevinkt. En het netwerkcriterium wordt een
eigenschap van de workflow zelf ("the test step runs without outbound network
access"), zodat allowlist en stappen samen het criterium kunnen halen.

### Ronde 6 — de praktijktest (2026-09-28 en 2026-09-29)

De skill was na ronde 5 niet op een verse lijst beproefd. Dat gebeurde nu, op
de FTD "CI/CD Simplification & Optimization" van PTA-Vision. De lijst die eruit
kwam, was formeel correct en in de praktijk niet werkbaar. De maatstaf was mijn
eigen prompt: phases per use case, met per phase een to-do en een DoD als
checklist.

Wat er bovenkwam, in volgorde van ernst. De skill verbood phases ("one list is
one group"), terwijl de prompt ze vroeg. De stappen herhaalden de
acceptatiecriteria, omdat het hoe open moest blijven. Twee taken waren pas na de
merge af te vinken, omdat de triggers push-only werden. De ceiling sloot de
observatie uit, waardoor de DoD van de FTD onbereikbaar werd. Een review uit de
DoD had geen taak die hem uitvoerde. De bron stond per taak in plaats van per
item, waardoor toevoegingen niet te onderscheiden waren van de FTD. En een
conventie uit de bron bleek bij nalezen niet te bestaan.

Daarna heb ik de eerste phase van de referentielijst zelf uitgevoerd. Dat
leverde de tweede helft van de lessen op. Een item als "laat de client-job
`vitest run` draaien" was voor mij niet uit te voeren zonder uitleg. Lokaal
ontbraken `node_modules` en `vendor/`. De database was lokaal niet bereikbaar
onder de naam die CI gebruikt. En een lokaal geïnstalleerde validator zou een
dependency buiten Devbox zijn geworden.

Na de test kwamen er drie eisen bij. Er komen drie varianten: solo, team en
mens met agent. Elke actie verwijst met een wikilink naar de juiste plek in de
FTD. En een beginnend programmeur moet met de lijst verder kunnen.

**Besloten:** phases met een to-do en een DoD vervangen het groepsmodel uit
ronde 5. Het taakcontract met dertien velden vervalt. Items zijn één actie of
één controle, met pad, commando en verwachte uitkomst. Elk item krijgt een
wikilink of de markering "aanvulling", met een eigen sectie Aanvullingen. De
verificatiestap wordt phase 0. De tijdscheck en de dekking vanuit de bron worden
verplicht. NFR's krijgen een vierde landingsplek in de observatiephase. Drie
varianten in een nieuwe reference. Beginnersregels in de itemregels. De taalregel
wordt vereenvoudigd tot één taal met een vaste labeltabel. De referentielijst
`ftd-tasks.md` is de maatstaf voor de volgende test.

Twee eerdere keuzes zijn daarmee bewust teruggedraaid. "Eén lijst is één groep"
uit ronde 5 vervalt, omdat phases het lidmaatschapsprobleem oplossen. En "owner
= executor" uit ronde 2 is verruimd: in de teamvariant wordt vastgelegd wie wat
doet. Eigenaarschap in de zin van verantwoordelijkheid blijft buiten de lijst.

## Bewust niet gedaan

- **Het testartefact bijwerken.** `takenlijst-ftd-exam-checker-v1-3.md` is niet
  conform de huidige regels. Dat is bewust zo gelaten: het is een test, geen
  doel op zich.
- **Signaleren dat een bron al (deels) geïmplementeerd lijkt.** Afgewezen: niet
  gewenst in de skill. De verificatiestap uit ronde 6 is iets anders. Die
  controleert alleen wat de lijst zelf nodig heeft.
- **Een script voor de linkcheck meeleveren.** De skill beschrijft de controle
  (elk item gemarkeerd, elke wikilink naar een bestaande kop), maar levert er
  geen script voor. Dat kan later als `scripts/`, als de controle vaak
  handmatig blijkt.

## Openstaand

- De skill is na ronde 6 nog niet op een verse lijst beproefd. De volgende test
  is dezelfde FTD met dezelfde prompt, vergeleken met `ftd-tasks.md`.
- De teamvariant is alleen op papier ontworpen. Er is nog geen lijst met
  persoonlijke lijsten en overdrachten gemaakt.
- De regel dat Obsidian een dubbele punt weglaat in links naar koppen, heb ik
  in de praktijk gezien, maar niet in de officiële documentatie nagelezen.
- Of de OKF-validator frontmatter van het type "tasks" accepteert, is niet
  bekend. De skill kopieert daarom de frontmatter van een bestaand document in
  de doelmap.

## Bronnen

Grondslag voor het ontwerp (eerder onderzocht, 2026-09-23):

- Anthropic, *Equipping agents for the real world with Agent Skills* (2025) en
  *Skill authoring best practices*: progressive disclosure, degrees of
  freedom, evals-first, feedback loops.
- Agent Skills-specificatie (agentskills.io, 2025): formaat `SKILL.md`,
  `scripts/`, `references/`, `assets/`.
- Bill Wake, *INVEST in Good Stories, and SMART Tasks* (2003): INVEST en
  SMART. De weging van Time-boxed komt van de observatie dat omvang al in de
  story zit.
- PMBOK / WBS-praktijk: 100%-regel, mutually exclusive, work packages,
  terminal elementen.
- Cucumber / Gherkin: waarneembare uitkomsten in `Then`-stappen.
- Cialdini (2021) en Meincke e.a. (2025): commitment via checklists en
  bright-line rules.

Toegevoegd in ronde 6:

- De praktijktest zelf: `ftd.md` (FTD-ci-cd-simplification v1.1) en de
  referentielijst `ftd-tasks.md`, 2026-09-28.
- dorny/paths-filter, README (geraadpleegd 2026-09-28): op push werkt de action
  met git en vergelijkt hij standaard met de default branch. Dat was de
  aanleiding voor de regel dat claims uit de bron worden nagelezen.
