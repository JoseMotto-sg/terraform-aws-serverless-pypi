# Serverless PyPI

S3-backed serverless PyPI.

Requests to your PyPI server will be proxied through a Lambda function that pulls content from an S3 bucket and reponds with the same HTML content that you might find in a conventional PyPI server.

Requests to the base path (eg, `/simple/`) will respond with the contents of an `index.html` file at the root of your S3 bucket.

Requests to the package index (eg, `/simple/fizz/`) will dynamically generate an HTML file based on the contents of keys under that namespace (eg, `s3://your-bucket/fizz/`). URLs for package downloads are presigned S3 URLs with a default lifespan of 15 minutes.

Package uploads/removals on S3 will trigger a Lambda function that reindexes the bucket and generates a new `index.html`. This is done to save time when querying the base path when your bucket contains a multitude of packages.

[![Serverless PyPI](https://github.com/amancevice/terraform-aws-serverless-pypi/blob/master/serverless-pypi.png?raw=true)](https://github.com/amancevice/terraform-aws-serverless-pypi)

## Usage

```hcl
module serverless_pypi {
  source  = "amancevice/serverless-pypi/aws"
  version = "~> 0.2"

  # ...
  api_name                       = "pypi.example.com"
  api_endpoint_configuation_type = "REGIONAL | EDGE | PRIVATE"
  lambda_function_name_api       = "pypi-api"
  lambda_function_name_reindex   = "pypi-reindex"
  role_name                      = "pypi-role"
  s3_bucket_name                 = "pypi.example.com"
  s3_presigned_url_ttl           = 900
  # ...
}
```

## S3 Bucket Organization

This tool is highly opinionated about how your S3 bucket is organized. Your root keyspace should only contain the auto-generated `index.html` and "directories" of your PyPI packages.

Packages should exist one level deep in the bucket where the prefix is the name of the project.

Example:

```
s3://your-bucket/
├── index.html
├── my-cool-package/
│   ├── my-cool-package-0.1.2.tar.gz
│   ├── my-cool-package-1.2.3.tar.gz
│   └── my-cool-package-2.3.4.tar.gz
└── my-other-package/
    ├── my-other-package-0.1.2.tar.gz
    ├── my-other-package-1.2.3.tar.gz
    └── my-other-package-2.3.4.tar.gz
```

## Auth

Please note that this tool provides **NO** authentication layer for your PyPI server. This is difficult to implement because `pip` is not very forgiving with any kind of auth pattern outside Basic Auth.

One solution to this is to deploy the API Gateway as a private endpoint inside a VPC. You can do this by setting `api_endpoint_configuation_type = "PRIVATE"`.

You will need to set up a VPC endpoint for this to work, however. Be warned that creating a VPC endpoint for API Gateway can have unintended consequences if you are not prepared. I've broken things by doing this.

I have also provided a very simple authentication implementation using API Gateway authorizers. This module is provided as a proof-of-concept and **should not** be used in production.

Add a dirt-simple Basic authentication layer to your serverless PyPI with the `serverless-pypi-basic-auth` module:

```hcl
module serverless_pypi_basic_auth {
  source               = "amancevice/serverless-pypi-basic-auth/aws"
  version              = "~> 0.1"
  api                  = module.serverless_pypi.api
  basic_auth_username  = "<pypi-user>"
  basic_auth_password  = "<pypi-password>"
  lambda_function_name = "pypi-authorizer"
  role_name            = "pypi-authorizer-role"
}
```

You will also need to update your serverless PyPI module with the authorizer ID and authorization strategy:

```hcl
module serverless_pypi {
  source  = "amancevice/serverless-pypi/aws"
  version = "~> 0.2"

  # ...
  api_authorization = "CUSTOM"
  api_authorizer_id = module.serverless_pypi_basic_auth.authorizer.id
  # ...
}
```
