#!/bin/bash
# Quick Setup Script for YouTube Islamic Stories Automation

echo "=================================================="
echo "YouTube Islamic Stories Automation - Quick Setup"
echo "=================================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
}

# Check FFmpeg
echo "📋 Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg is installed"
else
    echo "⚠️  FFmpeg not found"
    echo "   Install with: brew install ffmpeg"
    read -p "Install FFmpeg now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install ffmpeg
    fi
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt || {
    echo "❌ Failed to install dependencies"
    exit 1
}

echo "✅ Dependencies installed"

# Create .env file if doesn't exist
echo ""
if [ ! -f "config/.env" ]; then
    echo "📝 Creating .env file..."
    cp config/.env.example config/.env
    echo "✅ Created config/.env"
    echo ""
    echo "⚠️  IMPORTANT: Edit config/.env and add your API keys!"
    echo "   Required keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - GOOGLE_APPLICATION_CREDENTIALS"
    echo "   - YOUTUBE_CLIENT_SECRETS"
    echo "   - PEXELS_API_KEY"
else
    echo "✅ config/.env already exists"
fi

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit config/.env with your API keys"
echo "2. Get API credentials (see README.md for links)"
echo "3. Test the system: python main.py --dry-run"
echo "4. Create your first video: python main.py"
echo ""
echo "For detailed setup instructions, see README.md"
echo "For usage examples, see the walkthrough artifact"
echo ""
