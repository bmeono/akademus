$r = Invoke-RestMethod -Uri "https://akademus.onrender.com/auth/login" -Method POST -ContentType "application/json" -Body '{"email":"admin@akademus.com","password":"admin123"}' -UseBasicParsing
$token = $r.access_token
$headers = @{Authorization = "Bearer $token"}
Invoke-RestMethod -Uri "https://akademus.onrender.com/dashboard/ultimo-simulacro" -Headers $headers -UseBasicParsing | ConvertTo-Json -Depth 10