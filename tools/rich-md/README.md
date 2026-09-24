# Rich Markdown

Local Google Docs-style editing for one repository Markdown file at a time.

```sh
scripts/rich-md research/README.md
```

The launcher installs project-local Node dependencies on first use, builds the UI, starts or reuses a server bound to `127.0.0.1`, and opens a Chrome app window when Chrome is available. Server identity, PID, port, and a random session token are kept under `$TMPDIR/excerlock-rich-md`, not in the repository.

Files must already exist, have a `.md` extension, and resolve inside this repository. Saves use SHA-256 conflict checks and atomic same-directory replacement. Markdown features the rich converter cannot safely preserve (including frontmatter, tables, raw HTML, reference links, and directives) make the document read-only instead of risking data loss.

Run verification with:

```sh
cd tools/rich-md
npm test
npm run build
```
