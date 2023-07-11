from typing import Optional

import yaml
import json

PERMITTED_LICENSES_PATH = "./.github/permitted-licenses.yml"
INPUT_FILE_PATH = "target/generated-sources/license/LICENSES.yml"


class WarningLicense:
    def __init__(self, name: str, warning: str):
        self.name = name
        self.warning = warning


class WarningLicenses(list[WarningLicense]):
    def __init__(self):
        super().__init__()

    def __contains__(self, license_name: str):
        for l in self:
            if l.name == license_name:
                return True
        return False

    def __getitem__(self, license_name: str) -> Optional[WarningLicense]:
        for l in self:
            if l.name == license_name:
                return l
        return None


def load_warning_licenses() -> WarningLicenses:
    dicts: list[dict[str, str]] = yaml.safe_load(open(PERMITTED_LICENSES_PATH, 'r'))["permitted-with-warning"]
    result: WarningLicenses = WarningLicenses()
    for warning_license in dicts:
        result.append(WarningLicense(warning_license.get("name"), warning_license.get("warning")))
    return result


def warning_multiple_licenses(a: str):
    return "Artifact \"" + a + "\" had multiple licenses, not all are permitted but at least one. " \
                               "Typically this means that we can choose between them and since one " \
                               "is permitted, everything is fine but this should be checked manually!\n"


permitted_licenses: list[str] = yaml.safe_load(open(PERMITTED_LICENSES_PATH, 'r'))["permitted"]
warning_licenses: WarningLicenses = load_warning_licenses()
artifacts: dict[str, list[str]] = yaml.safe_load(open(INPUT_FILE_PATH, 'r'))
print("All licenses:\n", json.dumps(artifacts, indent=2))
print("\n\n")

non_permitted_licenses: dict[str] = {}
warning_str: str = ""


def check_license(l: str, artifact: str) -> bool:
    global warning_str
    if l in permitted_licenses:
        return True
    warning_license = warning_licenses[l]
    if warning_license is None:
        return False

    warning_str += artifact + ": " + warning_license.warning + "\n"
    return True


for artifact, licenses in artifacts.items():
    if len(licenses) == 1:
        if not check_license(licenses[0], artifact):
            non_permitted_licenses[artifact] = licenses
    else:
        all_valid: bool = True
        one_valid: bool = False
        for l in licenses:
            if not check_license(l, artifact):
                all_valid = False
            else:
                one_valid = True
        if not all_valid:
            if one_valid:
                warning_str += warning_multiple_licenses(artifact)
            else:
                non_permitted_licenses[artifact] = licenses

if len(warning_str) > 0:
    print("\033[93mWarnings:\n" + warning_str + "\033[0m\n")
if len(non_permitted_licenses) > 0:
    print("\033[91mSome dependencies do have non-permitted licenses:\033[0m\n",
          json.dumps(non_permitted_licenses, indent=2))
    exit(1)
else:
    print("\033[92mAll dependencies permitted.\033[0m")
    exit(0)
