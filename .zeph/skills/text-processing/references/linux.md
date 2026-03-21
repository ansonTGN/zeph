# Linux (GNU) Text Processing

GNU coreutils provide extended flags not available on BSD/macOS.

## sed (GNU sed)

```bash
# In-place edit (no backup suffix needed)
sed -i 's/foo/bar/g' file.txt

# In-place with backup
sed -i.bak 's/foo/bar/g' file.txt

# Case-insensitive replace (GNU-only I flag)
sed 's/foo/bar/gI' file.txt

# Extended regex (-r or -E)
sed -r 's/([a-z]+)_([a-z]+)/\2_\1/g' file.txt
sed -E 's/([a-z]+)_([a-z]+)/\2_\1/g' file.txt    # also works

# Insert/append (GNU allows inline text)
sed '/pattern/i new line' file.txt
sed '/pattern/a new line' file.txt

# Null-separated records (for filenames with newlines)
sed -z 's/\n/,/g' file.txt
```

## sort (GNU sort)

```bash
# Human-readable numeric sort (1K, 2M, 3G) — GNU-only
sort -h file.txt

# Version sort (1.2 < 1.10) — GNU-only
sort -V versions.txt

# Parallel sort — GNU-only
sort --parallel=4 large.txt

# Random sort — GNU-only
sort -R file.txt

# Debug key parsing — GNU-only
sort --debug -k2 file.txt

# Compress temp files — GNU-only
sort --compress-program=gzip large.txt

# All except last N lines — GNU head only
head -n -5 file.txt
```

## cut (GNU cut)

```bash
# Complement (everything except selected) — GNU-only
cut -d',' -f2 --complement data.csv

# Zero-terminated lines — GNU-only
cut -z -d',' -f1 data.csv

# Output delimiter — GNU-only
cut -d',' -f1,3 --output-delimiter=$'\t' data.csv
```

## wc (GNU wc)

```bash
# Longest line length — GNU-only
wc -L file.txt

# Zero-terminated lines — GNU-only
wc -l --files0-from=filelist.txt
```

## awk (gawk — GNU awk)

```bash
# In-place edit — gawk 4.1+
gawk -i inplace '{gsub(/old/, "new")}1' file.txt

# Include files — gawk-only
gawk '@include "lib.awk"' file.txt

# Network (TCP/UDP) — gawk-only
gawk 'BEGIN { "/inet/tcp/0/host/80" |& getline; print }'

# Time functions — gawk-only
gawk 'BEGIN { print systime(); print strftime("%Y-%m-%d") }'

# Regex constants — gawk-only
gawk '$0 ~ @/pattern/i' file.txt     # case-insensitive regex
```

## GNU-specific tools

```bash
# tac — reverse lines (not on macOS)
tac file.txt

# shuf — randomize lines (not on macOS)
shuf file.txt
shuf -n 5 file.txt                   # random 5 lines

# numfmt — format numbers (not on macOS)
numfmt --to=iec 1048576              # → 1.0M
du -b file | numfmt --to=iec --field=1

# fold — wrap long lines
fold -w 80 file.txt
fold -s -w 80 file.txt              # break at spaces

# fmt — reformat paragraphs
fmt -w 72 file.txt

# expand/unexpand — tabs ↔ spaces
expand -t 4 file.txt
unexpand -t 4 --first-only file.txt

# comm — compare sorted files (column output)
comm sorted1.txt sorted2.txt
comm -23 sorted1.txt sorted2.txt     # lines only in first
comm -13 sorted1.txt sorted2.txt     # lines only in second
comm -12 sorted1.txt sorted2.txt     # lines in both
```

## Replace in multiple files

```bash
# GNU sed in-place across files
find . -name "*.txt" -exec sed -i 's/old/new/g' {} +

# With grep pre-filter (faster for large trees)
grep -rl "old" --include="*.txt" . | xargs sed -i 's/old/new/g'
```
