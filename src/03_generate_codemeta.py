import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

requirements_path = PROJECT_ROOT / "requirements.txt"
codemeta_path = PROJECT_ROOT / "codemeta.json"

with open(requirements_path, "r", encoding="utf-8") as f:
    dependencies = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

codemeta = {
    "@context": "https://doi.org/10.5063/schema/codemeta-2.0",
    "@type": "SoftwareSourceCode",
    "name": "Prediction of unemployment in Vienna districts using tourism and demographic data",
    "version": "v1.1.0",
    "identifier": "https://doi.org/10.70124/464th-2za78",
    "description": "Software and notebooks for a FAIR data science experiment predicting unemployment levels in Vienna districts using tourism and demographic data.",
    "license": "MIT",
    "programmingLanguage": "Python",
    "runtimePlatform": "Python 3.11.9",
    "codeRepository": "https://github.com/nicolasphilipp/unemployment-prediction",
    "softwareRequirements": dependencies
}

with open(codemeta_path, "w", encoding="utf-8") as f:
    json.dump(codemeta, f, indent=2)

print("codemeta.json generated successfully")