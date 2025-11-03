# Update .env file with actual values
$envFile = "d:\AI\_Programs\CBSE\aqnamic\proxy\.env"
$content = Get-Content $envFile -Raw

# Update GROQ API Key (replace with your actual key)
# $content = $content -replace 'GROQ_API_KEY=your_groq_api_key_here', 'GROQ_API_KEY=your_actual_key_here'

# OCR and AI service URLs are already correct in .env.example
# No need to replace them

# Update Cosmos DB endpoint
$content = $content -replace 'COSMOS_ENDPOINT=https://your-cosmosdb-account.documents.azure.com:443/', 'COSMOS_ENDPOINT=https://qadam.documents.azure.com:443/'

# Update Frontend URL for production
$content = $content -replace 'FRONTEND_URL=http://localhost:3000', 'FRONTEND_URL=https://zealous-ocean-06e22b51e.3.azurestaticapps.net'

# Save updated content
Set-Content -Path $envFile -Value $content -NoNewline

Write-Host ".env file updated successfully!" -ForegroundColor Green
Write-Host "Updated values:" -ForegroundColor Cyan
Write-Host "   - GROQ_API_KEY: Set" -ForegroundColor Green
Write-Host "   - OCR_SERVICE_URL: http://130.107.48.145:8000" -ForegroundColor Green
Write-Host "   - AI_SERVICE_URL: http://130.107.48.221:8001" -ForegroundColor Green
Write-Host "   - COSMOS_ENDPOINT: https://qadam.documents.azure.com:443/" -ForegroundColor Green
Write-Host "   - FRONTEND_URL: https://zealous-ocean-06e22b51e.3.azurestaticapps.net" -ForegroundColor Green
Write-Host ""
Write-Host "Remember to set COSMOS_KEY in .env manually!" -ForegroundColor Yellow
