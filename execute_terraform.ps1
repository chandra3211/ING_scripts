#PRE-PREP FOR AZURE RM SCRIPT
$scriptLocation = Join-Path -Path  $(SYSTEM.ARTIFACTSDIRECTORY) -ChildPath "$(sourcecode_azurebiab)\ps_modules"

Write-Output "set env proxy to  $env:http_proxy"
Write-Output "set env ARM_CLIENT_ID to  $env:ARM_CLIENT_ID"
Write-Output "set env ARM_TENANT_IDto  $env:ARM_TENANT_ID"
Write-Output "set env ARM_SUBSCRIPTION_ID $env:ARM_SUBSCRIPTION_ID"
$env:ARM_CLIENT_SECRET = "$(ARM_CLIENT_SECRET)"

Set-Location -Path $scriptLocation
Write-Output "set location to $scriptLocation"

Import-Module .\ingasr.psd1 -force

Azure-servicePrincipleSignon -clientID "$(ARM_CLIENT_ID)" -key "$(ARM_CLIENT_SECRET)" -tenantID "$(ARM_TENANT_ID)" -prod_proxy "$(prod_proxy)"

Write-Output "Connected to Azure..."

$region_tf_location = Join-Path -Path  $(SYSTEM.ARTIFACTSDIRECTORY) -ChildPath "$(sourcecode_azurebiab)\terraform\$(PLSTATE_REGION_NAME)\AZURE"

Write-Output "set location to $region_tf_location"

Set-Location -Path $region_tf_location

$starttime = Get-Date

$terraform_Path = & cmd /C where terraform

$cmd = "`"$terraform_Path`" init -lock=false -plugin-dir=`"$(azplugin_terraform)`" -get-plugins=false"

Write-Output "$cmd"

$stdoutOutput_init = & cmd /C $cmd 2>&1

if ($stdoutOutput_init -match "Terraform has been successfully initialized"){
    Write-Output "COMPLETED: terraform init for region - $(PLSTATE_REGION_NAME)"
}
else {
    Write-Error "Failed on terraform init for region - $(PLSTATE_REGION_NAME)"
    Write-Error -Exception "$stdoutOutput_init"
    exit 1
}

$cmd = "`"$terraform_Path`" plan -lock=false -parallelism=80 -out=terraform_plan"

Write-Output "$cmd"

$stdoutOutput_plan = & cmd /C $cmd 2>&1

if ($stdoutOutput_plan -match "An execution plan has been generated" ){
    Write-Output "COMPLETED: terraform plan for region - $(PLSTATE_REGION_NAME)"
}
else {
    Write-Error "Failed on terraform plan for region - $(PLSTATE_REGION_NAME)"
    Write-Error -Exception "$stdoutOutput_plan"
    exit 1
}

$cmd = "`"$terraform_Path`" apply -auto-approve -parallelism=80 -lock=false terraform_plan"

Write-Output "$cmd"

$stdoutOutput_apply = & cmd /C $cmd 2>&1

if ($stdoutOutput_apply -match "Apply complete!"){
    Write-Output "COMPLETED: terraform apply for region - $(PLSTATE_REGION_NAME)"
}
else {
    Write-Error "Failed on terraform apply for region - $(PLSTATE_REGION_NAME)"
    Write-Error -Exception "$stdoutOutput_apply"
    exit 1
}

$finishtime = Get-Date
$usedtime = $finishtime - $starttime
Write-Output "Used: $usedtime"

###

$cmd = "`"$terraform_Path`" init -lock=false -plugin-dir=`"$(azplugin_terraform)`" -get-plugins=false"

$stdoutOutput_init = & cmd /C $cmd 2>&1

if ($stdoutOutput_init -match "Terraform has been successfully initialized"){
    Write-Output "COMPLETED: terraform init for region - $(PLSTATE_REGION_NAME)"
}
else {
    Write-Error "Failed on terraform init for region - $(PLSTATE_REGION_NAME)"
    Write-Error -Exception "$stdoutOutput_init"
    exit 1
}

$cmd = "`"$terraform_Path`" plan -destroy -out=destroy_plan"

$stdoutOutput_plan = & cmd /C $cmd 2>&1

if ($stdoutOutput_plan -match "An execution plan has been generated"){
    Write-Output "COMPLETED: terraform destroy plan for region - $(PLSTATE_REGION_NAME)"
}
else {
    Write-Error "Failed on terraform destroy plan for region - $(PLSTATE_REGION_NAME)"
    Write-Error -Exception "$stdoutOutput_plan"
    exit 1
}

$cmd = "`"$terraform_Path`" destroy -auto-approve"

$stdoutOutput_destroy = & cmd /C $cmd 2>&1

Write-Output "$stdoutOutput_destroy"

if ($stdoutOutput_destroy -match "Destroy complete!"){
    Write-Output "COMPLETED: terraform destroy for region - $(PLSTATE_REGION_NAME)"
}
else {
    Write-Error "Failed on terraform destroy for region - $(PLSTATE_REGION_NAME)"
    Write-Error -Exception "$stdoutOutput_destroy"
    exit 1
}

