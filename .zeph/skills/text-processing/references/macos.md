# macOS (BSD) Text Processing

macOS ships with BSD variants of text tools. Key differences from GNU/Linux noted below.

## sed (BSD sed)

```bash
# In-place edit — REQUIRES empty string argument after -i
sed -i '' 's/foo/bar/g' file.txt

# In-place with backup
sed -i '.bak' 's/foo/bar/g' file.txt

# Extended regex — use -E (not -r)
sed -E 's/([a-z]+)_([a-z]+)/\2_\1/g' file.txt

# Insert/append — require newline after command
sed '/pattern/i\
new line' file.txt
sed '/pattern/a\
new line' file.txt

# No case-insensitive flag (no I modifier)
# Workaround: use character classes
sed 's/[Ff][Oo][Oo]/bar/g' file.txt
```

### BSD sed gotchas

- `sed -i` without `''` creates a backup with empty extension and edits the backup
- No `-z` (null-separator) flag
- No `I` flag for case-insensitive substitution
- Insert/append syntax requires literal newline after backslash

## sort (BSD sort)

```bash
# No -h (human-readable sort) — workaround:
# Pipe through awk to normalize sizes first

# No -V (version sort) — workaround:
sort -t. -k1,1n -k2,2n -k3,3n versions.txt

# No --parallel or --compress-program

# No -R (random sort) — use shuf if installed, or:
awk 'BEGIN{srand()}{print rand(), $0}' file.txt | sort -n | cut -d' ' -f2-
```

## head/tail (BSD)

```bash
# No negative count: head -n -5 does NOT work on macOS
# Workaround: use awk or calculate lines
total=$(wc -l < file.txt)
head -n $((total - 5)) file.txt

# tail works the same
tail -n 20 file.txt
tail -f logfile.log
tail -n +6 file.txt                  # from line 6 onward
```

## cut (BSD cut)

```bash
# No --complement flag — workaround with awk:
awk -F',' '{$2=""; print}' OFS=',' data.csv

# No --output-delimiter — workaround:
cut -d',' -f1,3 data.csv | tr ',' '\t'
```

## wc (BSD wc)

```bash
# No -L (longest line) — workaround:
awk '{ if (length > max) max = length } END { print max }' file.txt
```

## awk (BSD awk / nawk)

macOS ships with a POSIX-compliant awk. Most standard features work.

```bash
# toupper/tolower — available (POSIX standard)
awk '{print toupper($1)}' file.txt

# No in-place edit — redirect to temp file
awk '{gsub(/old/, "new")}1' file.txt > tmp && mv tmp file.txt

# No @include, no network, no strftime in BSD awk
# Install gawk for these: brew install gawk
```

## Missing GNU tools — install via Homebrew

```bash
# Install GNU coreutils (prefixed with g: gsort, gcut, gwc, etc.)
brew install coreutils

# Use GNU versions
gsort -h file.txt                    # human-readable sort
gcut --complement -d',' -f2 data.csv
gwc -L file.txt                     # longest line

# Install GNU sed
brew install gnu-sed
# Use as gsed, or add to PATH to replace BSD sed

# Install GNU awk
brew install gawk

# Other useful tools
brew install grep                    # GNU grep (ggrep)
brew install findutils               # GNU find (gfind)
```

## Replace in multiple files

```bash
# BSD sed requires -i ''
find . -name "*.txt" -exec sed -i '' 's/old/new/g' {} +

# With grep pre-filter
grep -rl "old" --include="*.txt" . | xargs sed -i '' 's/old/new/g'

# Alternative: use perl (always available on macOS)
find . -name "*.txt" -exec perl -pi -e 's/old/new/g' {} +
```

## macOS-specific text tools

```bash
# pbcopy/pbpaste — clipboard integration
cat file.txt | pbcopy               # copy to clipboard
pbpaste > output.txt                # paste from clipboard
pbpaste | sort | uniq               # process clipboard content

# textutil — rich text conversion (macOS-only)
textutil -convert txt document.rtf   # RTF to plain text
textutil -convert html document.docx # DOCX to HTML
```
