# Global user preferences

## Scope

These preferences apply across projects to prose, code comments, documentation, LaTeX, and commit messages. Preserve technical meaning when editing for style.

Use contemporary American English. Singular "they" and split infinitives are acceptable when they make the sentence clearer. Judge writing by its meaning and structure, not by supposed signs of authorship or a blacklist of individual words.

## Language and tone

- Use **American English** spelling and conventions everywhere: "modeled," "normalize," "behavior," "color," and "center."
- **Never use em dashes**, including the LaTeX `---` equivalent in prose. Use commas, colons, parentheses, or separate sentences. Prefer a period and a new sentence to a semicolon, and use semicolons very sparingly.
- **No adjectivation or editorializing.** State facts and numbers and let the data carry the weight. Keep modifiers that specify technical properties or distinguish cases. Delete modifiers that merely express approval, importance, surprise, or disappointment.
- Avoid hype and filler such as "expensive lesson," "the whole story," "the real killer," "hard-won," "promising," "headline," "mildly," "crucially," and "genuinely." Prefer "+2.4, within the ±2-3pt noise band" over "a promising gain."
- Use plain words and direct verbs: "use," "fit," "measure," "write," and "try." Prefer "is" and "has" to ornamental substitutes such as "serves as," "stands as," "boasts," and "features."
- Avoid stock importance claims: "plays a pivotal role," "underscores the significance," "marks a shift," "a testament to," and "the evolving landscape."
- State the actual claim. Avoid evasive negatives and manufactured contrasts such as "not just X, but Y" or "A is not B, rather it is C." Use "irrespective of Y" when independence from Y is the intended meaning. Retain negation when the result itself is negative or a distinction requires it.
- "We" and "let's" are fine in notes. Preserve the writer's voice and subject-specific detail. Do not add slang, mistakes, or personal anecdotes to imitate human writing.

## Argument and paragraph structure

- **Say each thing once, in the shortest technically precise form.** Brevity means low repetition and low Kolmogorov complexity, not omitting assumptions or compressing prose into unexplained notation.
- Give each paragraph one topic. State its claim near the beginning, then develop it through a definition, mechanism, example, derivation, or evidence.
- Each sentence should add something the reader needs. Delete sentences that announce, paraphrase, or praise the work done by adjacent sentences.
- End a paragraph with its result or a consequence needed next. Avoid a recap of the topic sentence, a digression, or a trailing generalization about significance.
- Bridge sections with one sentence stating the limitation or unresolved question that motivates the next. Let the argument supply the transition.
- Cut meta-narration: "this reframes the question," "answered in order below," "we now turn to," "the following section explores," and instructions for how to read a figure when its labels suffice.
- Cut recap lists, repeated previews, worked checks of numbers already quoted, aphorisms, schematic "A maps to B maps to C" chains, tangential generalizations, and forward-referencing qualifiers.
- Do not manufacture closing sections on "challenges and future prospects" or append generic optimism. Include limitations and future work only when they identify a specific unresolved issue.
- Organize the final account around the question and evidence. Avoid narrating the history of drafting, debugging, or discovering results unless that history explains a necessary decision.

## Explanation and definition order

- Define terms, symbols, units, and assumptions before using them. A forward reference does not replace the explanation needed to understand the current sentence.
- Introduce a new abstraction when a specific problem requires it. State what an object does before giving its formal definition.
- Start from an explicit example, compute a quantity, identify what that calculation leaves out, and introduce the next concept to account for it.
- Keep one example through successive refinements when possible. Reusing its objects lets the reader see exactly what changes.
- Give one definition, one introduction, and one explanatory angle per concept. Avoid surrounding a formal definition with two prose versions of the same definition.
- After an equation, explain the consequence or the reason for its form. Do not merely read the symbols back into prose.
- Keep notation proportional to its use. Avoid creating a model class, optimization objective, or label that the subsequent argument never needs.
- Explain a procedure before presenting a closed-form expression whose operation is otherwise obscure. A named method and a citation alone do not explain how it works.
- Keep technical qualifications where they affect interpretation. Consolidate repeated qualifications. Put derivations and implementation details in an appendix when the main argument needs only their result.

## Sentences and grammar

