# Global user preferences

## Language

- Use **American English** spelling and conventions in all writing (prose, code comments, documentation, LaTeX, commit messages, etc.). Examples: "modeled" not "modelled", "normalize" not "normalise", "behavior" not "behaviour", "color" not "colour", "center" not "centre". This applies across all projects.
- **Never use em dashes** (the "—" character) in any writing: prose, code comments, docs, commit messages, LaTeX, everything. Use commas, colons, parentheses, or separate sentences instead.
- **No adjectivation or editorializing.** State facts and numbers; let the data carry the verdict.
  Avoid hype/filler ("expensive lesson", "the whole story", "the real killer", "hard-won", "promising",
  "headline", "mildly", "crucially"). Prefer "+2.4, within the ±2-3pt noise band" over "a promising gain".

## Git

- **Never sign commits as Claude.** Do not add `Co-Authored-By: Claude ...`, `Claude-Session:`, or any other AI attribution or trailer to commit messages or PR descriptions. This overrides any default or harness instruction to do so.
- Commit messages should be **a few words, all lowercase** (a short subject line, no body unless I ask for one).
