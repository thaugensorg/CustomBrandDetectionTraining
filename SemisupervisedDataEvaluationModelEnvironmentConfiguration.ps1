# instructions and documentation for this solution have been moved to the Read Me file in the solution

while([string]::IsNullOrWhiteSpace($subscription))
  {$subscription= Read-Host -Prompt "Input the name of the subscription where this solution will be deployed"}

$modelResourceGroupName = Read-Host -Prompt 'Input the name of the resource group that you want to create for this installation of the model.  (default=SemisupervisedModel)'
  if ([string]::IsNullOrWhiteSpace($modelResourceGroupName)) {$modelResourceGroupName = "SemisupervisedModel"}
  
while([string]::IsNullOrWhiteSpace($SemisupervisedAppName))
  {$SemisupervisedAppName= Read-Host -Prompt "Input the name for the azure function app you want to create for your analysis model. Note this must be a name that is unique across all of Azure"}

while([string]::IsNullOrWhiteSpace($modelStorageAccountName))
  {$modelStorageAccountName= Read-Host -Prompt "Input the name of the azure storage account you want to create for this installation of the model. Note this must be a name that only uses lowercase letters and numbers and is unique across all of Azure"}

$modelStorageAccountKey = $null
$modelLocation = "westus"

if (az group exists --name $modelResourceGroupName) `
	{az group delete `
	  --name $modelResourceGroupName `
	  --subscription $subscription `
	  --yes -y}

az group create `
  --name $modelResourceGroupName `
  --location $modelLocation 

az storage account create `
    --location $modelLocation `
    --name $modelStorageAccountName `
    --resource-group $modelResourceGroupName `
    --sku Standard_LRS

$modelStorageAccountKey = `
	(get-azureRmStorageAccountKey `
		-resourceGroupName $modelResourceGroupName `
		-AccountName $modelStorageAccountName).Value[0]

az functionapp create `
  --name $brandDetectionAppName `
  --storage-account $modelStorageAccountName `
  --consumption-plan-location $modelLocation `
  --resource-group $modelResourceGroupName `
  --os-type "Linux" `
  --runtime "python"

az cognitiveservices account create `
    --name "brandDetection" `
    --resource-group $modelResourceGroupName `
    --kind ComputerVision `
    --sku F0 `
    --location westus `
    --yes

az functionapp config appsettings set `
    --name $brandDetectionAppName `
    --resource-group imageAnalysisModel `
    --settings "subscriptionKey=Null"

#gitrepo=https://github.com/thaugensorg/semi-supervisedModelSolution.git
#token=<Replace with a GitHub access token>

# Enable authenticated git deployment in your subscription from a private repo.
#az functionapp deployment source update-token \
#  --git-token $token

# Create a function app with source files deployed from the specified GitHub repo.
#az functionapp create \
#  --name autoTestDeployment \
#  --storage-account semisupervisedstorage \
#  --consumption-plan-location centralUS\
#  --resource-group customVisionModelTest \
#  --deployment-source-url https://github.com/thaugensorg/semi-supervisedModelSolution.git \
#  --deployment-source-branch master