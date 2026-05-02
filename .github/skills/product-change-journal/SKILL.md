---
name: product-change-journal
description: "Create and maintain a plain-language version history log for product design and development changes. Use when the user asks to document updates, key decisions, what changed, and why in non-technical language."
argument-hint: "Short summary of the latest work to log"
---

# Product Change Journal

## What This Skill Does
This skill keeps a running version log in a markdown file so each important update is captured clearly for non-technical readers.

The log covers:
- Product design updates
- Development progress written in plain language
- Key decisions and why they were taken
- What changed in each version
- What is next

## When To Use
Use this skill when the user asks to:
- Document changes after work is done
- Keep a version-by-version project history
- Summarize key decisions for stakeholders
- Write updates in simple, non-technical wording

## Output File
Always write to:
- [docs/product-change-log.md](../../../docs/product-change-log.md)

If the file does not exist, create it first using the structure in [log template](./assets/log-template.md).

## Procedure
1. Review recent work from this chat and changed files.
2. Choose the next integer version using this format: `v1`, `v2`, `v3`, and pair it with today's date.
3. Add a new entry at the top under "Change Entries" so newest entries always appear first.
4. Write the entry in clear non-technical language:
- Avoid jargon and implementation details.
- Explain customer or business impact.
- Keep sentences short and easy to scan.
5. Include all sections from the template:
- Date
- Version
- What We Improved
- Product Design Updates
- Development Updates (Plain Language)
- Key Decisions and Why
- Files/Areas Updated
- Risks or Follow-ups
- Next Steps
6. Keep factual accuracy:
- Do not invent decisions or outcomes.
- If details are missing, state assumptions briefly.
7. Save the file.

## Quality Checklist
Before finishing, confirm:
- Entry has a new `vN` version number and date
- Language is understandable by non-technical readers
- Design, development, and decisions are all covered
- Changes are specific, not vague
- Next steps are listed

## Example Prompts
- "Log today’s updates using Product Change Journal."
- "Add a new version entry in plain language."
- "Summarize this work for stakeholders in the change log."
star