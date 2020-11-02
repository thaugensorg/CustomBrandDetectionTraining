$subscription = 'Thaugen-semisupervised-vision-closed-loop-solution'
$location = 'westus'
$solutionNameRoot = 'MLPImgClass' # must be less than 20 characters or the storage acount variable must be provided as a constant
$modelAppName = $solutionNameRoot + 'ModelApp'
$storageAccountName = $solutionNameRoot.ToLower() + 'strg'
$cognitiveServicesAccountName = $modelAppName
$cognitiveServicesImageAnalysisEndpoint = "https://$location.api.cognitive.microsoft.com/vision/v2.0/analyze"

# login
Connect-AzAccount -Tenant '72f988bf-86f1-41af-91ab-2d7cd011db47' -SubscriptionId '9109f582-942b-4360-9c94-21793d69eed0'
Set-AzContext -SubscriptionId "9109f582-942b-4360-9c94-21793d69eed0"
# Connect-AzureRmAccount
# perform other Azure operations...

Write-Host("auth")

# Set-AzureRmContext($subscription)

$currentAzureContext = Get-AzContext

write-host($currentAzureContext.Tenant.Id)

$tenantId = $currentAzureContext.Tenant.Id

Write-Host($currentAzureContext.Account.Id)
$accountId = $currentAzureContext.Account.Id

# Connect-AzureAD -TenantId $tenantId -AccountId $accountId

# setupand configure ML Professoar engine for this instance of Image Analysis
$command = '.\MLProfessoarEngineConfig.ps1 ' +`
    '-subscription ' + $subscription + ' '+`
    '-frameworkResourceGroupName ' + $solutionNameRoot + 'Engine ' +`
    '-frameworkLocation ' + $location + ' '+`
    '-modelType Trained ' +`
    '-evaluationDataParameterName dataBlobUrl ' +`
    '-labelsJsonPath labels.regions[0].tags ' +`
    '-confidenceJSONPath confidence ' +`
    '-dataEvaluationServiceEndpoint https://$modelAppName.azurewebsites.net/api/EvaluateData ' +`
    '-confidenceThreshold .95 ' +`
    '-modelVerificationPercentage .05 ' +`
    '-trainModelServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/TrainModel ' +`
    '-tagsUploadServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/LoadLabelingTags ' +`
    '-LabeledDataServiceEndpoint https://' + $modelAppName + '.azurewebsites.net/api/AddLabeledData ' +`
    '-LabelingSolutionName FileName ' +`
    '-labelingTagsParameterName labelsJson ' +`
    '-testFileCount 20'

Invoke-Expression $command