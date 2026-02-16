import json
import sys

import requests

# Configuration
COLLECTOR_URL = "http://localhost:8550/v1/chat/completions"
HISTORY = []

def type_effect(text):
    """Simulates typing effect for smoother output."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        # time.sleep(0.002) # Ultra-fast typing

def print_separator():
    print("-" * 60)

def chat_loop():
    print("\n⚡ MR. VERMA TERMINAL CLIENT (Zero Bloat Edition)")
    print("   Type 'exit' to quit. Type 'clear' to reset history.\n")

    while True:
        try:
            user_input = input("\n👤 YOU: ").strip()
            if not user_input: continue

            if user_input.lower() in ("exit", "quit"):
                print("👋 Session Terminated.")
                break

            if user_input.lower() == "clear":
                global HISTORY
                HISTORY = []
                print("🧹 History cleared.")
                continue

            HISTORY.append({"role": "user", "content": user_input})

            payload = {
                "model": "moonshotai/kimi-k2.5", # Will be handled by collector
                "messages": HISTORY,
                "stream": True
            }

            print("\n🤖 MR. VERMA: ", end="", flush=True)

            try:
                with requests.post(COLLECTOR_URL, json=payload, stream=True, timeout=180) as resp:
                    resp.raise_for_status()

                    full_response = ""
                    for line in resp.iter_lines():
                        if line:
                            decoded = line.decode("utf-8")
                            if decoded.startswith("data: "):
                                data_str = decoded[6:]
                                if data_str == "[DONE]": break
                                try:
                                    chunk = json.loads(data_str)
                                    delta = chunk["choices"][0]["delta"].get("content", "")
                                    if delta:
                                        type_effect(delta)
                                        full_response += delta
                                except:
                                    pass

                    HISTORY.append({"role": "assistant", "content": full_response})
                    print("\n")

            except requests.exceptions.ConnectionError:
                print("❌ Error: Collector is offline. Is Docker running?")
            except Exception as e:
                print(f"❌ Error: {e}")

        except KeyboardInterrupt:
            print("\n👋 Interrupted.")
            break

if __name__ == "__main__":
    chat_loop()
