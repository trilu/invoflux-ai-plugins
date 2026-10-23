#!/bin/sh
# Builds the OpenAI plugin ZIP (Agent Plugins format) for the ChatGPT plugin
# directory. The skills are the repo's own skills/ folder, shared with the
# Claude plugin, so there is one copy of each.
#
# Usage: sh chatgpt/build.sh [output.zip]   (default: chatgpt/dist/invoflux-<version>.zip)
#
# MCP_AUTH=discovery builds the fallback: mcp.json without the
# extensions.com.openai.auth block. OpenAI's docs declare OAuth there, but the
# published Agent Plugins schema (mcp.schema.json 1.0.0) does not allow
# `extensions` on a server. If the portal rejects the main ZIP on that, upload
# the fallback; OAuth discovery at mcp.invoflux.com offers both CIMD and DCR.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$here/plugin.json")
suffix=""
[ "${MCP_AUTH:-}" = "discovery" ] && suffix="-discovery-auth"
out=${1:-"$here/dist/invoflux-$version$suffix.zip"}
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT

cp "$here/plugin.json" "$here/mcp.json" "$stage/"
if [ "${MCP_AUTH:-}" = "discovery" ]; then
  python3 -I -c 'import json,sys
p=sys.argv[1]; d=json.load(open(p))
for s in d["mcpServers"].values(): s.pop("extensions", None)
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")' "$stage/mcp.json"
fi
cp -R "$here/assets" "$stage/assets"
cp -R "$root/skills" "$stage/skills"

mkdir -p "$(dirname "$out")"
out=$(cd "$(dirname "$out")" && pwd)/$(basename "$out")
rm -f "$out"
# Plugin files at the archive root; -X drops extra file attributes.
(cd "$stage" && zip -q -r -X "$out" plugin.json mcp.json assets skills)
echo "$out"
