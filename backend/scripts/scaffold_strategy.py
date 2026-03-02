import os
import shutil
import sys
import yaml

def scaffold_strategy(strategy_name):
    base_dir = "/root/cautious-happiness/strategies"
    template_dir = os.path.join(base_dir, "template")
    target_dir = os.path.join(base_dir, strategy_name)

    if os.path.exists(target_dir):
        print(f"Error: Strategy '{strategy_name}' already exists at {target_dir}")
        return

    print(f"Scaffolding new strategy: {strategy_name}...")
    
    # Copy template to new directory
    shutil.copytree(template_dir, target_dir)

    # Update strategy_config.yaml with the new name
    config_path = os.path.join(target_dir, "strategy_config.yaml")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        config['name'] = strategy_name
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

    print(f"Successfully created strategy '{strategy_name}' at {target_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scaffold_strategy.py <strategy_name>")
        sys.exit(1)
    
    scaffold_strategy(sys.argv[1])