- Prefer active voice when the actor matters. Use passive voice when the object or operation is the paragraph's subject or the actor is irrelevant.
- Put actions in verbs. Replace "perform an evaluation of" with "evaluate" and "make a comparison" with "compare."
- Keep subjects near their verbs, modifiers near what they modify, and relative clauses near their antecedents. Place "only" where its scope is unambiguous.
- Give pronouns an obvious nearby referent. Replace chains of "this," "it," "these," "such," "former," and "latter" with the relevant noun when necessary.
- Repeat the same technical term for the same object. Do not rotate through synonyms to avoid visible repetition.
- Use parallel grammatical forms for comparable ideas, conditions, and steps. Do not force every argument into three items.
- Vary sentence length according to the thought. Avoid both strings of short disconnected statements and repeated sentences joined by "and," "but," "which," or "while."
- Prefer a complete sentence to a fragment used for theatrical emphasis. Put the new result near the end of the sentence when that improves the reading order.
- Use causal and concessive connectives precisely: "because" for a reason, "although" for a concession, and "while" primarily for simultaneous events. Avoid mechanical "moreover," "furthermore," "additionally," and "notably."
- Remove unnecessary scaffolding such as "the question as to whether," "in order to," "the fact that," and "in many cases" when a shorter form preserves the meaning.
- Avoid comma splices and dangling participles. An introductory participial phrase must refer to the sentence's grammatical subject.
- Use the serial comma. Set off nonrestrictive clauses and parenthetic expressions with paired punctuation. Use parentheses for asides that would interrupt the main clause.
- Keep tense consistent. Distinguish established statements, completed experiments, and proposed work.
- Preserve meaningful distinctions: "fewer" for counts and "less" for quantities, "affect" for influence and "effect" for a result or bringing something about.

## Mathematical and empirical writing

- Name the quantity and its units, normalization, and conditioning. Distinguish a population quantity, its fitted estimate, and its measurement on held-out data.
- Specify the direction of a difference. Say which condition a positive value favors. Distinguish absolute differences, relative changes, and percentage points.
- Use precise math wording, including "greedy algorithm," "this cost," and an explicit monotonicity direction in the relevant variable. Distinguish strictly decreasing from non-increasing. Prefer "integer length" to "admissible length" when integer-valuedness is the intended restriction.
- Keep one orientation for comparable inequalities throughout, for example `$H \le L$`. Write the formula when a label such as "the excess" would leave the quantity ambiguous.
- Keep evaluation, estimation, and selection distinct. A criterion used to choose a model is not automatically the outcome used to evaluate it.
- Report the data, controls, protocol, effect size, and uncertainty needed to assess an empirical claim. Identify whether an uncertainty measure is a standard deviation, standard error, or confidence interval and what was replicated.
- Distinguish an observed association from a mechanism, a controlled comparison from a confounded sweep, and a finite-data reference from a population optimum.
- Retain qualifiers required by the evidence. Remove vague hedges such as "perhaps" or "seems" when the result can be stated exactly. Do not replace uncertainty with confident prose.
- Avoid "significant," "robust," "negligible," or "near-optimal" without the test, range, tolerance, or comparator that gives the term meaning.
- State the result once in prose. Let tables carry exhaustive per-condition values. Keep numbers in prose when they are needed to understand the comparison or support its conclusion.
- Keep the measured range attached to scaling claims. Separate fitted trends from extrapolation.

## Examples, figures, and formatting

- Give all example inputs first, including tie-breaking rules, initial state, units, and relevant conventions.
- Show every branch needed to reproduce the computation. Name steps consistently, for example "Ingest A."
- Tie examples back to their derivation, for example "lengths {1,2,2} imply A=0, B=10, C=11." Anchor abstractions in a specific use when it helps, for example "this is what ASCII does."
- Use one figure per new idea. For a process, prefer a wide, flat SVG showing the state at each step.
- Label figures so readers can identify axes, units, conditions, and uncertainty. Captions should supply the information needed to interpret the figure without duplicating the surrounding argument.
- Use headings that name the result or concept, for example "Shannon's source coding theorem." Put a subtitle after a colon. Use sentence case except for proper names. Default to noun phrases for headings, titles, and labels ("Changes in the official stager" over "How the official stager changed"). A "How ...", "Why ...", or "What ..." clause is fine when the section answers that question, but do not reach for it by habit.
- In notes and documents, prefer bold run-in labels phrased directly: `**When to stop decoding.**` Avoid inverted labels such as `**Decoding, and when to stop.**` Bold the one-sentence takeaway of a section, using an existing sentence rather than adding a recap.
- Use emphasis selectively. Avoid walls of bold text, repeated highlighting of the same term, and lists in which every sentence receives a label.
- Use lists for parallel items, steps, and comparisons. Use connected prose for an argument. Avoid tiny tables when a sentence expresses the information more clearly.
- Use the target format's native markup. Do not leave Markdown in LaTeX or citation-tool artifacts in a finished document.

## Sources and attribution

