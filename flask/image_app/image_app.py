import uuid
from flask import Flask, request, jsonify
import os
import random
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
import argparse
import os
import torch
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline
import requests


app = Flask(__name__)

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

@app.route("/generate-image", methods=["POST"])
def generate_image():
    try:
        output_filename = f"{str(uuid.uuid4())}.jpg"
        output_path = os.path.join("imogen", output_filename)
        prompt, m1_guidance, m2_guidance, m1_inference_steps, m2_inference_steps, strength, image_width, image_height, cuda_device, output_file, model_1, model_2, image_prompt = parse_arguments(request)
        print(f'arguments: {parse_arguments(request)}')
        stage2_guidance = 12
        stage_2_inference_steps = 100
        device = f"cuda:{cuda_device}"
        print(f'Running on device {device}')

        model_id = model_1
        model_stage2_id = model_2

        # Create the 'imogen' folder if it doesn't exist
        if not os.path.exists("imogen"):
            os.makedirs("imogen")

        if image_prompt:
            with Image.open(image_prompt) as f:
                init_image = f.convert("RGB")
        else:
            scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
            with torch.cuda.device(device):
                pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, custom_pipeline="lpw_stable_diffusion", torch_dtype=torch.float16).to(device)
            if model_id != "dreamlike-art/dreamlike-photoreal-2.0":
                print('not dreamlike, setting safety checker')
                pipe.safety_checker = lambda images, clip_input: (images, [False] * len(images))
            image = pipe(
                prompt,
                width=image_width,
                height=image_height,
                num_inference_steps=m1_inference_steps,
                max_embeddings_multiples=3,
                negative_prompt="robot eyes, toy eyes, (blurry:1.3) (extra arms:1.3) (twisted body:1.3) (fused body parts:1.3) (children:1.5) (kids:1.5) (duplicate:1.3) out of frame (poorly drawn hands) (poorly drawn face) (deformed:1.3) (amputee:1.3) bad anatomy bad proportions (extra limbs) cloned face (disfigured:1.3) (malformed limbs) (missing arms) (missing legs) (extra arms) (extra legs) mutated hands (fused fingers) (extra fingers) (long neck:1.3)",
                guidance_scale=m1_guidance,
                generator=torch.Generator(device).manual_seed(random.randint(0, 696969))).images[0]

            # Save the generated image in the 'imogen' folder
            if model_stage2_id == None:
                image.save(output_path)
                return jsonify({"message": "Image generated successfully!"})

            init_image = image

        with torch.cuda.device(device):
            pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_stage2_id, custom_pipeline="lpw_stable_diffusion", torch_dtype=torch.float16)
        if model_stage2_id != "dreamlike-art/dreamlike-photoreal-2.0":
            print('not dreamlike, setting safety checker')
            pipe.safety_checker = lambda images, clip_input: (images, [False] * len(images))

        pipe = pipe.to(device)
        image = pipe(
            prompt,
            negative_prompt="robot eyes, toy eyes, (blurry:1.3) (extra arms:1.3) (duplicate:1.3) out of frame (poorly drawn hands) (poorly drawn face) (deformed:1.3) (crossed eyes:1.3) (cat: 1.3) (amputee:1.3) bad anatomy bad proportions (extra limbs) cloned face (disfigured:1.3) (malformed limbs) (missing arms) (missing legs) (extra arms) (extra legs) mutated hands (fused fingers) (extra fingers) (long neck:1.3)",
            image=init_image,
            num_inference_steps=m2_inference_steps,
            guidance_scale=m2_guidance,
            max_embeddings_multiples=3,
            strength=strength,
            generator=torch.Generator(device).manual_seed(random.randint(0, 8675309))).images[0]

        image.save(output_path)
        return jsonify({"message": "Image generated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
