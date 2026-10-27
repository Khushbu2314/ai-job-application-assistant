# Prompts used for this project

## Project idea

> Create a simple AI project that solves a real problem and is useful for a job application.

## Languages and libraries prompt

> Build the app in Python using Streamlit for the web page. Use the OpenAI Python library to connect to Groq's AI service, and python-dotenv to load settings such as the API key from a local `.env` file. Keep the project simple and use the libraries listed in `requirements.txt`.

The project is written in Python. It uses Streamlit, the OpenAI Python SDK, and python-dotenv. Brotli is also listed as a dependency to support the HTTP connection.

## What the app should do

> Make an assistant that compares a job description with a person's skills and experience. Show which skills match, suggest what to improve on a resume, and write a cover letter. Be honest: do not make up experience or assume someone lacks a skill just because they did not mention it.

## How the AI should respond

> Use only the information the person provides. Show examples from their profile when you say a skill matches. Point out job requirements that are not mentioned, and suggest ways to address them. Keep the advice clear and practical. Do not predict whether the person will get the job.

## What the app includes

- A form for the job description and the candidate's experience.
- A live AI option when a Groq API key and internet connection are available.
- A simple offline preview when the key is missing or the AI service cannot be reached. The preview is not AI-generated.
- Suggestions the candidate can review and edit before using.
- Downloads for the results and cover letter.

## When something goes wrong

- The app asks for both the job description and candidate experience if either is missing.
- If the AI service is offline, the app switches to the clearly labeled preview.
- If the API key, model, or request has another problem, the app shows an error so it can be checked.
- If an AI quote does not match the candidate's profile, the app asks the user to verify it.

Always check the suggestions and cover letter before using them. The app is a job-search helper, not a hiring decision tool.
