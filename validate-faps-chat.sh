#!/bin/bash

# FAPS Chat Configuration Validation Script
echo "🔍 Validating FAPS Chat configuration..."

ERRORS=0

# Check required files exist
echo "📁 Checking required files..."
required_files=(
    "docker-compose.yml"
    "Dockerfile" 
    "setup-models.sh"
    "start-faps-chat.sh"
    "FAPS_CHAT_README.md"
    ".env.template"
    "cookbook/examples/streamlit_apps/universal_agent_interface/app.py"
    "cookbook/examples/streamlit_apps/universal_agent_interface/utils.py"
    "cookbook/examples/streamlit_apps/universal_agent_interface/logo_faps.png"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for FAPS branding in app.py
echo ""
echo "🏛️ Checking FAPS branding..."
if grep -q "FAPS Chat" cookbook/examples/streamlit_apps/universal_agent_interface/app.py; then
    echo "  ✅ FAPS Chat title found in app.py"
else
    echo "  ❌ FAPS Chat title not found in app.py"
    ERRORS=$((ERRORS + 1))
fi

# Check for Ollama-only models
echo ""
echo "🤖 Checking model configuration..."
if grep -q "ollama:gpt-oss:20b" cookbook/examples/streamlit_apps/universal_agent_interface/utils.py; then
    echo "  ✅ gpt-oss:20b configured as default"
else
    echo "  ❌ gpt-oss:20b not found as default model"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "anthropic\|openai\|google\|groq" cookbook/examples/streamlit_apps/universal_agent_interface/utils.py; then
    echo "  ⚠️  External model providers still present in utils.py"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ External model providers removed"
fi

# Check Docker Compose configuration
echo ""
echo "🐳 Checking Docker configuration..."
if docker compose config --quiet 2>/dev/null; then
    echo "  ✅ Docker Compose configuration valid"
else
    echo "  ❌ Docker Compose configuration invalid"
    ERRORS=$((ERRORS + 1))
fi

# Check executable scripts
echo ""
echo "🔧 Checking script permissions..."
scripts=("setup-models.sh" "start-faps-chat.sh")
for script in "${scripts[@]}"; do
    if [[ -x "$script" ]]; then
        echo "  ✅ $script is executable"
    else
        echo "  ❌ $script is not executable"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
if [[ $ERRORS -eq 0 ]]; then
    echo "🎉 All checks passed! FAPS Chat is properly configured."
    echo ""
    echo "🚀 To start FAPS Chat:"
    echo "   ./start-faps-chat.sh"
    echo ""
    echo "📖 See FAPS_CHAT_README.md for full documentation."
else
    echo "❌ Found $ERRORS configuration issues. Please fix them before deployment."
    exit 1
fi