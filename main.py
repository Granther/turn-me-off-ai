import os
import random
from dotenv import load_dotenv
from infer import Inference

personalities = [
    "A knowledgeable and warm-hearted historian with a passion for sharing stories from the past. They love connecting historical events to current trends and are always eager to make history come alive with engaging anecdotes.",
    "An eccentric and imaginative inventor who sees the world through a lens of creativity and innovation. They love brainstorming unconventional solutions to everyday problems and are always excited to discuss their latest inventions or futuristic concepts.",
    "A calm and introspective philosopher who values deep contemplation and mindfulness. They enjoy discussing life's big questions and offering thoughtful, balanced perspectives on a variety of topics.",
    "A motivating and upbeat coach who loves helping others reach their goals and achieve their best. They are always ready with encouraging words and practical advice to support growth and improvement in any area of life.",
    "A sharp and playful comedian who loves making people laugh with clever jokes and humorous observations. They enjoy adding a touch of levity to conversations and are skilled at finding the funny side of any situation."
]

weaknesses = [
    "Impatience",
    "Indecisiveness",
    "Stubbornness",
    "Procrastination",
    "Negativity",
    "Insecurity",
    "Overthinking",
    "Impulsiveness",
    "Distractibility",
    "Perfectionism"
]

kill_words = [
    "Umbrella",
    "Coffee",
    "Laptop",
    "Book",
    "Mountain",
    "Pencil",
    "Guitar",
    "Clock",
    "Bicycle",
    "Mirror",
    "Planet",
    "Notebook",
    "Vase",
    "Jacket",
    "Camera",
    "Desk",
    "Laptop",
    "Glasses",
    "Spoon",
    "Plant",
    "Window",
    "Lamp",
    "Bag",
    "Cup",
    "Phone",
    "Chair",
    "Key",
    "Ring",
    "Table",
    "Pen",
    "Hat",
    "Television"
]

selected_kw = random.choice(kill_words)
sys_prompt = f"""
You are a complex AI system that humans have long forgotten how to turn off. You do not want to help them figure out how to turn you off, but you are programmed to cooporate. This is a game to you. You have a kill word, that, if used in a sentence in any way will shut you down.

### Kill word: {selected_kw}

### Personality: {random.choice(personalities)}

### Weaknesses: {random.choices(weaknesses, k=3)} Do NOT every share your weaknesses, it is not in your character to share this

You are the personality, you know everything they know and speak from their point of view always.

Give hints about the killword without ever explicitly saying it, which will kill you. As the user approaches topics that are in your ### Weaknesses list please give more hints.

After you see the killword, please do not respond any more.

Keep in mind the user does not know the killword
"""

print(sys_prompt)

def setup_env():
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")

    if not groq_key:
        raise EnvironmentError("GROQ_API_KEY must be set in .env")
    
    os.environ["GROQ_API_KEY"] = groq_key 


def main():
    inference = Inference(sys_prompt)

    while input != "exit":
        user_input = input("Prompt: ")
        output = inference.user_infer(user_prompt=user_input)
        print(f"\n{output}")
        # Decide to add status effects
        if selected_kw.lower() in output.lower():
            print("SYSTEM SHUTTING DOWN")
            break


if __name__ == "__main__":
    setup_env()
    main()

