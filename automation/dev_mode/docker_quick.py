"""
automation/dev_mode/docker_quick.py
Quick Docker commands for development
"""
import subprocess
from pathlib import Path
from typing import Optional
from automation.dev_mode._base import DevModeCommand


class DockerQuickCommand(DevModeCommand):
    """Command for quick Docker operations"""
    
    label = "Docker Quick Commands"
    description = "Common Docker operations for development"
    
    def run(self, interactive: bool = True, **kwargs) -> any:
        """Execute Docker command"""
        if interactive:
            return self._interactive_docker()
        else:
            return self._noninteractive_docker(**kwargs)
    
    def _interactive_docker(self):
        """Interactive Docker operations"""
        print("\n" + "="*70)
        print("🐳 DOCKER QUICK COMMANDS")
        print("="*70 + "\n")
        
        # Check if Docker is installed
        if not self.validate_binary('docker'):
            self.show_missing_binary_error(
                'docker',
                'https://www.docker.com/get-started'
            )
            input("\nPress Enter to continue...")
            return
        
        # Check if Docker is running
        if not self._is_docker_running():
            print("⚠️  Docker daemon is not running")
            print("💡 Start Docker Desktop or run: sudo systemctl start docker")
            input("\nPress Enter to continue...")
            return
        
        # Show Docker operations menu
        print("Docker Operations:")
        print("  1. Build Image")
        print("  2. Run Container")
        print("  3. Stop Container")
        print("  4. List Running Containers")
        print("  5. List All Containers")
        print("  6. List Images")
        print("  7. Prune Unused Resources")
        print("  8. Cancel")
        
        choice = input("\nYour choice (1-8): ").strip()
        
        if choice == '1':
            self._build_image()
        elif choice == '2':
            self._run_container()
        elif choice == '3':
            self._stop_container()
        elif choice == '4':
            self._list_containers(all_containers=False)
        elif choice == '5':
            self._list_containers(all_containers=True)
        elif choice == '6':
            self._list_images()
        elif choice == '7':
            self._prune_resources()
        elif choice == '8':
            print("\n❌ Operation cancelled")
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")
    
    def _noninteractive_docker(self, operation: str, **kwargs):
        """Non-interactive Docker operations"""
        operations = {
            'build': self._build_image,
            'run': self._run_container,
            'stop': self._stop_container,
            'list': self._list_containers,
            'prune': self._prune_resources
        }
        
        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")
        
        operations[operation](interactive=False, **kwargs)
    
    def _is_docker_running(self) -> bool:
        """Check if Docker daemon is running"""
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _build_image(self, interactive: bool = True, **kwargs):
        """Build Docker image"""
        print("\n🔨 BUILD DOCKER IMAGE")
        print("="*70 + "\n")
        
        if interactive:
            # Get image name
            image_name = input("Image name (e.g., myapp:latest): ").strip()
            if not image_name:
                print("❌ Image name cannot be empty")
                return
            
            # Get Dockerfile path
            dockerfile = input("Dockerfile path (default: ./Dockerfile): ").strip() or 'Dockerfile'
            
            # Get build context
            context = input("Build context (default: .): ").strip() or '.'
        else:
            image_name = kwargs.get('image_name')
            dockerfile = kwargs.get('dockerfile', 'Dockerfile')
            context = kwargs.get('context', '.')
            
            if not image_name:
                raise ValueError("image_name is required")
        
        # Check if Dockerfile exists
        dockerfile_path = Path(context) / dockerfile
        if not dockerfile_path.exists():
            print(f"❌ Dockerfile not found: {dockerfile_path}")
            return
        
        # Build command
        cmd = ['docker', 'build', '-t', image_name, '-f', dockerfile, context]
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            subprocess.run(cmd, check=True)
            print(f"\n✅ Image '{image_name}' built successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Build failed with exit code {e.returncode}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _run_container(self, interactive: bool = True, **kwargs):
        """Run Docker container"""
        print("\n▶️  RUN DOCKER CONTAINER")
        print("="*70 + "\n")
        
        if interactive:
            # Get image name
            image_name = input("Image name: ").strip()
            if not image_name:
                print("❌ Image name cannot be empty")
                return
            
            # Get container name
            container_name = input("Container name (optional): ").strip()
            
            # Port mapping
            port_map = input("Port mapping (e.g., 8080:80, optional): ").strip()
            
            # Run mode
            print("\nRun mode:")
            print("  1. Detached (background)")
            print("  2. Interactive (foreground)")
            mode_choice = input("Your choice (1-2, default: 1): ").strip() or '1'
            detached = (mode_choice == '1')
        else:
            image_name = kwargs.get('image_name')
            container_name = kwargs.get('container_name', '')
            port_map = kwargs.get('port_map', '')
            detached = kwargs.get('detached', True)
            
            if not image_name:
                raise ValueError("image_name is required")
        
        # Build command
        cmd = ['docker', 'run']
        
        if detached:
            cmd.append('-d')
        else:
            cmd.extend(['-it'])
        
        if container_name:
            cmd.extend(['--name', container_name])
        
        if port_map:
            cmd.extend(['-p', port_map])
        
        cmd.append(image_name)
        
        print(f"$ {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if detached:
                container_id = result.stdout.strip()[:12]
                print(f"✅ Container started: {container_id}")
                if port_map:
                    host_port = port_map.split(':')[0]
                    print(f"🌐 Access at: http://localhost:{host_port}")
            else:
                print("✅ Container stopped")
        
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to run container: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _stop_container(self, interactive: bool = True, **kwargs):
        """Stop Docker container"""
        print("\n🛑 STOP DOCKER CONTAINER")
        print("="*70 + "\n")
        
        # List running containers
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.ID}}\t{{.Names}}\t{{.Image}}'],
                capture_output=True,
                text=True,
                check=True
            )
            
            containers = result.stdout.strip().split('\n')
            containers = [c for c in containers if c]
            
            if not containers:
                print("ℹ️  No running containers")
                return
            
            if interactive:
                print("Running Containers:")
                for i, container in enumerate(containers, 1):
                    print(f"  {i}. {container}")
                
                choice = input(f"\nSelect container to stop (1-{len(containers)}): ").strip()
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(containers):
                        container_info = containers[choice_num - 1].split('\t')
                        container_id = container_info[0]
                    else:
                        print("❌ Invalid choice")
                        return
                except ValueError:
                    print("❌ Invalid input")
                    return
            else:
                container_id = kwargs.get('container_id')
                if not container_id:
                    raise ValueError("container_id is required")
            
            # Stop container
            cmd = ['docker', 'stop', container_id]
            print(f"\n$ {' '.join(cmd)}\n")
            
            subprocess.run(cmd, check=True)
            print(f"✅ Container {container_id} stopped")
        
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to stop container: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _list_containers(self, interactive: bool = True, all_containers: bool = False):
        """List Docker containers"""
        print("\n📋 DOCKER CONTAINERS")
        print("="*70 + "\n")
        
        cmd = ['docker', 'ps']
        if all_containers:
            cmd.append('-a')
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to list containers: {e}")
    
    def _list_images(self):
        """List Docker images"""
        print("\n📋 DOCKER IMAGES")
        print("="*70 + "\n")
        
        try:
            subprocess.run(['docker', 'images'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to list images: {e}")
    
    def _prune_resources(self, interactive: bool = True):
        """Prune unused Docker resources"""
        print("\n🧹 PRUNE UNUSED RESOURCES")
        print("="*70 + "\n")
        
        print("⚠️  This will remove:")
        print("  • All stopped containers")
        print("  • All unused networks")
        print("  • All dangling images")
        print("  • All build cache")
        
        if interactive:
            confirm = input("\nProceed? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("❌ Operation cancelled")
                return
        
        print("\n🔨 Pruning resources...\n")
        
        try:
            subprocess.run(['docker', 'system', 'prune', '-f'], check=True)
            print("\n✅ Resources pruned successfully!")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Prune failed: {e}")


# Export command instance
COMMAND = DockerQuickCommand()  