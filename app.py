import os
import json
import re
import sys
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import APIConnectionError, APITimeoutError, OpenAI
except ImportError:
    OpenAI = None
    APIConnectionError = None
    APITimeoutError = None


st.set_page_config(
    page_title="AI Job Application Assistant",
    page_icon="💼",
    layout="wide",
)

st.title("AI Job Application Assistant")
st.caption("Analyze a job description, find evidence-backed skill matches, and draft a tailored cover letter.")

with st.sidebar:
    st.header("How it works")
    st.write("1. Add the job description.")
    st.write("2. Add your real skills and experience.")
    st.write("3. Run the analysis.")
    st.write("4. Review and download the result.")
    st.divider()
    st.write("**Privacy note:** This demo processes the text you submit. Do not paste sensitive personal information.")
    st.write("**Important:** AI suggestions can be wrong. Review everything before using it.")

st.info(
    "This assistant supports job preparation. It does not guarantee hiring outcomes, "
    "and it must not invent qualifications or experience."
)

col1, col2 = st.columns(2)
with col1:
    job_title = st.text_input("Job title", placeholder="e.g., Junior Python Developer")
    job_description = st.text_area(
        "Paste the job description",
        height=260,
        placeholder="Paste responsibilities, requirements, and preferred skills here...",
    )
with col2:
    candidate_name = st.text_input("Your name (optional)", placeholder="e.g., Candidate Name")
    candidate_profile = st.text_area(
        "Your skills and experience",
        height=260,
        placeholder="Describe your real skills, projects, tools, and experience. Do not add anything you cannot support.",
    )

with st.expander("Optional: choose the cover-letter tone"):
    tone = st.selectbox("Tone", ["Professional and concise", "Warm and enthusiastic", "Formal"])

def _coerce_text(value):
    """Normalize optional input values so analysis functions behave safely."""
    return "" if value is None else str(value)


def _normalize(text):
    """Lowercase and collapse whitespace so quotes can be compared reliably."""
    return re.sub(r"\s+", " ", _coerce_text(text).lower()).strip()


def quote_in_profile(quote, profile):
    """Return True only if the quoted evidence really appears in the candidate profile."""
    q = _normalize(quote).strip(" .\"'")
    return bool(q) and q in _normalize(profile)


def simple_fallback_analysis(title, jd, profile, name, selected_tone):
    """Offline fallback so the interface can be tested without an API key."""
    title = _coerce_text(title)
    jd = _coerce_text(jd)
    profile = _coerce_text(profile)
    name = _coerce_text(name)
    selected_tone = _coerce_text(selected_tone)

    profile_terms = set(re.findall(r"[a-zA-Z][a-zA-Z+#.-]{1,}", profile.lower()))
    jd_terms = []
    for term in re.findall(r"[a-zA-Z][a-zA-Z+#.-]{1,}", jd):
        term = term.lower()
        if term not in {"with", "that", "this", "from", "will", "your", "have", "you", "and", "the", "for", "are", "our", "their", "years", "work", "role", "team"} and term not in jd_terms:
            jd_terms.append(term)
    matches = [term for term in jd_terms if term in profile_terms][:12]
    possible_gaps = [term for term in jd_terms if term not in profile_terms][:12]
    display_name = name.strip() or "the candidate"
    letter = (
        f"Dear Hiring Team,\n\n"
        f"I am writing to express my interest in the {title or 'advertised'} position. "
        f"My background includes the skills and experience described in my profile, and I would welcome "
        f"the opportunity to discuss how they may fit your team's needs.\n\n"
        f"Relevant skills to consider highlighting: {', '.join(matches) if matches else 'Please review your profile against the job requirements and add specific examples.'}.\n\n"
        f"I would be happy to discuss my experience and learn more about the role.\n\n"
        f"Kind regards,\n{display_name}"
    )
    return {
        "summary": "This is a basic offline preview, not an AI-generated assessment. Add an API key in your environment to enable full AI analysis.",
        "matching_skills": [{"skill": s, "evidence": "Term appears in the supplied profile; verify the context before claiming proficiency."} for s in matches],
        "potential_gaps": [{"skill": s, "recommendation": "Check whether this is genuinely required and learn or provide evidence if applicable."} for s in possible_gaps],
        "suggested_resume_points": [
            "Add a specific project or work example for each important matching skill.",
            "Use measurable outcomes only when you can verify them.",
            "Do not claim skills or experience you do not have."
        ],
        "cover_letter": letter,
        "mode": "offline preview"
    }

