# Application Submission Demo

Automate application form submission using Browser-Use and Gemini 3 Pro Preview with AI-powered form filling.

## What This Does

This template demonstrates automated application submission. The agent will:

1. Navigate to the application page
2. Fill out personal information (name, email, phone, address)
3. Upload your document file
4. Complete demographic and optional fields
5. Submit the application and confirm success

The template uses Google's `gemini-3-pro-preview` model which excels at complex multi-step tasks like form filling.

## Setup

### 1. Get Your API Key

You'll need a Google API key to use the Gemini model:
1. Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create a new API key
3. Copy the key

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

### 3. Install Dependencies

```bash
uv sync
```

## Usage

### Basic Usage (with included example data)

```bash
uv run main.py --document example_document.pdf
```

This will use the included `applicant_data.json` with example information.

### With Your Own Data

1. Create your own data JSON file (see format below)
2. Prepare your document as a PDF file
3. Run the script:

```bash
uv run main.py --data my_info.json --document my_document.pdf
```

### Data Format

Create a JSON file with your information:

```json
{
	"first_name": "Your",
	"last_name": "Name",
	"email": "your.email@example.com",
	"phone": "5551234567",
	"age": "21",
	"US_citizen": true,
	"sponsorship_needed": false,
	"postal_code": "12345",
	"country": "United States",
	"city": "YourCity",
	"address": "123 Your Street",
	"gender": "Your Gender",
	"race": "Your Race/Ethnicity",
	"Veteran_status": "I am not a veteran",
	"disability_status": "No, I do not have a disability"
}
```

## Support

For issues specific to Browser-Use, see:
- Documentation: [https://docs.browser-use.com](https://docs.browser-use.com)
- GitHub: [https://github.com/browser-use/browser-use](https://github.com/browser-use/browser-use)
- Browser Use Box: [https://browser-use.com/bux](https://browser-use.com/bux) for running Browser Use jobs from an always-on VPS or Telegram. [Watch the 15-second demo](https://www.tiktok.com/@browser_use/video/7639824093721758989).
