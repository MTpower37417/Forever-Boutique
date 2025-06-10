import os
import shutil
from pathlib import Path
import json
import re

def create_directory_structure():
    """Create the new directory structure."""
    directories = [
        'core/ui',
        'core/handlers',
        'core/feature_flags',
        'utils',
        'config',
        'data',
        'logs',
        'customer_data',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py in each directory
        init_file = Path(directory) / '__init__.py'
        if not init_file.exists():
            init_file.touch()

def move_files():
    """Move files to their appropriate directories."""
    moves = {
        # UI files
        'core/menu_ui.py': 'core/ui/',
        'core/main_menu_ui.py': 'core/ui/',
        
        # Handler files
        'core/product_handler.py': 'core/handlers/',
        'core/booking_handler.py': 'core/handlers/',
        'core/size_handler.py': 'core/handlers/',
        'core/faq_handler.py': 'core/handlers/',
        'core/store_info_handler.py': 'core/handlers/',
        'core/customer_follow_up.py': 'core/handlers/',
        'core/insight_handler.py': 'core/handlers/',
        'core/set_time_action.py': 'core/handlers/',
        'core/help_handler.py': 'core/handlers/',
        'core/customer_response_handler.py': 'core/handlers/',
        'core/ai_combined_reply_handler.py': 'core/handlers/',
        'core/admin_toggle_handler.py': 'core/handlers/',
        
        # Config files
        'core/path_config.py': 'config/',
        'config.env': 'config/',
        'schedule_config.json': 'config/',
        
        # Data files
        'data/products.json': 'data/',
        'data/faqs.json': 'data/',
        'data/store_info.json': 'data/',
        'data/size_guide.json': 'data/',
        'data/customers.json': 'data/',
        'data/last_follow_up.json': 'data/',
        'data/follow_up_logs.csv': 'data/',
        'data/customer_messages.json': 'data/',
        'data/answered_messages.json': 'data/',
        'data/response_cache.json': 'data/',
        
        # Log files
        'log.txt': 'logs/',
        'bot_log.txt': 'logs/'
    }
    
    for src, dest in moves.items():
        src_path = Path(src)
        dest_path = Path(dest)
        if src_path.exists():
            shutil.move(str(src_path), str(dest_path / src_path.name))

def merge_duplicate_files():
    """Merge duplicate configuration files."""
    # Merge path_config.py
    root_path_config = Path('path_config.py')
    core_path_config = Path('core/path_config.py')
    if root_path_config.exists() and core_path_config.exists():
        # Keep the more recent version
        if root_path_config.stat().st_mtime > core_path_config.stat().st_mtime:
            shutil.copy(str(root_path_config), 'config/path_config.py')
        else:
            shutil.copy(str(core_path_config), 'config/path_config.py')
        root_path_config.unlink()
        core_path_config.unlink()

def cleanup_empty_directories():
    """Remove empty directories."""
    for root, dirs, files in os.walk('.', topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            if not any(dir_path.iterdir()):
                dir_path.rmdir()

def main():
    """Main function to reorganize the project."""
    print("Starting project reorganization...")
    
    # Create new directory structure
    create_directory_structure()
    print("✅ Created directory structure")
    
    # Move files to appropriate locations
    move_files()
    print("✅ Moved files to appropriate directories")
    
    # Merge duplicate files
    merge_duplicate_files()
    print("✅ Merged duplicate files")
    
    # Clean up empty directories
    cleanup_empty_directories()
    print("✅ Cleaned up empty directories")
    
    print("Project reorganization completed!")

if __name__ == "__main__":
    main()

# 1. Create folders for organization (if they don't exist)
folders_to_create = [
    'scripts', 
    'config', 
    'data',
    'logs',
    'utils',
    'handlers',
    'templates',
    'tests'
]

for folder in folders_to_create:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")

# 2. Move files by type
file_mappings = {
    r'.*\.sh$': 'scripts',
    r'.*\.bat$': 'scripts',
    r'.*config.*\.json$': 'config',
    r'.*\.env$': 'config',
    r'.*_cache_utils\.py$': 'utils',
    r'.*utils\.py$': 'utils',
    r'.*customer.*\.json$': 'data',
    r'.*follow_up.*\.json$': 'data',
    r'.*_handler\.py$': 'handlers',
    r'.*\.log$': 'logs',
}

# Find duplicate JSON files
json_files = {}
for root, dirs, files in os.walk('.'):
    if './venv' in root or './__pycache__' in root:
        continue
    
    for file in files:
        if file.endswith('.json'):
            full_path = os.path.join(root, file)
            base_name = file
            
            if base_name not in json_files:
                json_files[base_name] = []
            
            json_files[base_name].append(full_path)

# Handle duplicate files
for base_name, paths in json_files.items():
    if len(paths) > 1:
        print(f"Found duplicate JSON: {base_name}")
        
        # Select most recently modified file
        newest_file = max(paths, key=os.path.getmtime)
        target_path = os.path.join('data', base_name)
        
        print(f"Keeping newest version: {newest_file} -> {target_path}")
        
        # Backup other files
        for path in paths:
            if path != newest_file:
                backup_name = os.path.join('data', 'backup_' + os.path.basename(path))
                print(f"Backing up: {path} -> {backup_name}")
                shutil.copy2(path, backup_name)
        
        # Move newest file to data
        shutil.copy2(newest_file, target_path)

# Move files by pattern
for root, dirs, files in os.walk('.'):
    if './venv' in root or './__pycache__' in root:
        continue
    
    for file in files:
        full_path = os.path.join(root, file)
        
        # Check if file matches any pattern
        for pattern, target_folder in file_mappings.items():
            if re.match(pattern, file):
                target_path = os.path.join(target_folder, file)
                
                # If file is not already in target folder
                if os.path.normpath(full_path) != os.path.normpath(target_path):
                    if not os.path.exists(target_path):
                        print(f"Moving: {full_path} -> {target_path}")
                        shutil.copy2(full_path, target_path)
                    else:
                        print(f"File already exists at target: {target_path}")

# 3. Merge configurations
config_files = [f for f in os.listdir('config') if f.endswith('.json')]
if len(config_files) > 0:
    print("\nMerging configuration files...")
    
    # Create main config
    main_config = {}
    
    for config_file in config_files:
        try:
            with open(os.path.join('config', config_file), 'r') as f:
                config_data = json.load(f)
                
            # Split config by filename
            section_name = os.path.splitext(config_file)[0]
            main_config[section_name] = config_data
            print(f"Added {config_file} to main configuration")
        except json.JSONDecodeError:
            print(f"Error parsing {config_file} - skipping")
    
    # Save main config
    with open('config/main_config.json', 'w') as f:
        json.dump(main_config, indent=2, sort_keys=True)
    print("Created main_config.json with all configurations")

# 4. Check production readiness
print("\nChecking production readiness...")

# Check for required files
required_files = [
    'config.env',
    'requirements.txt',
    'README.md',
    'core/fashion_bot.py',
    'core/customer_management.py',
    'core/handlers/customer_follow_up.py'
]

missing_files = [f for f in required_files if not os.path.exists(f)]
if missing_files:
    print("⚠️ Missing required files:")
    for file in missing_files:
        print(f"  - {file}")
else:
    print("✅ All required files present")

# Check for required directories
required_dirs = [
    'core',
    'core/handlers',
    'core/ui',
    'utils',
    'config',
    'data',
    'logs',
    'tests'
]

missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
if missing_dirs:
    print("⚠️ Missing required directories:")
    for dir in missing_dirs:
        print(f"  - {dir}")
else:
    print("✅ All required directories present") 