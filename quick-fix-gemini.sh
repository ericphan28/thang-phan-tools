#!/bin/bash
# Quick fix script for Gemini upload_file compatibility

echo "🔧 Applying Gemini compatibility fix..."

# Find running backend container
CONTAINER=$(docker ps --filter "name=utility-backend" --format "{{.Names}}" | head -1)

if [ -z "$CONTAINER" ]; then
    echo "❌ No backend container found"
    exit 1
fi

echo "📦 Found container: $CONTAINER"

# Create the patch
cat > /tmp/gemini_fix.py << 'EOF'
# Quick fix for generate_content_with_pdf method
import re

# Read current file
with open('/app/app/services/gemini_service.py', 'r') as f:
    content = f.read()

# Replace the problematic upload_file call
old_pattern = r'uploaded_file = genai\.upload_file\(pdf_path, mime_type="application/pdf"\)'
new_pattern = '''# Check if upload_file is available (newer versions)
            if hasattr(genai, 'upload_file'):
                print("📤 Using genai.upload_file() method (recommended)", flush=True)
                uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
            else:
                print("📤 Using base64 fallback method (older library version)", flush=True)
                import base64
                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                    pdf_base64 = base64.b64encode(pdf_bytes).decode()
                print(f"📄 PDF encoded: {len(pdf_base64)} characters", flush=True)'''

if old_pattern in content:
    content = re.sub(old_pattern, new_pattern, content)
    print("✅ Pattern replaced successfully")
    
    # Write back
    with open('/app/app/services/gemini_service.py', 'w') as f:
        f.write(content)
    print("✅ File updated")
else:
    print("❌ Pattern not found - file may already be patched")
EOF

# Apply the fix inside container
docker exec $CONTAINER python3 /tmp/gemini_fix.py

echo "🔄 Restarting container..."
docker restart $CONTAINER

echo "✅ Fix applied! Testing..."
sleep 5
docker logs $CONTAINER --tail 10