import base64
import re
from typing import Any
from collections.abc import Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ImageGenerateTool(Tool):
    @staticmethod
    def _extract_input_image(img: Any) -> tuple[bytes, str] | None:
        blob_bytes = None
        mime_type = "image/png"
        if hasattr(img, "blob") and img.blob:
            blob_bytes = img.blob
            mime_type = getattr(img, "mime_type", "image/png") or "image/png"
        elif hasattr(img, "read"):
            try:
                blob_bytes = img.read()
                mime_type = getattr(img, "mime_type", "image/png") or "image/png"
            except Exception:
                pass
        elif isinstance(img, dict):
            url = img.get("url") or img.get("remote_url") or img.get("path")
            mime_type = img.get("mime_type") or "image/png"
            if url and (url.startswith("http://") or url.startswith("https://")):
                try:
                    r = requests.get(url, timeout=30, verify=False)
                    blob_bytes = r.content
                    if r.headers.get("Content-Type"):
                        mime_type = r.headers.get("Content-Type").split(";")[0].strip()
                except Exception:
                    pass
            elif img.get("b64_data") or img.get("b64_json") or img.get("base64"):
                b64_str = img.get("b64_data") or img.get("b64_json") or img.get("base64")
                if "," in b64_str:
                    b64_str = b64_str.split(",", 1)[1]
                try:
                    blob_bytes = base64.b64decode(b64_str)
                except Exception:
                    pass
        elif isinstance(img, bytes):
            blob_bytes = img

        if blob_bytes:
            return blob_bytes, mime_type
        return None

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        prompt = tool_parameters.get("prompt", "")
        if not prompt:
            yield self.create_text_message("Please provide a prompt.")
            return

        api_key = self.runtime.credentials.get("api_key", "")
        base_url = self.runtime.credentials.get("endpoint_url", "")
        if not base_url.endswith("/"):
            base_url += "/"

        model = tool_parameters.get("model") or self.runtime.credentials.get("model_name", "gemini-3.1-flash-image")
        endpoint_type = self.runtime.credentials.get("endpoint_type", "chat_completions")
        
        size_key = tool_parameters.get("size", "square")
        image_resolution = tool_parameters.get("image_resolution", "1K")
        output_mime_type = tool_parameters.get("output_mime_type", "image/png")
        temperature = tool_parameters.get("temperature", 1.0)
        top_p = tool_parameters.get("top_p", 0.95)
        thinking_level = tool_parameters.get("thinking_level", "MINIMAL")
        safety_settings_val = tool_parameters.get("safety_settings", "OFF")
        quality = tool_parameters.get("quality", "standard")
        style = tool_parameters.get("style", "vivid")
        seed_id = tool_parameters.get("seed_id")
        watermark = tool_parameters.get("watermark", "disabled")

        input_images = tool_parameters.get("images") or []
        if not isinstance(input_images, list):
            input_images = [input_images]

        model_lower = str(model).lower()
        if any(m in model_lower for m in ["seedream-4-5", "seedream-4.5", "seedream-4_5", "seedream-5-0-lite", "seedream-5.0-lite", "seedream-5_0_lite"]):
            if image_resolution in ["1K", "1.5K"]:
                image_resolution = "2K"

        size_mapping_dalle = {
            "1K": {
                "square": "1024x1024", "1:1": "1024x1024",
                "vertical": "800x1424", "9:16": "800x1424",
                "horizontal": "1424x800", "16:9": "1424x800",
                "4:3": "1152x864",
                "3:4": "864x1152",
                "3:2": "1248x832",
                "2:3": "832x1248",
                "21:9": "1568x672",
            },
            "1.5K": {
                "square": "1536x1536", "1:1": "1536x1536",
                "vertical": "1152x2048", "9:16": "1152x2048",
                "horizontal": "2048x1152", "16:9": "2048x1152",
                "4:3": "1792x1344",
                "3:4": "1344x1792",
                "3:2": "1872x1248",
                "2:3": "1248x1872",
                "21:9": "2352x1008",
            },
            "2K": {
                "square": "2048x2048", "1:1": "2048x2048",
                "vertical": "1600x2848", "9:16": "1600x2848",
                "horizontal": "2848x1600", "16:9": "2848x1600",
                "4:3": "2304x1728",
                "3:4": "1728x2304",
                "3:2": "2496x1664",
                "2:3": "1664x2496",
                "21:9": "3136x1344",
            },
            "3K": {
                "square": "3072x3072", "1:1": "3072x3072",
                "vertical": "2304x4096", "9:16": "2304x4096",
                "horizontal": "4096x2304", "16:9": "4096x2304",
                "4:3": "3456x2592",
                "3:4": "2592x3456",
                "3:2": "3744x2496",
                "2:3": "2496x3744",
                "21:9": "4704x2016",
            },
            "4K": {
                "square": "4096x4096", "1:1": "4096x4096",
                "vertical": "3040x5504", "9:16": "3040x5504",
                "horizontal": "5504x3040", "16:9": "5504x3040",
                "4:3": "4704x3520",
                "3:4": "3520x4704",
                "3:2": "4992x3328",
                "2:3": "3328x4992",
                "21:9": "6240x2656",
            },
        }
        aspect_ratio_mapping = {
            "square": "1:1", "1:1": "1:1",
            "vertical": "9:16", "9:16": "9:16",
            "horizontal": "16:9", "16:9": "16:9",
            "4:3": "4:3",
            "3:4": "3:4",
            "3:2": "3:2",
            "2:3": "2:3",
            "21:9": "21:9",
        }

        headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        images_data = []

        if endpoint_type == "chat_completions":
            url = base_url + "chat/completions"
            
            image_config = {}
            if size_key in aspect_ratio_mapping:
                image_config["aspect_ratio"] = aspect_ratio_mapping[size_key]
            if image_resolution:
                image_config["image_size"] = image_resolution

            thinking_config = {}
            if thinking_level and thinking_level != "OFF":
                thinking_config["thinking_level"] = thinking_level

            safety_settings_list = []
            if safety_settings_val:
                for cat in [
                    "HARM_CATEGORY_HATE_SPEECH",
                    "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "HARM_CATEGORY_HARASSMENT",
                ]:
                    safety_settings_list.append({
                        "category": cat,
                        "threshold": safety_settings_val,
                    })

            content_parts = []
            for img in input_images:
                extracted = self._extract_input_image(img)
                if extracted:
                    b_bytes, m_type = extracted
                    b64_img = base64.b64encode(b_bytes).decode("utf-8")
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{m_type};base64,{b64_img}"
                        }
                    })

            if content_parts:
                content_parts.append({"type": "text", "text": prompt})
                messages_payload = [{"role": "user", "content": content_parts}]
            else:
                messages_payload = [{"role": "user", "content": prompt}]

            payload = {
                "model": model,
                "messages": messages_payload,
                "modalities": ["text", "image"],
                "response_modalities": ["TEXT", "IMAGE"],
                "stream": False,
                "temperature": float(temperature),
                "top_p": float(top_p),
            }

            if image_config:
                payload["image_config"] = image_config
            if thinking_config:
                payload["thinking_config"] = thinking_config
            if safety_settings_list:
                payload["safety_settings"] = safety_settings_list

            try:
                res = requests.post(url, headers=headers, json=payload, timeout=180)
                if res.status_code != 200:
                    yield self.create_text_message(f"API request failed ({res.status_code}): {res.text}")
                    return
                res_json = res.json()
                choices = res_json.get("choices", [])
                if choices:
                    msg = choices[0].get("message", {})
                    imgs = msg.get("images") or choices[0].get("images") or res_json.get("images") or msg.get("image")
                    if imgs and isinstance(imgs, list):
                        for img in imgs:
                            if isinstance(img, str):
                                images_data.append(img)
                            elif isinstance(img, dict):
                                url_val = img.get("url") or img.get("b64_json") or img.get("base64") or img.get("b64_data")
                                if isinstance(url_val, dict):
                                    url_val = url_val.get("url")
                                if not url_val and "image_url" in img:
                                    nested = img["image_url"]
                                    if isinstance(nested, dict):
                                        url_val = nested.get("url")
                                    elif isinstance(nested, str):
                                        url_val = nested
                                if url_val:
                                    images_data.append(url_val)
                    content = msg.get("content") or msg.get("parts")
                    if isinstance(content, list):
                        for part in content:
                            if isinstance(part, dict):
                                if "inline_data" in part and isinstance(part["inline_data"], dict):
                                    b64 = part["inline_data"].get("data")
                                    if b64:
                                        images_data.append(b64)
                                elif "inlineData" in part and isinstance(part["inlineData"], dict):
                                    b64 = part["inlineData"].get("data")
                                    if b64:
                                        images_data.append(b64)
                                elif part.get("type") in ("image_url", "image") or "image_url" in part:
                                    img_obj = part.get("image_url") or part.get("image")
                                    url_val = img_obj.get("url") if isinstance(img_obj, dict) else (img_obj or part.get("url"))
                                    if url_val:
                                        images_data.append(url_val)
                    elif isinstance(content, str) and content:
                        if len(content) > 100 and not content.startswith("http") and not content.startswith("{") and not content.startswith("<"):
                            images_data.append(content)
                        else:
                            urls = re.findall(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+|https?://[^\s\)\"\']+', content)
                            if urls:
                                images_data.extend(urls)
            except Exception as e:
                yield self.create_text_message(f"Invocation error: {str(e)}")
                return
        else:
            url = base_url + "images/generations"

            # Special size handling for official OpenAI DALL-E models & Custom pixel resolution string (e.g. 2848x1600)
            if re.match(r"^\d+x\d+$", size_key, re.IGNORECASE):
                size_val = size_key
            elif "dall-e-3" in model_lower or "dalle-3" in model_lower:
                if size_key in ["vertical", "9:16", "3:4", "2:3"]:
                    size_val = "1024x1792"
                elif size_key in ["horizontal", "16:9", "4:3", "3:2", "21:9"]:
                    size_val = "1792x1024"
                else:
                    size_val = "1024x1024"
            elif "dall-e-2" in model_lower or "dalle-2" in model_lower:
                size_val = "1024x1024"
            else:
                resolution_sizes = size_mapping_dalle.get(image_resolution, size_mapping_dalle.get("2K", size_mapping_dalle["1K"]))
                size_val = resolution_sizes.get(size_key, resolution_sizes.get(size_key.lower(), resolution_sizes.get("square", "1024x1024")))

            # Universal safety check for Seedream models requiring min 3,686,400 pixels
            try:
                w_str, h_str = size_val.split("x")
                if int(w_str) * int(h_str) < 3686400 and any(m in model_lower for m in ["seedream-4-5", "seedream-4.5", "seedream-4_5", "seedream-5-0-lite", "seedream-5.0-lite", "seedream-5_0_lite"]):
                    size_val = size_mapping_dalle["2K"].get(size_key, "2048x2048")
            except Exception:
                pass

            payload = {
                "model": model,
                "prompt": prompt,
                "size": size_val,
                "quality": quality,
                "style": style,
                "response_format": "b64_json",
            }

            # Add input images for image-to-image (e.g. BytePlus Seedream)
            dalle_images = []
            for img in input_images:
                extracted = self._extract_input_image(img)
                if extracted:
                    b_bytes, m_type = extracted
                    b64_img = base64.b64encode(b_bytes).decode("utf-8")
                    dalle_images.append(f"data:{m_type};base64,{b64_img}")
            if len(dalle_images) == 1:
                payload["image"] = dalle_images[0]
            elif len(dalle_images) > 1:
                payload["image"] = dalle_images

            if watermark == "enabled":
                payload["watermark"] = True
            else:
                payload["watermark"] = False
            if seed_id:
                payload["extra_body"] = {"seed": seed_id}

            try:
                res = requests.post(url, headers=headers, json=payload, timeout=180)
                if res.status_code != 200:
                    yield self.create_text_message(f"API request failed ({res.status_code}): {res.text}")
                    return
                res_json = res.json()
                for item in res_json.get("data", []):
                    b64 = item.get("b64_json") or item.get("url")
                    if b64:
                        images_data.append(b64)
            except Exception as e:
                yield self.create_text_message(f"Invocation error: {str(e)}")
                return

        if not images_data:
            raw_preview = res.text[:1000] if 'res' in locals() and hasattr(res, 'text') else ""
            yield self.create_text_message(f"No image returned by API. Raw Response: {raw_preview}")
            return

        success_count = 0
        for img_val in images_data:
            if not isinstance(img_val, str):
                continue
            if img_val.startswith("http://") or img_val.startswith("https://"):
                try:
                    img_res = requests.get(img_val, timeout=30)
                    blob_bytes = img_res.content
                    mime_type = img_res.headers.get("Content-Type", output_mime_type or "image/png")
                except Exception as e:
                    yield self.create_text_message(f"Failed to fetch image URL: {str(e)}")
                    continue
            else:
                b64_str = img_val
                if "," in b64_str:
                    b64_str = b64_str.split(",", 1)[1]
                try:
                    blob_bytes = base64.b64decode(b64_str)
                    mime_type = output_mime_type or "image/png"
                except Exception as e:
                    yield self.create_text_message(f"Failed to decode base64 image: {str(e)}")
                    continue

            yield self.create_blob_message(
                blob=blob_bytes,
                meta={"mime_type": mime_type}
            )
            success_count += 1

        if success_count > 0:
            yield self.create_text_message(f"Successfully generated {success_count} image(s).")
