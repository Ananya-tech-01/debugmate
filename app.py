import streamlit as st
import re
import json
import datetime
from io import BytesIO

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DebugMate – Smart Error Translator",
    page_icon="🛠",
    layout="wide"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --bg:       #090e1a;
    --bg2:      #0f1729;
    --bg3:      #151f35;
    --border:   #1e2d4a;
    --accent:   #00d4ff;
    --accent2:  #7c3aed;
    --green:    #10b981;
    --yellow:   #f59e0b;
    --red:      #ef4444;
    --blue:     #3b82f6;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --mono:     'Fira Code', monospace;
    --sans:     'DM Sans', sans-serif;
}

*, body, .stApp { background-color: var(--bg) !important; color: var(--text); font-family: var(--sans); }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; max-width: 1400px !important; }

/* Header */
.dm-header {
    display: flex; align-items: center; gap: 1rem;
    padding: 1.2rem 0 0.5rem 0; margin-bottom: 0.5rem;
}
.dm-logo {
    font-family: var(--mono); font-size: 1.8rem; font-weight: 700;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}
.dm-tagline { color: var(--muted); font-size: 0.85rem; margin-top: 2px; }

/* Cards */
.dm-card {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 14px; padding: 1.4rem; margin: 0.8rem 0;
    transition: border-color 0.2s;
}
.dm-card:hover { border-color: #2a3f6a; }

/* Severity borders */
.sev-critical { border-left: 3px solid var(--red); }
.sev-high     { border-left: 3px solid var(--yellow); }
.sev-medium   { border-left: 3px solid var(--blue); }
.sev-low      { border-left: 3px solid var(--green); }

/* Badges */
.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; font-family: var(--mono); letter-spacing: 0.5px; }
.badge-critical { background: rgba(239,68,68,0.15); color: var(--red); border: 1px solid rgba(239,68,68,0.3); }
.badge-high     { background: rgba(245,158,11,0.15); color: var(--yellow); border: 1px solid rgba(245,158,11,0.3); }
.badge-medium   { background: rgba(59,130,246,0.15); color: var(--blue); border: 1px solid rgba(59,130,246,0.3); }
.badge-low      { background: rgba(16,185,129,0.15); color: var(--green); border: 1px solid rgba(16,185,129,0.3); }

