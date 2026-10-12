# Integrations

Composition and external-service adapters live outside sections so each section retains its own data and decisions.

- [contacts-mcp](contacts-mcp/README.md): connects canonical people/handles and messages to creator operations, reusing its approval inbox, inbound pipeline and scheduled jobs. Configure `CONTACTS_MCP_URL` and `CONTACTS_MCP_TOKEN` in the repository's private `.env`; never commit or log their values. No services are deployed automatically.
- [Crawlee / Crawl4AI](crawlee-crawl4ai/README.md): local web capture and Markdown extraction, with its own environment and tests.
- [Mem0 local](mem0-local/README.md): project memory policy and registration checks.
