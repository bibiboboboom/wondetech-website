#!/usr/bin/env python3
"""
Push local files to GitHub via the REST API,
using the authentication from the WorkBuddy GitHub MCP connector.
"""
import json, base64, os, sys, urllib.request, urllib.parse, urllib.error

REPO_OWNER = "bibiboboboom"
REPO_NAME   = "wondetech-website"
BRANCH     = "main"
COMMIT_MSG = "feat: redesign Risk Intelligence page with scenario-driven visual workflow"

# --- Try to get GitHub token from MCP connector or env ---
def get_gh_token():
    # 1. Try env vars (user may have set GITHUB_TOKEN)
    for k in ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT"):
        v = os.environ.get(k)
        if v:
            return v
    # 2. Try git credential helper
    import subprocess
    try:
        out = subprocess.run(
            ["git", "config", "--global", "credential.helper"],
            capture_output=True, text=True
        ).stdout.strip()
        if out:
            print(f"[info] credential.helper = {out}", file=sys.stderr)
    except Exception:
        pass
    return None

token = get_gh_token()
if not token:
    print("ERROR: No GitHub token found.", file=sys.stderr)
    print("Please set GITHUB_TOKEN env var, or push manually:", file=sys.stderr)
    sys.exit(1)

print(f"[info] Token found (len={len(token)}), pushing...")

# --- Read local files ---
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

html = read_file("risk-intelligence.html")
css  = read_file("risk-intelligence.css")
print(f"[info] HTML {len(html)} bytes, CSS {len(css)} bytes")

# --- GitHub API helpers ---
def gh_api(method, url, data=None, token=token):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        req.data = body
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"[error] HTTP {e.code}: {body}", file=sys.stderr)
        raise

# --- Step 1: get the latest commit SHA on main ---
print("[info] Getting latest commit SHA...")
    repo_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/ref/heads/{BRANCH}"
    ref_data = gh_api("GET", repo_url)
    latest_sha = ref_data["object"]["sha"]
    print(f"[info] Latest commit SHA: {latest_sha[:10]}...")

# --- Step 2: create a tree with the two updated files ---
    # Read the current tree
    commit_data = gh_api("GET", f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{latest_sha}")
    base_tree_sha = commit_data["tree"]["sha"]

    # Create blobs for each file
    blobs = {}
    for path, content in [("risk-intelligence.html", html), ("risk-intelligence.css", css)]:
        print(f"[info] Creating blob for {path}...")
        blob_data = gh_api("POST", f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/blobs", {
            "content": content,
            "encoding": "utf-8"
        })
        blobs[path] = blob_data["sha"]
        print(f"[info]   Blob SHA: {blob_data['sha'][:10]}...")

    # Create a new tree
    tree_items = [{"path": p, "mode": "100644", "type": "blob", "sha": s} for p, s in blobs.items()]
    print("[info] Creating new tree...")
    tree_data = gh_api("POST", f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees", {
        "base_tree": base_tree_sha,
        "tree": tree_items
    })
    new_tree_sha = tree_data["sha"]
    print(f"[info] New tree SHA: {new_tree_sha[:10]}...")

# --- Step 3: create a new commit ---
    print("[info] Creating commit...")
    commit_data = gh_api("POST", f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits", {
        "message": COMMIT_MSG,
        "tree": new_tree_sha,
        "parents": [latest_sha]
    })
    new_commit_sha = commit_data["sha"]
    print(f"[info] New commit SHA: {new_commit_sha[:10]}...")

# --- Step 4: update the branch reference ---
    print(f"[info] Updating {BRANCH} to {new_commit_sha[:10]}...")
    ref_data = gh_api("PATCH", repo_url, {
        "sha": new_commit_sha,
        "force": False
    })
    print("[success] Files pushed successfully!")
    print(f"[info] Commit: {new_commit_sha}")
    print(f"[info] View at: https://github.com/{REPO_OWNER}/{REPO_NAME}/commit/{new_commit_sha}")

except Exception as e:
    print(f"[error] Push failed: {e}", file=sys.stderr)
    sys.exit(1)
