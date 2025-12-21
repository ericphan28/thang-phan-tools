#!/usr/bin/env python3
"""
Auto Deploy - No Manual Password Input Required
Deploys all 4 tools to VPS automatically
"""

import paramiko
import os
import sys
from pathlib import Path
import time

# VPS Configuration
VPS_IP = "165.99.59.47"
VPS_USER = "root"
VPS_PASSWORD = "@8Alm523jIqS"
VPS_PATH = "/opt/utility-server"
LOCAL_PATH = r"D:\Thang\thang-phan-tools"

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_step(step, total, text):
    print(f"[{step}/{total}] {text}...")

def connect_ssh():
    """Create SSH connection"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(VPS_IP, username=VPS_USER, password=VPS_PASSWORD, timeout=30)
        return client
    except Exception as e:
        print(f"Error connecting to VPS: {e}")
        sys.exit(1)

def execute_command(client, command, show_output=True):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    if show_output and output:
        print(output)
    if error and exit_status != 0:
        print(f"Error: {error}")
    
    return output, error, exit_status

def setup_ssh_key(client):
    """Setup SSH key for passwordless access"""
    print_step(1, 5, "Setting up SSH key for passwordless access")
    
    # Check if SSH key exists locally
    ssh_key_path = Path.home() / ".ssh" / "id_rsa.pub"
    
    if not ssh_key_path.exists():
        print("  Generating SSH key...")
        os.system('ssh-keygen -t rsa -b 4096 -f "%USERPROFILE%\\.ssh\\id_rsa" -N ""')
    
    # Read public key
    with open(ssh_key_path, 'r') as f:
        public_key = f.read().strip()
    
    # Install public key on VPS
    commands = [
        "mkdir -p ~/.ssh",
        "chmod 700 ~/.ssh",
        f"echo '{public_key}' >> ~/.ssh/authorized_keys",
        "chmod 600 ~/.ssh/authorized_keys",
        "sort -u ~/.ssh/authorized_keys -o ~/.ssh/authorized_keys"
    ]
    
    for cmd in commands:
        execute_command(client, cmd, show_output=False)
    
    print("  ✓ SSH key installed!")

def install_management_tools(client):
    """Install Docker, Cockpit, Portainer, and Dozzle"""
    print_step(2, 5, "Installing management tools (Docker, Cockpit, Portainer, Dozzle)")
    
    install_script = """
export DEBIAN_FRONTEND=noninteractive
set -e

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "  Installing Docker..."
    curl -fsSL https://get.docker.com | sh > /dev/null 2>&1
    systemctl enable docker > /dev/null 2>&1
    systemctl start docker
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "  Installing Docker Compose..."
    curl -sL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Install Cockpit
echo "  Installing Cockpit..."
apt-get update -qq > /dev/null 2>&1
apt-get install -y -qq cockpit cockpit-docker cockpit-packagekit > /dev/null 2>&1
systemctl enable --now cockpit.socket > /dev/null 2>&1

# Install Portainer
echo "  Installing Portainer..."
docker volume create portainer_data > /dev/null 2>&1
docker rm -f portainer > /dev/null 2>&1 || true
docker run -d -p 9443:9443 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest > /dev/null 2>&1

# Install Dozzle
echo "  Installing Dozzle..."
docker rm -f dozzle > /dev/null 2>&1 || true
docker run -d --name dozzle -p 9999:8080 --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  amir20/dozzle:latest > /dev/null 2>&1

# Configure Firewall
echo "  Configuring firewall..."
ufw --force enable > /dev/null 2>&1
ufw allow 22/tcp > /dev/null 2>&1
ufw allow 80/tcp > /dev/null 2>&1
ufw allow 443/tcp > /dev/null 2>&1
ufw allow 9090/tcp > /dev/null 2>&1
ufw allow 9443/tcp > /dev/null 2>&1
ufw allow 9999/tcp > /dev/null 2>&1
ufw reload > /dev/null 2>&1

