# Terraria Find Pyramid Worlds - PowerShell Version
# Generate worlds until finding specified number with pyramids
# Usage: .\find_pyramid_worlds.ps1 [SIZE] [DIFFICULTY] [EVIL] [PYRAMID_TARGET] [MAX_ATTEMPTS]

param(
    [int]$SIZE = 2,
    [int]$DIFFICULTY = 1,
    [int]$EVIL = 1,
    [int]$PYRAMID_TARGET = 1,
    [int]$MAX_ATTEMPTS = 100
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
    exit 1
}

if ($DIFFICULTY -lt 1 -or $DIFFICULTY -gt 3) {
    Write-Host "Error: DIFFICULTY must be 1, 2, or 3"
    exit 1
}

if ($EVIL -lt 1 -or $EVIL -gt 3) {
    Write-Host "Error: EVIL must be 1, 2, or 3"
    exit 1
}

if ($PYRAMID_TARGET -lt 1 -or $PYRAMID_TARGET -gt 50) {
    Write-Host "Error: PYRAMID_TARGET must be between 1 and 50"
    exit 1
}

if ($MAX_ATTEMPTS -lt 1 -or $MAX_ATTEMPTS -gt 500) {
    Write-Host "Error: MAX_ATTEMPTS must be between 1 and 500"
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

# Get Python checker script path
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PYTHON_CHECKER = Join-Path $SCRIPT_DIR "lihzahrd_parser.py"

if (-not (Test-Path $PYTHON_CHECKER)) {
    Write-Host "Error: Python checker not found: $PYTHON_CHECKER"
    exit 1
}

# Parameter name mappings
$SIZE_NAME = @{1="Small"; 2="Medium"; 3="Large"}
$DIFFICULTY_NAME = @{1="Normal"; 2="Expert"; 3="Master"}
$EVIL_NAME = @{1="Random"; 2="Corruption"; 3="Crimson"}

Write-Host "========================================="
Write-Host "Terraria Find Pyramid Worlds"
Write-Host "========================================="
Write-Host "World Size: $($SIZE_NAME[$SIZE])"
Write-Host "Difficulty: $($DIFFICULTY_NAME[$DIFFICULTY])"
Write-Host "Evil Type: $($EVIL_NAME[$EVIL])"
Write-Host "Pyramid Target: $PYRAMID_TARGET"
Write-Host "Max Attempts: $MAX_ATTEMPTS"
Write-Host "========================================="
Write-Host ""

$START_TIME = Get-Date
$PYRAMIDS_FOUND = 0
$TOTAL_GENERATED = 0
$PYRAMID_WORLDS = @()

while ($PYRAMIDS_FOUND -lt $PYRAMID_TARGET -and $TOTAL_GENERATED -lt $MAX_ATTEMPTS) {
    $TOTAL_GENERATED++
    $REMAINING = $PYRAMID_TARGET - $PYRAMIDS_FOUND

    Write-Host "[$TOTAL_GENERATED/$MAX_ATTEMPTS] Generating world (Need $REMAINING more pyramids)..."

    # Generate unique world name
    $TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
    $WORLD_NAME = "World_${TIMESTAMP}_${TOTAL_GENERATED}"
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

    # Wait for world file to be created
    $WAIT_TIME = 0
    $MAX_WAIT = 300
    $WORLD_CREATED = $false

    while ($WAIT_TIME -lt $MAX_WAIT) {
        Start-Sleep -Seconds 2
        $WAIT_TIME += 2

        $AFTER_FILES = (Get-ChildItem -Path $WORLD_DIR -Filter "*.wld" -ErrorAction SilentlyContinue).Count
        if ($AFTER_FILES -gt $BEFORE_FILES) {
            $WORLD_CREATED = $true
            break
        }
    }

    # Kill TerrariaServer processes
    Get-Process | Where-Object {$_.ProcessName -like "*TerrariaServer*"} | Stop-Process -Force -ErrorAction SilentlyContinue

    Start-Sleep -Seconds 1

    # Find the created world file
    if (-not (Test-Path $WORLD_PATH)) {
        $LATEST_WORLD = Get-ChildItem -Path $WORLD_DIR -Filter "*.wld" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($LATEST_WORLD) {
            $WORLD_PATH = $LATEST_WORLD.FullName
            $WORLD_NAME = $LATEST_WORLD.BaseName
        }
    }

    if (Test-Path $WORLD_PATH) {
        $FILE_SIZE = (Get-Item $WORLD_PATH).Length
        $SIZE_MB = [math]::Round($FILE_SIZE / 1MB, 2)
        Write-Host "✓ Generated: ${WORLD_NAME}.wld (${SIZE_MB}MB)"

        # Check for pyramids
        Write-Host "  Checking for pyramids..."

        $PYTHON_OUTPUT = & python $PYTHON_CHECKER $WORLD_PATH 2>&1 | Out-String

        if ($PYTHON_OUTPUT -match "Found (\d+) Sandstone Brick") {
            $BRICK_COUNT = $matches[1]
            if ([int]$BRICK_COUNT -gt 0) {
                if ($PYTHON_OUTPUT -match "First pyramid block at: \((\d+), (\d+)\)") {
                    $X = $matches[1]
                    $Y = $matches[2]
                    Write-Host "  🎉 PYRAMID FOUND! Count: $BRICK_COUNT, First block at: ($X, $Y)" -ForegroundColor Green
                    $PYRAMIDS_FOUND++
                    $PYRAMID_WORLDS += $WORLD_NAME
                }
            } else {
                Write-Host "  ○ No pyramid - deleting..." -ForegroundColor Gray
                Remove-Item -Path $WORLD_PATH -Force
                $TMP_FILE = $WORLD_PATH -replace "\.wld$", ".twld"
                if (Test-Path $TMP_FILE) {
                    Remove-Item -Path $TMP_FILE -Force
                }
            }
        } else {
            Write-Host "  ○ No pyramid - deleting..." -ForegroundColor Gray
            Remove-Item -Path $WORLD_PATH -Force
            $TMP_FILE = $WORLD_PATH -replace "\.wld$", ".twld"
            if (Test-Path $TMP_FILE) {
                Remove-Item -Path $TMP_FILE -Force
            }
        }
    } else {
        Write-Host "✗ Error: World file not found"
    }

    Write-Host ""
}

$END_TIME = Get-Date
$ELAPSED = $END_TIME - $START_TIME

Write-Host "========================================="
Write-Host "Search complete!"
Write-Host "Pyramids found: $PYRAMIDS_FOUND / $PYRAMID_TARGET"
Write-Host "Total worlds generated: $TOTAL_GENERATED"
$SUCCESS_RATE = if ($TOTAL_GENERATED -gt 0) { [math]::Round(($PYRAMIDS_FOUND / $TOTAL_GENERATED) * 100, 1) } else { 0 }
Write-Host "Success rate: $SUCCESS_RATE%"
Write-Host "Time elapsed: $($ELAPSED.ToString('hh\:mm\:ss'))"
Write-Host ""

if ($PYRAMIDS_FOUND -gt 0) {
    Write-Host "Worlds with pyramids:"
    foreach ($world in $PYRAMID_WORLDS) {
        Write-Host "  - $world"
    }
}

Write-Host ""
Write-Host "World directory: $WORLD_DIR"
Write-Host "========================================="

if ($PYRAMIDS_FOUND -lt $PYRAMID_TARGET) {
    Write-Host ""
    Write-Host "⚠️  Warning: Reached max attempts ($MAX_ATTEMPTS) before finding all pyramids" -ForegroundColor Yellow
}
