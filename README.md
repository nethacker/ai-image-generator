# ai-image-generator
[![Pylint](https://github.com/nethacker/ai-image-generator/actions/workflows/pylint.yml/badge.svg)](https://github.com/nethacker/ai-image-generator/actions/workflows/pylint.yml)
# AI Image Generator API Service
* License: (MIT), Copyright (C) 2024, Author Phil Chen
  * This is a example application the author of this repository is not liable for damages or losses arising from your use or inability to use the code.

### Description

This repo provides an example of an AI Image Generator API that creates 4 images asynchronously and stores them in <a href="https://aws.amazon.com/s3/" target="_blank">S3</a>. The API leverages Amazon Titan Image Generator which is accessed via <a href="https://aws.amazon.com/bedrock/" target="_blank">Amazon Bedrock</a>. Generating the images asyncronously allows for a quicker experience when processing multiple images.

The workflow is:

1. Create a execute a POST request to the `generate_images` endpoint, that has `prompt`, `output_folder` and `file_name_prefix`.
    1. `prompt` is the description of the image you want generated.
    2. `output_folder` is the S3 folder path structure.
    3. `file_name_prefix` is the name of the image file which will end up with a random string of numbers appended to it.
    4. Example POST request BODY: `{"prompt": "red porsche", "output_folder": "000/111", "file_name_prefix": "porsche_image"}`
2. 4 images will be generated based on your prompt and uploaded to the S3 bucket you specify in `image_generation.py` under `AI_S3_BUCKET_NAME`
3. You will get a JSON manifest of file names after the images are generated.
    1. Example response: `{"images": ["000/111/porsche_image-1195732086.png", "000/111/porsche_image-1182855275.png", "000/111/porsche_image-1597191391.png", "000/111/porsche_image-181944233.png"]}`

<p align="center">
<img src="flow-diagram.svg" alt="AI Image Generator API Process Flow" />
</p>

### Prerequisites for macOS laptop local setup

* <a href="https://aws.amazon.com" target="_blank"> Amazon Web Services Account</a>
* Enable Amazon Bedrock Access (Specifically Amazon Titan Embeddings and Claude 3.5 Sonnet) see: <a href="https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html" target="_blank">Manage access to Amazon Bedrock foundation models</a>
* AWS CLI <a href="https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html" target="_blank">installed</a>
* AWS CLI IAM user with Full Amazon Bedrock Access and Full Amazon S3 Access
* Verified on Python 3.10, 3.11, 3.12
* Anaconda or Miniconda installed 
* AWS Default Region is set to us-east-1 you can change the region in the `image_generation.py` file under `region_name='us-east-1'`
* AWS S3 bucket

### Prerequisites for EC2 Ubuntu instance setup
* <a href="https://aws.amazon.com" target="_blank"> Amazon Web Services Account</a>
* Enable Amazon Bedrock Access (Specifically Amazon Titan Image Generator v2) see: <a href="https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html" target="_blank">Manage access to Amazon Bedrock foundation models</a>
* EC2 Instance Role with AmazonBedrockFullAccess and AmazonS3FullAccess (note you can make this more secure by making a custom policy)
* Verified on EC2 Instance Ubuntu 22.04 and Ubuntu 24.04
* Verified on Python 3.10, 3.11, 3.12
* Virtualenv
* AWS Default Region is set to us-east-1 you can change the region in the `image_generation.py` file under `region_name='us-east-1'
* AWS S3 bucket

### AWS Resource Cost

As with most AWS services you will incur costs for usage. 

* Pricing:
  * https://aws.amazon.com/bedrock/pricing/
  * https://aws.amazon.com/ec2/pricing/on-demand/

#### macOS laptop local setup

```
conda create -n "ai-image-generator" python=3.11.0

git clone git@github.com:nethacker/ai-image-generator.git

cd ai-image-generator

pip install -r requirements.txt

vim image_generation.py
```

Edit the line `AI_S3_BUCKET_NAME` and add your S3 bucket name


#### Run macOS laptop local setup

To run AI Image Generator API Service

```
flask run --port 8080
```

You can reach the API at `http://localhost:8080/`.

From a command line you can test the API out by running:

`curl -X POST --data '{"prompt": "red porsche", "output_folder": "000/111"}' http://127.0.0.1:8080/generate_images`


### EC2 Ubuntu instance setup steps
(This example assumes you have a ubuntu user with /home/ubuntu)

#### Install some dependencies
```
sudo apt -y update

sudo apt -y install build-essential openssl

sudo apt -y install libpq-dev libssl-dev libffi-dev zlib1g-dev

sudo apt -y install python3-pip python3-dev

sudo apt -y install nginx

sudo apt -y install virtualenvwrapper
```

#### Clone the GIT repository
```
cd /home/ubuntu

git clone https://github.com/nethacker/ai-image-generator.git
```

#### Setup the Python environment
```
virtualenv ai-image-generator_env

source ai-image-generator_env/bin/activate
```

#### Install the AI Image Generator API service package dependencies
```
cd /home/ubuntu/ai-image-generator

pip install -r requirements.txt
```

#### Setup systemd to daemonize and bootstrap the AI Image Generator API service (Port 8080)
```
sudo cp systemd/ai-image-generator.service /etc/systemd/system/

sudo systemctl start ai-image-generator

sudo systemctl enable ai-image-generator.service
```

#### Install NGINX to help scale and handle connections (Port 80)
```
sudo cp nginx/nginx_ai-image-generator.conf /etc/nginx/sites-available/nginx_ai-image-generator.conf

sudo rm /etc/nginx/sites-enabled/default

sudo ln -s /etc/nginx/sites-available/nginx_ai-image-generator.conf /etc/nginx/sites-enabled

sudo systemctl restart nginx
```

You can reach the API at `http://{yourhost}`.

From a command line you can test the API out by running:

`curl -X POST --data '{"prompt": "red porsche", "output_folder": "000/111"}' http://{yourhost}:80/generate_images`

### Notes

* Make sure to open up port 80 in your EC2 Security Group associated to the instance.
* For HTTPS (TLS) you can use AWS ALB or AWS CloudFront
* This AI Image Generator API service does not take into consideration security controls, that is your responsibility.
* Please read <a href="https://aws.amazon.com/bedrock/faqs/" target="_blank">Amazon Bedrock FAQ's</a> for general questions about AWS LLM resources used.