import requests
import os
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

headers = {
    "Authorization": f"token {os.environ['PAT_TOKEN']}",
    "Accept": "application/vnd.github.v3+json",
}

private_key = serialization.load_pem_private_key(
    os.environ["UPDATE_PRIVATE_KEY"].encode(),
    password=None,
)

repos = {
    "SL": {
        "user": "GoozyaStudio",
        "repo": "Solaris-2.0",
        "force_update": False,
        "grace_period_days": 3,
    },
    "SM": {
        "user": "GoozyaStudio",
        "repo": "SpecMerger",
        "force_update": False,
        "grace_period_days": 3,
    },
    "SC": {
        "user": "GoozyaStudio",
        "repo": "SpecCorrector",
        "force_update": False,
        "grace_period_days": 3,
    },
    "TC": {
        "user": "GoozyaStudio",
        "repo": "TAP-converter",
        "force_update": False,
        "grace_period_days": 3,
    },
    "WM": {
        "user": "GoozyaStudio",
        "repo": "WarningMaster",
        "force_update": False,
        "grace_period_days": 3,
    },
    "MC": {
        "user": "GoozyaStudio",
        "repo": "MaterialCalc",
        "force_update": False,
        "grace_period_days": 3,
    },
    "WB": {
        "user": "GoozyaGod",
        "repo": "GS_WakeBot",
        "force_update": False,
        "grace_period_days": 3,
    },
    "PC": {
        "user": "GoozyaStudio",
        "repo": "ProductionCalc",
        "force_update": False,
        "grace_period_days": 3,
    },
    "SG": {
        "user": "GoozyaStudio",
        "repo": "StickerGen",
        "force_update": False,
        "grace_period_days": 3,
    },
    "PE": {
        "user": "GoozyaStudio",
        "repo": "PDF-Extractor",
        "force_update": False,
        "grace_period_days": 3,
    },
    "DA": {
        "user": "GoozyaStudio",
        "repo": "Dir-Analyzer",
        "force_update": False,
        "grace_period_days": 3,
    },
}


def get_latest_release(username, repository):
    url = f"https://api.github.com/repos/{username}/{repository}/releases/latest"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    data = response.json()

    return {"version": data["tag_name"], "published": data["published_at"]}


with open("profile/README_template.md", "r", encoding="utf-8") as f:
    content = f.read()

policy = {}

for tag, info in repos.items():
    release = get_latest_release(info["user"], info["repo"])

    if release is None:
        version = "n/a"
        published = None
    else:
        version = release["version"]
        published = release["published"]

    policy[tag] = {
        "version": version,
        "published": published,
        "force_update": info["force_update"],
        "grace_period_days": info["grace_period_days"],
    }

    content = content.replace(f"{{{{{tag}_VERSION}}}}", version)

raw = json.dumps(
    policy, ensure_ascii=False, separators=(",", ":"), sort_keys=True
).encode("utf-8")

signature = private_key.sign(
    raw,
    padding.PKCS1v15(),
    hashes.SHA256(),
)

public_key = private_key.public_key()

public_key.verify(
    signature,
    raw,
    padding.PKCS1v15(),
    hashes.SHA256(),
)

with open("profile/README.md", "w", encoding="utf-8") as f:
    f.write(content)

with open("profile/update_policy.json", "wb") as f:
    f.write(raw)

with open("profile/update_policy.sig", "wb") as f:
    f.write(signature)
