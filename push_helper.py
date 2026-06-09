import json, sys, os

# Read local files
html = open('risk-intelligence.html', 'r', encoding='utf-8').read()
css  = open('risk-intelligence.css', 'r', encoding='utf-8').read()

payload = {
    "owner": "bibiboboboom",
    "repo": "wondetech-website",
    "branch": "main",
    "message": "feat: redesign Risk Intelligence page with scenario-driven visual workflow",
    "files": [
        {"path": "risk-intelligence.html", "content": html},
        {"path": "risk-intelligence.css",  "content": css}
    ]
}

# Output payload size
print(f"HTML size: {len(html)} bytes")
print(f"CSS size:  {len(css)} bytes")
print(f"Total payload size: {len(json.dumps(payload))} bytes")

# Write payload to file for review
with open('C:/Users/lenovo/WorkBuddy/push_payload2.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)

print("Payload written to push_payload2.json")
print("Now please push manually from your machine, or provide a GitHub token.")
