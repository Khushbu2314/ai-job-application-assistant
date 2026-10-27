# AI Job Application Assistant

Looking at a job description and figuring out how to present your experience can take time. This small app helps with that first step: it compares a job posting with the skills and experience you provide, suggests what to highlight, and drafts a cover letter for you to review.

It was built as a practical, beginner-friendly project for an AI Growth & Automation Associate assessment.

## What the app does

1. You paste in a job description and describe your own experience.
2. The app looks for skills that appear in both and points to evidence from your profile.
3. It lists job requirements that your profile does not mention. That does not necessarily mean you lack those skills; it may mean you have not included them yet.
4. It suggests resume improvements and drafts a cover letter.
5. You can edit the letter and download it, or download a JSON report with the results.

You can optionally add your name and choose a cover-letter tone.

## How the AI works

When a Groq API key and internet connection are available, the app sends the job description and candidate profile to a model available through Groq. It asks the model to stick to the information you supplied, avoid making up experience, and return the results in a structured format.

The app uses the OpenAI Python SDK as a client because Groq supports its API format. **The requests go to Groq, not to OpenAI.** The app does not need an OpenAI API key.

If you do not set a Groq key, or the live service cannot be reached, the app uses a basic keyword-based preview. This lets you try the interface offline, but it is not AI analysis and its matches may miss context.

## Technology used

- **Python** runs the app.
- **Streamlit** provides the web interface.
- **Groq API** provides live AI analysis when configured.
- **OpenAI Python SDK** sends requests using the API format supported by Groq.
- **python-dotenv** reads local settings from a `.env` file.
- **Brotli** is included as an HTTP dependency.

The dependency list is in [`requirements.txt`](./requirements.txt). The prompts and project decisions are in [`prompts.md`](./prompts.md).

## Run it on Windows

You will need Python 3.10 or later.

1. Open Command Prompt or PowerShell in the project folder.
2. Install the required packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

4. Open the local address Streamlit prints in the terminal. It is usually `http://localhost:8501`.

The app works without an API key in offline preview mode. To use live AI, follow the next section.

## Set up live analysis with Groq

1. Get an API key from Groq.
2. In the project folder, create a file named `.env`.
3. Add your key and, optionally, choose a model available to your Groq account:

   ```dotenv
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-20b
   ```

   If you leave out `GROQ_MODEL`, the app uses `openai/gpt-oss-20b` by default. The `openai/` text is part of that model's name; the request still goes to Groq.

4. Save the file and start or restart the app.

Keep your API key private. The `.env` file is excluded by `.gitignore`; do not upload it or paste the key into a public repository. API use may have account limits or costs.

## Using the app offline

The app can still create a simple preview when there is no Groq key or the API connection fails. It compares words in the job description with words in the profile and uses a generic cover-letter draft.

The preview is meant to show how the app works, not to provide a detailed or AI-generated assessment. For a live analysis, connect to the internet and configure a valid Groq key.

If the key or model is invalid, or the API rejects the request for another reason, the app shows an error rather than pretending the live analysis succeeded.

## Try the sample information

The project includes sample text in [`sample_data.txt`](./sample_data.txt). You can paste it into the app to test the workflow. It describes a sample Junior Python Developer role and candidate profile.

Use your own accurate information for a real draft. Do not claim a skill or experience unless you can support it.

## A few important things to know

- This is a job-search helper, not a hiring or resume-screening system.
- It cannot predict whether you will get an interview or job offer.
- AI can misunderstand information or produce incorrect suggestions. Check every claim and edit the cover letter before using it.
- The offline preview uses simple keyword matching and is not AI.
- Avoid entering sensitive personal information, especially when using a hosted service.

## Project files

```text
ai_job_application_assistant/
├── app.py             # Streamlit app and analysis logic
├── prompts.md         # Plain-language prompts used for the project
├── requirements.txt   # Python libraries needed to run the app
├── sample_data.txt    # Example job description and candidate profile
├── README.md          # Project overview and setup guide
└── .gitignore         # Keeps local environments and secrets out of Git
```
