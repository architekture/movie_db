from nornir import InitNornir
from nornir.core.filter import F as nf

nr = InitNornir(config_file="archives/config.yml")

inv = nr.filter(
    # nf(needs_case_replacement=True)
    # nf(publisher__contains="Criterion")
    # nf(aspect_ratio__le=1.9)
    # & nf(aspect_ratio__ge=1.4)
)

for i in inv.inventory.hosts:
    dvc = inv.inventory.hosts[i]
    if dvc["release"]["discs"] == 1:
        discs = f"{dvc['release']['discs']} Disc"
    elif dvc["release"]["discs"] > 1:
        discs = f"{dvc['release']['discs']} Discs"
    if isinstance(dvc["director"], list):
        dvc["director"] = " & ".join(dvc["director"])
    data = f"{dvc['title']} ({dvc['year']}/{dvc['runtime']} min/{dvc['release']['aspect_ratio']}:1/dir. {dvc['director']}) - [{dvc['format']}|{dvc['resolution']}p|{dvc['release']['publisher']} ({discs})] "
    if dvc["steelbook"]:
        data += "*"
    elif dvc["slipcover"]:
        data += "†"
    if dvc["boutique_release"]:
        data += "‡"
    if not dvc["color"]:
        data += "§"
    if dvc["animation"]:
        data += "‖"
    print(data)
print(
    f"\nTotal number of titles: {len(inv.inventory.hosts)}\n"
    "\n* Steelbook®"
    "\n† Has slipcover"
    "\n‡ Boutique label release"
    "\n§ Film presented in black & white"
    "\n‖ Animated feature"
    )
