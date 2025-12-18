# Multi-Hop RAG Resume Screening Pipeline
# Converted from Google Colab notebook

import os
import sys
import logging
import json
import re
import requests
from datetime import datetime
from pathlib import Path
from typing import TypedDict, Annotated
import uuid

# Configure logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("capstone")
logger.setLevel(logging.INFO)

# ===========================================
# DOCUMENT LOADING & CHUNKING
# ===========================================

from pypdf import PdfReader

def load_text_from_file(path: str) -> str:
    try:
        if path.endswith(".pdf"):
            logger.info(f"Reading PDF file: {path}")
            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
        else:
            logger.info(f"Reading text file: {path}")
            return open(path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"Failed to load file: {path}. Error: {e}")
        return ""


def load_documents(folder: str):
    logger.info(f"Loading documents from folder: {folder}")
    docs = []
    
    if not os.path.exists(folder):
        logger.warning(f"Folder does not exist: {folder}")
        return docs
        
    for file in os.listdir(folder):
        fullpath = os.path.join(folder, file)
        if os.path.isfile(fullpath):
            text = load_text_from_file(fullpath)
            if len(text.strip()) < 10:
                logger.warning(f"File seems empty or unreadable: {file}")
                continue
            docs.append({"id": file, "text": text})
            logger.info(f"Loaded document: {file} (length={len(text)} chars)")
    
    logger.info(f"Total documents loaded: {len(docs)}")
    return docs


def chunk_text(text: str, chunk_size=300, overlap=40):
    if not text or len(text) < 20:
        logger.warning("Text too short to chunk.")
        return []
    
    logger.info(f"Chunking text into segments (size={chunk_size}, overlap={overlap})")
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        chunk = " ".join(words[start:start + chunk_size])
        chunks.append(chunk)
        start += chunk_size - overlap
    
    logger.info(f"Created {len(chunks)} chunks.")
    return chunks


# ===========================================
# VECTOR DATABASE
# ===========================================

import chromadb
from chromadb.utils import embedding_functions

# Global collection reference
collection = None

def create_vector_db(resume_path: str, job_path: str):
    """Create vector database with proper metadata tagging."""
    global collection
    
    logger.info("Initializing ChromaDB client & embedding function...")
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    chroma_client = chromadb.Client()
    
    # Delete old collection if exists
    try:
        chroma_client.delete_collection("hiring_rag")
        logger.info("✓ Deleted old collection 'hiring_rag'")
    except Exception:
        logger.info("No existing collection to delete")
    
    # Create fresh collection
    collection = chroma_client.create_collection(
        name="hiring_rag",
        embedding_function=embedder
    )
    logger.info("✓ Created new Chroma collection 'hiring_rag'")
    
    # Load and add resumes
    resume_docs = load_documents(resume_path)
    logger.info(f"Loading {len(resume_docs)} RESUMES...")
    
    for doc in resume_docs:
        chunks = chunk_text(doc['text'])
        ids = [f"resume_{doc['id']}_chunk{i}" for i in range(len(chunks))]
        metadatas = [{"type": "resume", "source": doc['id']} for _ in chunks]
        
        if chunks:
            collection.add(documents=chunks, ids=ids, metadatas=metadatas)
            logger.info(f"  ✓ Added {len(chunks)} chunks from {doc['id']} (RESUME)")
    
    # Load and add job descriptions
    job_docs = load_documents(job_path)
    logger.info(f"Loading {len(job_docs)} JOB DESCRIPTIONS...")
    
    for doc in job_docs:
        chunks = chunk_text(doc['text'])
        ids = [f"job_{doc['id']}_chunk{i}" for i in range(len(chunks))]
        metadatas = [{"type": "job", "source": doc['id']} for _ in chunks]
        
        if chunks:
            collection.add(documents=chunks, ids=ids, metadatas=metadatas)
            logger.info(f"  ✓ Added {len(chunks)} chunks from {doc['id']} (JOB)")
    
    logger.info("✅ Vector DB creation completed successfully.")
    return collection


# ===========================================
# GROQ LLM CLIENT
# ===========================================

from groq import Groq

# Get API key from environment
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not set in environment. Please set it before running.")
    logger.warning("Run: export GROQ_API_KEY='your-api-key-here'")

client = None


def init_groq_client():
    global client, GROQ_API_KEY
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    if GROQ_API_KEY:
        client = Groq(api_key=GROQ_API_KEY)
        logger.info("✓ Groq client initialized")
    else:
        raise ValueError("GROQ_API_KEY not set. Please set it before running.")


