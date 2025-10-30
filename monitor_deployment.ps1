# Monitor deployment and test new endpoint
Write-Host "🔍 Monitoring Backend Deployment" -ForegroundColor Cyan
Write-Host "="*60

# Check GitHub Actions status
Write-Host "`n📊 Checking GitHub Actions..." -ForegroundColor Yellow
Write-Host "   URL: https://github.com/sikdars25/qadam/actions"
Write-Host "   Waiting for deployment to complete..."

# Wait for deployment
Write-Host "`n⏳ Waiting 3 minutes for deployment..." -ForegroundColor Yellow
for ($i = 180; $i -gt 0; $i -= 10) {
    Write-Host "   $i seconds remaining..." -NoNewline
    Start-Sleep -Seconds 10
    Write-Host "`r" -NoNewline
}

Write-Host "`n✅ Deployment should be complete!" -ForegroundColor Green

# Test backend health
Write-Host "`n🏥 Testing backend health..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "https://qadam-backend.azurewebsites.net/api/health"
    Write-Host "✅ Backend is healthy!" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# Test new OCR endpoint
Write-Host "`n🧪 Testing new /api/ocr/extract endpoint..." -ForegroundColor Cyan
Write-Host "   Running Python test script..."

python test_simple_ocr_endpoint.py

Write-Host "`n" + "="*60
Write-Host "✅ Monitoring complete!" -ForegroundColor Green
Write-Host "="*60
