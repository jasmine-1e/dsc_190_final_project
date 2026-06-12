# dsc_190_project
# survey-dashboard

Takes two CSVs from the UCSD IPPS supplier survey (one for structured responses, one for the open-ended text) and generates an interactive HTML dashboard you can just open in your browser — no server needed.

## Usage

```bash
uv add "git+https://github.com/<your-username>/survey-dashboard.git"
```

**Build a dashboard file:**
```bash
survey-dashboard build --structured s_res_fake_500.csv --freetext s_res_free_response_fake.csv --output dashboard.html
```

Add `--open` to open it in your browser right away.

**Or just open it immediately without saving:**
```bash
survey-dashboard serve --structured s_res_fake_500.csv --freetext s_res_free_response_fake.csv
```

**Just want the JSON file** (e.g. for GitHub Pages):
```bash
survey-dashboard json --structured s_res_fake_500.csv --freetext s_res_free_response_fake.csv --output survey_data.json
```

The two CSVs need to have the same number of rows in the same order — one row per respondent. See `src/survey_dashboard/merge.py` for the expected column names.
