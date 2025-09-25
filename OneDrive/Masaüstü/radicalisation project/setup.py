"""
Setup script for the Digital Radicalization Research Project
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    else:
        print(f"✅ Python version OK: {sys.version}")
        return True

def install_basic_packages():
    """Install basic required packages"""
    basic_packages = [
        "requests",
        "beautifulsoup4", 
        "pyyaml",
        "regex",
        "tqdm"
    ]
    
    optional_packages = [
        "pandas",
        "numpy",
        "langdetect",
        "textblob",
        "geopy",
        "matplotlib",
        "seaborn"
    ]
    
    print("\n📦 Installing basic packages...")
    for package in basic_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
    print("\n📦 Installing optional packages (may fail, but system will still work)...")
    for package in optional_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {package} (optional)")

def create_directories():
    """Create necessary directories"""
    directories = ["data", "output", "logs", "config"]
    
    print("\n📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/")

def run_demo_test():
    """Run a demo test to verify installation"""
    print("\n🧪 Running demo test...")
    try:
        # Run the basic demo
        result = subprocess.run([sys.executable, "demo.py", "--stats"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Demo test passed!")
            print("📊 Keyword statistics loaded successfully")
            return True
        else:
            print("❌ Demo test failed!")
            print("Error output:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Demo test timed out")
        return False
    except Exception as e:
        print(f"❌ Demo test error: {str(e)}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Test the system:")
    print("   python demo.py --full")
    print("\n2. Run keyword analysis:")
    print("   python demo.py --stats")
    print("\n3. Test classifier:")
    print("   python demo.py --classifier")
    print("\n4. Run main demo:")
    print("   python main.py --demo")
    print("\n📚 Documentation:")
    print("   - Read README.md for detailed instructions")
    print("   - Check output/ folder for generated reports")
    print("   - View logs/ folder for system logs")
    print("\n⚠️  Important Notes:")
    print("   - This demo uses simulated data")
    print("   - For real data collection, you'll need API keys")
    print("   - Respect platform terms of service")
    print("   - Use responsibly for research purposes only")

def main():
    """Main setup function"""
    print("🚀 Digital Radicalization Research Project Setup")
    print("="*55)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    create_directories()
    
    # Ask user about package installation
    install_packages = input("\n❓ Install Python packages? (y/n): ").lower().strip()
    if install_packages in ['y', 'yes']:
        install_basic_packages()
    else:
        print("⚠️  Skipping package installation. Some features may not work.")
    
    # Run demo test
    test_demo = input("\n❓ Run demo test? (y/n): ").lower().strip()
    if test_demo in ['y', 'yes']:
        demo_success = run_demo_test()
        if not demo_success:
            print("\n⚠️  Demo test failed, but you can still try running manually")
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        print("Please try running the commands manually")