/* Code blocks */
.dm-code {
    background: #060b14; border: 1px solid var(--border);
    border-radius: 10px; padding: 1rem 1.2rem;
    font-family: var(--mono); font-size: 0.82rem; color: #a8d8ff;
    white-space: pre-wrap; word-break: break-word; line-height: 1.7;
    position: relative; margin: 0.5rem 0;
}
.dm-code-error { border-left: 3px solid var(--red); color: #fca5a5; }
.dm-code-fixed { border-left: 3px solid var(--green); color: #6ee7b7; }

/* Section labels */
.sec-label {
    font-family: var(--mono); font-size: 0.68rem; color: var(--muted);
    text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.4rem;
}

/* Steps */
.step-row { display: flex; gap: 0.8rem; margin: 0.45rem 0; align-items: flex-start; }
.step-num {
    background: var(--bg3); border: 1px solid var(--border); border-radius: 6px;
    min-width: 22px; height: 22px; display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-family: var(--mono); color: var(--accent); font-weight: 700; flex-shrink: 0;
}
.step-txt { font-size: 0.9rem; line-height: 1.55; color: var(--text); }

/* Info banner */
.info-bar {
    background: rgba(0,212,255,0.07); border: 1px solid rgba(0,212,255,0.2);
    border-radius: 8px; padding: 0.6rem 1rem; font-size: 0.83rem; color: #67e8f9;
    margin-bottom: 1rem;
}

/* History item */
.hist-row {
    background: var(--bg3); border: 1px solid var(--border); border-radius: 8px;
    padding: 0.6rem 0.9rem; margin: 0.3rem 0; font-size: 0.82rem;
}

/* Diff view */
.diff-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.5rem; }
.diff-label { font-size: 0.75rem; font-family: var(--mono); margin-bottom: 0.4rem; font-weight: 700; }
.diff-error-label { color: var(--red); }
.diff-fix-label   { color: var(--green); }

/* Copy button style hint */
.copy-hint { font-size: 0.72rem; color: var(--muted); font-family: var(--mono); }

/* Streamlit overrides */
.stTextArea textarea {
    background: var(--bg2) !important; border: 1px solid var(--border) !important;
    color: var(--text) !important; font-family: var(--mono) !important;
    border-radius: 10px !important; font-size: 0.83rem !important;
}
.stTextInput input {
    background: var(--bg2) !important; border: 1px solid var(--border) !important;
    color: var(--text) !important; border-radius: 8px !important;
}
.stSelectbox > div > div {
    background: var(--bg2) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
.stButton button {
    background: linear-gradient(135deg, #0ea5e9, #7c3aed) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-family: var(--sans) !important; font-weight: 600 !important;
    transition: opacity 0.2s !important;
}
.stButton button:hover { opacity: 0.85 !important; }
.stDownloadButton button {
    background: var(--bg3) !important; border: 1px solid var(--border) !important;
    color: var(--text) !important; border-radius: 8px !important;
}
.stTabs [data-baseweb="tab-list"] { background: var(--bg2) !important; border-radius: 10px !important; border: 1px solid var(--border) !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; color: var(--muted) !important; font-family: var(--sans) !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { background: var(--bg3) !important; color: var(--accent) !important; }
.stExpander { background: var(--bg2) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }
div[data-testid="stSidebarContent"] { background: var(--bg2) !important; border-right: 1px solid var(--border) !important; }
.stRadio label { color: var(--text) !important; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ERROR DATABASE  (HTTP + Python + Git + JS + SQL)
# ─────────────────────────────────────────────
ERROR_DB = {
    # HTTP
    r"\b400\b|bad request": {"name": "HTTP 400 – Bad Request", "meaning": "The server couldn't understand your request due to invalid syntax or missing data.", "causes": "Missing required fields, malformed JSON, or invalid query parameters.", "fixes": ["Check all required form fields or API parameters.", "Validate JSON body using a JSON validator.", "Review API docs for correct parameter names and types."], "severity": "medium", "category": "HTTP"},
    r"\b401\b|unauthorized": {"name": "HTTP 401 – Unauthorized", "meaning": "You tried to access a resource without valid credentials.", "causes": "Missing or expired token, wrong credentials, or session timeout.", "fixes": ["Log out and log back in.", "Regenerate your API key or token.", "Ensure the Authorization header is sent correctly."], "severity": "high", "category": "HTTP"},
    r"\b403\b|forbidden": {"name": "HTTP 403 – Forbidden", "meaning": "Server understood the request but refuses — you lack permission.", "causes": "Wrong role/permission, IP blocked, or restricted resource.", "fixes": ["Ask your admin to verify your account permissions.", "Confirm you're logged into the correct account.", "Check if your IP is firewalled."], "severity": "high", "category": "HTTP"},
    r"\b404\b|not found": {"name": "HTTP 404 – Not Found", "meaning": "The page or resource you requested doesn't exist.", "causes": "Typo in URL, deleted resource, or broken link.", "fixes": ["Double-check the URL spelling.", "Search the homepage for the moved content.", "Confirm the API endpoint path in documentation."], "severity": "low", "category": "HTTP"},
    r"\b500\b|internal server error": {"name": "HTTP 500 – Internal Server Error", "meaning": "The server crashed while processing your request.", "causes": "Bug in server code, database failure, or misconfiguration.", "fixes": ["Refresh and retry after a minute.", "Check server logs for the exact traceback.", "Report to your IT/dev team with timestamp."], "severity": "critical", "category": "HTTP"},
    r"\b502\b|bad gateway": {"name": "HTTP 502 – Bad Gateway", "meaning": "A gateway server got an invalid response from the upstream server.", "causes": "Upstream service down, overloaded, or returning bad data.", "fixes": ["Wait a few minutes and retry.", "Check status pages for outages.", "Restart the upstream service or check load balancer config."], "severity": "critical", "category": "HTTP"},
    r"\b503\b|service unavailable": {"name": "HTTP 503 – Service Unavailable", "meaning": "Server is temporarily down — maintenance or overload.", "causes": "Heavy traffic, scheduled maintenance, or resource exhaustion.", "fixes": ["Retry in a few minutes.", "Check the service's status page.", "Monitor CPU/RAM/disk if you manage the server."], "severity": "critical", "category": "HTTP"},
    # Python
    r"nameerror|name '.*' is not defined": {"name": "Python – NameError", "meaning": "You used a variable or function that doesn't exist yet.", "causes": "Typo in name, variable used before assignment, or wrong scope.", "fixes": ["Check spelling of the variable/function name.", "Define the variable before using it.", "Verify scope — is it inside/outside a function?"], "severity": "medium", "category": "Python"},
    r"\btypeerror\b": {"name": "Python – TypeError", "meaning": "An operation was applied to an incompatible data type.", "causes": "Mixing types (string + int), calling non-callables, wrong arg count.", "fixes": ["Use print(type(var)) to inspect types.", "Convert types explicitly: int(), str(), float().", "Check the function signature for expected argument types."], "severity": "medium", "category": "Python"},
    r"indexerror|list index out of range": {"name": "Python – IndexError", "meaning": "You accessed a list/array at a position that doesn't exist.", "causes": "Index exceeds list length, empty list, or off-by-one error.", "fixes": ["Check len(list) before indexing.", "Use range(len(list)) in loops.", "Handle empty list case with: if list:"], "severity": "medium", "category": "Python"},
    r"\bkeyerror\b": {"name": "Python – KeyError", "meaning": "You accessed a dict key that doesn't exist.", "causes": "Wrong key name, missing data, or key was deleted.", "fixes": ["Use dict.get('key', default) to avoid crashes.", "Print dict.keys() to see valid keys.", "Check for trailing spaces or wrong casing in keys."], "severity": "medium", "category": "Python"},
    r"importerror|modulenotfounderror": {"name": "Python – ModuleNotFoundError", "meaning": "Python can't find the package you're importing.", "causes": "Package not installed, wrong venv active, or typo in module name.", "fixes": ["Run: pip install <module_name>", "Confirm you activated the correct virtual environment.", "Check for typos in the import statement."], "severity": "high", "category": "Python"},
    r"\bsyntaxerror\b": {"name": "Python – SyntaxError", "meaning": "Your code has a grammar mistake Python can't parse.", "causes": "Missing colon, unclosed brackets, or invalid syntax.", "fixes": ["Check the line number in the error message.", "Look for missing colons (:) after if/for/def/class.", "Check for mismatched parentheses or brackets."], "severity": "high", "category": "Python"},
    r"valueerror": {"name": "Python – ValueError", "meaning": "A function received an argument of correct type but invalid value.", "causes": "Converting invalid string to int, wrong array shape, empty sequence.", "fixes": ["Validate input before passing to the function.", "Use try/except around type conversions.", "Check data shape/format matches what the function expects."], "severity": "medium", "category": "Python"},
    r"zerodivisionerror": {"name": "Python – ZeroDivisionError", "meaning": "Your code attempted to divide a number by zero.", "causes": "Denominator variable is 0, empty list average, or bad math logic.", "fixes": ["Add a check: if denominator != 0: before dividing.", "Use try/except ZeroDivisionError to handle gracefully.", "Trace where the denominator gets its value."], "severity": "medium", "category": "Python"},
    r"recursionerror|maximum recursion depth": {"name": "Python – RecursionError", "meaning": "A function called itself too many times without stopping.", "causes": "Missing or unreachable base case in a recursive function.", "fixes": ["Add/fix the base case in your recursive function.", "Use sys.setrecursionlimit() cautiously if needed.", "Consider converting to an iterative loop instead."], "severity": "high", "category": "Python"},
    # Git errors (Level 1 improvement #3)
    r"fatal: not a git repository": {"name": "Git – Not a Repository", "meaning": "You ran a git command outside of a git-tracked folder.", "causes": "Wrong directory, forgot to run git init, or .git folder deleted.", "fixes": ["Run git init to initialize a new repo here.", "Use cd to navigate into your project folder first.", "Check if the .git folder exists: ls -la"], "severity": "medium", "category": "Git"},
    r"fatal: remote origin already exists": {"name": "Git – Remote Already Exists", "meaning": "You tried to add a remote named 'origin' that already exists.", "causes": "git remote add origin run twice, or origin set to wrong URL.", "fixes": ["Run: git remote set-url origin <new_url> to update it.", "Run: git remote -v to see current remotes.", "Remove and re-add: git remote remove origin then git remote add origin <url>"], "severity": "low", "category": "Git"},
    r"merge conflict|conflict.*merge|automatic merge failed": {"name": "Git – Merge Conflict", "meaning": "Two branches changed the same lines and Git can't auto-merge.", "causes": "Same file edited in both branches, diverged histories.", "fixes": ["Open conflicting files and resolve markers: <<<<<<<, =======, >>>>>>>", "After resolving, run: git add . then git commit", "Use a visual merge tool: git mergetool"], "severity": "high", "category": "Git"},
    r"error: failed to push|rejected.*non-fast-forward": {"name": "Git – Push Rejected", "meaning": "Your push was rejected because the remote has commits you don't have.", "causes": "Someone else pushed before you, or histories diverged.", "fixes": ["Run: git pull --rebase origin main to sync first.", "Then push again: git push origin main", "Force push only if you're sure: git push --force-with-lease"], "severity": "high", "category": "Git"},
    r"detached head": {"name": "Git – Detached HEAD", "meaning": "You checked out a specific commit instead of a branch.", "causes": "git checkout <commit-hash> puts you in detached HEAD state.", "fixes": ["Create a new branch here: git checkout -b my-branch", "Or go back to main: git checkout main", "Your changes are safe — just create a branch to keep them."], "severity": "medium", "category": "Git"},
    # JavaScript errors (Level 1 improvement #3)
    r"referenceerror|is not defined.*js|uncaught referenceerror": {"name": "JS – ReferenceError", "meaning": "You referenced a variable or function that doesn't exist.", "causes": "Typo in variable name, used before declaration, or wrong scope.", "fixes": ["Check spelling of the variable name.", "Ensure the variable is declared (let/const/var) before use.", "Check if it's inside a function scope where it's not visible."], "severity": "medium", "category": "JavaScript"},
    r"typeerror.*undefined|cannot read prop|cannot read properties of": {"name": "JS – TypeError: Cannot Read Properties", "meaning": "You tried to access a property on something that is undefined or null.", "causes": "Object not initialized, async data not loaded yet, or wrong variable name.", "fixes": ["Add null check: if (obj && obj.property)", "Use optional chaining: obj?.property", "Ensure async data is loaded before accessing it."], "severity": "high", "category": "JavaScript"},
    r"syntaxerror.*unexpected token|unexpected token": {"name": "JS – SyntaxError: Unexpected Token", "meaning": "The JavaScript parser found something it didn't expect.", "causes": "Missing comma, unclosed bracket, or invalid JS syntax.", "fixes": ["Check the line/column number in the browser console.", "Look for missing commas in objects/arrays.", "Validate JSON with a JSON linter if parsing JSON."], "severity": "high", "category": "JavaScript"},
    # SQL errors (Level 1 improvement #3)
    r"relation.*does not exist|table.*doesn't exist|no such table": {"name": "SQL – Table Not Found", "meaning": "The query references a table that doesn't exist in the database.", "causes": "Typo in table name, wrong database/schema selected, or table not created.", "fixes": ["Run: SHOW TABLES; (MySQL) or \\dt (PostgreSQL) to list tables.", "Check if you're connected to the correct database.", "Run your CREATE TABLE migration if it hasn't been run."], "severity": "high", "category": "SQL"},
    r"duplicate entry|unique constraint|violates unique": {"name": "SQL – Duplicate Entry / Unique Constraint", "meaning": "You tried to insert a value that already exists in a unique column.", "causes": "Duplicate primary key, re-running inserts, or duplicate email/username.", "fixes": ["Use INSERT IGNORE or ON DUPLICATE KEY UPDATE (MySQL).", "Use INSERT ... ON CONFLICT DO NOTHING (PostgreSQL).", "Check existing data before inserting: SELECT * WHERE column = value"], "severity": "medium", "category": "SQL"},
    r"ora-\d{5}": {"name": "Oracle DB Error (ORA-xxxxx)", "meaning": "An Oracle database error occurred — check the ORA code for specifics.", "causes": "Varies by ORA code — invalid object, permission issue, or connection failure.", "fixes": ["Look up your specific ORA code on Oracle documentation.", "Common fix: ORA-00942 = table not found → check table name/schema.", "ORA-01017 = invalid credentials → verify username/password."], "severity": "high", "category": "SQL"},
    # Network/System
    r"connection refused|econnrefused": {"name": "Connection Refused", "meaning": "The app tried connecting to a service that rejected it.", "causes": "Target service not running, wrong port, or firewall blocking.", "fixes": ["Verify the service is running (MySQL, Redis, etc.).", "Check host and port in your config file.", "Inspect firewall rules blocking the connection."], "severity": "critical", "category": "Network"},
    r"timeout|timed out|etimedout": {"name": "Timeout Error", "meaning": "The operation waited too long for a response and gave up.", "causes": "Slow network, overloaded server, heavy query, or large transfer.", "fixes": ["Check network speed and latency.", "Optimize slow DB queries — add indexes.", "Increase timeout setting in your config."], "severity": "high", "category": "Network"},
    r"nullpointerexception|nonetype.*has no attribute|\battributeerror\b": {"name": "Null / None Reference Error", "meaning": "You used an object or value that is None/null — it was never set.", "causes": "Function returned None, optional data missing, or wrong variable.", "fixes": ["Add null check: if variable is not None:", "Trace where the variable gets assigned — the bug is there.", "Use default values to avoid None: var = func() or default"], "severity": "high", "category": "General"},
    r"permission denied": {"name": "Permission Denied", "meaning": "The OS blocked the action — insufficient access rights.", "causes": "Wrong file permissions, no admin rights, or restricted path.", "fixes": ["Linux/Mac: chmod 755 file or use sudo carefully.", "Windows: Right-click → Run as Administrator.", "Check ownership: ls -la (Linux) or file Properties (Windows)."], "severity": "high", "category": "OS"},
    r"out of memory|memoryerror|\boom\b": {"name": "Out of Memory (OOM)", "meaning": "The program consumed all available RAM.", "causes": "Loading too much data, memory leak, or insufficient RAM.", "fixes": ["Process data in chunks instead of all at once.", "Check for objects that are never released (memory leak).", "Add RAM or use memory-efficient data structures."], "severity": "critical", "category": "System"},
    r"ssl.*error|certificate.*expired|ssl handshake|certificate_verify_failed": {"name": "SSL / TLS Certificate Error", "meaning": "A secure connection failed due to invalid/expired SSL certificate.", "causes": "Expired cert, self-signed cert not trusted, wrong system clock.", "fixes": ["Check certificate expiry with an SSL checker tool.", "Sync your system clock — SSL validation depends on it.", "For local dev: add the cert to trusted store or set verify=False (dev only)."], "severity": "high", "category": "Security"},
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

LANGUAGES = {
    "English": "English", "Hindi (हिंदी)": "Hindi",
    "Bengali (বাংলা)": "Bengali", "Tamil (தமிழ்)": "Tamil",
    "Telugu (తెలుగు)": "Telugu", "Marathi (मराठी)": "Marathi",
    "Spanish": "Spanish", "French": "French",
    "German": "German", "Japanese": "Japanese",
}


# ─────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────
def rule_based_translate(error_text):
    el = error_text.lower()
    matches = [info for pat, info in ERROR_DB.items() if re.search(pat, el)]
    if not matches:
        return None
    matches.sort(key=lambda x: SEVERITY_ORDER.get(x["severity"], 99))
    return matches[0]


def call_ai(system_prompt, user_content, api_key, provider="groq", max_tokens=1500):
    """Universal AI caller — supports Groq (free), Gemini (free) and Claude."""
    if provider == "groq":
        from groq import Groq
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=max_tokens,
            temperature=0.2
        )
        return resp.choices[0].message.content.strip()
    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        models_to_try = ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash"]
        last_error = None
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name=model_name, system_instruction=system_prompt)
                resp = model.generate_content(user_content)
                return resp.text.strip()
            except Exception as e:
                last_error = e
                continue
        raise Exception(f"All Gemini models failed: {last_error}")
    else:  # claude
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": user_content}],
            system=system_prompt
        )
        return msg.content[0].text.strip()


def ai_translate(error_text, description, api_key, language="English", provider="gemini"):
    try:
        lang_note = f"\nWrite 'meaning', 'causes', and all 'fixes' in {language}. Keep 'name' and 'category' in English." if language != "English" else ""
        desc_note = f"\nUser context: {description}" if description.strip() else ""
        system = f"""You are DebugMate, an expert debugger AI. Given an error message and optional user context, respond ONLY with valid JSON — no markdown, no code fences.
Use this structure:
{{"name":"Short error name","meaning":"1-2 sentence plain explanation","causes":"1-2 sentence root cause","fixes":["Step 1","Step 2","Step 3"],"severity":"critical|high|medium|low","category":"HTTP|Python|JavaScript|SQL|Git|Network|OS|System|General"}}
{lang_note}{desc_note}"""
        raw = call_ai(system, f"Translate this error:\n\n{error_text}", api_key, provider)
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}


def ai_code_debug(code, description, api_key, language_out="English", provider="gemini"):
    """Analyzes buggy code, explains the error, returns corrected code with diff."""
    try:
        lang_note = f"\nWrite all explanations in {language_out}." if language_out != "English" else ""
        desc_note = f"\nUser says: {description}" if description.strip() else ""
        system = f"""You are DebugMate, an expert code debugger. Analyze the code, find ALL bugs, and return ONLY valid JSON — no markdown, no code fences.
Structure:
{{
  "error_summary": "One-line summary of what's wrong",
  "bugs_found": ["Bug 1 description", "Bug 2 description"],
  "original_code": "The original code as-is",
  "fixed_code": "The fully corrected code",
  "explanation": "Clear explanation of what was changed and why",
  "severity": "critical|high|medium|low",
  "language": "Python|JavaScript|SQL|Java|C++|etc"
}}
{lang_note}{desc_note}"""
        raw = call_ai(system, f"Debug this code:\n\n```\n{code}\n```", api_key, provider, max_tokens=2000)
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}


def ai_smart_intent(user_input, description, api_key, provider="gemini"):
    """Detects if input is an error message or code, then routes accordingly."""
    try:
        system = """You are DebugMate. Detect whether the user input is:
1. An error message / log line → return {"intent": "error"}
2. Source code with bugs → return {"intent": "code"}
3. Both code AND error → return {"intent": "both"}
Return ONLY valid JSON."""
        raw = call_ai(system, f"User description: {description}\n\nInput:\n{user_input}", api_key, provider, max_tokens=100)
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw).get("intent", "error")
    except Exception:
        return "error"


