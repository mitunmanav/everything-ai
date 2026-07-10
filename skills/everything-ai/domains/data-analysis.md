# Data Analysis

## Scope Defaults
Treat CSV, spreadsheet, metrics, analysis, and dashboard requests as an evidence workflow: understand the table, clean only what is safe, compute trustworthy summaries, surface anomalies, and explain limits. Start read-only when the data source is unclear. Prefer reproducible scripts, saved queries, and clear column assumptions over manual spreadsheet edits.

Default scope includes data inventory, schema notes, row counts, missing values, duplicate checks, type normalization, core metrics, trend or segment views, chart recommendations, and a plain-language findings report. Exclude destructive cleanup, live database writes, private data sharing, and business-critical decisions without confirmation.

## Checklist
- Identify each input file, sheet, table, or metric source and record row and column counts.
- Map columns to business meanings and flag ambiguous names.
- Check missing values, duplicates, impossible values, date ranges, and outliers.
- Preserve the raw data and perform transformations in a repeatable step.
- Calculate headline metrics with formulas or code that can be inspected.
- Segment results by the dimensions most likely to explain variation.
- Separate facts from interpretations and mark confidence for each finding.
- Recommend dashboard views only after the useful decisions are clear.

## Pitfalls
- Trusting column names without checking examples and types.
- Deleting rows or overwriting a spreadsheet before preserving the original.
- Reporting averages that hide segment, cohort, or time-based differences.
- Treating correlation as causation.
- Building a dashboard before defining who will use it and what decision it supports.
- Ignoring privacy, credentials, and personally identifiable information in exported data.

## Success Looks Like
The user receives a reproducible analysis with clear inputs, cleaned assumptions, verified calculations, useful charts or tables, and a concise findings report. The output names what changed, what is uncertain, which data quality issues matter, and which next question should be answered with more data or stakeholder context.

## Examples
Example 1: "Analyze this sales CSV." Load the file read-only, profile columns, normalize dates and currency, summarize revenue by month and channel, flag missing customer IDs, and report the top drivers plus caveats.

Example 2: "Make a dashboard for our metrics." First identify the decision owner and core metrics, then propose views for acquisition, activation, retention, revenue, and data quality before building or changing any live dashboard.

## Frameworks

- **EDA first**: Explore before modeling. Distributions, missing values, outliers, correlations — always check these first.
- **Show the data first**: Plot raw data before aggregating. Aggregates hide patterns, outliers, and bimodal distributions.
- **Reproducibility**: Every step logged, random seeds set, outputs versioned. Analysis that can't be reproduced isn't analysis.

## Live Facts

The following facts go stale — search before using:
- Current version of pandas, numpy, scikit-learn (breaking changes between major versions)
- Current best practices for specific analysis types (LLM eval frameworks, etc.)
