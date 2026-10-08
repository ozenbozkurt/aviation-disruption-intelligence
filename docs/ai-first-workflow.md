# AI-first EUROCONTROL case-study workflow

The repetitive work should be automated. The analyst's job is to understand
the question, review the evidence, challenge the explanation and communicate
the result.

## What GitHub Actions now does

A manual **EUROCONTROL Case Study** workflow can:

1. fetch every day in a requested date range,
2. skip and disclose missing dates,
3. write a clean CSV,
4. calculate simple period-level metrics,
5. identify the sample's highest-stress day by ATFM delay per flight,
6. write a Markdown analyst brief,
7. write an AI-ready explanation prompt,
8. package the outputs as a downloadable GitHub Actions artifact.

No local PowerShell work is required for the normal workflow.

## What the human should learn

You do **not** need to memorize setup commands.

You should be able to explain:

- what the source is,
- what each metric means,
- what changed across the period,
- which statements are observations versus hypotheses,
- what extra data would be required before claiming a cause,
- what an operations team might investigate next.

That is the higher-value skill.

## Run it in GitHub

Open **Actions -> EUROCONTROL Case Study -> Run workflow**.

Choose a country and date range, then run it. When the job finishes, download
the generated artifact.

For portfolio-quality work, review the generated Markdown instead of accepting
it blindly. The report deliberately avoids inventing causal explanations.