def batch_translate(log_text, api_key, mode, language="English", provider="gemini"):
    lines = log_text.strip().split('\n')
    results, seen = [], set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if mode == "🔧 Rule-Based (Offline)":
            r = rule_based_translate(line)
            if r and r["name"] not in seen:
                seen.add(r["name"])
                results.append({"input": line[:100], "result": r})
        else:
            r = ai_translate(line, "", api_key, language, provider)
            if "error" not in r and r.get("name", "") not in seen:
                seen.add(r.get("name", ""))
                results.append({"input": line[:100], "result": r})
    return results


def translate_result(result, api_key, language, provider="gemini"):
    try:
        system = f"Translate 'meaning', 'causes', all 'fixes' items to {language}. Keep 'name','severity','category' in English. Return ONLY valid JSON."
        raw = call_ai(system, json.dumps(result), api_key, provider)
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception:
        return result


# ── PDF GENERATION ──
def generate_pdf(results, title="DebugMate Report"):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        styles = getSampleStyleSheet()
        S = {
            "title":  ParagraphStyle('T', parent=styles['Title'], fontSize=20, textColor=colors.HexColor('#0ea5e9'), spaceAfter=4),
            "meta":   ParagraphStyle('M', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'), spaceAfter=16),
            "name":   ParagraphStyle('N', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#0f172a'), spaceBefore=12, spaceAfter=4),
            "label":  ParagraphStyle('L', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#64748b'), fontName='Helvetica-Bold', spaceAfter=2, spaceBefore=8),
            "body":   ParagraphStyle('B', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#1e293b'), spaceAfter=4, leading=14),
            "code":   ParagraphStyle('C', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#1e293b'), fontName='Courier', spaceAfter=4, leading=13, backColor=colors.HexColor('#f1f5f9'), leftIndent=10, rightIndent=10),
            "fix":    ParagraphStyle('F', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#1e293b'), leftIndent=14, spaceAfter=3, leading=14),
        }
        SEV = {"critical": "#dc2626", "high": "#d97706", "medium": "#2563eb", "low": "#16a34a"}

        story = [
            Paragraph("🛠 DebugMate", S["title"]),
            Paragraph(title, ParagraphStyle('sub', parent=styles['Normal'], fontSize=14, textColor=colors.HexColor('#334155'), spaceAfter=4)),
            Paragraph(f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}  |  {len(results)} item(s)", S["meta"]),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=12),
        ]

        for i, item in enumerate(results):
            r = item["result"]
            # Code debug result
            if "fixed_code" in r:
                story.append(Paragraph(f'Input: <i>{item["input"][:80]}</i>', ParagraphStyle('inp', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'), spaceAfter=4)))
                story.append(Paragraph(f"Code Debug: {r.get('error_summary','')}", S["name"]))
                story.append(Paragraph("BUGS FOUND", S["label"]))
                for b in r.get("bugs_found", []):
                    story.append(Paragraph(f"• {b}", S["body"]))
                story.append(Paragraph("EXPLANATION", S["label"]))
                story.append(Paragraph(r.get("explanation", ""), S["body"]))
                story.append(Paragraph("FIXED CODE", S["label"]))
                story.append(Paragraph(r.get("fixed_code", "").replace('\n', '<br/>'), S["code"]))
            else:
                sev = r.get("severity", "medium")
                sev_hex = SEV.get(sev, "#888")
                story.append(Paragraph(f'Input: <i>{item["input"][:80]}</i>', ParagraphStyle('inp', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'), spaceAfter=4)))
                story.append(Paragraph(f'{r.get("name","?")}  <font color="{sev_hex}" size="9">[{sev.upper()}]</font>', S["name"]))
                story.append(Paragraph("MEANING", S["label"]))
                story.append(Paragraph(r.get("meaning", ""), S["body"]))
                story.append(Paragraph("CAUSES", S["label"]))
                story.append(Paragraph(r.get("causes", ""), S["body"]))
                story.append(Paragraph("FIX STEPS", S["label"]))
                for j, fix in enumerate(r.get("fixes", []), 1):
                    story.append(Paragraph(f"{j}. {fix}", S["fix"]))
            if i < len(results) - 1:
                story += [Spacer(1, 8), HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=8)]

        doc.build(story)
        buf.seek(0)
        return buf
    except Exception as e:
        st.error(f"PDF error: {e} — run: pip install reportlab")
        return None


# ─────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────
def badge(level):
    b = {"critical": "badge-critical", "high": "badge-high", "medium": "badge-medium", "low": "badge-low"}
    icons = {"critical": "⚠ CRITICAL", "high": "🔶 HIGH", "medium": "🔷 MEDIUM", "low": "✅ LOW"}
    cls = b.get(level, "badge-medium")
    txt = icons.get(level, level.upper())
    return f'<span class="badge {cls}">{txt}</span>'


def render_error_result(result):
    sev = result.get("severity", "medium")
    fixes_html = "".join([
        f'<div class="step-row"><div class="step-num">{i+1}</div><div class="step-txt">{f}</div></div>'
        for i, f in enumerate(result.get("fixes", []))
    ])
    st.markdown(f"""
    <div class="dm-card sev-{sev}">
        <div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.9rem;">
            {badge(sev)}
            <span style="font-family:var(--mono);font-size:0.72rem;color:var(--muted);">📁 {result.get('category','General')}</span>
        </div>
        <div style="font-size:1.05rem;font-weight:700;color:var(--text);margin-bottom:.9rem;">{result.get('name','Unknown Error')}</div>
        <div class="sec-label">💡 What it means</div>
        <div style="font-size:.9rem;line-height:1.6;margin-bottom:.9rem;color:var(--text);">{result.get('meaning','N/A')}</div>
        <div class="sec-label">🔎 Root cause</div>
        <div style="font-size:.9rem;line-height:1.6;margin-bottom:.9rem;color:var(--text);">{result.get('causes','N/A')}</div>
        <div class="sec-label">🛠 Fix steps</div>
        {fixes_html}
    </div>
    """, unsafe_allow_html=True)


def render_code_result(result):
    orig = result.get("original_code", "")
    fixed = result.get("fixed_code", "")
    bugs = result.get("bugs_found", [])
    bugs_html = "".join([f'<div class="step-row"><div class="step-num">!</div><div class="step-txt">{b}</div></div>' for b in bugs])
    sev = result.get("severity", "medium")

    st.markdown(f"""
    <div class="dm-card sev-{sev}">
        <div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.9rem;">
            {badge(sev)}
            <span style="font-family:var(--mono);font-size:0.72rem;color:var(--muted);">💻 {result.get('language','Code')} · Code Debug</span>
        </div>
        <div style="font-size:1.05rem;font-weight:700;color:var(--text);margin-bottom:.9rem;">
            {result.get('error_summary','Bug Analysis')}
        </div>
        <div class="sec-label">🐛 Bugs found</div>
        {bugs_html}
        <div class="sec-label" style="margin-top:.9rem;">📝 Explanation</div>
        <div style="font-size:.9rem;line-height:1.6;color:var(--text);margin-bottom:1rem;">{result.get('explanation','')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Side-by-side diff
    st.markdown('<div class="diff-grid">', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="diff-label diff-error-label">❌ Original (Buggy)</div>', unsafe_allow_html=True)
        st.code(orig, language=result.get("language", "python").lower())
        st.download_button("📋 Copy Original", data=orig, file_name="original.py", mime="text/plain", use_container_width=True, key="copy_orig")
    with col_b:
        st.markdown('<div class="diff-label diff-fix-label">✅ Fixed Code</div>', unsafe_allow_html=True)
        st.code(fixed, language=result.get("language", "python").lower())
        st.download_button("📋 Copy Fixed Code", data=fixed, file_name="fixed.py", mime="text/plain", use_container_width=True, key="copy_fixed")
    st.markdown('</div>', unsafe_allow_html=True)


def copy_buttons_for_error(result, key_prefix="err"):
    fixes_text = "\n".join([f"{i+1}. {f}" for i, f in enumerate(result.get("fixes", []))])
    full_text = f"""Error: {result.get('name')}
Severity: {result.get('severity','').upper()}
Category: {result.get('category','')}

Meaning: {result.get('meaning','')}

Root Cause: {result.get('causes','')}

Fix Steps:
{fixes_text}"""
    uid = abs(hash(result.get('name','') + key_prefix)) % 100000
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📋 Copy Full Response", data=full_text, file_name="error_analysis.txt", mime="text/plain", use_container_width=True, key=f"full_{uid}")
    with c2:
        st.download_button("📋 Copy Fix Steps Only", data=fixes_text, file_name="fix_steps.txt", mime="text/plain", use_container_width=True, key=f"fix_{uid}")


def add_to_history(inp, result, kind="error"):
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, {
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "input": inp[:60],
        "result": result,
        "kind": kind
    })
    st.session_state.history = st.session_state.history[:30]


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for k, v in [("history", []), ("last_result", None), ("last_kind", "error"), ("batch_results", []), ("vs_hist", [])]:
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ DebugMate Settings")
    mode = st.radio("**Engine**", ["🔧 Rule-Based (Offline)", "🤖 AI Mode"])
    api_key = None
    provider = "groq"

    # Auto-load secret key if deployed on Streamlit Cloud
    secret_key = st.secrets.get("GROQ_API_KEY", None) if hasattr(st, "secrets") else None

    if mode == "🤖 AI Mode":
        if secret_key:
            # Hosted mode — key is hidden, user sees nothing
            api_key = secret_key
            provider = "groq"
            st.markdown('<div class="info-bar">✅ AI Mode ready — powered by Groq · Llama 3.3</div>', unsafe_allow_html=True)
        else:
            # Local mode — user enters their own key
            ai_prov = st.selectbox("**AI Provider**", [
                "🆓 Groq — Llama 3.3 (Best Free)",
                "🆓 Gemini (Google Free)",
                "💜 Claude (Anthropic)"
            ])
            if "Groq" in ai_prov:
                provider = "groq"
            elif "Gemini" in ai_prov:
                provider = "gemini"
            else:
                provider = "claude"

            if provider == "groq":
                st.markdown('<div class="info-bar">🆓 Free · 14,400 req/day · No credit card</div>', unsafe_allow_html=True)
                api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
                st.markdown('<a href="https://console.groq.com" target="_blank" style="font-size:0.78rem;color:#00d4ff;">→ Get free key at console.groq.com</a>', unsafe_allow_html=True)
            elif provider == "gemini":
                st.markdown('<div class="info-bar">🆓 Free · 1500 req/day · No credit card</div>', unsafe_allow_html=True)
                api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
                st.markdown('<a href="https://aistudio.google.com/app/apikey" target="_blank" style="font-size:0.78rem;color:#00d4ff;">→ Get free key at aistudio.google.com</a>', unsafe_allow_html=True)
            else:
                api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
                st.markdown('<a href="https://console.anthropic.com" target="_blank" style="font-size:0.78rem;color:#00d4ff;">→ console.anthropic.com</a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🌐 Output Language")
    lang_label = st.selectbox("Explain in:", list(LANGUAGES.keys()))
    sel_lang = LANGUAGES[lang_label]
    if sel_lang != "English" and mode == "🔧 Rule-Based (Offline)":
        st.info("🌐 Language translation requires AI Mode.")

    st.markdown("---")
    st.markdown("### 📋 Session History")
    if st.session_state.history:
        if st.button("🗑 Clear All"):
            st.session_state.history = []
            st.rerun()
        icons_sev = {"critical": "🔴", "high": "🟠", "medium": "🔵", "low": "🟢"}
        for item in st.session_state.history[:15]:
            r = item["result"]
            sev = r.get("severity", "") if "severity" in r else r.get("severity", "medium")
            icon = icons_sev.get(sev, "⚪")
            kind_icon = "💻" if item["kind"] == "code" else "⚡"
            st.markdown(
                f'<div class="hist-row">{icon}{kind_icon} <b>{item["time"]}</b><br>'
                f'<span style="color:var(--muted);font-size:0.78rem;">{item["input"]}…</span></div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown('<span style="color:var(--muted);font-size:0.85rem;">No history yet.</span>', unsafe_allow_html=True)

    # ── VS Code Extension info (Level 3 - #10) ──
    st.markdown("---")
    st.markdown("### 🔌 Integrations")
    st.markdown("""
<div style="font-size:0.8rem;color:var(--muted);line-height:1.6;">
<b style="color:var(--text);">VS Code Extension</b> (coming soon)<br>
Highlight any error in editor → get fix in sidebar.<br><br>
<b style="color:var(--text);">API Access</b><br>
Run locally on port 8501 and call via HTTP from any tool.
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="dm-header">
    <div>
        <div class="dm-logo">🛠 DebugMate</div>
        <div class="dm-tagline">Smart error translator · Code debugger · Batch log scanner · Multilingual · PDF export</div>
    </div>
</div>
<hr style="margin-bottom:1.2rem;">
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ Error Translator",
    "💻 Code Debugger",
    "📄 Batch / Log Scanner",
    "📊 Error Trend Dashboard"
])


# ══════════════════════════════════════════════
# TAB 1 — Error Translator (single)
# ══════════════════════════════════════════════
with tab1:
    st.markdown("#### Paste your error message")
    st.markdown('<div class="info-bar">🧠 <b>Smart Intent Detection</b> — paste error messages, log lines, or switch to <b>Code Debugger</b> tab for buggy code.</div>', unsafe_allow_html=True)

    # Description box (new feature)
    description = st.text_input(
        "📝 Brief description (optional but helpful)",
        placeholder="e.g. 'This error appears when I try to log in' or 'happens when I run my Flask app'",
        help="Tell DebugMate what you were doing when this happened. Helps AI Mode give a more targeted fix."
    )

    error_input = st.text_area(
        "Error message / log line:",
        placeholder="Paste your error here...\n\nExamples:\n  403 Forbidden\n  NameError: name 'df' is not defined\n  fatal: not a git repository\n  Cannot read properties of undefined",
        height=140
    )

    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        go_btn = st.button("🔍 Translate & Fix", use_container_width=True)
    with c2:
        if st.button("🗑 Clear", use_container_width=True):
            st.session_state.last_result = None
            st.rerun()
    with c3:
        st.markdown('<span class="copy-hint">Results auto-saved to history →</span>', unsafe_allow_html=True)

    if go_btn:
        if not error_input.strip():
            st.warning("Please paste an error message.")
        elif mode == "🤖 AI Mode" and not api_key:
            st.error("Enter your Anthropic API key in the sidebar.")
        else:
            with st.spinner("Analyzing..."):
                if mode == "🔧 Rule-Based (Offline)":
                    result = rule_based_translate(error_input)
                    if not result:
                        st.warning("Not in rule database. Switch to AI Mode for this error.")
                        result = None
                    elif sel_lang != "English" and api_key:
                        result = translate_result(result, api_key, sel_lang, provider)
                else:
                    result = ai_translate(error_input, description, api_key, sel_lang, provider)
                    if "error" in result:
                        st.error(f"API Error: {result['error']}")
                        result = None

                if result:
                    st.session_state.last_result = {"input": error_input[:100], "result": result}
                    st.session_state.last_kind = "error"
                    add_to_history(error_input, result, "error")
                    # Add to trend tracking
                    if "trend_data" not in st.session_state:
                        st.session_state.trend_data = []
                    st.session_state.trend_data.append({
                        "time": datetime.datetime.now().isoformat(),
                        "category": result.get("category", "General"),
                        "severity": result.get("severity", "medium"),
                        "name": result.get("name", "")
                    })

    if st.session_state.last_result and st.session_state.last_kind == "error":
        result = st.session_state.last_result["result"]
        st.markdown("---")
        st.markdown("### 📋 Analysis Result")
        render_error_result(result)

        # Copy buttons
        st.markdown("**📤 Export / Copy**")
        copy_buttons_for_error(result)

        # PDF
        pdf_buf = generate_pdf([st.session_state.last_result], "Error Analysis Report")
        if pdf_buf:
            st.download_button(
                "📥 Download PDF Report", data=pdf_buf,
                file_name=f"debugmate_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf", use_container_width=True, key="tab1_pdf_main"
            )


# ══════════════════════════════════════════════
# TAB 2 — Code Debugger (NEW: code + diff)
# ══════════════════════════════════════════════
with tab2:
    st.markdown("#### Paste your buggy code")
    st.markdown('<div class="info-bar">💻 <b>Code Debugger</b> — paste any code with bugs. DebugMate finds all issues and returns a corrected version with a side-by-side comparison. <b>Requires AI Mode.</b></div>', unsafe_allow_html=True)

    code_desc = st.text_input(
        "📝 What should this code do? (optional but helps a lot)",
        placeholder="e.g. 'This function should sort a list and return the top 3 items' or 'Flask route to register a user'",
        key="code_desc"
    )

    code_input = st.text_area(
        "Paste your code here:",
        placeholder="def calculate_average(numbers):\n    total = 0\n    for n in numbers:\n        total += n\n    return total / len(numbers)  # bug: crashes on empty list",
        height=220,
        key="code_input"
    )

    if mode == "🔧 Rule-Based (Offline)":
        st.warning("⚠️ Code Debugger requires AI Mode. Switch the engine in the sidebar.")
    else:
        c1, c2 = st.columns([3, 1])
        with c1:
            debug_btn = st.button("🐛 Debug My Code", use_container_width=True, key="debug_btn")
        with c2:
            if st.button("🗑 Clear Code", use_container_width=True, key="clear_code"):
                st.session_state.last_result = None
                st.rerun()

        if debug_btn:
            if not code_input.strip():
                st.warning("Paste some code first.")
            elif not api_key:
                st.error("Enter your Anthropic API key in the sidebar.")
            else:
                with st.spinner("Analyzing code for bugs..."):
                    result = ai_code_debug(code_input, code_desc, api_key, sel_lang, provider)
                    if "error" in result:
                        st.error(f"API Error: {result['error']}")
                    else:
                        st.session_state.last_result = {"input": code_input[:100], "result": result}
                        st.session_state.last_kind = "code"
                        add_to_history(code_input, result, "code")
                        if "trend_data" not in st.session_state:
                            st.session_state.trend_data = []
                        st.session_state.trend_data.append({
                            "time": datetime.datetime.now().isoformat(),
                            "category": result.get("language", "Code"),
                            "severity": result.get("severity", "medium"),
                            "name": result.get("error_summary", "Code Bug")
                        })

        if st.session_state.last_result and st.session_state.last_kind == "code":
            result = st.session_state.last_result["result"]
            st.markdown("---")
            st.markdown("### 📋 Debug Result")
            render_code_result(result)

            # Full export
            st.markdown("**📤 Export**")
            full_report = f"""DebugMate Code Debug Report
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY: {result.get('error_summary','')}
SEVERITY: {result.get('severity','').upper()}
LANGUAGE: {result.get('language','')}

BUGS FOUND:
{chr(10).join(['• ' + b for b in result.get('bugs_found',[])])}

EXPLANATION:
{result.get('explanation','')}

ORIGINAL CODE:
{result.get('original_code','')}

FIXED CODE:
{result.get('fixed_code','')}
"""
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📋 Copy Full Report", data=full_report, file_name="debug_report.txt", mime="text/plain", use_container_width=True, key="tab2_txt")
            with c2:
                pdf_buf = generate_pdf([st.session_state.last_result], "Code Debug Report")
                if pdf_buf:
                    st.download_button("📥 Download PDF", data=pdf_buf, file_name=f"code_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", mime="application/pdf", use_container_width=True, key="tab2_pdf")


# ══════════════════════════════════════════════
# TAB 3 — Batch / Log Scanner (Level 2 #6)
# ══════════════════════════════════════════════
with tab3:
    st.markdown("#### Paste entire log file or multiple error lines")
    st.markdown('<div class="info-bar">📄 <b>Batch Scanner</b> — paste a full log file. DebugMate scans every line, finds all distinct errors, and translates each one. AI Mode covers unknown errors.</div>', unsafe_allow_html=True)

    # Stack trace parser (Level 2 #7)
    batch_desc = st.text_input(
        "📝 Context (optional)",
        placeholder="e.g. 'This is the log from my Django server crash at 3pm'",
        key="batch_desc"
    )

    log_input = st.text_area(
        "Log / error block:",
        placeholder="Paste multiple errors or a full log here...\n\n403 Forbidden\nNameError: name 'df' is not defined\nfatal: not a git repository\nSSL: CERTIFICATE_VERIFY_FAILED\nIndexError: list index out of range",
        height=220,
        key="log_input"
    )

    c1, c2 = st.columns([3, 1])
    with c1:
        scan_btn = st.button("🔍 Scan & Translate All", use_container_width=True, key="scan_btn")
    with c2:
        if st.button("🗑 Clear Results", use_container_width=True, key="clear_batch"):
            st.session_state.batch_results = []
            st.rerun()

    # Stack trace parser (Level 2 #7)
    if log_input.strip():
        traceback_lines = [l for l in log_input.split('\n') if 'file "' in l.lower() or 'line ' in l.lower() or 'traceback' in l.lower()]
        if traceback_lines:
            st.markdown('<div class="info-bar">🔍 <b>Stack Trace Detected</b> — most relevant line highlighted below.</div>', unsafe_allow_html=True)
            most_relevant = traceback_lines[-1].strip()
            st.code(f"→ {most_relevant}", language="text")

    if scan_btn:
        if not log_input.strip():
            st.warning("Paste a log or multiple error lines first.")
        elif mode == "🤖 AI Mode" and not api_key:
            st.error("Enter your Anthropic API key in the sidebar.")
        else:
            with st.spinner(f"Scanning {len(log_input.split(chr(10)))} lines..."):
                st.session_state.batch_results = batch_translate(log_input, api_key, mode, sel_lang, provider)

    if st.session_state.batch_results:
        results = st.session_state.batch_results
        st.markdown(f"### 📋 Found {len(results)} Distinct Error(s)")

        # Summary row
        sev_counts = {}
        for item in results:
            s = item["result"].get("severity", "medium")
            sev_counts[s] = sev_counts.get(s, 0) + 1

        cols = st.columns(4)
        for i, (sev, icon, color) in enumerate([("critical","⚠","#ef4444"),("high","🔶","#f59e0b"),("medium","🔷","#3b82f6"),("low","✅","#10b981")]):
            with cols[i]:
                count = sev_counts.get(sev, 0)
                st.markdown(f'<div class="dm-card" style="text-align:center;padding:.8rem;border-left:3px solid {color}"><div style="font-size:1.5rem;">{icon}</div><div style="font-size:1.3rem;font-weight:700;color:{color}">{count}</div><div style="font-size:0.75rem;color:var(--muted);">{sev.upper()}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        for item in results:
            r = item["result"]
            with st.expander(f"{'🔴' if r.get('severity')=='critical' else '🟠' if r.get('severity')=='high' else '🔵' if r.get('severity')=='medium' else '🟢'}  {r.get('name','Unknown')}  —  `{item['input'][:60]}`"):
                render_error_result(r)
                copy_buttons_for_error(r, key_prefix=f"batch_{results.index(item)}")

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            pdf_buf = generate_pdf(results, "Batch Error Scan Report")
            if pdf_buf:
                st.download_button("📥 Download Full PDF Report", data=pdf_buf,
                                   file_name=f"batch_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                   mime="application/pdf", use_container_width=True, key="tab3_pdf_main")
        with c2:
            all_text = "\n\n".join([
                f"ERROR: {it['result'].get('name','?')}\nSeverity: {it['result'].get('severity','')}\nMeaning: {it['result'].get('meaning','')}\nFixes:\n" +
                "\n".join([f"  {j+1}. {f}" for j, f in enumerate(it['result'].get('fixes', []))])
                for it in results
            ])
            st.download_button("📋 Copy All as Text", data=all_text,
                               file_name="batch_errors.txt", mime="text/plain", use_container_width=True, key="tab3_txt_main")


# ══════════════════════════════════════════════
# TAB 4 — Error Trend Dashboard (Level 3 #11)
# ══════════════════════════════════════════════
with tab4:
    st.markdown("#### Error Trend Dashboard")
    st.markdown('<div class="info-bar">📊 <b>Session Analytics</b> — tracks every error you translate this session. Shows frequency, category breakdown, and severity trends to help identify recurring patterns.</div>', unsafe_allow_html=True)

    trend_data = st.session_state.get("trend_data", [])

    if not trend_data:
        st.markdown("""
        <div class="dm-card" style="text-align:center;padding:3rem;">
            <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
            <div style="font-size:1.1rem;font-weight:600;margin-bottom:.5rem;">No data yet</div>
            <div style="color:var(--muted);font-size:.9rem;">Translate some errors in the other tabs and come back here to see your patterns.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary metrics
        total = len(trend_data)
        cats = {}
        sevs = {}
        for d in trend_data:
            cats[d["category"]] = cats.get(d["category"], 0) + 1
            sevs[d["severity"]] = sevs.get(d["severity"], 0) + 1

        top_cat = max(cats, key=cats.get) if cats else "N/A"
        top_sev = max(sevs, key=sevs.get) if sevs else "N/A"
        critical_count = sevs.get("critical", 0)

        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            (c1, "Total Errors", total, "📊"),
            (c2, "Top Category", top_cat, "📁"),
            (c3, "Most Common Severity", top_sev.upper(), "🎯"),
            (c4, "Critical Errors", critical_count, "⚠️"),
        ]
        for col, label, val, icon in metrics:
            with col:
                st.markdown(f'<div class="dm-card" style="text-align:center;padding:.9rem;"><div style="font-size:1.5rem;">{icon}</div><div style="font-size:1.4rem;font-weight:700;color:var(--accent);">{val}</div><div style="font-size:0.75rem;color:var(--muted);">{label}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**Errors by Category**")
            for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
                pct = int((count / total) * 100)
                bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                st.markdown(f"""
                <div class="dm-card" style="padding:.7rem 1rem;margin:.3rem 0;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:.3rem;">
                        <span style="font-family:var(--mono);font-size:.82rem;">{cat}</span>
                        <span style="color:var(--accent);font-family:var(--mono);font-size:.82rem;">{count} ({pct}%)</span>
                    </div>
                    <div style="font-family:var(--mono);font-size:.65rem;color:var(--muted);">{bar}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_right:
            st.markdown("**Errors by Severity**")
            sev_colors = {"critical": "#ef4444", "high": "#f59e0b", "medium": "#3b82f6", "low": "#10b981"}
            for sev in ["critical", "high", "medium", "low"]:
                count = sevs.get(sev, 0)
                if count == 0:
                    continue
                pct = int((count / total) * 100)
                color = sev_colors[sev]
                bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                st.markdown(f"""
                <div class="dm-card sev-{sev}" style="padding:.7rem 1rem;margin:.3rem 0;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:.3rem;">
                        <span style="font-family:var(--mono);font-size:.82rem;color:{color};">{sev.upper()}</span>
                        <span style="font-family:var(--mono);font-size:.82rem;color:{color};">{count} ({pct}%)</span>
                    </div>
                    <div style="font-family:var(--mono);font-size:.65rem;color:var(--muted);">{bar}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Recent Error Log**")
        for d in reversed(trend_data[-10:]):
            t = d["time"][:19].replace("T", " ")
            sev_c = sev_colors.get(d["severity"], "#888")
            st.markdown(f'<div class="dm-card" style="padding:.6rem 1rem;margin:.2rem 0;display:flex;justify-content:space-between;align-items:center;"><span style="font-family:var(--mono);font-size:.78rem;color:var(--muted);">{t}</span><span style="font-size:.85rem;">{d["name"][:50]}</span><span style="font-family:var(--mono);font-size:.72rem;color:{sev_c};">{d["severity"].upper()}</span></div>', unsafe_allow_html=True)

        # Export trend as CSV
        st.markdown("---")
        csv = "time,name,category,severity\n" + "\n".join([f'{d["time"]},{d["name"]},{d["category"]},{d["severity"]}' for d in trend_data])
        st.download_button("📥 Export Trend Data (CSV)", data=csv, file_name="debugmate_trends.csv", mime="text/csv", key="tab4_csv")

        if st.button("🗑 Reset Dashboard"):
            st.session_state.trend_data = []
            st.rerun()


# ── Footer ──
st.markdown("---")
st.markdown('<div style="text-align:center;color:var(--muted);font-size:0.78rem;font-family:var(--mono);">🛠 DebugMate · Error Translator + Code Debugger + Batch Scanner + PDF Export + Multilingual + Trend Dashboard</div>', unsafe_allow_html=True)