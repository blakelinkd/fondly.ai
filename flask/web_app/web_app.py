from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv, set_key
import os

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file


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
        return response.content, response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, port=8080)