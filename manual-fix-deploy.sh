#!/bin/bash
# Manual fix for immediate deployment

echo "🔧 Deploying Gemini fix manually..."

# Start container without the broken file first
docker run -d --name utility-backend-temp \
  --network utility-server_utility-network \
  -p 8000:8000 \
  -e GEMINI_API_KEY=AIzaSyAesIpOllwdwj6PbHMcE3gi2TA6wWXWO6I \
  -e USE_GEMINI_API=true \
  -e GEMINI_MODEL=gemini-2.5-flash \
  -e DB_USER=utility_user \
  -e DB_PASSWORD=d6cedf9e7d73d9c63ca5e4deab86e18d \
  -e DB_NAME=utility_db \
  -e DB_PORT=5432 \
  -e SECRET_KEY=your-secret-key-here-change-in-production \
  -e ENVIRONMENT=production \
  ghcr.io/ericphan28/thang-phan-tools-backend:latest

echo "Container started, now applying fix..."

# Create the corrected file
cat > /tmp/gemini_service_fixed.py << 'EOF'
# Apply the fix for hasattr(genai, 'upload_file') check
import re

# Read the file
with open('/app/app/services/gemini_service.py', 'r') as f:
    content = f.read()

# Fix 1: Add hasattr check
old_upload = 'uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")'
new_upload = '''# Check if upload_file is available (newer versions)
            if hasattr(genai, 'upload_file'):
                print("📤 Using genai.upload_file() method (recommended)", flush=True)  
                uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")'''

if old_upload in content:
    content = content.replace(old_upload, new_upload)

# Fix 2: Add base64 fallback
base64_fallback = '''            else:
                # Fallback for older versions: use base64 encoding
                print("📤 Using base64 fallback method (older library version)", flush=True)
                import base64
                
                # Read PDF and encode to base64
                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                    pdf_base64 = base64.b64encode(pdf_bytes).decode()
                
                print(f"📄 PDF encoded: {len(pdf_base64)} characters", flush=True)
                
                # Create content with inline data
                model_obj = genai.GenerativeModel(model)
                print(f"🤖 Model created: {model}", flush=True)
                
                print(f"💬 Sending prompt + PDF (base64) to Gemini...", flush=True)
                response = model_obj.generate_content([
                    prompt,
                    {
                        "mime_type": "application/pdf", 
                        "data": pdf_base64
                    }
                ], **kwargs)'''

# Insert after the upload_file part
marker = 'print(f"✅ File uploaded to Gemini: {uploaded_file.name}", flush=True)'
if marker in content:
    content = content.replace(marker, marker + '\n' + base64_fallback)

# Write the corrected file
with open('/app/app/services/gemini_service.py', 'w') as f:
    f.write(content)

print("✅ Gemini service fixed!")
EOF

# Apply the fix
docker exec utility-backend-temp python3 /tmp/gemini_service_fixed.py

# Test if fix worked
echo "🧪 Testing fix..."
docker exec utility-backend-temp python3 -c "print('Testing import...'); import app.services.gemini_service; print('✅ Import successful')"

if [ $? -eq 0 ]; then
    echo "✅ Fix successful! Promoting to production..."
    docker stop utility-backend-prod 2>/dev/null || true
    docker rm utility-backend-prod 2>/dev/null || true
    docker rename utility-backend-temp utility-backend-prod
    docker restart utility-backend-prod
    echo "🎉 Deployment complete!"
else
    echo "❌ Fix failed, cleaning up..."
    docker rm -f utility-backend-temp
fi