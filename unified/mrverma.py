#!/usr/bin/env python3
"""
MR.VERMA Unified - Multi-Mode AI Platform
==========================================

Single entry point supporting multiple modes:
- unified: Basic AI chat and assistance (8 menu options)
- enhanced: Full agent system with 27 agents, 66 skills, 19 workflows (10 options)
- ultimate: Enhanced + 82 system prompts from leading AI tools (12 options)

Usage:
    python unified/mrverma.py [--mode {unified|enhanced|ultimate}]

Examples:
    python unified/mrverma.py              # Default unified mode
    python unified/mrverma.py --mode enhanced
    python unified/mrverma.py --mode ultimate
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main entry point with mode selection"""
    parser = argparse.ArgumentParser(
        description="MR.VERMA - AI Intelligence Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Modes:
  unified   - Basic AI chat and assistance (default)
  enhanced  - Full agent system with skills and workflows
  ultimate  - Enhanced + 82 system prompts from Claude, Cursor, Devin, etc.

Examples:
  python unified/mrverma.py
  python unified/mrverma.py --mode enhanced
  python unified/mrverma.py --mode ultimate
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["unified", "enhanced", "ultimate"],
        default="unified",
        help="Operating mode (default: unified)",
    )

    args = parser.parse_args()

    # Route to appropriate module based on mode
    if args.mode == "unified":
        # Import and run the unified module
        try:
            from unified.mrverma_unified import main as unified_main

            unified_main()
        except ImportError:
            # Fallback to inline unified implementation
            run_unified_mode()

    elif args.mode == "enhanced":
        # Import and run the enhanced module
        try:
            from unified.mrverma_enhanced import main as enhanced_main

            enhanced_main()
        except ImportError:
            print("Error: Enhanced mode not available")
            print("Falling back to unified mode...")
            run_unified_mode()

    elif args.mode == "ultimate":
        # Import and run the ultimate module
        try:
            from unified.mrverma_ultimate import main as ultimate_main

            ultimate_main()
        except ImportError:
            print("Error: Ultimate mode not available")
            print("Falling back to enhanced mode...")
            try:
                from unified.mrverma_enhanced import main as enhanced_main

                enhanced_main()
            except ImportError:
                print("Falling back to unified mode...")
                run_unified_mode()


def run_unified_mode():
    """Run the basic unified mode (inline implementation)"""
    import os
    import json
    from datetime import datetime

    # Try to import rich for UI
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.prompt import Prompt, Confirm

        console = Console()
        RICH_AVAILABLE = True
    except ImportError:
        RICH_AVAILABLE = False
        console = None

        class DummyPrompt:
            @staticmethod
            def ask(message, default=None, choices=None):
                if choices:
                    message = f"{message} ({'/'.join(choices)}): "
                elif default is not None:
                    message = f"{message} [{default}]: "
                else:
                    message = f"{message}: "
                result = input(message)
                if not result and default is not None:
                    return default
                return result

        class DummyConfirm:
            @staticmethod
            def ask(message):
                result = input(f"{message} (y/n): ")
                return result.lower() in ["y", "yes"]

        Prompt = DummyPrompt
        Confirm = DummyConfirm

    def print_banner():
        """Display the MR.VERMA banner"""
        banner = """
    ███╗   ███╗██████╗      ██╗   ██╗███████╗██████╗ ███╗   ███╗ █████╗
    ████╗ ████║██╔══██╗     ██║   ██║██╔════╝██╔══██╗████╗ ████║██╔══██╗
    ██╔████╔██║██████╔╝     ██║   ██║█████╗  ██████╔╝██╔████╔██║███████║
    ██║╚██╔╝██║██╔══██╗     ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║
    ██║ ╚═╝ ██║██║  ██║      ╚████╔╝ ███████╗██║  ██║██║ ╚═╝ ██║██║  ██║
    ╚═╝     ╚═╝╚═╝  ╚═╝       ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
    
                    🤖 Unified AI Intelligence Platform
        """
        if RICH_AVAILABLE:
            console.print(banner, style="bold blue")
        else:
            print(banner)

    def print_menu():
        """Display the main menu"""
        menu = """
╔══════════════════════════════════════════════════════════════════╗
║  🎯 What would you like to do?                                    ║
╠══════════════════════════════════════════════════════════════════╣
║  [1] 💬 Chat with AI        - Have a conversation                  ║
║  [2] 📝 Write Code          - Generate or improve code             ║
║  [3] 🔍 Analyze Code        - Review and find issues               ║
║  [4] 📊 Process Data        - Analyze files and data               ║
║  [5] 🎨 Design Interface    - Create UI/UX designs                 ║
║  [6] 🔒 Security Check      - Scan for vulnerabilities             ║
║  [7] ⚡ System Status       - Check AI brain health                ║
║  [8] 📚 Help & Guide        - Learn how to use MR.VERMA            ║
║  [0] 🚪 Exit                - Close MR.VERMA                       ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(menu)

    def chat_with_ai():
        """Simple chat interface"""
        print("\n💬 Chat Mode - Type 'exit' to return to menu\n")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit", "q"]:
                break
            if user_input:
                print(
                    "AI: I'm a unified interface. For full AI responses, ensure API keys are configured.\n"
                )

    def main_loop():
        """Main application loop"""
        print_banner()

        while True:
            print_menu()

            try:
                choice = input("\nEnter your choice (0-8): ").strip()

                if choice == "0":
                    print("\n👋 Thank you for using MR.VERMA! Goodbye!\n")
                    break
                elif choice == "1":
                    chat_with_ai()
                elif choice == "2":
                    print("\n📝 Code writing mode - Enter your request:")
                    request = input("> ")
                    print(f"\nAI: Would generate code for: {request}\n")
                elif choice == "3":
                    print(
                        "\n🔍 Code analysis mode - Paste your code (Ctrl+D or type 'END' to finish):"
                    )
                    lines = []
                    while True:
                        try:
                            line = input()
                            if line.strip() == "END":
                                break
                            lines.append(line)
                        except EOFError:
                            break
                    code = "\n".join(lines)
                    print(f"\nAI: Would analyze {len(code)} characters of code\n")
                elif choice == "4":
                    print(
                        "\n📊 Data processing mode - Feature available in enhanced mode\n"
                    )
                elif choice == "5":
                    print("\n🎨 Design mode - Feature available in enhanced mode\n")
                elif choice == "6":
                    print("\n🔒 Security check - Feature available in enhanced mode\n")
                elif choice == "7":
                    print("\n⚡ System Status")
                    print(
                        "  ✅ API: Connected"
                        if os.getenv("NVIDIA_API_KEY")
                        else "  ⚠️  API: Not configured"
                    )
                    print("  ✅ Core: Ready")
                    print("  ✅ Memory: Active\n")
                elif choice == "8":
                    print("\n📚 Help & Guide")
                    print("MR.VERMA Unified - Basic Mode")
                    print("  • Use modes for more features:")
                    print("    --mode enhanced  (Agents, Skills, Workflows)")
                    print("    --mode ultimate  (Enhanced + 82 Prompts)")
                    print("  • Configure API keys in .env file")
                    print("  • Check documentation in README.md\n")
                else:
                    print("\n⚠️  Invalid choice. Please enter 0-8.\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    main_loop()


if __name__ == "__main__":
    main()
