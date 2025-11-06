import base64

def encode_image(image_path):
    """Convert image to base64 for LLM input."""
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{b64}"
    except Exception:
        return ""
    

def query_openrouter(client, model, prompt, image_path):
    """Send text + image to OpenRouter model."""
    image_b64 = encode_image(image_path)
    if not image_b64:
        return "Image not found or unreadable."

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_b64}},
                    ],
                }
            ],
            max_tokens=100,
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"API error: {e}"


def query_openrouter_multi_image(client, model, prompt, image_paths):
    """Send text + multiple images to OpenRouter model."""
    content = [{"type": "text", "text": prompt}]
    
    for image_path in image_paths:
        image_b64 = encode_image(image_path)
        if image_b64:
            content.append({"type": "image_url", "image_url": {"url": image_b64}})
    
    if len(content) == 1:  # Only text, no valid images
        return "No valid images found."

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            max_tokens=100,
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"API error: {e}"