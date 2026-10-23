"""Checks the ChatGPT plugin ZIP before upload.

Two layers, both from OpenAI's own documentation (read 2026-10-23):
1. The published Agent Plugins JSON schemas for plugin.json and mcp.json.
2. The final directory-submission rules from
   https://developers.openai.com/plugins/deploy/submission-errors and
   https://developers.openai.com/plugins/deploy/submission (limits, paths,
   images, review cases, translations, no hooks / apps / secrets).
Plus Invoflux's own public-copy rule: no em dashes.

Usage: python3 -I chatgpt/validate.py chatgpt/dist/invoflux-1.0.0.zip
Exit code 0 = no errors.
"""
import json, re, struct, sys, unicodedata, urllib.request, zipfile

SCHEMAS = {
    "plugin.json": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
    "mcp.json": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
}
CATEGORIES = {"Productivity", "Creativity", "Developer Tools", "Business & Operations",
              "Data & Analytics", "Communication", "Education & Research", "Security",
              "Finance", "Healthcare", "Travel", "Entertainment", "Other"}
errors = []

def err(msg): errors.append(msg)

def supported(text, multiline=False):
    for ch in text:
        if ch == "\n" and multiline: continue
        if unicodedata.category(ch) in ("Cc", "Cf", "Zl", "Zp"): return False
    return text.strip() != ""

def one_line(field, text, limit):
    if not isinstance(text, str) or not supported(text): err(f"{field}: empty or unsupported characters")
    elif len(text) > limit: err(f"{field}: {len(text)} characters, limit {limit}")

def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n": return None
    return struct.unpack(">II", data[16:24])

def walk_strings(node, path=""):
    if isinstance(node, str): yield path, node
    elif isinstance(node, dict):
        for k, v in node.items(): yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node): yield from walk_strings(v, f"{path}[{i}]")

zf = zipfile.ZipFile(sys.argv[1])
names = zf.namelist()
files = {n: zf.read(n) for n in names if not n.endswith("/")}

# Archive layout
for n in names:
    if n.startswith("/") or "\\" in n or ".." in n.split("/") or n != n.strip():
        err(f"archive path not allowed: {n}")
    if n.count("/") >= 20: err(f"archive path too deep: {n}")
for banned in ("hooks/", ".app.json", ".claude-plugin/", ".codex-plugin/"):
    if any(n.startswith(banned) or n == banned for n in names): err(f"archive contains {banned}")
for req in ("plugin.json", "mcp.json"):
    if req not in files: err(f"missing {req} at the archive root")
if errors: print("\n".join(errors)); sys.exit(1)

manifest = json.loads(files["plugin.json"].decode("utf-8"))
mcp = json.loads(files["mcp.json"].decode("utf-8"))

# 1. Published schemas
try:
    import jsonschema
    # OpenAI's docs declare OAuth under each server's extensions.com.openai,
    # which the published schema does not list: check the rest against the
    # schema and that block against the documented shape below.
    mcp_core = json.loads(json.dumps(mcp))
    for s in mcp_core.get("mcpServers", {}).values():
        ext = s.pop("extensions", None)
        if ext is not None and set(ext) != {"com.openai"}: err("server extensions: only com.openai is documented")
    for fname, doc in (("plugin.json", manifest), ("mcp.json", mcp_core)):
        schema = json.load(urllib.request.urlopen(SCHEMAS[fname], timeout=20))
        for e in jsonschema.Draft202012Validator(schema).iter_errors(doc):
            err(f"{fname} schema: {'/'.join(map(str, e.path))}: {e.message}")
except ImportError:
    err("python jsonschema is not installed; schema check not run")

# 2. Final submission rules
if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", manifest.get("name", "")): err("name format")
if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", manifest.get("version", "")): err("version is not semver")
desc = manifest.get("description", "")
if not supported(desc, True) or len(desc) > 1024: err(f"description: {len(desc)} characters, limit 1024")
if not manifest.get("author", {}).get("name"): err("author.name missing")

oa = manifest.get("extensions", {}).get("com.openai", {})
ui = oa.get("interface", {})
one_line("displayName", ui.get("displayName"), 30)
one_line("shortDescription", ui.get("shortDescription"), 30)
one_line("developerName", ui.get("developerName"), 80)
ld = ui.get("longDescription", "")
if not supported(ld, True) or len(ld) > 4000: err(f"longDescription: {len(ld)} characters, limit 4000")
if ui.get("category") not in CATEGORIES: err(f"category {ui.get('category')!r} is not supported")
caps = ui.get("capabilities", [])
if len(caps) > 20: err("more than 20 capabilities")
for c in caps: one_line("capability", c, 120)
for f in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
    u = ui.get(f, "")
    if not re.fullmatch(r"https://[^/@\s]+(/\S*)?", u) or len(u) > 1024: err(f"{f}: not an HTTPS URL without credentials")
