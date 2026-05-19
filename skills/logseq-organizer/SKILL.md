---
name: logseq-organizer
description: Use when the user asks to organize, tidy, review, restructure, merge, rename, tag, or summarize their Logseq graph, pages, journals, project notes, personal knowledge base, or work notes.
---

# Logseq Organizer

## Core Principle

The user's Logseq is a flexible capture space. Do not force rigid templates, PARA/GTD systems, heavy taxonomies, or "perfect" note structures. The agent's job is to organize after the fact while preserving the user's natural input style.

## Default Approach

- Preserve free-form journal capture as the primary writing surface.
- Add structure by creating lightweight indexes, aliases, links, tags, and cleanup queues.
- Prefer reversible, low-risk changes over moving large blocks or rewriting personal notes.
- Keep user wording unless clarity requires small edits.
- Separate "capture" from "curation": the user can write loosely; the agent can later synthesize, connect, and normalize.

## Workflow

1. Inspect the graph before changing it.
   - Prefer the Logseq MCP tools when available: `list_pages`, `get_page_content`.
   - If editing files directly, use the graph root's `pages/` and `journals/` files and check git status first.
2. Identify the user's actual axes from existing notes.
   - For work notes, look for project tags, repo names, systems, collaborators, recurring tasks, and recent journal references.
   - Treat frequent existing terms as evidence; do not invent a new classification scheme first.
3. Make the smallest useful organizing change.
   - Good: a project overview page, alias normalization, broken-link cleanup, duplicate-page notes, backlinks, a short "待清理" list.
   - Bad: mandatory templates, broad page rewrites, moving old journal history into a new hierarchy, deleting pages without explicit approval.
4. Normalize gently.
   - Fix obvious typo/case drift such as `Dobuan` vs `Douban` or `Douban/anti` vs `Douban/Anti` when the target is clear.
   - Preserve useful short aliases such as `Yushi` while pointing new work toward the canonical page.
5. Report what changed and what remains risky.
   - Mention any sensitive data discovered at a high level only; do not quote secrets.
   - If Logseq auto-saves or creates backup files, note that separately.

## Editing Rules

- Do not introduce rigid templates unless the user explicitly asks for them.
- If a checklist or schema is useful, put it in a cleanup/index page as optional guidance, not as a required note-taking format.
- Do not delete or merge pages unless the user explicitly approves the exact pages.
- Do not expose secrets in the final answer. Say "明文密钥/账号材料" instead of repeating values.
- If a previous assistant-created structure feels too rigid, remove or soften it before adding more structure.

## Preferred Outputs

- A lightweight "总览/索引" page for navigation.
- A "待清理队列" with concrete duplicate pages, typo pages, stale links, and sensitive-material migration reminders.
- Short naming conventions based on the graph's existing usage.
- Focused mechanical edits for clear duplicate references.

## Anti-Patterns

- Turning Logseq into a project management database.
- Requiring every page to have frontmatter, fields, or a fixed section order.
- Rewriting journal entries to match a template.
- Creating a taxonomy before reading the user's actual notes.
- Treating personal notes like product documentation.
