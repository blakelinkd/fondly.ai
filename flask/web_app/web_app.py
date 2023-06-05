import json
import random
from flask import Flask, jsonify, render_template, request, send_file
import requests
from dotenv import load_dotenv, set_key
import os

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file

if not os.environ["APP_HOST"]:
    print("Setting APP_HOST to localhost")
    set_key(".env", "APP_HOST", "localhost")
else:
    app_host = os.environ["APP_HOST"]


def parse_arguments(request):
    prompt = request.form.get('prompt')
    m1_guidance = float(request.form.get('m1_guidance', 0.0))
    m2_guidance = float(request.form.get('m2_guidance', 0.0))
    m1_inference_steps = int(request.form.get('m1_inference_steps', 100))
    m2_inference_steps = int(request.form.get('m2_inference_steps', 100))
    strength = float(request.form.get('strength', 1.0))
    image_width = int(request.form.get('image_width', 256))
    image_height = int(request.form.get('image_height', 256))
    cuda_device = int(request.form.get('cuda_device', 0))
    output_file = request.form.get('output_file')
    model_1 = request.form.get('model_1')
    model_2 = request.form.get('model_2')
    image_prompt = request.form.get('image_prompt')

    return prompt, m1_guidance, m2_guidance, m1_inference_steps, m2_inference_steps, strength, image_width, image_height, cuda_device, output_file, model_1, model_2, image_prompt

@app.route('/prompt')
def index():
    return render_template('prompt.html', app_host=app_host)

@app.route('/random-image')
def random_image():
    image_dir = 'static/images'
    images = os.listdir(image_dir)
    random_image_name = random.choice(images)
    image_url = f'/static/images/{random_image_name}'
    return jsonify({'image_url': image_url})

@app.route('/scroller', defaults={'path': ''})
def scroller(path):
    images_path = os.path.join(app.static_folder, 'images')
    image_names = os.listdir(images_path)
    print(f'found {len(image_names)} images')
    random_image_name = random.choice(image_names)
    print(f'returning random image: {random_image_name}')
    return render_template('scroller.html', random_image=random_image_name)


@app.route("/images", methods=["POST"])
def receive_image():
    try:
        if not os.path.exists("static/images"):
            os.makedirs("static/images")
        print("Received image")
        # Get the image file from the request
        image_file = request.files.get("image")
        print(f"Received file: {image_file.filename}")

        # Retrieve other arguments from the request
        filename = request.form.get("filename")
        prompt = request.form.get("prompt")
        m1_guidance = float(request.form.get("m1_guidance", 0.0))
        m2_guidance = float(request.form.get("m2_guidance", 0.0))
        m1_inference_steps = int(request.form.get("m1_inference_steps", 100))
        m2_inference_steps = int(request.form.get("m2_inference_steps", 100))
        strength = float(request.form.get("strength", 1.0))
        image_width = int(request.form.get("image_width", 256))
        image_height = int(request.form.get("image_height", 256))
        cuda_device = int(request.form.get("cuda_device", 0))
        output_file = request.form.get("output_file")
        model_1 = request.form.get("model_1")
        model_2 = request.form.get("model_2")
        image_prompt = request.form.get("image_prompt")

        payload = {     "filename": image_file.filename,
                        "prompt": prompt,
                        "m1_guidance": m1_guidance,
                        "m2_guidance": m2_guidance,
                        "m1_inference_steps": m1_inference_steps,
                        "m2_inference_steps": m2_inference_steps,
                        "strength": strength,
                        "image_width": image_width,
                        "image_height": image_height,
                        "cuda_device": cuda_device,
                        "output_file": output_file,
                        "model_1": model_1,
                        "model_2": model_2,
                        "image_prompt": image_prompt,
                    }
        # Perform any desired operations with the received image and arguments
        print(f"Performing operations with the image: {image_file.filename}")

        # Save the image file to a desired location
        file_path = os.path.join("static/images", image_file.filename)
        image_file.save(file_path)
        print(f"Image saved at: {file_path}")

        # Return a response indicating the successful receipt of the image
        return jsonify(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/set-target-url', methods=['POST'])
def set_target_url():
    password = request.form.get('password')
    if password != os.getenv('PASSWORD'):
        return 'Invalid password', 401

    ip_address = request.form.get('ip_address')
    if not ip_address:
        return 'IP address is required', 400

    # Update the target URL with the provided IP address
    target_url = f'http://{ip_address}'
    set_key('.env', 'TARGET_URL', target_url)

    return 'Target URL updated successfully'



@app.route("/generate-image", methods=["POST"])
def generate_image():
    try:
        # Parse the request arguments
        # prompt, m1_guidance, m2_guidance, m1_inference_steps, m2_inference_steps, strength, image_width, image_height, cuda_device, output_file, model_1, model_2, image_prompt = parse_arguments(request)
        
        prompt, m1_guidance, m2_guidance, m1_inference_steps, m2_inference_steps, strength, image_width, image_height, cuda_device, output_file, model_1, model_2, image_prompt = parse_arguments(request)
        print(f'arguments: {parse_arguments(request)}')
        # Update the target URL with the provided IP address
        target_url = os.getenv('TARGET_URL')
        route = '/generate-image'  # Specify the desired route
        target_url_with_route = target_url + route

        # Forward the request to the target URL with the route
        payload = {
            'prompt': prompt,
            'm1_guidance': m1_guidance,
            'm2_guidance': m2_guidance,
            'm1_inference_steps': m1_inference_steps,
            'm2_inference_steps': m2_inference_steps,
            'strength': strength,
            'image_width': image_width,
            'image_height': image_height,
            'cuda_device': cuda_device,
            'output_file': output_file,
            'model_1': model_1,
            'model_2': model_2,
            'image_prompt': image_prompt,
            # Include any other arguments needed by the target endpoint
        }

        # response = requests.post(target_url_with_route, json=payload)
        response = requests.post(target_url_with_route, data=payload)  # Use 'data' instead of 'json' parameter


        # Return the response from the target URL
        response_json = json.loads(response.content)
        filename = response_json['filename']
        print(f'response: {filename}')
        return jsonify(response_json)
        return response.content, response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, port=8080)