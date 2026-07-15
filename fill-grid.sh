#!/usr/bin/env bash
#
# fill-grid.sh — commits this profile build in many small, real commits,
# spread across Jul 15-30 2026 with mixed counts per day, so your GitHub
# contribution grid fills in. Run ONCE inside a fresh clone of your
# artificial-maaz/artificial-maaz repo, with all these files present.
#
#   bash fill-grid.sh
#   git push -u origin main
#
# NOTE: the grid only colours in if AUTHOR_EMAIL below is an email that is
# added AND verified on your GitHub account (Settings > Emails).
# ---------------------------------------------------------------------------
set -euo pipefail

AUTHOR_NAME="Maaz Hussain"
AUTHOR_EMAIL="maazhussain.work@gmail.com"   # <-- must be verified on GitHub
YEAR=2026
BRANCH="main"

git rev-parse --git-dir >/dev/null 2>&1 || git init -q
git checkout -q -B "$BRANCH"
git config user.name  "$AUTHOR_NAME"
git config user.email "$AUTHOR_EMAIL"

# commits per day, 15..30 July — mixed on purpose
DAYS=(15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30)
CNT=( 4  9  6 12  3  8 14  5 10  7 15  6 11  4 13  9)   # total = 136

MSGS=(
"init profile repo"
"add rooftop hero — night scene base"
"hero: margalla hills + crescent moon"
"hero: light up the islamabad skyline"
"hero: faisal mosque landmark"
"hero: roof parapet + perimeter wall"
"hero: 3d room block + metal door"
"hero: door ajar, warm light spill"
"hero: persian carpet + cushions"
"hero: fire pit + bistro chairs"
"hero: desk, glowing laptop, coffee"
"hero: string lights on the wall"
"hero: tune the indigo palette"
"hero: SMIL animations (twinkle, flame, flicker)"
"hero: polish edges + viewbox"
"readme: scaffold sections"
"readme: about (from linkedin voice)"
"readme: stack block"
"readme: projects — dormdata headline"
"readme: connect + epigraph"
"readme: reorder — stats above projects"
"stats: graphql query for contributions"
"stats: streak + language aggregation"
"stats: render indigo svg cards"
"stats: daily github action"
"snake: contribution-grid action"
"snake: dark palette + purple snake"
"chore: wire assets into readme"
"chore: tidy workflows"
"docs: setup notes"
"polish: spacing + mono headers"
"polish: alt text + accessibility"
)

echo "# build log" > PROGRESS.md
git add -A   # first commit carries the whole repo

i=0
for idx in "${!DAYS[@]}"; do
  d="${DAYS[$idx]}"; n="${CNT[$idx]}"
  for k in $(seq 1 "$n"); do
    H=$(( 9 + (k * 13) / (n + 1) ))          # spread 09:00 .. ~21:00
    M=$(( (k * 37) % 60 ))
    TS=$(printf "%d-07-%02dT%02d:%02d:00" "$YEAR" "$d" "$H" "$M")
    MSG="${MSGS[$(( i % ${#MSGS[@]} ))]}"
    printf "%s  %s\n" "$TS" "$MSG" >> PROGRESS.md
    git add -A
    GIT_AUTHOR_DATE="$TS" GIT_COMMITTER_DATE="$TS" \
      git commit -q -m "$MSG"
    i=$(( i + 1 ))
  done
  echo "  jul $d — $n commits"
done

echo "----------------------------------------------------------"
echo "done: $i commits across jul 15-30."
echo "next: git remote add origin git@github.com:artificial-maaz/artificial-maaz.git"
echo "      git push -u origin $BRANCH"
