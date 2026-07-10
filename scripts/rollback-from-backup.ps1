param(
  [Parameter(Mandatory = $true)]
  [string]$BackupTag,
  [string]$RollbackBranch
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RollbackBranch)) {
  $RollbackBranch = "rollback/$BackupTag"
}

Write-Host "Fetching tags from origin ..."
git fetch origin --tags

git rev-parse --verify "refs/tags/$BackupTag" 1>$null

Write-Host "Creating rollback branch $RollbackBranch from $BackupTag ..."
git switch -c $RollbackBranch $BackupTag

Write-Host "Pushing rollback branch ..."
git push -u origin $RollbackBranch

Write-Host "Done. Open PR from $RollbackBranch into main."
