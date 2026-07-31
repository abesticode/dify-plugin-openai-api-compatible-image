# OpenAI-API Compatible Image

<p align="center">
  <img src="_assets/icon.svg" alt="OpenAI-API Compatible Image" width="120" />
</p>

**Author:** [abesticode](https://github.com/abesticode)  
**Version:** 0.0.1  
**Type:** tool  
**Repo:** https://github.com/abesticode/dify-plugin-openai-api-compatible-image


## Description

A universal image generation and editing tool plugin for [Dify](https://dify.ai) that works with any **OpenAI-compatible API endpoint**. This plugin outputs images as **File/Blob**, making it easy to chain with other tools in Dify workflows.

It supports two endpoint styles:
- **Chat Completions** (`/v1/chat/completions`) — for multimodal models like Google Gemini
- **Images Generations** (`/v1/images/generations`) — for DALL-E style endpoints

## Features

### 🎨 Tool Operations
| Tool | Description |
|------|-------------|
| **Image Generator** | Generate images from text prompts and edit images using any supported OpenAI-compatible or Vertex API provider. Outputs as File/Blob. |

### 🖼️ Supported Providers & Models
| Provider | Endpoint Style | Example Models | Notes |
|----------|---------------|----------------|-------|
| **Google Vertex AI** (via proxy) | Chat Completions | `gemini-3.1-flash-image`, `gemini-2.0-flash-exp` | Supports thinking level, safety settings, aspect ratio, image editing |
| **OpenAI** | Images Generations | `dall-e-3`, `dall-e-2`, `gpt-image-1` | Supports quality (standard/HD), style (vivid/natural) |
| **LiteLLM** (Proxy) | Both | Any model routed through LiteLLM | Use LiteLLM proxy URL as endpoint |
| **BytePlus / Seedream** | Images Generations | Seedream models | Supports watermark, seed, image-to-image |
| **Azure OpenAI** | Images Generations | `dall-e-3` | Use Azure endpoint URL |
| **Any OpenAI-compatible API** | Both | Varies | Any provider exposing `/v1/chat/completions` or `/v1/images/generations` |

### 📐 Flexible Customization
- **Aspect Ratios**: Square (1:1), Vertical (9:16), Horizontal (16:9), Standard (4:3), Portrait (3:4)
- **Resolution Control**: 1K, 2K, or 4K resolution tiers
- **Advanced Control**: Temperature, Top P, Quality, Style, Watermark, and Output MIME Type
- **Safety & Reasoning**: Thinking Level and Safety Thresholds (for Gemini/Vertex AI)

## Installation

1. Install the plugin from the Dify Marketplace or upload the `.difypkg` file
2. Navigate to your Dify workspace tools or agent settings
3. Add the **OpenAI-API Compatible Image** tool to your workflow
4. Configure the required credentials:
   - **API Endpoint URL**: Your OpenAI-compatible API base URL
   - **Model Name**: The model you want to use (e.g., `gemini-3.1-flash-image`)
   - **API Key**: Your API key (if required)

## Getting API Credentials

Depending on your provider, generate the required API Key and obtain the Base URL (Endpoint).
For proxy services like LiteLLM, refer to your local or hosted proxy configuration.

---

## How to Use

### Step 1: Authorization & Provider Config
Set up your provider credentials inside Dify.
- **API Endpoint URL**: Base URL of the OpenAI-compatible API (e.g., `https://api.openai.com/v1`)
- **API Key**: API key for authentication
- **Model Name**: Default model name (e.g., `gemini-3.1-flash-image`, `dall-e-3`)
- **Endpoint Style**: Choose `Chat Completions` for multimodal/Gemini, or `Images Generations` for DALL-E

### Step 2: Configure Tool Parameters
When using the tool in a workflow or agent, configure the following parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| Prompt | Yes | Text prompt describing the image to generate |
| Input Image(s) | No | Optional reference images for editing (PNG/JPEG/WebP) |
| Size / Aspect Ratio | No | Image dimensions (Default: Square) |
| Image Resolution | No | Resolution tier (1K/2K/4K) |

---

## Setup Examples

### Google Gemini via LiteLLM
```text
API Endpoint URL: http://localhost:4000/v1
API Key: sk-your-litellm-key
Model Name: gemini/gemini-3.1-flash-image
Endpoint Style: Chat Completions
```

### Google Vertex AI (Direct via OpenAI-compatible proxy)
```text
API Endpoint URL: https://your-vertex-proxy.example.com/v1
API Key: your-vertex-api-key
Model Name: gemini-3.1-flash-image
Endpoint Style: Chat Completions
```

### OpenAI DALL-E 3
```text
API Endpoint URL: https://api.openai.com/v1
API Key: sk-your-openai-key
Model Name: dall-e-3
Endpoint Style: Images Generations
```

### BytePlus Seedream
```text
API Endpoint URL: https://api.byteplus.com/v1
API Key: your-byteplus-key
Model Name: seedream-3.0
Endpoint Style: Images Generations
```

### Azure OpenAI
```text
API Endpoint URL: https://your-resource.openai.azure.com/openai/deployments/dall-e-3
API Key: your-azure-key
Model Name: dall-e-3
Endpoint Style: Images Generations
```

## Error Handling

The plugin provides descriptive error messages for common issues:
- Invalid API key or authentication failures
- Unsupported model endpoints
- Content filtered by safety guidelines

## Best Practices

1. **Choose the Right Endpoint Style**: Ensure you select `Chat Completions` for Gemini/multimodal models, and `Images Generations` for DALL-E.
2. **Experiment with Parameters**: Use Temperature and Top P to add variations, or use a fixed Seed ID to generate reproducible results.
3. **Workflow Integration**: Since this tool outputs standard Dify `File/Blob` types, you can easily pipe the generated image to other AI models or save it directly.

## Support

For issues and feature requests, please contact [abesticode](https://github.com/abesticode/dify-plugin-openai-api-compatible-image).

## License

This plugin is provided as-is for use with the Dify platform. (See [LICENSE](./LICENSE) for details).
