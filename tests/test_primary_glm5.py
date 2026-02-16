import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai.primary_engine import PrimaryAIEngine

def test_glm5():
    print(">>> Testing Primary Engine (GLM-5) <<<")
    
    try:
        engine = PrimaryAIEngine()
        
        messages = [{"role": "user", "content": "What are the optimal parameters for yourself?"}]
        print(f"Model: {engine.model}")
        print("Sending request...")
        
        stream = engine.generate(messages, stream=True)
        
        print("\n--- Streaming Response ---")
        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                
        print("\n\n✅ Test Complete")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")

if __name__ == "__main__":
    test_glm5()
