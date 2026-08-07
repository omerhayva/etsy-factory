# Product Factory Report

## Purpose
Module 09 adds an orchestration layer that connects the existing research, niche intelligence, product intelligence, design intelligence, SEO/compliance, and commercial validation engines into one automated workflow.

## Workflow
1. Research
2. Niche Intelligence
3. Product Intelligence
4. Design Intelligence
5. SEO & Compliance
6. Commercial Validation
7. Export

## Inputs
The factory accepts:
- Niche
- Audience
- Product Category
- Language
- Market

## Quality Control
If commercial validation returns `NEEDS IMPROVEMENT`, the factory retries once using the improvement recommendations from the first validation pass.
If the retry still does not meet the quality threshold, the factory does not export approved product folders.

## Persistence
The database now tracks:
- `factory_runs`
- `pipeline_logs`
- `workflow_reports`

## Export Output
For each approved product, the factory creates a dedicated folder containing:
- `listing.json`
- `listing.md`
- `design_prompt.txt`
- `summary.txt`

## Integration Notes
The factory reuses the existing engines and does not duplicate the underlying research, product, design, SEO, or commercial scoring logic.
