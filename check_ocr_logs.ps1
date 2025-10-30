# Check OCR Function App logs
Write-Host "📋 Checking OCR Function App Logs..." -ForegroundColor Cyan
Write-Host "="*60

# Get recent logs from Application Insights
$query = @"
traces
| where timestamp > ago(30m)
| where cloud_RoleName == 'qadam-ocr-addrcugfg4d4drg7'
| order by timestamp desc
| take 50
| project timestamp, message, severityLevel
"@

Write-Host "`nQuerying Application Insights for OCR errors..."
az monitor app-insights query `
    --app qadam-ocr-addrcugfg4d4drg7 `
    --analytics-query $query `
    --output table

Write-Host "`n" + "="*60
Write-Host "Checking for exceptions..."

$exceptionsQuery = @"
exceptions
| where timestamp > ago(30m)
| where cloud_RoleName == 'qadam-ocr-addrcugfg4d4drg7'
| order by timestamp desc
| take 20
| project timestamp, type, outerMessage, problemId
"@

az monitor app-insights query `
    --app qadam-ocr-addrcugfg4d4drg7 `
    --analytics-query $exceptionsQuery `
    --output table
