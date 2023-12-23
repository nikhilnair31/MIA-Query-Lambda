# MIA-Query-Lambda
## General
* Secrets and keys stored as environment variables 
* `lambda_function.py` runs first.

## Run the following to Deploy
* Login first with 
    * `aws ecr get-login-password | docker login --username AWS --password-stdin 832214191436.dkr.ecr.ap-south-1.amazonaws.com`
* One time 
    * `aws ecr create-repository --repository-name mia-query-lambda`
* Build docker image with 
    * `docker build -t mia-query-lambda .`
* `docker tag mia-query-lambda:latest 832214191436.dkr.ecr.ap-south-1.amazonaws.com/mia-query-lambda:latest`
* `docker push 832214191436.dkr.ecr.ap-south-1.amazonaws.com/mia-query-lambda:latest`