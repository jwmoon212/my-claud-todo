# =============================================================================
# find_kenji.ps1
# Finds all files in C:\Downloads that contain the word "Kenji"
# (in filename OR file content) and moves them into C:\Downloads\Kenji.
#
# Usage:
#   .\find_kenji.ps1            <- dry run (safe, nothing is moved)
#   .\find_kenji.ps1 -Execute   <- actually moves the files
# =============================================================================

# --- STEP 1: Define a parameter so the script has two modes ----------------
# When you run the script without -Execute it just SHOWS what it would do.
# This is the "dry run" safety net. Nothing touches the disk until you're ready.
param(
    [switch]$Execute
)

# --- STEP 2: Set the folder paths ------------------------------------------
# $SourceFolder  = where to search
# $DestFolder    = where matching files will land
$SourceFolder = "C:\Downloads"
$DestFolder   = "C:\Downloads\Kenji"

# --- STEP 3: Tell the user which mode we're in -----------------------------
if ($Execute) {
    Write-Host ""
    Write-Host "=== EXECUTE MODE — files WILL be moved ===" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "=== DRY RUN MODE — nothing will be moved ===" -ForegroundColor Cyan
    Write-Host "    Run with -Execute when you're ready."
}
Write-Host ""

# --- STEP 4: Check that the source folder exists ---------------------------
# If C:\Downloads doesn't exist, stop early with a clear message.
if (-not (Test-Path $SourceFolder)) {
    Write-Host "ERROR: Source folder not found: $SourceFolder" -ForegroundColor Red
    exit 1
}

# --- STEP 5: Gather every file in the source folder (non-recursive) --------
# Get-ChildItem lists files. -File means "skip folders".
# Remove -Recurse here intentionally — only the top level of Downloads.
# Add -Recurse if you want to search subfolders too.
Write-Host "Scanning: $SourceFolder" -ForegroundColor Gray
$AllFiles = Get-ChildItem -Path $SourceFolder -File

Write-Host "Total files found: $($AllFiles.Count)"
Write-Host ""

# --- STEP 6: Filter files that match "Kenji" -------------------------------
# We check TWO things for each file:
#   (a) Does the filename itself contain "Kenji"?
#   (b) Is the file a text file, and does its content contain "Kenji"?
$MatchedFiles = @()   # empty array — we'll add matches here

foreach ($File in $AllFiles) {

    $MatchReason = $null   # reset each loop

    # (a) Check filename  ------------------------------------------------
    if ($File.Name -match "Kenji") {
        $MatchReason = "filename contains 'Kenji'"
    }

    # (b) Check content — only for text-like extensions ------------------
    # Reading binary files (images, zips) would produce garbage, so we
    # limit content scanning to common text-based file types.
    if (-not $MatchReason) {
        $TextExtensions = @(".txt", ".md", ".csv", ".json", ".xml",
                            ".html", ".htm", ".log", ".py", ".js",
                            ".ts", ".css", ".yaml", ".yml", ".ini",
                            ".cfg", ".ps1", ".sh", ".bat", ".docx")

        if ($TextExtensions -contains $File.Extension.ToLower()) {
            # Select-String is PowerShell's grep — it searches file content
            $Hit = Select-String -Path $File.FullName -Pattern "Kenji" -Quiet
            if ($Hit) {
                $MatchReason = "content contains 'Kenji'"
            }
        }
    }

    # If either check matched, record this file
    if ($MatchReason) {
        $MatchedFiles += [PSCustomObject]@{
            File   = $File
            Reason = $MatchReason
        }
    }
}

# --- STEP 7: Report what we found ------------------------------------------
if ($MatchedFiles.Count -eq 0) {
    Write-Host "No files containing 'Kenji' were found in $SourceFolder." -ForegroundColor Green
    exit 0
}

Write-Host "Files matching 'Kenji' ($($MatchedFiles.Count) found):" -ForegroundColor Green
foreach ($Match in $MatchedFiles) {
    Write-Host "  [+] $($Match.File.Name)  <-- $($Match.Reason)" -ForegroundColor White
}
Write-Host ""

# --- STEP 8: Dry run ends here ---------------------------------------------
if (-not $Execute) {
    Write-Host "Dry run complete. No files were moved." -ForegroundColor Cyan
    Write-Host "To move the files above, run:"
    Write-Host "    .\find_kenji.ps1 -Execute" -ForegroundColor Yellow
    exit 0
}

# --- STEP 9: Create the destination folder if it doesn't exist yet ---------
# -Force means "don't error if the folder already exists".
if (-not (Test-Path $DestFolder)) {
    Write-Host "Creating folder: $DestFolder"
    New-Item -ItemType Directory -Path $DestFolder -Force | Out-Null
} else {
    Write-Host "Destination folder already exists: $DestFolder"
}
Write-Host ""

# --- STEP 10: Move the matched files ---------------------------------------
$Moved  = 0
$Failed = 0

foreach ($Match in $MatchedFiles) {
    $Source = $Match.File.FullName
    $Dest   = Join-Path $DestFolder $Match.File.Name

    # If a file with the same name already exists in Kenji\, skip it safely
    if (Test-Path $Dest) {
        Write-Host "  SKIP (already exists): $($Match.File.Name)" -ForegroundColor DarkYellow
        continue
    }

    try {
        Move-Item -Path $Source -Destination $Dest -ErrorAction Stop
        Write-Host "  MOVED: $($Match.File.Name)" -ForegroundColor Green
        $Moved++
    } catch {
        Write-Host "  ERROR moving $($Match.File.Name): $_" -ForegroundColor Red
        $Failed++
    }
}

# --- STEP 11: Summary ------------------------------------------------------
Write-Host ""
Write-Host "Done. Moved: $Moved  |  Failed: $Failed  |  Skipped: $($MatchedFiles.Count - $Moved - $Failed)"
Write-Host "Files are in: $DestFolder"
