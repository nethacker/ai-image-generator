import io, os, base64, json, random
import boto3
from PIL import Image

AI_S3_BUCKET_NAME = "tiled-genai"
AI_IMAGE_GENERATOR_TMP_PATH = "/tmp/ai_image_generator/"
NEGATIVE_PROMPTS = "poorly rendered, poor background details"

# Set AI Image Generation Settings
def ai_image_settings(prompt):

    # Unique AI Image Random Seed Generation
    random_seed = random.randint(0,2147833647)

    # Amazon Titan Generative AI Image Settings
    body = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                "text": prompt,                    # Required
                "negativeText": NEGATIVE_PROMPTS   # Optional
             },
            "imageGenerationConfig": {
            "seed": (random_seed), # Range: 0 to 214783647
            "numberOfImages": 1,   # Range: 1 to 5
            "quality": "premium",  # Options: standard or premium
            "height": 1024,        # Supported height list in the docs
            "width": 1024,         # Supported width list in the docs
            "cfgScale": 9          # Range: 1.0 to 10.0
            }
    }

    json_string = json.dumps(body, indent=4)
    return json_string

# AI Image Generation and Storage
def ai_image_generation(prompt, local_file_name, output_folder):

    # Invoke Amazon Titan Image Generator v2
    boto3_bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    ai_model = boto3_bedrock.invoke_model(
        body=ai_image_settings(prompt),
        modelId="amazon.titan-image-generator-v2:0",
        accept="application/json",
        contentType="application/json"
    )

    # Process the AI Image
    response_body = json.loads(ai_model.get("body").read())
    image_base64 = response_body["images"][0]

    # Decode Base64 Bytes and Save Image
    ai_image = Image.open(
        io.BytesIO(
            base64.decodebytes(
                bytes(image_base64, "utf-8")
            )
        )
    )

    ai_image.save(f"{AI_IMAGE_GENERATOR_TMP_PATH}/{output_folder}/{local_file_name}")

    # Store images in S3
    s3 = boto3.client('s3')
    bucket = AI_S3_BUCKET_NAME
    file_name = (f"{AI_IMAGE_GENERATOR_TMP_PATH}/{output_folder}/{local_file_name}")
    key_name = os.path.join(output_folder, local_file_name)
    s3.upload_file(file_name, bucket, key_name, ExtraArgs={'ContentType': "image/png"})

    # Delete Temporary Local Copy
    os.remove(f"{AI_IMAGE_GENERATOR_TMP_PATH}/{output_folder}/{local_file_name}")

# Local Cleanup Function
def delete_files_in_directory(directory_path, rm_dir=False):
    try:
        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        if (rm_dir):
            os.rmdir(directory_path)

        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")
