import os
from pathlib import Path

def create_structure():
    # Define the root directory
    root = Path("procode_bot")

    # Define the folder structure
    folders = [
        root / "backend" / "venv",
        root / "backend" / "scripts",
        root / "backend" / "uploads",  # Added for temporary file storage (Images/PDFs)
        root / "backend" / "app" / "prompts",
        root / "backend" / "app" / "tools",
        root / "frontend" / "assets",
    ]

    # Define the files to create
    files = [
        # Backend Root
        root / "backend" / ".env",
        root / "backend" / ".gitignore",
        root / "backend" / "Dockerfile",
        root / "backend" / "requirements.txt",
        
        # Backend Scripts
        root / "backend" / "scripts" / "ingest.py",

        # Backend App
        root / "backend" / "app" / "__init__.py",
        root / "backend" / "app" / "config.py",
        root / "backend" / "app" / "server.py",
        root / "backend" / "app" / "agent.py",
        root / "backend" / "app" / "state.py",

        # Backend Prompts
        root / "backend" / "app" / "prompts" / "system.md",

        # Backend Tools
        root / "backend" / "app" / "tools" / "__init__.py",
        root / "backend" / "app" / "tools" / "pricing.py",
        root / "backend" / "app" / "tools" / "pdf_gen.py",
        root / "backend" / "app" / "tools" / "emailer.py",
        root / "backend" / "app" / "tools" / "rag.py",

        # Frontend
        root / "frontend" / "app.py",
        root / "frontend" / "requirements.txt",
    ]

    print(f"🚀 Creating project structure at: {root.absolute()}...\n")

    # Create Directories
    for folder in folders:
        try:
            folder.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {folder}")
        except Exception as e:
            print(f"❌ Error creating directory {folder}: {e}")

    # Create Files
    for file_path in files:
        try:
            if not file_path.exists():
                file_path.touch()
                print(f"📄 Created file: {file_path}")
            else:
                print(f"⚠️  File already exists: {file_path}")
        except Exception as e:
            print(f"❌ Error creating file {file_path}: {e}")

    print("\n✨ Project structure created successfully!")
    print("👉 You can now delete this script and proceed to Phase 1.")

if __name__ == "__main__":
    create_structure()