echo "  ✓ Management tools installed!"
"""
    
    output, error, status = execute_command(client, install_script)
    print(output)

def upload_project_files(client):
    """Upload project files to VPS"""
    print_step(3, 5, "Uploading project files")
    
    # Create directory
    execute_command(client, f"mkdir -p {VPS_PATH}", show_output=False)
    
    # Use SFTP to upload files
    sftp = client.open_sftp()
    
    def upload_directory(local_dir, remote_dir):
        """Recursively upload directory"""
        for item in os.listdir(local_dir):
            local_path = os.path.join(local_dir, item)
            remote_path = f"{remote_dir}/{item}"
            
            # Skip unnecessary files
            if item in ['.git', '__pycache__', 'node_modules', '.pyc', 'venv', 'env']:
                continue
            
            if os.path.isfile(local_path):
                print(f"  Uploading {item}...")
                try:
                    sftp.put(local_path, remote_path)
                except:
                    pass
            elif os.path.isdir(local_path):
                try:
                    sftp.mkdir(remote_path)
                except:
                    pass
                upload_directory(local_path, remote_path)
    
    print("  Uploading files (this may take a minute)...")
    upload_directory(LOCAL_PATH, VPS_PATH)
    sftp.close()
    
    print("  ✓ Files uploaded successfully!")

def configure_env(client):
    """Configure .env file with random passwords"""
    print_step(4, 5, "Configuring environment variables")
    
    config_script = f"""
cd {VPS_PATH}
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Generate random passwords
DB_PASS=$(openssl rand -hex 16)
REDIS_PASS=$(openssl rand -hex 16)
SECRET=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# Update .env file
sed -i "s/your_strong_password_here_123/$DB_PASS/g" .env
sed -i "s/your_redis_password_here_456/$REDIS_PASS/g" .env
sed -i "s/your-super-secret-key-change-this-to-random-string/$SECRET/g" .env
sed -i "s/another-secret-key-for-jwt-tokens/$JWT_SECRET/g" .env

echo "  ✓ .env configured with random passwords"
"""
    
    output, _, _ = execute_command(client, config_script)
    print(output)

def deploy_utility_server(client):
    """Deploy Utility Server with docker-compose"""
    print_step(5, 5, "Deploying Utility Server")
    
    deploy_script = f"""
cd {VPS_PATH}
echo "  Building frontend..."
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..
echo "  Building containers with cache..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
docker-compose build --build-arg BUILDKIT_INLINE_CACHE=1
echo "  Starting containers..."
docker-compose down 2>/dev/null || true
docker-compose up -d
echo "  Waiting for containers to start..."
sleep 15
echo ""
echo "  ✓ Utility Server deployed!"
echo ""
docker-compose ps
"""
    
    output, _, _ = execute_command(client, deploy_script)
    print(output)

def verify_deployment(client):
    """Verify all services are running"""
    print("\nVerifying deployment...")
    
    # Check services
    output, _, _ = execute_command(client, "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
    print(output)
    
    # Check Cockpit
    output, _, _ = execute_command(client, "systemctl is-active cockpit")
    print(f"Cockpit: {output.strip()}")

def main():
    print_header("AUTO DEPLOYMENT - NO MANUAL INPUT")
    print("Deploying 4 tools to VPS:")
    print("  1. Cockpit (VPS Management)")
    print("  2. Portainer (Docker Management)")
    print("  3. Dozzle (Logs Viewer)")
    print("  4. Utility Server (Your API)")
    
    try:
        # Connect to VPS
        print("\nConnecting to VPS...")
        client = connect_ssh()
        print("✓ Connected!")
        
        # Execute deployment steps
        setup_ssh_key(client)
        install_management_tools(client)
        upload_project_files(client)
        configure_env(client)
        deploy_utility_server(client)
        verify_deployment(client)
        
        # Success message
        print_header("DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("Access your services:\n")
        print(f"1. Cockpit (VPS Management)")
        print(f"   → http://{VPS_IP}:9090")
        print(f"   Login: root / @8Alm523jIqS\n")
        
        print(f"2. Portainer (Docker Management)")
        print(f"   → https://{VPS_IP}:9443")
        print(f"   Setup admin account on first visit\n")
        
        print(f"3. Dozzle (Logs Viewer)")
        print(f"   → http://{VPS_IP}:9999")
        print(f"   No login required\n")
        
        print(f"4. Utility Server (API)")
        print(f"   → http://{VPS_IP}/docs")
        print(f"   → http://{VPS_IP}/health\n")
        
        print("=" * 60)
        
        # Close connection
        client.close()
        
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
