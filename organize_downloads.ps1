# organize_downloads.ps1
# Organizes C:\Downloads: images â†' Pictures, PDFs â†' Documents, old files â†' Archive
# Runs a dry-run first, then prompts before moving anything.

$source    = "C:\Downloads"
$pictures  = Join-Path $source "Pictures"
$documents = Join-Path $source "Documents"
$archive   = Join-Path $source "Archive"

$imageExts = @(".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico")
$cutoff    = (Get-Date).AddDays(-30)

# Only top-level files, skip existing subfolders
$files = Get-ChildItem -Path $source -File

$moves = @()

foreach ($file in $files) {
    $ext  = $file.Extension.ToLower()
    $dest = $null

    if ($imageExts -contains $ext) {
        $dest = $pictures
    } elseif ($ext -eq ".pdf") {
        $dest = $documents
    } elseif ($file.LastWriteTime -lt $cutoff) {
        $dest = $archive
    }

    if ($dest) {
        $moves += [PSCustomObject]@{
            File        = $file.Name
            From        = $file.FullName
            To          = Join-Path $dest $file.Name
            Destination = $dest
            Reason      = if ($imageExts -contains $ext) { "image" }
                          elseif ($ext -eq ".pdf") { "PDF" }
                          else { "older than 30 days" }
        }
    }
}

# --- Dry run report ---
if ($moves.Count -eq 0) {
    Write-Host "Nothing to move." -ForegroundColor Green
    exit
}

Write-Host "`n=== DRY RUN â€" nothing has been moved yet ===`n" -ForegroundColor Cyan

$groups = $moves | Group-Object Destination
foreach ($g in $groups) {
    $label = Split-Path $g.Name -Leaf
    Write-Host "[$label]  ($($g.Count) file(s))" -ForegroundColor Yellow
    foreach ($m in $g.Group) {
        Write-Host "  $($m.File)  [$($m.Reason)]"
    }
    Write-Host ""
}

Write-Host "Total: $($moves.Count) file(s) will be moved.`n" -ForegroundColor Cyan

# --- Confirm ---
$answer = Read-Host "Proceed? (yes/no)"
if ($answer.Trim().ToLower() -notin @("yes", "y")) {
    Write-Host "Aborted. No files were moved." -ForegroundColor Red
    exit
}

# --- Move ---
foreach ($dest in @($pictures, $documents, $archive)) {
    if (-not (Test-Path $dest)) {
        New-Item -ItemType Directory -Path $dest | Out-Null
    }
}

$moved  = 0
$errors = 0

foreach ($m in $moves) {
    try {
        # Avoid overwriting â€" append a counter if the target already exists
        $target = $m.To
        $base   = [System.IO.Path]::GetFileNameWithoutExtension($m.File)
        $ext    = [System.IO.Path]::GetExtension($m.File)
        $n      = 1
        while (Test-Path $target) {
            $target = Join-Path $m.Destination "$base`_$n$ext"
            $n++
        }
        Move-Item -Path $m.From -Destination $target
        Write-Host "Moved: $($m.File) â†' $(Split-Path $m.Destination -Leaf)" -ForegroundColor Green
        $moved++
    } catch {
        Write-Host "ERROR moving $($m.File): $_" -ForegroundColor Red
        $errors++
    }
}

Write-Host "`nDone. $moved moved, $errors error(s)." -ForegroundColor Cyan

