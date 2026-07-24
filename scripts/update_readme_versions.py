import requests
import os
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import time

POLICY_VERSION = 1
RETRY_COUNT = 3
RETRY_DELAY = 1
REQUEST_TIMEOUT = (5, 10)
EMPTY_VERSION_DISPLAY = "—"
HEADERS = {
    "Authorization": f"token {os.environ['PAT_TOKEN']}",
    "Accept": "application/vnd.github.v3+json",
}
REPOS = {
    "SL": {
        "user": "GoozyaStudio",
        "repo": "Solaris-2.0",
        "force_update": True,
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


def get(session, url, **kwargs):
    last_error = None

    for attempt in range(RETRY_COUNT):
        try:
            response = session.get(url, **kwargs)
            response.raise_for_status()
            return response

        except requests.RequestException as error:
            if error.response is not None:
                error.response.close()
            last_error = error

            if attempt + 1 < RETRY_COUNT:
                time.sleep(RETRY_DELAY * (attempt + 1))

    raise last_error


def get_latest_release(session, username, repository):
    url = f"https://api.github.com/repos/{username}/{repository}/releases/latest"

    try:
        with get(session, url, timeout=REQUEST_TIMEOUT) as response:
            data = response.json()
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            return None
        raise

    return {"version": data["tag_name"], "published": data["published_at"]}


private_key = serialization.load_pem_private_key(
    os.environ["UPDATE_PRIVATE_KEY"].encode(),
    password=None,
)
public_key = private_key.public_key()

with open("profile/README_template.md", "r", encoding="utf-8") as f:
    readme_content = f.read()

payload = {
    "policy_version": POLICY_VERSION,
    "projects": {},
}

with requests.Session() as session:
    session.headers.update(HEADERS)

    for tag, info in REPOS.items():
        release = get_latest_release(session, info["user"], info["repo"])

        if release is None:
            version = None
            published = None
        else:
            version = release["version"]
            published = release["published"]

        payload["projects"][tag] = {
            "version": version,
            "published": published,
            "force_update": info["force_update"],
            "grace_period_days": info["grace_period_days"],
        }

        readme_content = readme_content.replace(
            f"{{{{{tag}_VERSION}}}}",
            version if version is not None else EMPTY_VERSION_DISPLAY,
        )

raw_payload = json.dumps(
    payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
).encode("utf-8")

signature = private_key.sign(
    raw_payload,
    padding.PKCS1v15(),
    hashes.SHA256(),
)

public_key.verify(
    signature,
    raw_payload,
    padding.PKCS1v15(),
    hashes.SHA256(),
)

update_file = {
    "payload": payload,
    "signature": base64.b64encode(signature).decode("ascii"),
}

with open("profile/README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

with open("profile/update_policy.json", "w") as f:
    json.dump(update_file, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
