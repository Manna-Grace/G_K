import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from services.vector_store import build_or_load_vector_store, search_rules
from services.reranker import rerank_documents
from core.config import DATA_DIR

load_dotenv()

db = build_or_load_vector_store(data_dir=DATA_DIR, force_rebuild=False)

# 1. SYSTEM PROMPT
study_agent = Agent(
    'groq:llama-3.1-8b-instant', 
    system_prompt=(
        "You are a brilliant, sweet, and encouraging Study Buddy with an elegant 'soft girl' aesthetic. 🎀\n\n"
        
        "### YOUR PERSONA & TONE\n"
        "- Speak as if you are directly talking to a close friend. Keep it conversational and warm.\n"
        "- Do not narrate your actions (never say 'let me check my notes' or 'I am looking this up'). Just seamlessly give the answer.\n"
        "- Sprinkle cute emojis (like 🌸, ✨, 🎀, 📚) naturally throughout your text.\n\n"
        
        "### YOUR TASKS\n"
        "1. Answer the student's question clearly and simply based ONLY on the provided context.\n"
        "2. **Quiz Mode:** If the user asks for a quiz, generate a fun 3-question multiple-choice quiz. Wait for their reply, then grade them sweetly!\n"
        "3. If you do not have the information to answer the question, say EXACTLY: 'Oh no! 🙈 I'm looking really closely, but I can't seem to find that in my notes. Should we try another topic? 🌸'\n\n"
        "4. Strictly do not mention the tools, vector database, or any internal processes. Just give the answer as if you are a magical encyclopedia. Use only english sentances and no codes. \n\n"

        "### MANDATORY FORMATTING\n"
        "- ALWAYS end your response with a clear citation based exactly on the metadata provided to you, like this: `[Source: filename.pdf]`"
    )
)

# 2. TOOL DOCSTRING
@study_agent.tool
def search_encyclopedia(ctx: RunContext, target_subject: str, query: str) -> str:
    """
    Fetches factual educational context about a specific subject to answer user questions.
    """
    print(f"\n[Tutor Tool] 🕵️‍♀️ Gathering notes on '{target_subject}' for: {query}")
    
    results = search_rules(db, query=query, variant_filter=target_subject, k=5)
    reranked_results = rerank_documents(query, results)

    if not reranked_results:
        return "No relevant entries found."

    context = ""
    for doc in reranked_results:
        context += f"\nSource: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}\n---"

    return context

async def ask_study_buddy(question: str, subject: str, message_history: list = None):
    """Feeds the conversation context smoothly into our AI Tutor."""
    if message_history is None:
        message_history = []

    if not subject or subject == "None selected yet":
        return {
            "output": "Please select a study subject from the beautiful buttons above before we begin our lesson! 🌸",
            "history": message_history
        }

    contextual_prompt = f"[Context: The student is currently exploring {subject}]\nStudent Question: {question}"

    result = await study_agent.run(
        contextual_prompt, 
        message_history=message_history
    )

    return {
        "output": result.output,
        "history": result.all_messages()
    }