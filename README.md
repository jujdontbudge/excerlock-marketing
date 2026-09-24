# ExcerLock Marketing

Marketing research and creative production for ExcerLock, an app that blocks chosen apps until the user walks, hits a step goal or goes to the gym. The app itself lives in a separate repository.

Agents start at `AGENTS.md`. The layout and its rules are drawn in `docs/repo-map.excalidraw` (open it at excalidraw.com).

## Layout

| Folder | What's in it |
|---|---|
| `sections/` | One folder per kind of marketing work. Today: `slideshows/`, organic TikTok photo slideshows. |
| `accounts/` | Our TikTok accounts: who each character is, and her reference images (gitignored). |
| `core/` | Skills and workflows every section uses (research, image prompting, style clone, image review, video, make-universal) and `product.md`. |
| `library/` | Style digests of other creators' photos. |
| `research/` | Finished evidence reports. |
| `scripts/`, `integrations/`, `tools/` | `lint`, `link-skills`, the crawler, Mem0 and the rich Markdown editor. |
| `docs/adr/` | Why the big decisions were made. |

## Everyday commands

- `pi-marketing`: start Pi in this workspace.
- `scripts/lint`: check the module rules and links.
- `scripts/link-skills`: register skills after adding one.
- `scripts/rich-md FILE.md`: edit a Markdown file in a rich editor.
