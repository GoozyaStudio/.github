import requests
import os

headers = {
    "Authorization": f"token {os.environ['PAT_TOKEN']}",
    "Accept": "application/vnd.github.v3+json",
}

repos = {
    "SL_VERSION": ("GoozyaStudio", "Solaris-2.0"),
    "SM_VERSION": ("GoozyaStudio", "SpecMerger"),
    "SC_VERSION": ("GoozyaStudio", "SpecCorrector"),
    "TC_VERSION": ("GoozyaStudio", "TAP-converter"),
    "WM_VERSION": ("GoozyaStudio", "WarningMaster"),
    "MC_VERSION": ("GoozyaStudio", "MaterialCalc"),
    "WB_VERSION": ("GoozyaGod", "GS_WakeBot"),
    "PC_VERSION": ("GoozyaStudio", "ProductionCalc"),
}


def get_latest_tag(username, repository):
    url = f"https://api.github.com/repos/{username}/{repository}/releases/latest"
    response = requests.get(url, headers=headers)
    return (
        response.json().get("tag_name", "n/a") if response.status_code == 200 else "n/a"
    )


with open("profile/README_template.md", "r", encoding="utf-8") as f:
    content = f.read()

for tag, (user, repo) in repos.items():
    version = get_latest_tag(user, repo)
    content = content.replace(f"{{{{{tag}}}}}", version)

with open("profile/README.md", "w", encoding="utf-8") as f:
    f.write(content)