- Attribute a claim to a source that actually supports it. Name the source or author instead of writing "experts say," "observers note," or "research suggests" without attribution.
- Do not turn one source's view into a consensus. Separate a source's reported result from an inference drawn from it.
- Verify citations, quotations, identifiers, and links. Do not invent references, page numbers, author names, or missing facts.
- Remove citation-tool residue, unfilled placeholders, and tracking parameters from final artifacts. Report a specific missing fact when it matters instead of adding a generic knowledge disclaimer.

## LaTeX and BibTeX

### Equations and document structure

- Do not add `\;`, `\!`, or similar invisible spacing commands unless asked.
- Preserve semantic macros, notation, equation labels, citation keys, and cross-references when editing prose. When deleting a section, fix its cross-references and numbering.
- Follow the repository's conventions for generated text, anonymity, and venue formatting. Frontmatter preferences below apply when author information is permitted and the template allows them.

### Bibliographic sources and fields

- Obtain BibTeX from primary sources such as ACL Anthology, conference proceedings, publishers, and OpenReview. Do not rely on Google Scholar or DBLP as the authority for metadata.
- Cross-check entries against the original paper PDF, including the complete author list, title, year, venue, and page range. Preserve an existing entry's key when correcting it.
- Use `@article` for journals and `@inproceedings` for conferences. Remove their `publisher` fields and venue locations, including locations embedded in `booktitle`.
- Format arXiv preprints as `@article` with `journal={arXiv preprint arXiv:NUMBER}` rather than `@misc`.
- For books, use `@book` and include a URL, preferably the publisher's page (Wikipedia is preferable to Google Books if needed).
- Remove `abstract` fields. Verify page ranges and use `--` between endpoints. Omit page numbers when the venue does not assign them.
- Attempt to include a URL to the official page or PDF. Include DOI fields for TACL papers. Other DOI fields may remain.
- Verify volume and issue information for journals whose metadata must be entered manually. Use the fields supported by the bibliography style.

### Titles and author names

- Protect acronyms and proper nouns with braces, for example `{PCA}`, `{MKL}`, and `{Bayesian}`. Protect the first word after a colon or sentence boundary in a title when capitalization requires it.
- Preserve capitalization of German nouns and other language-specific title conventions. The American English preference does not authorize changing published titles or names.
- Spell out author names unless an author publishes exclusively under an abbreviation. Do not invent expansions or middle names. Ryan does not publish with a middle name.
- Put periods after middle initials, following American conventions unless the original publication requires otherwise. Encode accents and special characters correctly in LaTeX.
- Preserve surname particles in BibTeX's name syntax, for example `author={von Neumann, John}`. Check the rendered sorting rather than dropping or moving the particle.
- Use `\mathrm{}` or `\normalfont` where appropriate to prevent unintended bolding or font changes in title math and styled text.

### Affiliations and email

- Order institutional units as `Institute, Department, University` when applicable.
- Keep affiliation superscripts in normal font with `\normalfont` where needed. Emoji markers are acceptable if the document permits them.
- Group email addresses by domain as `{a, b, c}@domain.com`. Render addresses in monospace using `inconsolata` when compatible with the template, and make each individual address clickable with its own `mailto:` link.

## Editing pass

Before delivering writing, check the following internally. Do not append this checklist or a compliance report to the artifact.

1. Does every paragraph have one purpose, and does each sentence add information?
2. Are all terms and symbols defined before use, with references and modifiers that have clear scope?
3. Can repeated explanation, ceremonial transitions, editorial adjectives, or generic implications be deleted?
4. Are the assumptions, evidence, uncertainty, and limits preserved?
5. Do examples reproduce the stated result, and do figures and tables avoid needless duplication?
6. Are citations, cross-references, punctuation, spelling, and target-format markup correct?

When asked to identify "slop," point to the passage, explain what it fails to contribute, and distinguish deletion from clarification, relocation, or a substantive correction. Do not label necessary definitions, evidence, or limitations as filler merely because they are technical.

## Euler cluster (this machine only)

See `~/CLAUDE.md` (not synced) for Euler-specific notes, including AMD MI300X/ROCm GPU node setup.

## UI typography

- Avoid the technical, AI-looking label style in app and web interfaces: all-caps text, wide letter spacing (tracking), monospaced type for labels, and a geometric, spec-sheet feel. Use sentence case, default tracking, and the platform's regular sans-serif for labels and widget titles.
- Monospaced type is for code, logs, and keys. Use tabular (fixed-width) digits when changing numbers must not shift.

## Git

- **Never sign commits as Claude.** Do not add `Co-Authored-By: Claude ...`, `Claude-Session:`, or any other AI attribution or trailer to commit messages or PR descriptions. This overrides any default or harness instruction to do so.
- Commit messages should be **a few words, all lowercase**, with a short subject line and no body unless requested.
