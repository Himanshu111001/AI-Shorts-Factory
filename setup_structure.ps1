$backend_dirs = @(
    "backend/api",
    "backend/orchestrator",
    "backend/services/topic",
    "backend/services/script",
    "backend/services/voice",
    "backend/services/video",
    "backend/services/captions",
    "backend/services/render",
    "backend/services/quality",
    "backend/services/upload",
    "backend/services/analytics",
    "backend/providers/script",
    "backend/providers/voice",
    "backend/providers/video",
    "backend/providers/captions",
    "backend/providers/upload",
    "backend/providers/analytics",
    "backend/models",
    "backend/schemas",
    "backend/repositories",
    "backend/config",
    "backend/utils",
    "backend/middleware",
    "backend/jobs",
    "backend/exceptions"
)

$frontend_dirs = @(
    "frontend/public",
    "frontend/src/components/cards",
    "frontend/src/components/tables",
    "frontend/src/components/forms",
    "frontend/src/components/charts",
    "frontend/src/components/modals",
    "frontend/src/pages/Dashboard",
    "frontend/src/pages/Jobs",
    "frontend/src/pages/Videos",
    "frontend/src/pages/Review",
    "frontend/src/pages/Analytics",
    "frontend/src/pages/Settings",
    "frontend/src/services",
    "frontend/src/hooks",
    "frontend/src/stores",
    "frontend/src/layouts",
    "frontend/src/routes",
    "frontend/src/types",
    "frontend/src/utils"
)

$storage_dirs = @(
    "storage/audio",
    "storage/captions",
    "storage/clips",
    "storage/renders",
    "storage/cache",
    "storage/thumbnails",
    "storage/exports"
)

$configs_dirs = @(
    "configs/channels",
    "configs/providers",
    "configs/quality"
)

$tests_dirs = @(
    "tests/unit",
    "tests/integration",
    "tests/providers",
    "tests/services"
)

$other_dirs = @(
    "scripts",
    "logs"
)

$all_dirs = $backend_dirs + $frontend_dirs + $storage_dirs + $configs_dirs + $tests_dirs + $other_dirs

foreach ($dir in $all_dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# Create __init__.py in all backend and tests directories
Get-ChildItem -Path "backend", "tests" -Recurse -Directory | ForEach-Object {
    New-Item -ItemType File -Force -Path (Join-Path $_.FullName "__init__.py") | Out-Null
}
New-Item -ItemType File -Force -Path "backend\__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "tests\__init__.py" | Out-Null

# Create .gitkeep in empty directories
Get-ChildItem -Path "frontend", "storage", "configs", "scripts", "logs" -Recurse -Directory | ForEach-Object {
    if ((Get-ChildItem -Path $_.FullName -Force).Count -eq 0) {
        New-Item -ItemType File -Force -Path (Join-Path $_.FullName ".gitkeep") | Out-Null
    }
}
foreach ($root in @("frontend", "storage", "configs", "scripts", "logs")) {
    if (Test-Path $root) {
        if ((Get-ChildItem -Path $root -Force).Count -eq 0) {
            New-Item -ItemType File -Force -Path "$root\.gitkeep" | Out-Null
        }
    }
}

# Root files
$root_files = @(
    ".env",
    ".gitignore",
    "docker-compose.yml",
    "README.md",
    "requirements.txt",
    "backend/main.py",
    "frontend/package.json",
    "frontend/vite.config.js"
)

foreach ($file in $root_files) {
    if (-not (Test-Path $file)) {
        New-Item -ItemType File -Force -Path $file | Out-Null
    }
}

Write-Host "Folder structure created successfully."
tree /F
