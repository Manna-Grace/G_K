import chainlit as cl
from core.agent import ask_study_buddy

# 🖼️ We are using high-quality aesthetic Unsplash URLs for the images!
WELCOME_MESSAGE = """
<div class="hero">
    <div class="hero-title">Study Oasis 🌸</div>
    <div class="hero-subtitle">Your elegant, magical guide to learning beautifully.</div>
</div>

<div class="variant-grid">
    <div class="variant-card">
        <img class="card-image" src="/public/images/space.jpg" alt="Space">
        <div class="variant-name">Astronomy</div>
        <div class="variant-desc">Explore the dreamy mysteries of the stars and our universe.</div>
    </div>
    <div class="variant-card">
        <img class="card-image" src="/public/images/history.jpg" alt="History">
        <div class="variant-name">Antiquity</div>
        <div class="variant-desc">Travel back in time to the elegance of ancient civilizations.</div>
    </div>
    <div class="variant-card">
        <img class="card-image" src="/public/images/animals.jpg" alt="Animals">
        <div class="variant-name">Fauna</div>
        <div class="variant-desc">Discover the fascinating and beautiful creatures of our world.</div>
    </div>
    <div class="variant-card">
        <img class="card-image" src="/public/images/art.jpg" alt="Art">
        <div class="variant-name">Fine Art</div>
        <div class="variant-desc">Immerse yourself in the breathtaking evolution of human creativity.</div>
    </div>
</div>
"""

@cl.on_chat_start
async def start():
    cl.user_session.set("message_history", [])
    cl.user_session.set("current_subject", "None selected yet")

    await cl.Message(content=WELCOME_MESSAGE).send()

    # We keep the buttons simple and elegant below the beautiful grid
    await cl.Message(
        content="Choose a subject to set our focus before we begin our lesson:",
        actions=[
            cl.Action(name="subject", payload={"value": "space"}, label="Astronomy"),
            cl.Action(name="subject", payload={"value": "ancient_history"}, label="Antiquity"),
            cl.Action(name="subject", payload={"value": "animals"}, label="Fauna"),
            cl.Action(name="subject", payload={"value": "art_history"}, label="Fine Art"),
        ]
    ).send()

@cl.action_callback("subject")
async def on_subject(action: cl.Action):
    selected_value = action.payload["value"]
    cl.user_session.set("current_subject", selected_value)
    
    clean_name = selected_value.replace("_", " ").title()
    if clean_name == "Space": clean_name = "Astronomy"
    if clean_name == "Ancient History": clean_name = "Antiquity"
    if clean_name == "Art History": clean_name = "Fine Art"
    
    await cl.Message(
        content=f"✨ I have my elegant notes ready for **{clean_name}**. What would you like to explore today? (You can also ask me for a quick quiz!)"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("message_history")
    selected_subject = cl.user_session.get("current_subject")
    
    thinking = cl.Message(content="📖 Gently turning the pages of my encyclopedia...")
    await thinking.send()

    result = await ask_study_buddy(
        question=message.content, 
        subject=selected_subject, 
        message_history=history
    )

    thinking.content = result["output"]
    await thinking.update()
    cl.user_session.set("message_history", result["history"])