#!/bin/bash

# Landing Page Generator - Setup Script
# This script helps you set up the landing page generator quickly

echo "🚀 Landing Page Generator - Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Install requirements
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 No .env file found. Let's create one!"
    echo ""

    # Copy example
    cp .env.example .env

    # Prompt for API keys
    read -p "Enter your Anthropic API key (required): " ANTHROPIC_KEY
    read -p "Enter your OpenAI API key (required): " OPENAI_KEY
    read -p "Enter your Netlify token (optional, press Enter to skip): " NETLIFY_TOKEN
    read -p "Enter your Airtable API key (optional, press Enter to skip): " AIRTABLE_KEY

    # Write to .env
    echo "ANTHROPIC_API_KEY=$ANTHROPIC_KEY" > .env
    echo "OPENAI_API_KEY=$OPENAI_KEY" >> .env

    if [ ! -z "$NETLIFY_TOKEN" ]; then
        echo "NETLIFY_TOKEN=$NETLIFY_TOKEN" >> .env
    fi

    if [ ! -z "$AIRTABLE_KEY" ]; then
        echo "AIRTABLE_API_KEY=$AIRTABLE_KEY" >> .env
        read -p "Enter your Airtable Base ID: " AIRTABLE_BASE
        echo "AIRTABLE_BASE_ID=$AIRTABLE_BASE" >> .env
    fi

    echo "✅ .env file created!"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "=========================================="
echo "🎉 Setup complete!"
echo ""
echo "To start the app, run:"
echo "  streamlit run app.py"
echo ""
echo "The app will open at http://localhost:8501"
echo ""
echo "For deployment instructions, see DEPLOYMENT.md"
echo "=========================================="