# ===========================================
# MULTI-HOP RAG (PHASE 1)
# ===========================================

def hop1_candidate_retrieval(job_description: str):
    """Retrieve only resume chunks (not job descriptions)."""
    logger.info("Running Hop 1 — Vector retrieval based on job description.")
    logger.info("Retrieving top 8 relevant RESUME chunks...")
    
    results = collection.query(
        query_texts=[job_description],
        n_results=8,
        where={"type": "resume"}
    )
    
    logger.info("Retrieval complete.")
    return results


def hop2_experience_refinement(chunks):
    """Use Groq LLM to refine the candidate ranking."""
    logger.info("Running Hop 2 — LLM experience relevance analysis.")
    
    text = "\n\n".join(chunks)
    
    prompt = f"""
    You are evaluating candidate resume chunks for job match.

    Resume Chunks:
    {text}

    Task:
    - Rate how relevant these chunks are to the job description.
    - Identify strengths and weaknesses.
    - Provide a final relevance score (0–100).
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.2
        )
        logger.info("LLM refinement successful.")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq LLM call failed: {e}")
        return "LLM error — check logs."


def hop3_skill_review(chunks, job_description: str):
    """Hop 3: RAG-based skill review."""
    logger.info("Running Hop 3 — RAG-based skill review.")
    
    skill_results = collection.query(
        query_texts=[f"required skills: {job_description}"],
        n_results=5
    )
    
    required_skills = skill_results["documents"][0] if skill_results["documents"] else []
    candidate_text = "\n".join(chunks)
    
    prompt = f"""
    You are a technical skill evaluator.

    Required Skills (from job posting):
    {chr(10).join(required_skills)}

    Candidate Skills (from resume):
    {candidate_text}

    Task:
    - Compare candidate skills against required skills
    - Identify matching skills, missing skills, and additional skills
    - Provide skill match score (0-100)
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.2
        )
        logger.info("Hop 3 skill review completed.")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Hop 3 skill review failed: {e}")
        return "Skill review error — check logs."


def run_multi_hop(job_description: str):
    """Main function performing three-hop RAG pipeline."""
    logger.info("=== Starting Multi-Hop Retrieval Pipeline ===")
    
    # Hop 1
    retrieved = hop1_candidate_retrieval(job_description)
    chunks = retrieved["documents"][0] if retrieved["documents"] else []
    logger.info(f"Hop 1 retrieved {len(chunks)} chunks.")
    
    if not chunks:
        logger.warning("No chunks retrieved. Check your resume data.")
        return {"retrieved_chunks": [], "refined_analysis": "", "skill_review": ""}
    
    # Hop 2
    refinement = hop2_experience_refinement(chunks)
    logger.info("Hop 2 experience analysis completed.")
    
    # Hop 3
    skill_review = hop3_skill_review(chunks, job_description)
    logger.info("Hop 3 skill review completed.")
    
    logger.info("=== Multi-Hop Retrieval Completed ===")
    
    return {
        "retrieved_chunks": chunks,
        "refined_analysis": refinement,
        "skill_review": skill_review
    }


# ===========================================
# PEC AGENTS (PHASE 2)
# ===========================================

def extract_json_from_response(text: str) -> str:
    """Extract JSON from LLM response."""
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    return text.strip()


