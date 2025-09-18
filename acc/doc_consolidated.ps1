# doc_python_consolidated.ps1 - Enhanced Python Project Documentation Generator
# Generates comprehensive project documentation with Python-specific analysis

# Configuration
$script:sqlite3Available = $false
try {
    $null = Get-Command sqlite3 -ErrorAction Stop
    $script:sqlite3Available = $true
}
catch {
    $commonPaths = @(
        "C:\Program Files\SQLite\sqlite3.exe",
        "C:\sqlite\sqlite3.exe",
        "C:\tools\sqlite\sqlite3.exe"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $script:sqlite3Available = $true
            $env:PATH += ";$(Split-Path $path)"
            break
        }
    }
}

# Get target directory
$currentDir = $PSScriptRoot
if ((Split-Path -Leaf $currentDir) -eq "acc") {
    $targetDir = Split-Path -Parent $currentDir
} else {
    $targetDir = $currentDir
    $accDir = Join-Path $currentDir "acc"
    if (!(Test-Path $accDir)) {
        New-Item -ItemType Directory -Path $accDir | Out-Null
    }
}

# Enhanced gitignore parser for Python projects
function Get-GitIgnorePatterns {
    param([string]$BasePath)
    
    $gitignorePath = Join-Path $BasePath ".gitignore"
    $patterns = @()
    
    if (Test-Path $gitignorePath) {
        $content = Get-Content $gitignorePath
        foreach ($line in $content) {
            $line = $line.Trim()
            if ($line -and !$line.StartsWith("#") -and $line -ne "") {
                # Handle negation patterns
                if ($line.StartsWith("!")) {
                    # Store negation patterns for later processing
                    $patterns += $line
                } else {
                    $patterns += $line
                }
            }
        }
    }
    
    # Add Python-specific patterns if not already present
    $pythonPatterns = @(
        "__pycache__", "*.pyc", "*.pyo", "*.pyd",
        ".Python", "*.egg-info", "dist", "build",
        ".venv", "venv", "env", ".env",
        ".pytest_cache", ".coverage", "htmlcov"
    )
    
    foreach ($pattern in $pythonPatterns) {
        if ($pattern -notin $patterns) {
            $patterns += $pattern
        }
    }
    
    return $patterns
}

