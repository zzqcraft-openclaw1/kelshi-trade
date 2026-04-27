# Morning Workflow

A simple daily workflow for using `kelshi-trade` as a paper-only NBA research tool.

## 1. Run Preflight

```bash
kelshi-trade doctor
```

If preflight fails, fix setup issues before trusting any downstream output.

Check for:
- paper-only mode still enabled
- writable db / reports / var paths
- either:
  - a usable local raw snapshot, or
  - read-only Kalshi credentials

## 2. Run the Daily Paper Review

```bash
kelshi-trade run-nba-paper-review
```

This should:
- use the current raw snapshot or fetch one in read-only mode
- extract and filter NBA-linked markets
- generate review reports
- optionally write game-winner forecast output
- write a run manifest for reproducibility

## 3. Open the Newest Run Folder

Look under:
- `reports/runs/<run_id>/nba_paper_review/`
- `var/runs/<run_id>/`

Start with:
- top review report
- best-per-game report
- summary-by-game report
- forecast JSON if present

## 4. Check the Manifest

Open `run_manifest.json` and confirm:
- run timestamp
- source snapshot used
- output artifact paths
- candidate/filter counts

If the manifest looks wrong, treat the run as suspect until explained.

## 5. Triage the Slate

Focus first on the cleanest game-winner markets.

Avoid getting distracted by noisy candidates just because they appear in output.

This is a research workflow, not a permission slip to force action.

## 6. Record a Thesis Before Any Simulated Action

For any market worth attention, write down:
- why it looks interesting
- what assumption matters most
- what would invalidate the view
- why the market may be wrong

If there is no clear thesis, skip it.

## 7. Prefer Fewer Better Spots

The system is designed around discipline, not activity.

Remember the core rule:
- no edge -> no trade
- narrow scope beats forced action

## 8. Capture a Market Baseline Near Tip

For NBA game-winner markets, also capture Kalshi odds about 30 minutes before the game starts.

Store at least:
- capture timestamp
- market id
- implied probability
- YES bid / YES ask if available
- any market quality concerns

This gives a stronger baseline than the earlier morning snapshot and lets us evaluate whether the tool beats the market closer to game time.

## 9. Review Later

After the slate resolves:
- compare forecast vs outcome
- compare forecast vs the 30-min pregame market baseline
- review good skips and bad takes
- note where confidence was fake or unsupported
- feed lessons back into the model and workflow

## Suggested Daily Rhythm

- 07:00 — `kelshi-trade doctor`
- 07:02 — `kelshi-trade run-nba-paper-review`
- 07:05–07:15 — review reports and manifest
- 07:15+ — deeper human judgment on the best candidates only

## Guiding Principle

The point is not to generate more output.
The point is to generate **cleaner decisions** inside a paper-only workflow.
