param(
  [string]$Owner = "mitunmanav",
  [string]$Repo = "everything-ai",
  [string]$DefaultBranch = "main",
  [switch]$ApplyBranchProtection,
  [string[]]$StatusCheckContexts = @("test", "CodeQL")
)

$ErrorActionPreference = "Stop"
$repoRef = "$Owner/$Repo"

Write-Host "Applying GitHub baseline settings to $repoRef ..."
gh auth status 1>$null

gh api -X PATCH "repos/$repoRef" `
  -f delete_branch_on_merge=true `
  -f allow_auto_merge=true `
  -f allow_squash_merge=true `
  -f allow_merge_commit=false `
  -f allow_rebase_merge=false `
  -f has_wiki=false `
  -f has_projects=false 1>$null

gh api -X PUT "repos/$repoRef/actions/permissions/workflow" `
  -f default_workflow_permissions=read `
  -F can_approve_pull_request_reviews=false 1>$null

$desiredLabels = @(
  @{ name = "security"; color = "d73a4a"; description = "Security fix or hardening work" },
  @{ name = "ci"; color = "1d76db"; description = "CI or workflow updates" },
  @{ name = "chore"; color = "cfd3d7"; description = "Maintenance or housekeeping changes" },
  @{ name = "release"; color = "5319e7"; description = "Release prep and versioning work" },
  @{ name = "test"; color = "0e8a16"; description = "Test coverage or test harness changes" },
  @{ name = "scripts"; color = "fbca04"; description = "Tooling and scripts updates" }
)

$existingLabels = @(gh api "repos/$repoRef/labels?per_page=100" --jq ".[].name")
foreach ($label in $desiredLabels) {
  if ($existingLabels -contains $label.name) {
    gh api -X PATCH "repos/$repoRef/labels/$($label.name)" `
      -f new_name=$($label.name) `
      -f color=$($label.color) `
      -f description=$($label.description) 1>$null
  } else {
    gh api -X POST "repos/$repoRef/labels" `
      -f name=$($label.name) `
      -f color=$($label.color) `
      -f description=$($label.description) 1>$null
  }
}

if ($ApplyBranchProtection) {
  $requiredStatusChecks = @{
    strict = $true
    contexts = $StatusCheckContexts
  }

  $protection = @{
    required_status_checks = $requiredStatusChecks
    enforce_admins = $true
    required_pull_request_reviews = @{
      dismiss_stale_reviews = $true
      require_code_owner_reviews = $true
      required_approving_review_count = 1
      require_last_push_approval = $false
    }
    restrictions = $null
    required_linear_history = $true
    allow_force_pushes = $false
    allow_deletions = $false
    block_creations = $false
    required_conversation_resolution = $true
    lock_branch = $false
    allow_fork_syncing = $false
  }

  $payload = $protection | ConvertTo-Json -Depth 8
  $payload | gh api -X PUT "repos/$repoRef/branches/$DefaultBranch/protection" --input - 1>$null
  Write-Host "Branch protection updated on $DefaultBranch with checks: $($StatusCheckContexts -join ', ')"
} else {
  Write-Host "Branch protection left unchanged. Re-run with -ApplyBranchProtection to enforce checks."
}

Write-Host "Done."
