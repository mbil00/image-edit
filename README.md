# image-edit

AI-powered image editing CLI with Unix piping support.

## Installation

Install with pipx (recommended):

```bash
pipx install image-edit
```

Or with pip:

```bash
pip install image-edit
```

Install from source:

```bash
git clone https://github.com/your-username/image-edit.git
cd image-edit
pip install -e .
```

## Configuration

Set your Gemini API key using the config command:

```bash
image-edit config set api-key YOUR_API_KEY
```

Or use an environment variable:

```bash
export GEMINI_API_KEY="your-api-key"
```

### Configuration Options

```bash
# Set the model (default: gemini-3-pro-image-preview)
image-edit config set model gemini-2.0-flash-exp

# View all settings
image-edit config show

# View a specific setting
image-edit config get model

# Reset a setting to default
image-edit config unset model
```

Available settings:

| Key | Description | Default |
|-----|-------------|---------|
| `api-key` | Gemini API key | (none) |
| `model` | Gemini model to use | `gemini-3-pro-image-preview` |
| `default-format` | Output format (png, jpeg, webp, gif) | `png` |
| `default-quality` | Quality setting | `1K` |

Configuration is stored in `~/.config/image-edit/config.toml`. Environment variables take precedence over the config file.

## Usage

### Edit images with custom prompts

```bash
# File input/output
image-edit edit "make the sky purple" -i sunset.jpg -o result.png

# Unix piping
cat photo.png | image-edit edit "watercolor style" > art.png

# Pipe chains
cat photo.jpg | image-edit edit enhance | image-edit edit "vintage filter" > output.png
```

### Use predefined templates

```bash
image-edit edit remove-bg -i portrait.jpg -o nobg.png
image-edit edit enhance -i blurry.jpg -o clear.png
image-edit edit vintage -i photo.jpg -o retro.png
```

### Generate new images

```bash
image-edit generate "a sunset over mountains" -o sunset.png
```

### List available templates

```bash
image-edit templates
```

### Check provider status

```bash
image-edit providers
```

## Available Templates

| Template | Aliases | Description |
|----------|---------|-------------|
| `remove-bg` | `nobg`, `removebg` | Remove background, make transparent |
| `enhance` | `improve`, `fix` | Improve quality, clarity, and lighting |
| `upscale` | `resize`, `enlarge`, `hd` | Increase resolution intelligently |
| `vintage` | `retro`, `film` | Apply vintage/retro film effect |
| `sepia` | `brown`, `antique` | Apply sepia tone effect |
| `sharpen` | `crisp`, `clarity` | Sharpen and increase clarity |
| `bw` | `blackwhite`, `grayscale`, `mono` | Convert to black and white |
| `blur-bg` | `bokeh`, `portrait-mode` | Blur background, keep subject sharp |
| `cartoon` | `comic`, `illustrated` | Convert to cartoon/illustration style |
| `watercolor` | `painting`, `artistic` | Apply watercolor painting effect |

## Custom Templates

Create `~/.config/image-edit/templates.toml`:

```toml
[[template]]
name = "corporate-headshot"
prompt = "Transform into professional corporate headshot with clean background..."
description = "Professional headshot"
aliases = ["headshot", "linkedin"]
```

## License

MIT
