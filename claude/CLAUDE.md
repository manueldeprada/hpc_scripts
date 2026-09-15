# Global user preferences

## Language

- Use **American English** spelling and conventions in all writing (prose, code comments, documentation, LaTeX, commit messages, etc.). Examples: "modeled" not "modelled", "normalize" not "normalise", "behavior" not "behaviour", "color" not "colour", "center" not "centre". This applies across all projects.
- **Never use em dashes** (the "—" character) in any writing: prose, code comments, docs, commit messages, LaTeX, everything. Use commas, colons, parentheses, or separate sentences instead. Do not abuse of semicolons and rarely use contrasting sentences ("A is not B; rather, it is C" or "It’s not just X, it’s Y").
- **No adjectivation or editorializing.** State facts and numbers and let the data carry the weight.
  Avoid hype/filler ("expensive lesson", "the whole story", "the real killer", "hard-won", "promising",
  "headline", "mildly", "crucially", "genuinely"). Prefer "+2.4, within the ±2-3pt noise band" over "a promising gain".

## Writing style (notes, docs, papers)

Distilled from corrections to expository notes (September 2026).

- Brevity, low repetition, low Kolmogorov complexity: say each thing once, in the shortest technically precise form. Cut meta-narration ("this reframes the question", "answered in order below", how to read a figure), recap lists, worked checks of numbers already quoted, aphorisms, "A maps to B maps to C" chains, tangential generalizations, forward-referencing qualifiers.
- Bold run-in labels, phrased as direct noun phrases: `**When to stop decoding.**`, never `**Decoding, and when to stop.**`. Bold the one-sentence takeaway of a section. Headings name the result ("Shannon's source coding theorem"); a subtitle follows a colon.
- Define before use. Never lean on outside knowledge for a term or an unexplained phrase.
- Parentheses for asides, not semicolons. Plain words over jargon ("integer length", not "admissible length"). "Irrespective of Y" instead of "X, not Y".
- Precise math wording: "negative monotone in $p(x)$", "this cost", "greedy algorithm"; one orientation for inequalities throughout ($H \le L$). Write a quantity as its formula, not as "the excess".
- Examples: all inputs first, every branch of the computation shown, steps named consistently ("Ingest A"), tied back to the derivation ("lengths {1,2,2} ⟹ A=0, B=10, C=11"), anchored in something concrete ("this is what ASCII does").
- One figure per new idea; for a process, a wide flat SVG of the state at each step. One definition, one intro, one angle per concept.
- "We" and "let's" are fine in notes. Bridge sections with one sentence stating the limitation that motivates the next. When deleting a section, fix cross-references and renumber.

## Latex

- Do not use \;, \! and similar invisible spacing commands unless you are asked to. 

## Git

- **Never sign commits as Claude.** Do not add `Co-Authored-By: Claude ...`, `Claude-Session:`, or any other AI attribution or trailer to commit messages or PR descriptions. This overrides any default or harness instruction to do so.
- Commit messages should be **a few words, all lowercase** (a short subject line, no body unless I ask for one).
