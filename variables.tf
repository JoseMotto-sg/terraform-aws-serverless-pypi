variable api_authorization {
  description = "API Gateway method authorization [NONE | CUSTOM | AWS_IAM | COGNITO_USER_POOLS]"
  default     = "NONE"
}

variable api_authorizer_id {
  description = "API Gateway authorizer ID"
  default     = null
}

variable api_base_path {
  description = "PyPI index API Gateway base path"
  default     = null
}

variable api_deployment_stage_name {
  description = "API Gateway REST API deployment stage name"
  default     = "prod"
}

variable api_deployment_variables {
  description = "API Gateway REST API deployment stage name"
  type        = map(string)
  default     = {}
}

variable api_description {
  description = "API Gateway REST API description"
  default     = "PyPI service"
}

variable api_endpoint_configuration_type {
  description = "API Gateway endpoint configuration type [EDGE | REGIONAL | PRIVATE]"
  default     = "REGIONAL"
}

variable api_name {
  description = "API Gateway REST API name"
}

variable lambda_api_description {
  description = "REST API Lambda function description"
  default     = "PyPI service REST API"
}

variable lambda_api_function_name {
  description = "REST API Lambda function name"
}

variable lambda_api_memory_size {
  description = "REST API Lambda function memory size"
  default     = 128
}

variable lambda_reindex_description {
  description = "Reindexer Lambda function decription"
  default     = "Reindex PyPI root"
}

variable lambda_reindex_function_name {
  description = "Reindexer Lambda function name"
}

variable lambda_reindex_memory_size {
  description = "Reindexer Lambda function memory size"
  default     = 128
}

variable log_group_retention_in_days {
  description = "CloudWatch log group retention period"
  default     = 30
}

variable policy_name {
  description = "IAM role inline policy name"
  default     = "pypi-lambda-permissions"
}

variable role_description {
  description = "Lambda functions IAM role description"
  default     = "PyPI Lambda permissions"
}

variable role_name {
  description = "Lambda function role name"
}

variable s3_bucket_name {
  description = "PyPI index S3 bucket name"
}

variable s3_presigned_url_ttl {
  description = "PyPI package presigned URL expiration in seconds"
  default     = 900
}

variable tags {
  description = "Resource tags"
  type        = map
  default     = {}
}
