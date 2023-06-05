import uuid
from flask import Flask, request, jsonify
import os
import random
import requests
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
import argparse
import os
import torch
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline
from dotenv import load_dotenv, set_key


app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file


if not os.environ["APP_HOST"]:
    print("Setting APP_HOST to localhost")
    set_key(".env", "APP_HOST", "localhost")
else:
    app_host = os.environ["APP_HOST"]


def parse_arguments(request):
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

    return (
        prompt,
        m1_guidance,
        m2_guidance,
        m1_inference_steps,
        m2_inference_steps,
        strength,
        image_width,
        image_height,
        cuda_device,
        output_file,
        model_1,
        model_2,
        image_prompt,
    )


@app.route("/generate-image", methods=["POST"])
def generate_image():
    try:
        output_filename = f"{str(uuid.uuid4())}.png"
        output_path = os.path.join("static/images", output_filename)
        (
            prompt,
            m1_guidance,
            m2_guidance,
            m1_inference_steps,
            m2_inference_steps,
            strength,
            image_width,
            image_height,
            cuda_device,
            output_file,
            model_1,
            model_2,
            image_prompt,
        ) = parse_arguments(request)
        print(f"arguments: {parse_arguments(request)}")
        stage2_guidance = 12
        stage_2_inference_steps = 100
        device = f"cuda:{cuda_device}"
        print(f"Running on device {device}")

        model_id = model_1
        model_stage2_id = model_2

        # Create the 'static/images' folder if it doesn't exist
        if not os.path.exists("static/images"):
            os.makedirs("static/images")

        if image_prompt:
            with Image.open(image_prompt) as f:
                init_image = f.convert("RGB")
        else:
            scheduler = EulerDiscreteScheduler.from_pretrained(
                model_id, subfolder="scheduler"
            )
            with torch.cuda.device(device):
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    scheduler=scheduler,
                    custom_pipeline="lpw_stable_diffusion",
                    torch_dtype=torch.float16,
                ).to(device)
            if model_id != "dreamlike-art/dreamlike-photoreal-2.0":
                print("not dreamlike, setting safety checker")
                pipe.safety_checker = lambda images, clip_input: (
                    images,
                    [False] * len(images),
                )
            image = pipe(
                prompt,
                width=image_width,
                height=image_height,
                num_inference_steps=m1_inference_steps,
                max_embeddings_multiples=3,
                negative_prompt="robot eyes, toy eyes, (blurry:1.3) (extra arms:1.3) (twisted body:1.3) (fused body parts:1.3) (children:1.5) (kids:1.5) (duplicate:1.3) out of frame (poorly drawn hands) (poorly drawn face) (deformed:1.3) (amputee:1.3) bad anatomy bad proportions (extra limbs) cloned face (disfigured:1.3) (malformed limbs) (missing arms) (missing legs) (extra arms) (extra legs) mutated hands (fused fingers) (extra fingers) (long neck:1.3)",
                guidance_scale=m1_guidance,
                generator=torch.Generator(device).manual_seed(
                    random.randint(0, 696969)
                ),
            ).images[0]

            if model_stage2_id == "None":
                image.save(output_path)
                print(f"no stage2 model set.")
                # Make a POST request to the remote endpoint with the image file and other arguments
                # Make a POST request to the remote endpoint with the image file and other arguments
                with open(output_path, "rb") as file:
                    files = {"image": file}
                    payload = {
                        "files": files,
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
                    print("trying to upload image to remote endpoint")
                    target_url = os.getenv("APP_HOST")
                    route = "/images"  # Specify the desired route
                    target_url_with_route = target_url + route
                    print(f"calling {target_url_with_route}")
                    response = requests.post(target_url_with_route, data=payload, files=files)
                    if response.status_code == 200:
                        print("image uploaded successfully")
                    else:
                        print("image upload failed")
                    # return jsonify(payload)
                    return response.content, response.status_code

        init_image = image
        with torch.cuda.device(device):
            pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_stage2_id,
                custom_pipeline="lpw_stable_diffusion",
                torch_dtype=torch.float16,
            )

        if model_stage2_id != "dreamlike-art/dreamlike-photoreal-2.0":
            print("not dreamlike, setting safety checker")
            pipe.safety_checker = lambda images, clip_input: (
                images,
                [False] * len(images),
            )

        pipe = pipe.to(device)
        image = pipe(
            prompt,
            negative_prompt="robot eyes, toy eyes, (blurry:1.3) (extra arms:1.3) (duplicate:1.3) out of frame (poorly drawn hands) (poorly drawn face) (deformed:1.3) (crossed eyes:1.3) (cat: 1.3) (amputee:1.3) bad anatomy bad proportions (extra limbs) cloned face (disfigured:1.3) (malformed limbs) (missing arms) (missing legs) (extra arms) (extra legs) mutated hands (fused fingers) (extra fingers) (long neck:1.3)",
            image=init_image,
            num_inference_steps=m2_inference_steps,
            guidance_scale=m2_guidance,
            max_embeddings_multiples=3,
            strength=strength,
            generator=torch.Generator(device).manual_seed(random.randint(0, 8675309)),
        ).images[0]

        image.save(output_path)
        # Make a POST request to the remote endpoint with the image file and other arguments
        remote_url = "https://fondly.ai/images"
        files = {"image": open(output_path, "rb")}
        payload = {
            "filename": output_path,
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

        target_url = os.getenv("APP_HOST")
        route = "/images"  # Specify the desired route
        target_url_with_route = target_url + route
        print(f"calling endpoint at {target_url_with_route}")
        response = requests.post(target_url_with_route, files=files, data=payload)
        return jsonify(
            {"message": "Image generated successfully and sent to remote endpoint!"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False)
