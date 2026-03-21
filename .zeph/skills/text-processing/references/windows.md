# Windows Text Processing (PowerShell)

Windows uses PowerShell cmdlets instead of Unix text tools.

## Equivalents Quick Reference

| Unix | PowerShell |
|------|-----------|
| `cat file` | `Get-Content file` |
| `head -n 10` | `Get-Content file -Head 10` |
| `tail -n 10` | `Get-Content file -Tail 10` |
| `tail -f` | `Get-Content file -Wait -Tail 10` |
| `grep pattern` | `Select-String -Pattern "pattern" file` |
| `wc -l` | `(Get-Content file).Count` |
| `sort` | `Get-Content file \| Sort-Object` |
| `uniq` | `Get-Content file \| Sort-Object -Unique` |
| `tr 'a-z' 'A-Z'` | `(Get-Content file).ToUpper()` |
| `sed 's/old/new/g'` | `(Get-Content file) -replace 'old','new'` |
| `cut -d',' -f2` | `Import-Csv file \| Select-Object Column2` |

## Reading Files

```powershell
# Read entire file
Get-Content file.txt

# First/last N lines
Get-Content file.txt -Head 20
Get-Content file.txt -Tail 20

# Follow file (like tail -f)
Get-Content file.txt -Wait -Tail 10

# Read as single string
Get-Content file.txt -Raw

# Read with encoding
Get-Content file.txt -Encoding UTF8

# Line count
(Get-Content file.txt).Count
(Get-Content file.txt | Measure-Object -Line).Lines
```

## Search (grep equivalent)

```powershell
# Basic pattern search
Select-String -Pattern "error" file.txt

# Case-sensitive
Select-String -Pattern "Error" file.txt -CaseSensitive

# Regex
Select-String -Pattern "\d{3}-\d{4}" file.txt

# Multiple files
Select-String -Pattern "TODO" -Path "*.cs" -Recurse

# Invert match (lines NOT matching)
Select-String -Pattern "debug" file.txt -NotMatch

# Context lines (like grep -C)
Select-String -Pattern "error" file.txt -Context 2,2

# Count matches
(Select-String -Pattern "error" file.txt).Count

# Extract matched text only
Select-String -Pattern "(\w+)@(\w+)" file.txt | ForEach-Object { $_.Matches.Value }
```

## Find and Replace (sed equivalent)

```powershell
# Replace in output (not in-place)
(Get-Content file.txt) -replace 'old', 'new'

# In-place replace
(Get-Content file.txt) -replace 'old', 'new' | Set-Content file.txt

# Regex replace
(Get-Content file.txt) -replace '\d+', 'NUM'

# Multiple replacements
(Get-Content file.txt) -replace 'foo', 'bar' -replace 'baz', 'qux'

# Delete lines matching pattern
Get-Content file.txt | Where-Object { $_ -notmatch 'pattern' } | Set-Content output.txt

# Delete empty lines
Get-Content file.txt | Where-Object { $_.Trim() -ne '' } | Set-Content output.txt
```

## Sorting and Deduplication

```powershell
# Sort alphabetically
Get-Content file.txt | Sort-Object

# Sort descending
Get-Content file.txt | Sort-Object -Descending

# Numeric sort
Get-Content file.txt | Sort-Object { [int]$_ }

# Unique (deduplicate)
Get-Content file.txt | Sort-Object -Unique

# Sort by field (CSV)
Import-Csv data.csv | Sort-Object Column1

# Group and count (like sort | uniq -c)
Get-Content file.txt | Group-Object | Sort-Object Count -Descending | Select-Object Count, Name
```

## Field Extraction (cut/awk equivalent)

```powershell
# Split and extract field
Get-Content file.txt | ForEach-Object { ($_ -split ',')[1] }

# CSV processing (native)
Import-Csv data.csv | Select-Object Name, Email
Import-Csv data.csv | Where-Object { [int]$_.Age -gt 30 }

# Tab-delimited
Import-Csv data.tsv -Delimiter "`t"

# Custom delimiter split
Get-Content file.txt | ForEach-Object { ($_ -split ':')[0] }
```

## Calculations (awk equivalent)

```powershell
# Sum a column
Import-Csv data.csv | Measure-Object -Property Amount -Sum | Select-Object Sum

# Average
Import-Csv data.csv | Measure-Object -Property Score -Average | Select-Object Average

# Min/Max
Import-Csv data.csv | Measure-Object -Property Value -Minimum -Maximum

# Count by category (like awk group_by)
Import-Csv data.csv | Group-Object Category | Select-Object Name, Count
```

## Character Translation (tr equivalent)

```powershell
# To uppercase
(Get-Content file.txt).ToUpper()

# To lowercase
(Get-Content file.txt).ToLower()

# Replace characters
(Get-Content file.txt -Raw) -replace ':', "`t"

# Remove characters
(Get-Content file.txt -Raw) -replace '[0-9]', ''

# Remove carriage returns (DOS → Unix)
(Get-Content file.txt -Raw) -replace "`r`n", "`n" | Set-Content -NoNewline output.txt
```

## Multi-file Operations

```powershell
# Replace across files
Get-ChildItem -Recurse -Filter "*.txt" | ForEach-Object {
    (Get-Content $_.FullName) -replace 'old', 'new' | Set-Content $_.FullName
}

# Search across files
Get-ChildItem -Recurse -Filter "*.cs" | Select-String -Pattern "TODO"

# Merge files
Get-ChildItem *.txt | ForEach-Object { Get-Content $_ } | Set-Content merged.txt
```

## Clipboard

```powershell
# Copy to clipboard
Get-Content file.txt | Set-Clipboard

# Paste from clipboard
Get-Clipboard

# Process clipboard
Get-Clipboard | Sort-Object -Unique | Set-Clipboard
```
