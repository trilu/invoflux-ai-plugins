# Invoflux for ChatGPT

The package uploaded to the OpenAI plugin directory (platform.openai.com, Plugins). It uses the portable Agent Plugins format: `plugin.json` (listing, review test cases, release notes and translations under `extensions.com.openai`), `mcp.json` (the remote server, OAuth with CIMD; DCR stays available as the fallback) and `assets/logo.png`. The skills are the repo's own `skills/` folder, shared with the Claude plugin, and are copied in at build time.

No hooks, no app references, no credentials. Reviewer credentials go in the portal's Review details, never in this package.

```
sh chatgpt/build.sh                          # chatgpt/dist/invoflux-<version>.zip
MCP_AUTH=discovery sh chatgpt/build.sh       # fallback without the auth block in mcp.json
python3 -I chatgpt/validate.py chatgpt/dist/invoflux-<version>.zip
```

`validate.py` checks the published JSON schemas and the final submission rules from OpenAI's docs (limits, images, five positive and three negative test cases, translations, no secrets).

A listing, logo, skill or translation change needs a new ZIP with a higher `version`. Tool changes on the server do not: OpenAI rescans the server.
