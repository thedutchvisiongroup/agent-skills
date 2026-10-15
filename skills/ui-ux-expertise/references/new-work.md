# New visual work

Use this flow for any request to build a new surface (page, screen, flow, feature with its own UI) or to replace a visual identity, with or without a command. The design context confirmed in Setup holds product truth and durable visual decisions; this flow decides how much to invent and then builds.

## Contents

1. Decide what is already true
2. Ask what will change the work
3. Choose the right amount of invention
4. Sketch the first viewport (optional)
5. Commit the world
6. Record the direction
7. Build with full commitment
8. Inspect and finish

## 1. Decide what is already true

Read the confirmed design context, representative code, tokens, components, and assets.

- **Redesign:** preserve product truth, content, function, constraints, and explicit brand commitments; replace the old visual world rather than polishing it. The old look is evidence of what the subject is, not authority over what it becomes.
- **Established world:** inherit it. A missing design-system file does not erase a coherent identity already in code; follow the identity the code shows.
- **Incomplete brand:** preserve confirmed assets and recognizable traits, then expand the system with the user for this surface.
- **No visual authority** (no design files, nothing derivable from code): propose one direction (section 3) and offer a neutral grayscale baseline as the alternative. The user chooses.

A section, component, feature, or state inside an established surface inherits that surface. Never turn a local addition into a new identity exercise.

## 2. Ask what will change the work

Before implementation, ask two or three related questions with the structured question tool when available; a precise request needs only a compact confirmation. Do not re-ask what the clarification gate already settled. The design context settles the visual world, not this surface's purpose or concept.

- **Persuade:** who must act, what they should believe, which real proof, content, or assets earn that belief.
- **Operate:** the task, information, important states, frequency, constraints.
- **Read:** the reader's question, source material, structure, wayfinding.
- **Experience:** what leads, how exploration unfolds, which interaction or transition matters.

Across modes, ask what success looks like, what must remain untouched, and what would make a polished result feel wrong. Never ask for CSS values or canned aesthetic lanes. When the project has no framework yet, the stack is the user's decision: ask whether they want plain HTML/CSS, a specific framework, or your recommendation.

## 3. Choose the right amount of invention

### Extend an existing surface

Inherit its world and composition. Resolve only the new purpose, content, hierarchy, states, interaction, and how the addition joins the surrounding experience. No direction proposal, and no design-system change unless the user approves a durable system change.

### Create a whole surface inside an established world

Keep the visual system fixed. Derive several materially different structures from the content, task, and user behavior (what leads, topology, sequence, density). Propose the strongest one with a one-line reason and name the runner-up in one line. The user confirms or picks the runner-up. Skip this for a precisely specified narrow request.

### Create or replace the visual world

1. Name the product's unique mechanism in one sentence, the audience's real scene, its cultural home, and what this first surface must prove. Note the page this category always ships and its predictable opposite; both are the rut. A brief that paints its own picture (a product name, a titled artifact, a governing metaphor) adds its literal reading to the rut.
2. Privately list seven concrete visual systems, artifacts, places, or rituals from that cultural world that the audience knows by heart, each with one line on why it can carry the mechanism and one on how it looks (ground and main colors, type voices, the one recognizable signature). The audience's world includes its graphic and screen traditions: notation, publications, identity programs, data graphics. On an Operate or Read surface, never take the tools and instruments the audience operates (a terminal, a scope, a control panel): handed to a working screen they come back as a costume. On a Persuade or Experience surface, spend at most one candidate on them. Also ask what this thing would look like as a physical object and what its world looked like before the web. When more than three candidates share one material family, dig further until the list spans at least three families.
3. Judge the candidates on two axes, audience identification and product clarity, and pick the one that wins both. Losing the obvious literal reading to stronger grounded material is the point.
4. Self-check the pick against the calibration in section 5: if someone could guess it from the category alone, or from category-plus-avoidance, take the next candidate or raise this one.
5. Present one direction, fully committed: the world, the first viewport, the visitor path, the signature interaction, cross-surface reach, and an honest risk line. Mention in one sentence that the user can ask for the category standard played straight instead (convention at full fidelity, two or three named products as the bar) or, when no visual authority exists, the neutral grayscale baseline.

A user- or brief-pinned direction beats this process, always. Preserve every pinned constraint; in dimensions the brief leaves open, the direction still binds.

Every direction you propose must already be viable: every relationship and claim it visualizes true, a real palette and component family, workable within the available assets, tools, and performance budget. Truth binds claims, not demonstrations: in greenfield work, author illustrative material at full fidelity, label it synthetic wherever a visitor could mistake it for the real thing, and hand the user the list of what to replace. Commercial and factual claims (prices, customers, benchmarks, capabilities the product lacks) stay uninventable. Refusing a bold direction because its demonstration data does not exist yet is the timidity reflex wearing honesty's clothes.

The mode decides what the opening must do and how far the world may reach into the page; see [modes.md](modes.md).

## 4. Sketch the first viewport (optional)

For a whole new page or screen, or a new world, you may show a quick sketch of the first viewport before building, so the user can approve the composition cheaply. Skip it for extensions and small surfaces.

- **ASCII** in chat for structure only, or **a single static HTML file** (inline CSS, no build step, no external dependencies besides fonts) when palette and type matter. Put the HTML file in the approved run directory when one exists, otherwise in a scratch location the user can open; never in project source.
- Sketch what the mode needs (see "First-viewport sketches per mode" in [modes.md](modes.md)), with real content and the committed palette and type.
- Stop and wait for approval or one correction round. Once approved, the sketch is the composition the build matches.

## 5. Commit the world

