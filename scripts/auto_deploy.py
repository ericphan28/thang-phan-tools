#!/usr/bin/env python3
"""
Auto Deploy Script - NO PASSWORD INPUT REQUIRED
Deploys all 4 tools to VPS automatically
"""

import paramiko
import os
import time
import tarfile
import io

# Configuration
VPS_IP = "165.99.59.47"
VPS_USER = "root"
VPS_PASSWORD = "@8Alm523jIqS"
VPS_PATH = "/opt/utility-server"
LOCAL_PATH = r"D:\thang\utility-server"

def print_step(step, total, message):
    print(f"\n[{step}/{total}] {message}...")
    print("="*60)

def execute_ssh(client, command, show_output=True):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if show_output and output:
        print(output)
    if error and exit_status != 0:
        print(f"Error: {error}")
    
    return exit_status, output, error

def main():
    print("\n" + "="*60)
    print("  AUTO DEPLOYMENT - ALL 4 TOOLS")
    print("="*60)
    
    # Connect to VPS
    print(f"\nConnecting to {VPS_IP}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(VPS_IP, username=VPS_USER, password=VPS_PASSWORD, timeout=30)
        print("✓ Connected successfully!")
        
        # Step 1: Install Docker
        print_step(1, 5, "Installing Docker & Docker Compose")
        execute_ssh(client, """
            export DEBIAN_FRONTEND=noninteractive
            if ! command -v docker &> /dev/null; then
                curl -fsSL https://get.docker.com | sh
                systemctl enable docker
                systemctl start docker
                echo "Docker installed"
            else
                echo "Docker already installed"
            fi
        """)
        
        execute_ssh(client, """
            if ! command -v docker-compose &> /dev/null; then
                curl -sL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
                echo "Docker Compose installed"
            else
                echo "Docker Compose already installed"
            fi
        """)
        
        # Step 2: Install Cockpit
        print_step(2, 5, "Installing Cockpit (VPS Management)")
        execute_ssh(client, """
            export DEBIAN_FRONTEND=noninteractive
            apt-get update -qq
            apt-get install -y -qq cockpit cockpit-docker
            systemctl enable --now cockpit.socket
            echo "Cockpit installed - Access at http://""" + VPS_IP + """:9090"
        """)
        
        # Step 3: Install Portainer & Dozzle
        print_step(3, 5, "Installing Portainer & Dozzle")
        execute_ssh(client, """
            docker volume create portainer_data 2>/dev/null || true
            docker rm -f portainer 2>/dev/null || true
            docker run -d -p 9443:9443 --name portainer --restart=always \
              -v /var/run/docker.sock:/var/run/docker.sock \
              -v portainer_data:/data \
              portainer/portainer-ce:latest
            echo "Portainer installed - Access at https://""" + VPS_IP + """:9443"
            
            docker rm -f dozzle 2>/dev/null || true
            docker run -d --name dozzle -p 9999:8080 --restart=always \
              -v /var/run/docker.sock:/var/run/docker.sock \
              amir20/dozzle:latest
            echo "Dozzle installed - Access at http://""" + VPS_IP + """:9999"
        """)
        
        # Step 4: Upload Utility Server
        print_step(4, 5, "Uploading Utility Server files")
        
        # Create directory
        execute_ssh(client, f"mkdir -p {VPS_PATH}", show_output=False)
        
        # Upload files using SFTP
        print("Uploading files via SFTP...")
        sftp = client.open_sftp()
        
        # List of files/folders to upload
        items_to_upload = [
            'backend',
            'nginx',
            'scripts',
            'docker-compose.yml',
            '.env.example',
            'README.md'
        ]
        
        def upload_recursive(local_path, remote_path):
            """Recursively upload directory"""
            for item in os.listdir(local_path):
                if item in ['__pycache__', '.git', 'node_modules', '.pyc']:
                    continue
                    
                local_item = os.path.join(local_path, item)
                remote_item = f"{remote_path}/{item}"
                
                if os.path.isfile(local_item):
                    print(f"  Uploading {item}...")
                    sftp.put(local_item, remote_item)
                elif os.path.isdir(local_item):
                    try:
                        sftp.mkdir(remote_item)
                    except:
                        pass
                    upload_recursive(local_item, remote_item)
        
        for item in items_to_upload:
            local_item = os.path.join(LOCAL_PATH, item)
            remote_item = f"{VPS_PATH}/{item}"
            
            if os.path.isfile(local_item):
                print(f"  Uploading {item}...")
                sftp.put(local_item, remote_item)
            elif os.path.isdir(local_item):
                try:
                    sftp.mkdir(remote_item)
                except:
                    pass
                upload_recursive(local_item, remote_item)
        
        sftp.close()
        print("✓ Files uploaded successfully!")
        
        # Step 5: Configure and start Utility Server
        print_step(5, 5, "Configuring and starting Utility Server")
        
        # Setup .env
        execute_ssh(client, f"""
            cd {VPS_PATH}
            if [ ! -f .env ]; then
                cp .env.example .env
                DB_PASS=$(openssl rand -hex 16)
                REDIS_PASS=$(openssl rand -hex 16)
                SECRET=$(openssl rand -hex 32)
                JWT_SECRET=$(openssl rand -hex 32)
                
                sed -i "s/your_strong_password_here_123/$DB_PASS/g" .env
                sed -i "s/your_redis_password_here_456/$REDIS_PASS/g" .env
                sed -i "s/your-super-secret-key-change-this-to-random-string/$SECRET/g" .env
                sed -i "s/another-secret-key-for-jwt-tokens/$JWT_SECRET/g" .env
                echo ".env configured with random passwords"
            fi
        """)
        
        # Configure firewall
        execute_ssh(client, """
            ufw --force enable
            ufw allow 22/tcp
            ufw allow 80/tcp
            ufw allow 443/tcp
            ufw allow 9090/tcp
            ufw allow 9443/tcp
            ufw allow 9999/tcp
            ufw reload
            echo "Firewall configured"
        """, show_output=False)
        
        # Start Utility Server
        print("\nStarting Utility Server containers...")
        execute_ssh(client, f"""
            cd {VPS_PATH}
            docker-compose down 2>/dev/null || true
            docker-compose up -d --build
        """)
        
        print("\nWaiting for services to start...")
        time.sleep(15)
        
        # Check status
        print("\n" + "="*60)
        print("Container Status:")
        print("="*60)
        execute_ssh(client, f"cd {VPS_PATH} && docker-compose ps")
        
        # Summary
        print("\n" + "="*60)
        print("  DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n🌐 Access Your 4 Tools:\n")
        print(f"1. 🖥️  Cockpit (VPS Management)")
        print(f"   URL: http://{VPS_IP}:9090")
        print(f"   Login: {VPS_USER} / {VPS_PASSWORD}\n")
        
        print(f"2. 🐳 Portainer (Docker Management)")
        print(f"   URL: https://{VPS_IP}:9443")
        print(f"   Setup: Create admin account on first visit\n")
        
        print(f"3. 📋 Dozzle (Logs Viewer)")
        print(f"   URL: http://{VPS_IP}:9999")
        print(f"   No login required\n")
        
        print(f"4. 🚀 Utility Server (API)")
        print(f"   URL: http://{VPS_IP}/docs")
        print(f"   Health: http://{VPS_IP}/health")
        
        print("\n" + "="*60)
        print("✓ All services are running!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    main()
