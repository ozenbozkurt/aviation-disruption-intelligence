# Power BI handoff: EUROCONTROL daily CSV

This step turns an API response into a **table**.

That matters because analytical tools such as Excel and Power BI are happiest
when every observation is a row and every variable is a column.

## Run one real export

After installing the EUROCONTROL extra:

```sh
python -m pip install -e ".[eurocontrol]"
```

run:

```sh
python examples/export_eurocontrol_daily.py \
  --country IT \
  --date 2026-03-27 \
  --output data/eurocontrol_it_2026-03-27.csv
```

On PowerShell you can put the command on one line:

```powershell
python examples/export_eurocontrol_daily.py --country IT --date 2026-03-27 --output data/eurocontrol_it_2026-03-27.csv
```

The script calls the public EUROCONTROL Data app beta API and creates a flat
CSV with:

- country,
- snapshot ID and date,
- total flights,
- total ATFM-delay minutes,
- ATFM delay per flight,
- arrival punctuality,
- departure punctuality,
- source/provenance.

## Why flat CSV?

A nested API response is good for software, but awkward for a dashboard.

A flat CSV looks conceptually like this:

| country | date | flights | ATFM delay | arrival punctuality |
| --- | --- | ---: | ---: | ---: |
| Italy | 2026-03-27 | 5586 | 397 | 77.0152 |

Now Power BI can read the columns directly, calculate trends, and draw charts.

## Important

The command makes a real network request. Automated tests do **not** call
EUROCONTROL; they use local typed test data so CI remains reliable.
