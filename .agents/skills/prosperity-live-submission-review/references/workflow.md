# Live Review Checklist

Use this after every downloaded submission bundle.

1. analyze the downloaded `.log` with `scripts/analyze_submission_log.py`
2. extract reconstructed round files with `scripts/extract_submission_round_data.py`
3. compare hidden order-book rows against the public sample files when they exist
4. estimate product contribution, make/take split, and max inventory
5. identify one or two repeated live trade patterns worth acting on
6. reject changes that only help the hidden reconstruction while clearly hurting the public challenge window
7. end with one explicit upload recommendation