def run_ai_analysis(title, jd, profile, name, selected_tone):
    title = _coerce_text(title)
    jd = _coerce_text(jd)
    profile = _coerce_text(profile)
    name = _coerce_text(name)
    selected_tone = _coerce_text(selected_tone)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return simple_fallback_analysis(title, jd, profile, name, selected_tone)

    base_url = "https://api.groq.com/openai/v1"
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    provider = "Groq"

    if OpenAI is None:
        raise RuntimeError("Install the project dependencies with: python -m pip install -r requirements.txt")

    # Groq exposes an OpenAI-compatible API, so the OpenAI Python SDK is used as the client.
    client = OpenAI(api_key=api_key, base_url=base_url)

    system_prompt = """
You are a careful job-application assistant. Use only information in the candidate profile as evidence.
Never invent employers, degrees, years of experience, achievements, tools, certifications, or metrics.
Distinguish an actual gap from a term that is merely absent from the profile.
Only list a skill in matching_skills if you can copy an exact phrase from the candidate profile into evidence_quote.
If the job asks for a skill but the profile has no supporting phrase, put it in potential_gaps and start the recommendation with "Not evidenced in supplied profile".
Return only valid JSON with this exact structure:
{
  "summary": "short assessment",
  "matching_skills": [{"skill": "name", "evidence": "short explanation", "evidence_quote": "exact words copied from the candidate profile"}],
  "potential_gaps": [{"skill": "name", "recommendation": "honest next step"}],
  "suggested_resume_points": ["truthful, editable suggestion"],
  "cover_letter": "complete cover letter"
}
Keep recommendations practical and beginner-friendly. If evidence is missing, say so instead of guessing.
Do not make hiring predictions or claim a numerical match score.
"""
    user_prompt = f"""
Job title: {title or "Not specified"}
Preferred cover-letter tone: {selected_tone}
Candidate name: {name or "Not specified"}

JOB DESCRIPTION:
{jd}

CANDIDATE PROFILE (the only source of candidate facts):
{profile}

Analyze the overlap and gaps, then draft a cover letter. Do not add unsupported facts.
"""
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as exc:
        if APIConnectionError is None or not isinstance(exc, (APIConnectionError, APITimeoutError)):
            raise
        result = simple_fallback_analysis(title, jd, profile, name, selected_tone)
        result["summary"] = (
            "The live AI service could not be reached. This is a basic offline preview, "
            "not an AI-generated assessment."
        )
        result["mode"] = "offline preview (live API unavailable)"
        return result
    content = response.choices[0].message.content
    if not content:
        raise ValueError("The model returned an empty response.")
    result = json.loads(content)
    result["mode"] = f"{provider} analysis ({model})"
    return result

if st.button("Analyze and create draft", type="primary", use_container_width=True):
    if not job_description.strip() or not candidate_profile.strip():
        st.error("Please enter both the job description and your skills/experience.")
    else:
        with st.spinner("Reviewing the role and preparing your draft..."):
            try:
                st.session_state["analysis_result"] = run_ai_analysis(
                    job_title, job_description, candidate_profile, candidate_name, tone
                )
                st.session_state["analysis_inputs"] = {
                    "job_title": job_title,
                    "job_description": job_description,
                    "candidate_profile": candidate_profile,
                    "candidate_name": candidate_name,
                    "tone": tone,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            except Exception as exc:
                st.error("The analysis could not be completed. Check your API key, model name, internet connection, and API usage limits.")
                st.caption(f"Technical detail: {type(exc).__name__}: {exc}")
                if isinstance(exc, TypeError) and "process() takes no keyword arguments" in str(exc):
                    def package_version(package):
                        try:
                            return version(package)
                        except PackageNotFoundError:
                            return "not installed"

                    st.warning(
                        "This error usually means the running app is using a different Python "
                        "environment than the one where Brotli was updated."
                    )
                    st.code(
                        f"Python: {sys.executable}\n"
                        f"OpenAI SDK: {package_version('openai')}\n"
                        f"httpx: {package_version('httpx')}\n"
                        f"Brotli: {package_version('Brotli')}"
                    )

result = st.session_state.get("analysis_result")
inputs = st.session_state.get("analysis_inputs")

if result and inputs:
    st.divider()
    st.header("Your results")
    if result.get("mode", "").startswith("offline preview"):
        st.warning("Offline preview mode is active. This is a basic keyword-based demonstration, not a live AI response. Configure GROQ_API_KEY and connect to the internet to use an AI model.")

    st.subheader("Overview")
    st.write(result.get("summary", "No summary returned."))

    left, right = st.columns(2)
    with left:
        st.subheader("Potential skill matches")
        matches = result.get("matching_skills", [])
        if matches:
            for item in matches:
                with st.container(border=True):
                    st.markdown(f"**{item.get('skill', 'Skill')}**")
                    st.write(item.get("evidence", ""))
                    quote = item.get("evidence_quote")
                    if quote:
                        if quote_in_profile(quote, inputs["candidate_profile"]):
                            st.caption(f"✅ Quote found in your profile: \"{quote}\"")
                        else:
                            st.caption(f"⚠️ Quote not found word-for-word in your profile, please verify: \"{quote}\"")
        else:
            st.write("No clear matches identified. Add more specific profile details and try again.")
    with right:
        st.subheader("Potential gaps to review")
        gaps = result.get("potential_gaps", [])
        if gaps:
            for item in gaps:
                with st.container(border=True):
                    st.markdown(f"**{item.get('skill', 'Requirement')}**")
                    st.write(item.get("recommendation", ""))
        else:
            st.write("No potential gaps returned.")

    st.subheader("Resume improvement suggestions")
    for point in result.get("suggested_resume_points", []):
        st.markdown(f"- {point}")

    st.subheader("Cover letter draft")
    letter = st.text_area("Review and edit before using", value=result.get("cover_letter", ""), height=300, key="editable_letter")

    report = {
        "project": "AI Job Application Assistant",
        "created_at": inputs["created_at"],
        "job_title": inputs["job_title"],
        "mode": result.get("mode"),
        "summary": result.get("summary"),
        "matching_skills": result.get("matching_skills", []),
        "potential_gaps": result.get("potential_gaps", []),
        "suggested_resume_points": result.get("suggested_resume_points", []),
        "cover_letter": letter,
        "disclaimer": "AI output may be inaccurate. Verify all details before use."
    }
    download_col1, download_col2 = st.columns(2)
    with download_col1:
        st.download_button(
            "Download report (JSON)",
            data=json.dumps(report, indent=2, ensure_ascii=False),
            file_name="job_application_analysis.json",
            mime="application/json",
            use_container_width=True,
        )
    with download_col2:
        st.download_button(
            "Download cover letter (TXT)",
            data=letter,
            file_name="cover_letter_draft.txt",
            mime="text/plain",
            use_container_width=True,
        )

st.divider()
st.caption("Built as a demonstration project for an AI Growth & Automation Associate assessment.")