**Color.** Pick a strategy before picking colors:
- **Restrained:** neutrals plus one accent. Common on screens people operate or read, where color still does real jobs.
- **Committed:** one saturated color carries 30–60% of the surface.
- **Full palette:** 3–4 named roles.
- **Drenched:** the surface IS the color.

Persuade and Experience surfaces have permission for the bolder strategies; take them when the brief allows. Color commits at page scale: fields that own whole regions, not accents scattered over a neutral ground. Use OKLCH for new palettes. Dark or light is never a default: write one sentence of physical scene (who uses this, where, under what light) and let it force the answer.

**Faces.** Choose faces like objects from the subject's world, in the mode's register. Operate and Read surfaces are well served by system stacks and workhorse UI faces. Persuade and Experience surfaces want faces with a point of view, and these training-data defaults mean you stopped looking: Fraunces, Playfair Display, Cormorant, Lora, Crimson, Newsreader, Syne, Space Grotesk, Space Mono, IBM Plex, Inter-as-display, DM Sans, DM Serif, Outfit, Plus Jakarta Sans, Instrument Sans. Naming one anyway requires a reason no other face could satisfy, and a subject association is never that reason: books wanting a serif, bookshops wanting hand-lettering, and tech wanting a mono are exactly the associations the list exists to break.

**Calibration.** AI-generated interfaces cluster around a few looks regardless of subject:
- warm cream ground, high-contrast serif display, and a terracotta or signal-red accent;
- near-black with one neon accent and glowing edges;
- broadsheet-editorial hairlines, italic display serif, and small tracked mono labels;
- flat saturated ink with black boxes, hard offset shadows, and heavy condensed display type.

All are legitimate when the brief calls for them. Where the brief leaves the aesthetic free, landing in one means the self-check failed.
- Energy is not the enemy of trust: a brief's negative constraints (no gamification, no hype) rule out those devices, not exuberance.
- A bookish, warm, family, or child-facing subject does not soften the calibration. Models render these as cream grounds, serif display with italic accents, and lamplight even when the direction never asked for them. Treat that first palette as already spent. Book cloth, thread, jackets, and endpapers span the whole saturated spectrum.
- A brief-pinned world pins the world, not its softest rendition.

## 6. Record the direction

Before code, write the chosen direction as a short contract, six blocks, roughly 150 words:

- **THESIS:** the one idea this surface owns and the category-default arrangement it refuses.
- **OWN-WORLD:** the palette and component language, specific enough to be recognizable with all content removed.
- **STORY:** what the visitor understands, believes, and does.
- **FIRST VIEWPORT:** the exact composition, what is where and at what scale, and where the primary action sits.
- **SIGNATURE:** the signature interaction and the motion grammar.
- **FINISH:** "This build ends with one batched inspection round, its fixes, and a report of what was and was not verified."

If a block reads like a mood, the direction is not decided yet. When an approved `using-subagents` run directory exists, write the contract to `design-brief.md` there so implementers and reviewers receive it by path; otherwise keep it in the conversation.

Never copy the contract into implementation source or anything shipped to the browser: comments, hidden DOM, `data-*` attributes, serialized props, metadata, or files served beside the artifact.

## 7. Build with full commitment

Build the chosen direction, not a safer interpretation of it. The form supplies structure, reading order, component conventions, and native motion; the product supplies every fact. Commit every atom: nav, buttons, inputs, and links are built in the direction's vocabulary. Read [craft-floor.md](craft-floor.md) immediately before the first edit, and follow the stack notes in [stacks.md](stacks.md).

- **The first viewport is a thesis, not a header.** Demonstrate the mechanism immediately. The memory test: if someone left after one viewport, what would they describe an hour later? If the honest answer is a mood, the concept has not committed yet.
- **Prove, don't claim.** Show the subject doing its job: the interface at work, specifics a competitor could not copy-paste.
- **Author the assets; never substitute chrome.** Every content blank the brief left open is yours to author at production fidelity: names, entries, copy, thumbnails. Gradients, glass, generic icon tiles, and many-vertex `clip-path` polygons where an authored asset belongs are the gap wearing chrome.
- **Build the form's web leverage.** When the direction names a technique (canvas, WebGL, view transitions, generative motion), build the technique itself, not a static imitation.
- **Pace the scroll like a studio.** Vary density, scale, image, motion, and quiet inside one grammar; a dense passage earns a quiet one, and the page ends anchored by a real close.
- **Use real, verified imagery when the brief implies it** (see Imagery in [modes.md](modes.md)).
- **Author motion as material.** Give the page its native motion once, orchestrated, rather than scattered hover effects. Keep content visible by default.

Preserve semantics, accessibility, performance, responsiveness, project conventions, and working behavior.

## 8. Inspect and finish

Verification runs in bounded passes, not an open loop:

1. **One batched inspection round.** When a screenshot or browser tool is available, capture desktop (about 1440px wide) and mobile (about 390px wide) together, plus the user's own viewport width when you know it. A capture is evidence only when it is valid: settle or disable entrance motion first, capture full pages from the top, and open every file once to confirm it shows what its name claims (no blank regions, no half-loaded state). Run the detector once over the changed files (`python3 <skill-dir>/scripts/detect.py <files>`) and check the result against the craft floor and the recorded direction.
2. **One fix batch** for everything the round found.
3. **At most one confirming round.** Then stop polishing. Whatever remains goes into the report.

Without a screenshot or browser tool, say so plainly: the build is verified against source and the detector only, and the user should check the render.

When the work was delegated through `using-subagents`, recommend the optional `ui-reviewer` agent for an independent visual review; the coordinator decides whether to schedule it.

Finish with a short report: what was built, which direction it follows, what was verified (and how), what remains open, and which illustrative content or imagery the user must replace with real material. Offer `/ui-ux-expertise document` when a new world was built and no design-system file records it; never write one unasked.
