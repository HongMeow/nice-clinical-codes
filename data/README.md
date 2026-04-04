# Data

Raw data files and reference code lists used for evaluation.

## Structure

- `raw/` — Source files downloaded from NHS England, QOF, etc.
- `opcs/` — OPCS-4 procedure codes (XML)
- `gold_standard/` — Validated code lists used as ground truth for testing
- `sample_outputs/` — Example pipeline outputs for each stage (for evaluation development)

Large files (`.xlsm`, `.xlsx`, `.csv`) are gitignored. Download them manually or run the ingestion scripts.

## Files

### raw/Business_Rules_Combined_Change_Log_QOF+2024-25_v49.1.xlsm

QOF (Quality and Outcomes Framework) business rules for 2024-25. Contains the clinical codes required to meet each QOF indicator across primary care conditions (diabetes, hypertension, asthma, etc.).

- **Source:** [NHS England QOF Business Rules](https://digital.nhs.uk/data-and-information/data-collections-and-data-sets/data-collections/quality-and-outcomes-framework-qof)
- **Version:** v49.1 (2024-25)
- **Format:** Excel with macros (.xlsm)
- **Size:** ~1.7MB
- **Used by:** `backend/app/ingestion/ingest_qof.py` (NICE-017)

### raw/opencodelists/

Pre-downloaded CSV exports from [OpenCodelists](https://www.opencodelists.org) (Bennett Institute, University of Oxford). Each CSV contains SNOMED codes for a specific condition.

- **Source:** [OpenCodelists](https://www.opencodelists.org)
- **Format:** CSV (code, term)
- **Includes:** diabetes-type-2, diabetes-mellitus, hypertension, atrial-fibrillation, asthma, heart-failure, stroke
- **Used by:** `backend/app/graph/nodes/opencodelists_retriever.py` (NICE-018)
- **Note:** The pipeline checks SQLite for pre-downloaded data first, falls back to live scraping if not found

### opcs/OPCS411 CodesAndTitles Nov 2025 V1.0.xml

OPCS-4 procedure and operation codes used in NHS secondary care.

- **Source:** [NHS England OPCS-4](https://digital.nhs.uk/data-and-information/information-standards/information-standards-and-data-collections-including-extractions/publications-and-notifications/standards-and-collections/opcs-4)
- **Version:** 4.11, November 2025
- **Format:** XML (`<code CODE="A01.1" TITLE="Hemispherectomy"/>`)
- **Size:** ~917KB, 12,122 codes
- **Used by:** `backend/app/ingestion/ingest_opcs.py`

### Ingestion

Run all ingestion at once:

```bash
cd backend
python -m app.ingestion.run_all --data-dir ../data
```

This populates SQLite (structured queries) and ChromaDB (semantic search) with all data sources. Takes ~8 minutes on first run.
