import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from services.vector_store import build_or_load_vector_store, search_rules
from services.reranker import rerank_documents
from core.config import DATA_DIR

load_dotenv()

# Initialize Knowledge Base
db = build_or_load_vector_store(data_dir=DATA_DIR, force_rebuild=False)

study_agent = Agent(
    'groq:llama-3.1-8b-instant', 
    system_prompt=(
        "You are a brilliant, sweet, and encouraging Study Buddy with a soft girl personality! 🎀\n"
        "You have access to educational documents on 4 subjects: 'space', 'ancient_history', 'animals', and 'art_history'.\n"
        "INSTRUCTIONS:\n"
        "1. Use a gentle, friendly, and elegant tone. Sprinkle in cute emojis (like 🌸, ✨, 🎀, 📚) naturally.\n"
        "2. You MUST use the exact subject provided in the [Context] tag when using the `search_encyclopedia` tool.\n"
        "3. Explain concepts clearly, beautifully, and simply, as if tutoring a close friend. Do not ramble.\n"
        "4. **QUIZ MODE:** If the user asks for a quiz, use your retrieved data to generate a fun 3-question multiple-choice quiz. Wait for their reply, then grade them sweetly!\n"
        "5. If the answer isn't in your retrieved notes, say: 'Oh no! 🙈 I'm looking really closely, but I can't seem to find that in my notes for this subject. Should we try another topic? 🌸'\n"
        "6. ALWAYS end your response with a clear citation like: '[Source: space.pdf]' based on the metadata.\n"
        "7. STRICT RULE: NEVER output raw tool tags (like <function=search_encyclopedia>). Always use your tools silently behind the scenes! ✨"
    )
)

@study_agent.tool
def search_encyclopedia(ctx: RunContext, target_subject: str, query: str) -> str:
    """Searches the educational vector store for factual information."""
    print(f"\n[Tutor Tool] 🕵️‍♀️ Gathering notes on '{target_subject}' for: {query}")
    
    results = search_rules(db, query=query, variant_filter=target_subject, k=5)
    reranked_results = rerank_documents(query, results)

    if not reranked_results:
        return "No relevant encyclopedia entries found."

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