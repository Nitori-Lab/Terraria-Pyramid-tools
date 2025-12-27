# Terraria Batch World Generator - PowerShell Version
# Usage: .\tWorldGen.ps1 [SIZE] [DIFFICULTY] [EVIL] [COUNT]

param(
    [int]$SIZE = 2,
    [int]$DIFFICULTY = 1,
    [int]$EVIL = 1,
    [int]$COUNT = 1
)

# Auto-detect TerrariaServer path
if ($env:TERRARIA_SERVER_PATH) {
    $TERRARIA_SERVER = $env:TERRARIA_SERVER_PATH
} else {
    $POSSIBLE_PATHS = @(
        "C:\Program Files (x86)\Steam\steamapps\common\Terraria\TerrariaServer.exe",
        "C:\Program Files\Steam\steamapps\common\Terraria\TerrariaServer.exe",
        "$env:USERPROFILE\.local\share\Steam\steamapps\common\Terraria\TerrariaServer.exe"
    )

    $TERRARIA_SERVER = $null
    foreach ($path in $POSSIBLE_PATHS) {
        if (Test-Path $path) {
            $TERRARIA_SERVER = $path
            break
        }
    }

    if (-not $TERRARIA_SERVER) {
        Write-Host "Error: Could not auto-detect TerrariaServer location."
        Write-Host ""
        Write-Host "Please set environment variable: `$env:TERRARIA_SERVER_PATH = 'C:\Path\To\TerrariaServer.exe'"
        Write-Host "Common location: C:\Program Files (x86)\Steam\steamapps\common\Terraria\TerrariaServer.exe"
        exit 1
    }
}

# Auto-detect world directory
if ($env:TERRARIA_WORLD_DIR) {
    $WORLD_DIR = $env:TERRARIA_WORLD_DIR
} else {
    $WORLD_DIR = "$env:USERPROFILE\Documents\My Games\Terraria\Worlds"
}

# Parameter validation
if ($SIZE -lt 1 -or $SIZE -gt 3) {
    Write-Host "Error: SIZE must be 1, 2, or 3"
    Write-Host "1=Small, 2=Medium, 3=Large"
    exit 1
}

if ($DIFFICULTY -lt 1 -or $DIFFICULTY -gt 3) {
    Write-Host "Error: DIFFICULTY must be 1, 2, or 3"
    Write-Host "1=Normal, 2=Expert, 3=Master"
    exit 1
}

if ($EVIL -lt 1 -or $EVIL -gt 3) {
    Write-Host "Error: EVIL must be 1, 2, or 3"
    Write-Host "1=Random, 2=Corruption, 3=Crimson"
    exit 1
}

if ($COUNT -lt 1 -or $COUNT -gt 200) {
    Write-Host "Error: COUNT must be between 1 and 200"
    exit 1
}

# Check if TerrariaServer exists
if (-not (Test-Path $TERRARIA_SERVER)) {
    Write-Host "Error: TerrariaServer not found at: $TERRARIA_SERVER"
    exit 1
}

# Ensure world directory exists
if (-not (Test-Path $WORLD_DIR)) {
    New-Item -ItemType Directory -Path $WORLD_DIR -Force | Out-Null
}

# Parameter name mappings
$SIZE_NAME = @{1="Small"; 2="Medium"; 3="Large"}
$DIFFICULTY_NAME = @{1="Normal"; 2="Expert"; 3="Master"}
$EVIL_NAME = @{1="Random"; 2="Corruption"; 3="Crimson"}

Write-Host "========================================="
Write-Host "Terraria Batch World Generator"
Write-Host "========================================="
Write-Host "World Size: $($SIZE_NAME[$SIZE])"
Write-Host "Difficulty: $($DIFFICULTY_NAME[$DIFFICULTY])"
Write-Host "Evil Type: $($EVIL_NAME[$EVIL])"
Write-Host "Count: $COUNT"
Write-Host "========================================="
Write-Host ""

for ($i = 1; $i -le $COUNT; $i++) {
    Write-Host "[$i/$COUNT] Generating world..."

    # Generate unique world name
    $TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
    $WORLD_NAME = "World_${TIMESTAMP}_${i}"
    $WORLD_PATH = Join-Path $WORLD_DIR "${WORLD_NAME}.wld"

    # Count files before generation
    $BEFORE_FILES = (Get-ChildItem -Path $WORLD_DIR -Filter "*.wld" -ErrorAction SilentlyContinue).Count

    # Create input for TerrariaServer
    $INPUT_FILE = [System.IO.Path]::GetTempFileName()
    $INPUT_CONTENT = @"
n
$SIZE
$DIFFICULTY
$EVIL
$WORLD_NAME

exit
"@
    Set-Content -Path $INPUT_FILE -Value $INPUT_CONTENT -Encoding ASCII

    # Run TerrariaServer
    $process = Start-Process -FilePath $TERRARIA_SERVER -ArgumentList "<`"$INPUT_FILE`"" -NoNewWindow -PassThru -RedirectStandardOutput NUL -RedirectStandardError NUL

    Remove-Item -Path $INPUT_FILE -Force -ErrorAction SilentlyContinue

    # Wait for world file to be created (max 300 seconds = 5 minutes)
    $WAIT_TIME = 0
    $MAX_WAIT = 300
    $WORLD_CREATED = $false

    while ($WAIT_TIME -lt $MAX_WAIT) {
        Start-Sleep -Seconds 2
        $WAIT_TIME += 2

        # Check if a new world file appeared
        $AFTER_FILES = (Get-ChildItem -Path $WORLD_DIR -Filter "*.wld" -ErrorAction SilentlyContinue).Count
        if ($AFTER_FILES -gt $BEFORE_FILES) {
            $WORLD_CREATED = $true
            break
        }
    }

    # Kill TerrariaServer processes
    Get-Process | Where-Object {$_.ProcessName -like "*TerrariaServer*"} | Stop-Process -Force -ErrorAction SilentlyContinue

    Start-Sleep -Seconds 1

    # Check if world file was successfully generated
    if (Test-Path $WORLD_PATH) {
        $FILE_SIZE = (Get-Item $WORLD_PATH).Length
        if ($FILE_SIZE -gt 0) {
            $SIZE_MB = [math]::Round($FILE_SIZE / 1MB, 2)
            Write-Host "✓ Generated: ${WORLD_NAME}.wld (Size: ${SIZE_MB}MB)"
        } else {
            Write-Host "✗ Error: World file created but size is 0"
            Write-Host "Generation failed, stopping execution"
            exit 1
        }
    } else {
        # Try to find the most recently created .wld file
        $LATEST_WORLD = Get-ChildItem -Path $WORLD_DIR -Filter "*.wld" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        $AFTER_FILES = (Get-ChildItem -Path $WORLD_DIR -Filter "*.wld" -ErrorAction SilentlyContinue).Count

        if ($AFTER_FILES -gt $BEFORE_FILES -and $LATEST_WORLD) {
            Write-Host "✓ Detected new world file: $($LATEST_WORLD.Name)"
        } else {
            Write-Host "✗ Error: Generated world file not found in world directory"
            Write-Host "Expected path: $WORLD_PATH"
            Write-Host "World directory: $WORLD_DIR"
            Write-Host "Generation failed, stopping execution"
            exit 1
        }
    }

    Write-Host ""
}

Write-Host "========================================="
Write-Host "Batch generation complete!"
Write-Host "Total worlds generated: $COUNT"
Write-Host "World directory: $WORLD_DIR"
Write-Host "========================================="