def planner_agent(job_description: str, num_candidates: int) -> dict:
    """Create evaluation plan."""
    logger.info("PLANNER: Creating evaluation plan...")
    
    prompt = f"""You are a hiring planner. Create an evaluation plan for {num_candidates} candidates.

Job Description:
{job_description}

Create a structured evaluation plan with these components:
1. List of subtasks needed to evaluate candidates
2. Order of execution for these subtasks
3. Any special notes or conditions

Output ONLY valid JSON in this exact format:
{{
  "subtasks": ["screen_resume", "generate_interview_questions", "design_skill_assessment"],
  "order": ["screen_resume", "generate_interview_questions", "design_skill_assessment"],
  "notes": "If screening score < 0.5, skip interview and assessment steps."
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a JSON generator. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        raw_content = response.choices[0].message.content
        plan = json.loads(raw_content)
        
        if not all(key in plan for key in ['subtasks', 'order', 'notes']):
            raise ValueError("Missing required fields in plan")
        
        logger.info(f"PLANNER: Plan created with {len(plan['subtasks'])} subtasks")
        return plan
    except Exception as e:
        logger.error(f"PLANNER: Failed - {e}")
        return {
            "subtasks": ["screen_resume", "generate_interview_questions", "design_skill_assessment"],
            "order": ["screen_resume", "generate_interview_questions", "design_skill_assessment"],
            "notes": "Default plan - evaluate candidates sequentially"
        }


def screener_agent(job_description: str, candidate_chunks: list, rag_analysis: str) -> dict:
    """Screen candidates using RAG outputs."""
    logger.info("SCREENER: Evaluating candidate...")
    
    rag_truncated = rag_analysis[:2000] if len(rag_analysis) > 2000 else rag_analysis
    
    prompt = f"""
    You are a resume screener. Evaluate this candidate.

    Job Description:
    {job_description[:500]}

    Candidate Information:
    {rag_truncated}

    Output ONLY a JSON object:
    {{
      "passed": true,
      "score": 0.75,
      "matching_skills": ["Python", "Docker"],
      "missing_skills": ["Kubernetes"],
      "experience_match": 0.8,
      "justification": "Strong backend skills"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.2
        )
        
        raw_content = response.choices[0].message.content
        json_str = extract_json_from_response(raw_content)
        result = json.loads(json_str)
        
        logger.info(f"SCREENER: Score: {result['score']:.2f}, Passed: {result['passed']}")
        return result
    except Exception as e:
        logger.error(f"SCREENER: Failed - {e}")
        return {
            "passed": False, "score": 0.0, "matching_skills": [],
            "missing_skills": ["Unable to evaluate"], "experience_match": 0.0,
            "justification": "Error in screening"
        }


def interviewer_agent(candidate_name: str, screening_result: dict) -> list:
    """Generate interview questions."""
    skill_gaps = screening_result.get('missing_skills', [])
    logger.info(f"INTERVIEWER: Generating questions for {candidate_name}...")
    
    prompt = f"""
    Generate 5 targeted interview questions for {candidate_name}.

    Missing Skills: {', '.join(skill_gaps) if skill_gaps else 'General evaluation'}
    Experience Match: {screening_result.get('experience_match', 0.5)}

    Output ONLY a JSON array:
    [
      {{
        "question": "Describe your experience with Python",
        "rationale": "Assess Python proficiency",
        "difficulty": "medium",
        "estimated_time": "5 minutes"
      }}
    ]
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.3
        )
        
        json_str = extract_json_from_response(response.choices[0].message.content)
        questions = json.loads(json_str)
        
        logger.info(f"INTERVIEWER: Generated {len(questions)} questions")
        return questions
    except Exception as e:
        logger.error(f"INTERVIEWER: Failed - {e}")
        return [{"question": "Tell me about your relevant experience",
                 "rationale": "General assessment", "difficulty": "easy",
                 "estimated_time": "5 minutes"}]


def assessor_agent(screening_result: dict, job_description: str) -> list:
    """Design skill assessments."""
    skill_gaps = screening_result.get('missing_skills', [])
    logger.info(f"ASSESSOR: Designing assessments for {len(skill_gaps)} skill gaps...")
    
    prompt = f"""
    Design 2 practical assessments for these skill gaps:
    {', '.join(skill_gaps) if skill_gaps else 'General technical skills'}

    Job Context: {job_description[:300]}

    Output ONLY a JSON array:
    [
      {{
        "type": "coding_task",
        "title": "Python API Development",
        "description": "Build a REST API",
        "estimated_time": "45 minutes",
        "targets_skills": ["Python", "REST APIs"]
      }}
    ]
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        
        json_str = extract_json_from_response(response.choices[0].message.content)
        assessments = json.loads(json_str)
        
        logger.info(f"ASSESSOR: Designed {len(assessments)} assessments")
        return assessments
    except Exception as e:
        logger.error(f"ASSESSOR: Failed - {e}")
        return [{"type": "technical_test", "title": "General Assessment",
                 "description": "Complete evaluation", "estimated_time": "60 minutes",
                 "targets_skills": skill_gaps if skill_gaps else ["General"]}]


def critic_agent(candidate_name: str, all_outputs: dict) -> dict:
    """Review all outputs for quality."""
    logger.info(f"CRITIC: Reviewing outputs for {candidate_name}...")
    
    screening = all_outputs['screening']
    questions = all_outputs['interview_questions']
    assessments = all_outputs['assessments']
    
    questions_text = "\n".join([f"  Q{i+1}: {q['question']}" for i, q in enumerate(questions[:5])])
    assessments_text = "\n".join([f"  A{i+1}: {a['title']}" for i, a in enumerate(assessments)])
    
    prompt = f"""Review this candidate evaluation for quality.

CANDIDATE: {candidate_name}

SCREENING: Score={screening['score']:.2f}, Passed={screening['passed']}
Missing Skills: {', '.join(screening['missing_skills']) if screening['missing_skills'] else 'None'}

INTERVIEW QUESTIONS:
{questions_text}

ASSESSMENTS:
{assessments_text}

Rate quality 0.0-1.0. Output ONLY valid JSON:
{{
  "quality_score": 0.8,
  "issues": [{{"type": "issue", "severity": "low", "description": "Minor issue"}}],
  "suggestions": ["Suggestion here"],
  "consistency_check": {{"passed": true, "notes": "Good alignment"}},
  "hallucination_check": {{"passed": true, "notes": "No contradictions"}}
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a JSON generator. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        raw_content = response.choices[0].message.content
        feedback = json.loads(raw_content)
        
        logger.info(f"CRITIC: Quality={feedback.get('quality_score', 0):.2f}")
        return feedback
    except Exception as e:
        logger.error(f"CRITIC: Failed - {e}")
        return {
            "quality_score": 0.5,
            "issues": [{"type": "error", "severity": "high", "description": str(e)}],
            "suggestions": ["Review implementation"],
            "consistency_check": {"passed": False, "notes": "Error"},
            "hallucination_check": {"passed": False, "notes": "N/A"}
        }


# ===========================================
# HELPER FUNCTIONS
# ===========================================

def extract_candidate_name(chunk: str) -> str:
    """Extract candidate name from resume chunk."""
    lines = chunk.split('\n')
    first_line = lines[0].strip() if lines else ""
    
    if first_line and len(first_line.split()) <= 4:
        keywords = ['job', 'title', 'responsibilities', 'summary', 'email', 'phone', 'experience']
        if not any(kw in first_line.lower() for kw in keywords):
            return first_line
    
    for line in lines[:5]:
        if 'name:' in line.lower():
            return line.split(':', 1)[-1].strip()
    
    return "Unknown Candidate"


def extract_skills_from_job(job_description: str) -> list:
    """Extract key skills from job description."""
    patterns = [
        r'\b(Python|Java|JavaScript|TypeScript|Go|Rust|C\+\+|C#|Ruby|PHP)\b',
        r'\b(React|Angular|Vue|Django|Flask|FastAPI|Spring|Node\.js)\b',
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|CI/CD|DevOps)\b',
        r'\b(SQL|PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch)\b',
        r'\b(Machine Learning|AI|Data Science|NLP|Computer Vision)\b',
    ]
    
    skills = []
    for pattern in patterns:
        matches = re.findall(pattern, job_description, re.IGNORECASE)
        skills.extend([m.strip() for m in matches])
    
    seen = set()
    unique = []
    for skill in skills:
        if skill.lower() not in seen:
            seen.add(skill.lower())
            unique.append(skill)
    
    return unique[:5]


def extract_role_from_job(job_description: str) -> str:
    """Extract role from job description."""
    lines = job_description.split('\n')[:5]
    
    patterns = [
        r'(?:Job Title|Position|Role):\s*(.+)',
        r'(?:Senior|Junior|Lead)?\s*(?:Software|Data|ML)\s+(?:Engineer|Developer)',
    ]
    
    for line in lines:
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip() if match.lastindex else match.group(0).strip()
    
    return "Software Engineer"


# ===========================================
# COMPLETE PIPELINE
# ===========================================

def run_complete_hiring_pipeline(job_description: str) -> dict:
    """Complete pipeline integrating Phase 1 RAG with Phase 2 PEC agents."""
    logger.info("=" * 60)
    logger.info("Starting Complete Hiring Pipeline (Phase 1 + Phase 2)")
    logger.info("=" * 60)
    
    # Phase 1: Multi-Hop RAG
    logger.info("PHASE 1: Multi-Hop RAG Analysis")
    rag_results = run_multi_hop(job_description)
    
    candidate_chunks = rag_results['retrieved_chunks']
    hop2_analysis = rag_results['refined_analysis']
    hop3_skills = rag_results['skill_review']
    
    logger.info(f"PHASE 1 Complete: Retrieved {len(candidate_chunks)} candidates")
    
    if not candidate_chunks:
        return {"error": "No candidates found", "candidate_evaluations": []}
    
    # Phase 2: PEC Pattern
    logger.info("PHASE 2: PEC Agent Pipeline Starting")
    
    plan = planner_agent(job_description, len(candidate_chunks))
    all_candidate_results = []
    
    for i, chunk in enumerate(candidate_chunks[:3], 1):
        logger.info(f"Processing Candidate #{i}")
        
        candidate_name = extract_candidate_name(chunk)
        individual_analysis = f"Candidate Resume:\n{chunk}"
        
        # Screener
        screening = screener_agent(job_description, [chunk], individual_analysis)
        
        if screening['score'] < 0.5:
            logger.warning(f"Candidate {candidate_name} scored {screening['score']:.2f} - Skipping")
            all_candidate_results.append({
                'candidate_name': candidate_name,
                'screening': screening,
                'skipped': True
            })
            continue
        
        # Interviewer and Assessor
        questions = interviewer_agent(candidate_name, screening)
        assessments = assessor_agent(screening, job_description)
        
        # Critic
        critique = critic_agent(candidate_name, {
            'screening': screening,
            'interview_questions': questions,
            'assessments': assessments
        })
        
        all_candidate_results.append({
            'candidate_name': candidate_name,
            'candidate_chunk': chunk,
            'screening': screening,
            'interview_questions': questions,
            'assessments': assessments,
            'critique': critique
        })
    
    logger.info("=" * 60)
    logger.info("Complete Hiring Pipeline Finished Successfully")
    logger.info("=" * 60)
    
    return {
        'job_description': job_description,
        'plan': plan,
        'phase1_rag': {
            'retrieved_chunks': candidate_chunks,
            'hop2_analysis': hop2_analysis,
            'hop3_skills': hop3_skills
        },
        'candidate_evaluations': all_candidate_results
    }


def print_evaluation_summary(results: dict):
    """Print beautiful summary of results."""
    print("\n" + "=" * 80)
    print("📊 HIRING EVALUATION SUMMARY")
    print("=" * 80)
    
    evaluations = results.get('candidate_evaluations', [])
    
    for idx, candidate in enumerate(evaluations, 1):
        print(f"\n{'=' * 80}")
        print(f"CANDIDATE #{idx}: {candidate['candidate_name']}")
        print("=" * 80)
        
        screening = candidate['screening']
        print(f"\n✅ SCREENING RESULTS:")
        print(f"  • Overall Score: {screening['score']:.2f}/1.0")
        print(f"  • Passed: {'✓ YES' if screening['passed'] else '✗ NO'}")
        print(f"  • Experience Match: {screening.get('experience_match', 0.0):.2f}/1.0")
        print(f"  • Justification: {screening['justification']}")
        
        print(f"\n  💪 Matching Skills:")
        for skill in screening.get('matching_skills', []):
            print(f"     ✓ {skill}")
        
        print(f"\n  ⚠️  Missing Skills:")
        for skill in screening.get('missing_skills', []):
            print(f"     ✗ {skill}")
        
        if candidate.get('skipped'):
            print(f"\n❌ EVALUATION SKIPPED (low score)")
            continue
        
        if candidate.get('interview_questions'):
            print(f"\n❓ INTERVIEW QUESTIONS ({len(candidate['interview_questions'])}):")
            for q_idx, q in enumerate(candidate['interview_questions'][:3], 1):
                print(f"\n   Q{q_idx}. {q['question']}")
                print(f"      Rationale: {q['rationale']}")
        
        if candidate.get('critique'):
            critique = candidate['critique']
            print(f"\n🔍 CRITIC REVIEW:")
            print(f"  • Quality Score: {critique.get('quality_score', 0):.2f}/1.0")
    
    print("\n" + "=" * 80)
    print("✅ EVALUATION COMPLETE")
    print("=" * 80)


# ===========================================
# MAIN ENTRY POINT
# ===========================================

def main():
    """Main function to run the pipeline."""
    # Initialize Groq client
    init_groq_client()
    
    # Paths
    base_path = Path(__file__).parent
    resume_path = base_path / "resume"
    job_path = base_path / "job_description"
    
    # Create vector database
    global collection
    collection = create_vector_db(str(resume_path), str(job_path))
    
    # Sample job description
    sample_job_description = """
    We are seeking a highly motivated and experienced Software Engineer to join our dynamic team.
    The ideal candidate will have a strong background in Python, Java, and cloud platforms like AWS.
    Experience with machine learning frameworks and distributed systems is a plus.
    Responsibilities include designing, developing, and maintaining scalable software solutions,
    participating in code reviews, and collaborating with cross-functional teams.
    A Bachelor's degree in Computer Science or a related field is required.
    """
    
    # Run pipeline
    results = run_complete_hiring_pipeline(sample_job_description)
    
    # Print results
    print_evaluation_summary(results)
    
    return results


if __name__ == "__main__":
    main()