# Enhanced exclusion logic for Python projects
function Should-Exclude {
    param([string]$Name, [bool]$IsContainer, [string]$FullPath, [array]$GitIgnorePatterns, [string]$BasePath)
    
    # Critical directories to always exclude (performance)
    $criticalExclusions = @(
        '__pycache__', '.git', '.vs', '.vscode', 'node_modules', 
        '.pytest_cache', 'htmlcov', '.tox', '.nox'
    )
    
    if ($Name -in $criticalExclusions) { return $true }
    
    # Exclude binary and media files
    if (-not $IsContainer) {
        $binaryExtensions = @(
            '.pyc', '.pyo', '.pyd', '.dll', '.exe', '.so', '.dylib',
            '.ico', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg',
            '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
            '.mp4', '.mp3', '.wav', '.avi', '.mov',
            '.docx', '.xlsx', '.pptx'
        )
        
        $extension = [System.IO.Path]::GetExtension($Name).ToLower()
        if ($extension -in $binaryExtensions) { return $true }
    }
    
    # Don't exclude important Python directories
    $importantDirs = @('src', 'app', 'tests', 'docs', 'config', 'models', 'static', 'templates')
    if ($Name -in $importantDirs) { return $false }
    
    # Process gitignore patterns
    $relativePath = $FullPath.Replace($BasePath, "").TrimStart("\", "/").Replace("\", "/")
    
    foreach ($pattern in $GitIgnorePatterns) {
        if ($pattern.StartsWith("!")) {
            # Handle negation - if pattern matches, don't exclude
            $negPattern = $pattern.Substring(1)
            if (Test-PathPattern -Path $relativePath -Pattern $negPattern -Name $Name) {
                return $false
            }
        } else {
            if (Test-PathPattern -Path $relativePath -Pattern $pattern -Name $Name) {
                return $true
            }
        }
    }
    
    return $false
}

# Pattern matching helper
function Test-PathPattern {
    param([string]$Path, [string]$Pattern, [string]$Name)
    
    # Direct name match
    if ($Name -eq $Pattern) { return $true }
    
    # Wildcard patterns
    if ($Pattern.Contains("*")) {
        if ($Name -like $Pattern) { return $true }
        if ($Path -like $Pattern) { return $true }
    }
    
    # Directory patterns
    if ($Pattern.EndsWith("/")) {
        $dirPattern = $Pattern.TrimEnd("/")
        if ($Name -eq $dirPattern) { return $true }
    }
    
    # Path contains pattern
    if ($Path.Contains($Pattern)) { return $true }
    
    return $false
}

# Enhanced Python file analysis
function Analyze-PythonFile {
    param([string]$FilePath)
    
    try {
        $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
        if (-not $content) { return @() }
        
        $structures = @()
        $lines = $content -split "`n"
        
        # Extract shebang
        if ($lines[0] -match '^#!(.+)') {
            $structures += "        #!$($matches[1].Trim())"
        }
        
        # Extract module docstring
        if ($content -match '^"""([\s\S]*?)"""' -or $content -match "^'''([\s\S]*?)'''") {
            $docstring = $matches[1].Trim()
            if ($docstring) {
                $structures += "        '''$docstring'''"
            }
        }
        
        # Extract imports (more comprehensive)
        $importSection = @()
        foreach ($line in $lines) {
            if ($line -match '^(from .+ import .+|import .+)$') {
                $importSection += "        $($line.Trim())"
            }
        }
        if ($importSection.Count -gt 0) {
            $structures += $importSection
            $structures += ""
        }
        
        # Extract classes with methods
        $classMatches = [regex]::Matches($content, 'class\s+(\w+)(?:\([^)]*\))?:', [System.Text.RegularExpressions.RegexOptions]::Multiline)
        foreach ($match in $classMatches) {
            $className = $match.Groups[1].Value
            $structures += "        class $className" + ":"
            
            # Find class content
            $classStart = $match.Index
            $classContent = $content.Substring($classStart)
            
            # Extract class docstring
            if ($classContent -match 'class[^:]+:\s*"""([\s\S]*?)"""') {
                $classDoc = $matches[1].Trim()
                if ($classDoc) {
                    $structures += "            '''$classDoc'''"
                }
            }
            
            # Extract methods
            $methodMatches = [regex]::Matches($classContent, '\n\s+def\s+(\w+)\([^)]*\):', [System.Text.RegularExpressions.RegexOptions]::Multiline)
            foreach ($methodMatch in $methodMatches) {
                $methodName = $methodMatch.Groups[1].Value
                $structures += "            def $methodName()"
                
                # Extract method docstring
                $methodStart = $methodMatch.Index
                $methodContent = $classContent.Substring($methodStart, [Math]::Min(500, $classContent.Length - $methodStart))
                if ($methodContent -match 'def[^:]+:\s*"""([\s\S]*?)"""') {
                    $methodDoc = $matches[1].Trim()
                    if ($methodDoc) {
                        $structures += "                '''$methodDoc'''"
                    }
                }
            }
            $structures += ""
        }
        
        # Extract standalone functions
        $functionMatches = [regex]::Matches($content, '^def\s+(\w+)\([^)]*\):', [System.Text.RegularExpressions.RegexOptions]::Multiline)
        foreach ($match in $functionMatches) {
            $functionName = $match.Groups[1].Value
            $structures += "        def $functionName()"
            
            # Extract function docstring
            $funcStart = $match.Index
            $funcContent = $content.Substring($funcStart, [Math]::Min(300, $content.Length - $funcStart))
            if ($funcContent -match 'def[^:]+:\s*"""([\s\S]*?)"""') {
                $funcDoc = $matches[1].Trim()
                if ($funcDoc) {
                    $structures += "            '''$funcDoc'''"
                }
            }
        }
        
        # Extract global variables and constants
        $varMatches = [regex]::Matches($content, '^([A-Z_][A-Z0-9_]*)\s*=', [System.Text.RegularExpressions.RegexOptions]::Multiline)
        if ($varMatches.Count -gt 0) {
            $structures += "        # Constants:"
            foreach ($match in $varMatches) {
                $varName = $match.Groups[1].Value
                $structures += "        $varName"
            }
        }
        
        return $structures
    }
    catch {
        return @("        # Error analyzing Python file: $($_.Exception.Message)")
    }
}

# Configuration and requirements analysis
function Analyze-ConfigFile {
    param([string]$FilePath, [string]$FileName)
    
    try {
        $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
        if (-not $content) { return @() }
        
        $structures = @()
        $lines = $content -split "`n"
        
        switch -Regex ($FileName) {
            "requirements\.txt|Pipfile|pyproject\.toml" {
                $structures += "        # Python Dependencies:"
                $depCount = 0
                foreach ($line in $lines) {
                    $line = $line.Trim()
                    if ($line -and !$line.StartsWith("#")) {
                        $structures += "        $line"
                        $depCount++
                        if ($depCount -gt 20) {
                            $structures += "        # ... (truncated, $($lines.Count - $depCount) more dependencies)"
                            break
                        }
                    }
                }
            }
            "\.env|config\.py|settings\.py" {
                $structures += "        # Configuration Keys:"
                foreach ($line in $lines) {
                    if ($line -match '^([A-Z_][A-Z0-9_]*)\s*=') {
                        $key = $matches[1]
                        $structures += "        $key"
                    }
                }
            }
            "Dockerfile" {
                $structures += "        # Docker Configuration:"
                foreach ($line in $lines) {
                    if ($line -match '^(FROM|RUN|COPY|EXPOSE|CMD|ENTRYPOINT)\s+(.+)') {
                        $command = $matches[1]
                        $structures += "        $command ..."
                    }
                }
            }
        }
        
        return $structures
    }
    catch {
        return @("        # Error analyzing config file: $($_.Exception.Message)")
    }
}

# Enhanced SQLite analysis
function Analyze-SQLiteDatabase {
    param([string]$DbPath, [string]$Prefix = "")
    
    try {
        $structures = @()
        
        if (-not $script:sqlite3Available) {
            $structures += "$Prefix    # SQLite3 CLI not available"
            return $structures
        }
        
        $tablesQuery = ".tables"
        $tablesResult = & sqlite3 $DbPath $tablesQuery 2>$null
        
        if ($LASTEXITCODE -ne 0 -or -not $tablesResult) {
            $structures += "$Prefix    # No tables found or database locked"
            return $structures
        }
        
        $tableNames = @()
        foreach ($line in $tablesResult) {
            if ($line.Trim()) {
                $tableNames += $line.Trim() -split '\s+'
            }
        }
        
        foreach ($tableName in $tableNames) {
            if ($tableName.Trim()) {
                $structures += "$Prefix    Table: $tableName"
                
                # Get row count
                $countQuery = "SELECT COUNT(*) FROM $tableName"
                $countResult = & sqlite3 $DbPath $countQuery 2>$null
                if ($LASTEXITCODE -eq 0 -and $countResult) {
                    $structures += "$Prefix        Rows: $countResult"
                }
                
                # Get schema
                $schemaQuery = ".schema $tableName"
                $schemaResult = & sqlite3 $DbPath $schemaQuery 2>$null
                
                if ($LASTEXITCODE -eq 0 -and $schemaResult) {
                    $createStatement = $schemaResult -join " "
                    
                    if ($createStatement -match 'CREATE TABLE.*?\((.*)\)') {
                        $columnsPart = $matches[1]
                        
                        # Basic column extraction
                        $columns = $columnsPart -split ',' | ForEach-Object {
                            $col = $_.Trim()
                            if ($col -match '^(\w+)\s+([^,\s]+)') {
                                $colName = $matches[1]
                                $colType = $matches[2]
                                
                                $constraints = @()
                                if ($col -match 'PRIMARY KEY') { $constraints += "PK" }
                                if ($col -match 'NOT NULL') { $constraints += "NOT NULL" }
                                if ($col -match 'UNIQUE') { $constraints += "UNIQUE" }
                                
                                $constraintText = if ($constraints.Count -gt 0) { " (" + ($constraints -join ", ") + ")" } else { "" }
                                "$Prefix        $colName : $colType$constraintText"
                            }
                        }
                        
                        $structures += $columns | Where-Object { $_ }
                    }
                }
            }
        }
        
        return $structures
    }
    catch {
        return @("$Prefix    # Error analyzing database: $($_.Exception.Message)")
    }
}

# File content analysis dispatcher
function Analyze-FileContent {
    param([string]$FilePath, [string]$Extension, [string]$FileName)
    
    switch ($Extension.ToLower()) {
        ".py" { return Analyze-PythonFile $FilePath }
        ".txt" { 
            if ($FileName -eq "requirements.txt") {
                return Analyze-ConfigFile $FilePath $FileName
            }
        }
        ".toml" { 
            if ($FileName -like "*pyproject*" -or $FileName -like "*Pipfile*") {
                return Analyze-ConfigFile $FilePath $FileName
            }
        }
        ".env" { return Analyze-ConfigFile $FilePath $FileName }
        default { 
            if ($FileName -in @("Dockerfile", "config.py", "settings.py")) {
                return Analyze-ConfigFile $FilePath $FileName
            }
            return @() 
        }
    }
    
    return @()
}

# Check if file is SQLite database
function Is-SQLiteFile {
    param([string]$FilePath)
    
    try {
        $extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
        if ($extension -in @('.db', '.sqlite', '.sqlite3', '.sdb')) {
            return $true
        }
        
        if (Test-Path $FilePath) {
            $bytes = Get-Content $FilePath -Encoding Byte -TotalCount 16 -ErrorAction SilentlyContinue
            if ($bytes -and $bytes.Count -ge 16) {
                $sqliteHeader = [System.Text.Encoding]::ASCII.GetBytes("SQLite format 3")
                $match = $true
                for ($i = 0; $i -lt $sqliteHeader.Length; $i++) {
                    if ($i -ge $bytes.Length -or $bytes[$i] -ne $sqliteHeader[$i]) {
                        $match = $false
                        break
                    }
                }
                return $match
            }
        }
        
        return $false
    }
    catch {
        return $false
    }
}

# Directory tree generation
function Get-DirectoryTree {
    param(
        [string]$Path,
        [array]$GitIgnorePatterns,
        [string]$BasePath,
        [array]$Prefixes = @(),
        [bool]$IsLast = $true
    )
    
    $output = @()
    
    try {
        $allItems = Get-ChildItem -LiteralPath $Path -Force
        $items = $allItems | Where-Object { 
            -not (Should-Exclude -Name $_.Name -IsContainer $_.PSIsContainer -FullPath $_.FullName -GitIgnorePatterns $GitIgnorePatterns -BasePath $BasePath) 
        } | Sort-Object @{Expression={$_.PSIsContainer}; Descending=$true}, Name
        
        for ($i = 0; $i -lt $items.Count; $i++) {
            $item = $items[$i]
            $isLastItem = ($i -eq ($items.Count - 1))
            
            $currentPrefix = ($Prefixes -join "")
            if ($isLastItem) {
                $currentPrefix += "+-- "
                $nextPrefix = $Prefixes + @("    ")
            } else {
                $currentPrefix += "+-- "
                $nextPrefix = $Prefixes + @("|   ") 
            }
            
            if ($item.PSIsContainer) {
                $output += "$currentPrefix$($item.Name)/"
                $subItems = Get-DirectoryTree -Path $item.FullName -GitIgnorePatterns $GitIgnorePatterns -BasePath $BasePath -Prefixes $nextPrefix -IsLast $isLastItem
                $output += $subItems
            } else {
                $size = if ($item.Length -gt 0) { " ($([math]::Round($item.Length/1KB, 2)) KB)" } else { " (0 KB)" }
                $output += "$currentPrefix$($item.Name)$size"
                
                # Analyze file content
                if (Is-SQLiteFile -FilePath $item.FullName) {
                    $sqliteStructures = Analyze-SQLiteDatabase -DbPath $item.FullName -Prefix ($nextPrefix -join "")
                    $output += $sqliteStructures
                } else {
                    $extension = $item.Extension
                    $fileName = $item.Name
                    $codeStructures = Analyze-FileContent -FilePath $item.FullName -Extension $extension -FileName $fileName
                    foreach ($structure in $codeStructures) {
                        $output += ($nextPrefix -join "") + $structure
                    }
                }
            }
        }
    }
    catch {
        $prefix = ($Prefixes -join "")
        $output += "$prefix[ERROR] $($_.Exception.Message)"
    }
    
    return $output
}

# Create consolidated project file
function Create-ConsolidatedFile {
    param([string]$SourcePath, [array]$GitIgnorePatterns, [string]$OutputPath)
    
    try {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $projectName = Split-Path $SourcePath -Leaf
        $textPath = Join-Path $OutputPath "${projectName}_consolidated_${timestamp}.txt"
        
        Write-Host "Creating consolidated project file..." -ForegroundColor Green
        
        $filesToInclude = @()
        
        function Get-ProjectFiles {
            param($Path, $GitIgnorePatterns, $BasePath, [ref]$FileList)
            
            try {
                $allItems = Get-ChildItem -LiteralPath $Path -Force
                $items = $allItems | Where-Object { 
                    -not (Should-Exclude -Name $_.Name -IsContainer $_.PSIsContainer -FullPath $_.FullName -GitIgnorePatterns $GitIgnorePatterns -BasePath $BasePath) 
                }
                
                foreach ($item in $items) {
                    if ($item.PSIsContainer) {
                        Get-ProjectFiles -Path $item.FullName -GitIgnorePatterns $GitIgnorePatterns -BasePath $BasePath -FileList $FileList
                    } else {
                        # Only include text-based files for consolidation
                        $extension = $item.Extension.ToLower()
                        if ($extension -in @('.py', '.txt', '.md', '.yml', '.yaml', '.json', '.toml', '.cfg', '.ini', '.env', '.sql', '.html', '.css', '.js')) {
                            $FileList.Value += $item.FullName
                        }
                    }
                }
            }
            catch {
                Write-Warning "Error processing: $Path"
            }
        }
        
        Get-ProjectFiles -Path $SourcePath -GitIgnorePatterns $GitIgnorePatterns -BasePath $SourcePath -FileList ([ref]$filesToInclude)
        
        Write-Host "Consolidating $($filesToInclude.Count) files..." -ForegroundColor Yellow
        
        $consolidatedContent = @()
        $consolidatedContent += "# $projectName - Python Project Documentation"
        $consolidatedContent += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        $consolidatedContent += "=" * 80
        $consolidatedContent += ""
        
        # Group files by type for better organization
        $fileGroups = @{
            'Configuration' = @('.env', '.cfg', '.ini', '.toml', '.yml', '.yaml')
            'Documentation' = @('.md', '.txt')
            'Python Code' = @('.py')
            'Web Files' = @('.html', '.css', '.js')
            'Data Files' = @('.json', '.sql')
        }
        
        foreach ($groupName in $fileGroups.Keys) {
            $groupFiles = $filesToInclude | Where-Object { 
                $ext = [System.IO.Path]::GetExtension($_).ToLower()
                $ext -in $fileGroups[$groupName]
            }
            
            if ($groupFiles.Count -gt 0) {
                $consolidatedContent += "# $groupName Files"
                $consolidatedContent += "-" * 40
                $consolidatedContent += ""
                
                foreach ($file in $groupFiles | Sort-Object) {
                    $relativePath = $file.Substring($SourcePath.Length).TrimStart('\', '/')
                    
                    $consolidatedContent += "## File: $relativePath"
                    $consolidatedContent += ""
                    
                    try {
                        $content = Get-Content -LiteralPath $file -Raw -ErrorAction Stop
                        if ($content) {
                            $consolidatedContent += $content.TrimEnd()
                        } else {
                            $consolidatedContent += "[Empty file]"
                        }
                    }
                    catch {
                        $consolidatedContent += "[Error reading file: $($_.Exception.Message)]"
                    }
                    
                    $consolidatedContent += ""
                    $consolidatedContent += "-" * 40
                    $consolidatedContent += ""
                }
            }
        }
        
        # Write consolidated file
        $consolidatedContent | Out-File -FilePath $textPath -Encoding UTF8
        
        $textSize = [math]::Round((Get-Item $textPath).Length / 1KB, 2)
        Write-Host "Consolidated file created: $textPath ($textSize KB)" -ForegroundColor Green
        
        return $textPath
    }
    catch {
        Write-Error "Failed to create consolidated file: $($_.Exception.Message)"
        return $null
    }
}

# Main execution
Write-Host "Python Project Documentation Generator" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Analyzing: $targetDir" -ForegroundColor Green
Write-Host ""

# Clean up old files
Write-Host "Cleaning up old documentation files..." -ForegroundColor Yellow
$projectName = Split-Path $targetDir -Leaf
Get-ChildItem -Path $currentDir -Filter "${projectName}_*.txt" -ErrorAction SilentlyContinue | Remove-Item -Force
if (Test-Path (Join-Path $currentDir "directory_structure.txt")) {
    Remove-Item (Join-Path $currentDir "directory_structure.txt") -Force
}

# Generate documentation
$gitIgnorePatterns = Get-GitIgnorePatterns -BasePath $targetDir
$rootName = Split-Path -Leaf $targetDir
$tree = @("$rootName/")
$tree += Get-DirectoryTree -Path $targetDir -GitIgnorePatterns $gitIgnorePatterns -BasePath $targetDir

# Display structure
Write-Host "Project Structure:" -ForegroundColor Cyan
$tree | ForEach-Object { Write-Host $_ }

# Save directory structure
$outputDir = if ((Split-Path -Leaf $currentDir) -eq "acc") { $currentDir } else { Join-Path $targetDir "acc" }
if (!(Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir | Out-Null }

$structureFile = Join-Path $outputDir "directory_structure.txt"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$header = @(
    "Python Project Structure Documentation",
    "Generated: $timestamp",
    "Project: $targetDir",
    ("=" * 50),
    ""
)

if (-not $script:sqlite3Available) {
    $header += @(
        "Note: SQLite3 CLI not available - database analysis limited",
        ""
    )
}

($header + $tree) | Out-File -FilePath $structureFile -Encoding UTF8

# Create consolidated file
$consolidatedFile = Create-ConsolidatedFile -SourcePath $targetDir -GitIgnorePatterns $gitIgnorePatterns -OutputPath $currentDir

Write-Host ""
Write-Host "Documentation Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host "Structure File: $structureFile" -ForegroundColor White
if ($consolidatedFile) {
    Write-Host "Consolidated File: $consolidatedFile" -ForegroundColor White
}
Write-Host ""