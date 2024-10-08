import os
import json
import random
import time
import concurrent.futures
from flask import Flask, request
from flask_json import FlaskJSON, JsonError, json_response
from image_generation import ai_image_generation, delete_files_in_directory

AI_IMAGE_GENERATOR_TMP_PATH = "/tmp/ai_image_generator/"

ai_image_generator = Flask(__name__)
FlaskJSON(ai_image_generator)

# 500MB Upload File Size Limit
ai_image_generator.config['MAX_CONTENT_PATH'] = 500 * 1024 * 1024

# Data validations.
def ai_image_generator_data_validation(request_data):
    try:
        prompt = str(request_data['prompt'])
    except (KeyError, TypeError, ValueError) as e:
        raise JsonError(description='Invalid prompt.') from e
    try:
        output_folder = str(request_data['output_folder'])
    except (KeyError, TypeError, ValueError) as e:
        raise JsonError(description='Invalid output_folder.') from e

    try:
        file_name_prefix = str(request_data['file_name_prefix'])
    except (KeyError, TypeError, ValueError) as e:
        raise JsonError(description='Invalid file_name_prefix.') from e

    return prompt, output_folder, file_name_prefix

# Health check route.
@ai_image_generator.route("/")
def health():
    return json_response(health="true")

# Generate images route.
@ai_image_generator.route('/generate_images', methods=['POST'])
def generate_images():
    request_data = request.get_json(force=True)
    prompt, output_folder, file_name_prefix = ai_image_generator_data_validation(request_data)

    output_path = os.path.join(AI_IMAGE_GENERATOR_TMP_PATH, output_folder.strip())

    # Checks if output folder exists, makes one if not. Delete files in folder if it does exist.
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    else:
        delete_files_in_directory(output_path)

    #  Use a pool of threads to execute generation of 4 images asynchronously.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        file_name = [(f"{file_name_prefix}") + "-" + str(time.time()) + ".png", (f"{file_name_prefix}") + "-" + str(time.time()) + ".png", (f"{file_name_prefix}") + "-" + str(time.time()) + ".png", (f"{file_name_prefix}") + "-" + str(time.time()) + ".png"]
        for file in file_name:
            futures.append(executor.submit(ai_image_generation, prompt=prompt, local_file_name=file, output_folder=output_folder))
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

    # Return JSON output of location/files generated.
    keys = []
    for file in file_name:
        keys.append((os.path.join(output_folder, file)))

    manifest = {"images": keys}

    return json.dumps(manifest)

if __name__ == "__main__":
    ai_image_generator.run(host='0.0.0.0')
