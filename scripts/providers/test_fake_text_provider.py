import sys
import os

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.providers.text.fake import FakeTextGenerationProvider

def run_tests():
    print("--- Starting FakeTextGenerationProvider Verification ---")
    provider = FakeTextGenerationProvider()

    topic = "Machine Learning Basics"
    niche = "Tech Education"

    print("Inputs:")
    print(f"  Topic: '{topic}'")
    print(f"  Niche: '{niche}'\n")

    # Generate values in the specified order
    title = provider.generate_title(topic, niche)
    description = provider.generate_description(topic, title, niche)
    script = provider.generate_script(topic, title, niche)
    hashtags = provider.generate_hashtags(topic, title, niche)

    # Print the outputs clearly
    print("Generated Title:")
    print(f"  {title}\n")
    
    print("Generated Description:")
    print(f"  {description}\n")
    
    print("Generated Script:")
    print(f"  {script}\n")
    
    print("Generated Hashtags:")
    print(f"  {hashtags}\n")

    # Perform assertions
    assert title == "Machine Learning Basics | Tech Education", f"Unexpected title: {title}"
    
    assert description == "A short video about Machine Learning Basics. Created for the Tech Education niche.", f"Unexpected description: {description}"
    
    assert script == "Today we're talking about Machine Learning Basics. This content is for viewers interested in Tech Education.", f"Unexpected script: {script}"
    
    assert hashtags == [
        "#machine_learning_basics",
        "#tech_education",
        "#fake_generated"
    ], f"Unexpected hashtags: {hashtags}"

    # Final success message prints only if no assertion failed
    print("--- All assertions passed! FakeTextGenerationProvider works as expected. ---")

if __name__ == "__main__":
    run_tests()
