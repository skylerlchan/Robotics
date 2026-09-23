# Put-away: the job, and the instrument that says whether it works

One job: **put everything back where it lives.** One number: **clean runs in a row,
with nobody touching anything.** The bar is 100.

Everything here runs with the lerobot env python:

```bash
P=/Users/skyler/miniforge3/envs/lerobot_alohamini/bin/python
```

Keep the scorer in its own process. OpenCV and PyAV both ship libav on macOS, and
loading them together can crash.

## 1. Set up the job (15 minutes, no robot)

1. Edit `job.toml`: name each object and each bin, and say which bin each object
   belongs in. Start with 4 objects and 2 bins.
2. Print the markers and stick them on:
   ```bash
   $P markers.py          # writes markers.png, print at 100%
   ```
   Object markers go on top of each object, bin markers on the front of each bin.
3. Put the camera somewhere fixed, seeing the whole work area. Tape its feet down.
   Every run has to use the same view or the numbers drift.
4. Check the camera can see everything:
   ```bash
   $P score.py watch      # live overlay, q to quit
   $P score.py state      # one frame, printed
   ```
   Green cross = home. Red cross = out of place. Grey circle = a bin's catch area.

If the camera will not open, grant your terminal Camera access in
System Settings > Privacy & Security > Camera.

## 2. Score a run

```bash
$P score.py run --label teleop            # or --label act-v1
```

It reads the scene, waits for you to press Enter when the robot has finished or
given up, reads the scene again, and appends a line to `runs.jsonl` with before
and after photos in `runs/`.

If you had to touch anything, say so. That is the number that decides everything:

```bash
$P score.py run --label act-v1 --interventions 1 --notes "sock stuck on the rim"
```

## 3. See where you stand

```bash
$P report.py --by-label
```

Clean runs, objects put away, interventions per run, and the streak toward 100.

## The ladder

| Week | What you run | What you learn |
|---|---|---|
| 1 | `score.py run --label human` a few times, doing the job yourself | how long the job takes and whether the scoring is honest |
| 2 | teleop the arm through the job, `--label teleop` | whether the job is even doable with this hardware |
| 3 | record 50 demos, train ACT, `--label act-v1` over 50 runs | the success rate, which is the whole project in one number |
| 4 | run it daily with a phone takeover when stuck | interventions per run, and whether that curve is falling |

**Kill line, set now:** under 70% clean after 50 demos, with no improvement at
200 demos, or interventions per run not halving every two weeks. Then change the
job, not the model.

## Files

- `job.toml` — the job: objects, bins, where things live
- `score.py` — detect, score, log (`selftest`, `state`, `watch`, `run`)
- `markers.py` — printable marker sheet
- `report.py` — clean-run streak against the bar
- `runs.jsonl`, `runs/` — the log and the before/after photos (git-ignored; they
  are pictures of your home, and this repo is public)
