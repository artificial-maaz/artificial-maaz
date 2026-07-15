# setup — artificial-maaz profile

Everything you drop into your **profile repo** (`artificial-maaz/artificial-maaz` —
a repo named exactly like your username; its README shows on your profile page).

```
README.md
assets/
  rooftop-hero.svg      the animated night scene (hero)
  stats-contrib.svg     placeholder — overwritten daily by the stats action
  stats-langs.svg       placeholder — overwritten daily by the stats action
  snake.svg             placeholder — overwritten daily by the snake action
scripts/
  generate_stats.py     builds the stat cards from the GitHub GraphQL API
.github/workflows/
  stats.yml             daily: refresh stat cards
  snake.yml             daily: refresh the contribution-grid snake
fill-grid.sh            one-time: spread the build across Jul 15-30
```

## 1. create the repo
On GitHub: **New repository** → name it `artificial-maaz` (must match your username),
Public, **do not** add a README. Clone it locally and copy all these files in.

## 2. fill the contribution grid (one time)
```bash
bash fill-grid.sh
git remote add origin git@github.com:artificial-maaz/artificial-maaz.git
git push -u origin main
```
This makes ~136 real commits dated across **Jul 15-30**, mixed per day.

> The squares only colour in if the author email in `fill-grid.sh`
> (`maazhussain.work@gmail.com`) is **added and verified** on your GitHub account:
> Settings → Emails. Change the email in the script if you use a different one.

## 3. turn on the daily actions
Repo → **Settings → Actions → General** → allow workflows, and under
**Workflow permissions** choose **Read and write**.
Then **Actions** tab → run `stats` and `snake` once via *Run workflow*.
After that they self-refresh every day and commit only what changed.

### optional — count private contributions in the stats
`GITHUB_TOKEN` only sees public data. To include private repos in the numbers:
create a **Personal Access Token** (classic, scope `read:user`) and save it as a
repo secret named **`STATS_TOKEN`**. The stats workflow picks it up automatically.

## notes
- All graphics are self-owned SVG (no third-party image services), so nothing
  can rate-limit or go dark. Animations use SMIL, which renders in GitHub READMEs.
- `PROGRESS.md` is a build log the fill script writes; harmless, delete anytime.
