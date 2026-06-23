# uploads/

Drop files here for **Agent 08 (Challenger)** to analyze.

Supported formats:
- **PDF** (`.pdf`) — read natively by Claude (annual reports, decks, papers)
- **Word** (`.docx`)
- **Web/HTML** (`.htm`, `.html`)
- **Text/data** (`.txt`, `.md`, `.csv`, `.tsv`, `.json`, `.yaml`, `.log`)

Then run, e.g.:

```bash
python agent8_challenger.py "Analyze the uploaded 10-K for margin and growth risks"
```

By default Agent 08 reads **every** file in this folder. To target specific
files: `--files uploads/report.pdf uploads/notes.txt`.