prompts = ui.get("defaultPrompt", [])
prompts = [prompts] if isinstance(prompts, str) else prompts
if len(prompts) > 3: err("more than 3 default prompts")
for p in prompts:
    one_line("defaultPrompt", p, 128)
    if "@" in p: err(f"defaultPrompt has an @mention: {p}")
norm = [" ".join(unicodedata.normalize("NFKC", p).split()).casefold() for p in prompts]
if len(set(norm)) != len(norm): err("default prompts are not unique")

for key in ("logo", "composerIcon", "logoDark", "composerIconDark"):
    path = ui.get(key)
    if path is None: continue
    if not path.startswith("./"): err(f"{key}: path must start with ./")
    data = files.get(path[2:])
    if data is None: err(f"{key}: {path} is not in the archive"); continue
    if len(data) > 5 * 1024 * 1024: err(f"{key}: larger than 5 MiB")
    size = png_size(data)
    if not size: err(f"{key}: not a PNG (only PNG is checked here)")
    elif size[0] != size[1] or size[0] < 48 or size[0] > 4096: err(f"{key}: {size[0]}x{size[1]}, must be square, 48 to 4096 px")
if not ui.get("logo"): err("logo is required for submission")
if ui.get("screenshots"): err("screenshots: remove, or add one 706 px wide image per starter prompt")

review = oa.get("review", {})
cases = review.get("test_cases", {})
pos, neg = cases.get("positive", []), cases.get("negative", [])
if len(pos) != 5: err(f"{len(pos)} positive test cases, need exactly 5")
if len(neg) != 3: err(f"{len(neg)} negative test cases, need exactly 3")
for c in pos + neg:
    for f in ("description", "prompt"):
        if not c.get(f, "").strip(): err(f"test case missing {f}")
for c in pos:
    for f in ("tools_triggered", "expected_behavior"):
        if not c.get(f, "").strip(): err(f"positive case missing {f}: {c.get('prompt')}")
for banned in ("test_credentials", "reviewer_instructions"):
    if banned in review: err(f"review.{banned} is rejected in the ZIP")
if not isinstance(review.get("commerce"), bool): err("review.commerce must be a boolean")
pub = oa.get("publication", {})
if not pub.get("release_notes", "").strip(): err("release_notes missing")
for loc, tr in (pub.get("translations") or {}).items():
    if tr.get("subtitle") is not None: one_line(f"translations.{loc}.subtitle", tr["subtitle"], 30)
    d = tr.get("description")
    if d is not None and (not supported(d, True) or len(d) > 4000): err(f"translations.{loc}.description: {len(d)} characters or unsupported text")

# mcp.json: one remote server, OAuth via cimd/dcr, nothing secret
servers = mcp.get("mcpServers", {})
if len(servers) != 1: err(f"{len(servers)} MCP servers; plugin-level test cases need exactly one")
for name, s in servers.items():
    if not str(s.get("url", "")).startswith("https://"): err(f"server {name}: url must be HTTPS")
    if s.get("headers"): err(f"server {name}: public submission rejects headers")
    auth = s.get("extensions", {}).get("com.openai", {}).get("auth", {})
    if auth and auth.get("type") not in ("oauth", "mixed"): err(f"server {name}: auth.type must be oauth or mixed")
    client = auth.get("client", {})
    if client and client.get("mode") not in ("provided", "dcr", "cimd"): err(f"server {name}: client.mode")
    if client.get("mode") in ("cimd", "dcr") and set(client) - {"mode"}: err(f"server {name}: {client['mode']} client must carry no client fields")
blob = json.dumps(mcp) + json.dumps(manifest)
if re.search(r'"(clientSecret|client_secret|apiKey|token)"', blob): err("a secret-looking field is present")

# Skills
skills = sorted({n.split("/")[1] for n in files if n.startswith("skills/") and n.count("/") >= 2})
if not skills: err("a public submission ZIP needs at least one skill")
for sk in skills:
    body = files.get(f"skills/{sk}/SKILL.md")
    if body is None: err(f"skills/{sk}: no SKILL.md"); continue
    text = body.decode("utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m: err(f"skills/{sk}: no YAML front matter"); continue
    fm = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    if not fm.get("name") or not fm.get("description"): err(f"skills/{sk}: name and description required")
    if len(f"{manifest['name']}:{fm.get('name','')}") > 64: err(f"skills/{sk}: plugin:skill identity over 64 characters")
    if not m.group(2).strip(): err(f"skills/{sk}: empty instructions")
    if re.search(r"\bClaude\b", text): err(f"skills/{sk}: names Claude; use provider-neutral wording")

# Invoflux public-copy rule
for path, s in list(walk_strings(manifest)) + [(f"skills/{sk}", files[f"skills/{sk}/SKILL.md"].decode()) for sk in skills]:
    if "—" in s: err(f"em dash in {path}")

if errors:
    print("\n".join(f"ERROR {e}" for e in errors)); sys.exit(1)
print(f"OK: {len(files)} files, {len(skills)} skills, {len(pos)}+{len(neg)} test cases, "
      f"{len(pub.get('translations') or {})} translations")
