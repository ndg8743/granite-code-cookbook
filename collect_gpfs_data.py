"""
Collect GPFS/IBM Storage Scale data from GitHub repos and documentation.
"""
import os
import subprocess
import json
from pathlib import Path

# Directory to store cloned repos and extracted data
DATA_DIR = Path("gpfs_data")
REPOS_DIR = DATA_DIR / "repos"
OUTPUT_DIR = DATA_DIR / "extracted"

# IBM Storage Scale GitHub repositories
REPOS = [
    "https://github.com/IBM/ibm-spectrum-scale-csi.git",
    "https://github.com/IBM/ibm-spectrum-scale-cloud-install.git",
    "https://github.com/IBM/ibm-spectrum-scale-bridge-for-grafana.git",
    "https://github.com/IBM/ibm-spectrum-scale-container-native.git",
]

# GPFS diagnostic tools knowledge (from user's research)
GPFS_KNOWLEDGE = """
## Built-in GPFS Diagnostic & Verification Commands

IBM Storage Scale includes a comprehensive suite of "mm" commands for testing and diagnostics:

### Core Diagnostic Tools
- **mmdiag** - Displays diagnostic information about the internal GPFS state on the current node
  - mmdiag --network - Check network connectivity and pending operations
  - mmdiag --iohist - Lists last 512 I/O operations performed
  
- **mmfsadm** - Intended for use by trained service personnel. It extracts data from GPFS without using locking, so it can collect data even in the event of locking errors.
  - mmfsadm dump waiters - Find long-lasting processes
  - mmfsadm dump all - Comprehensive debug dump
  - mmfsadm showtrace - Display current trace levels
  - mmfsadm dump deadlock - Deadlock detection

- **mmhealth** - Health monitoring that creates alerts based on callhome data for recent findings

- **mmnetverify** - Network verification command

- **gpfs.snap** - A debug data collection script that gathers all logs and configurations from nodes. Run "gpfs.snap -deadlock" if a deadlock is suspected.

- **mmtracectl** - Sets up and enables tracing using default settings for various common problem scenarios. Trace level can be set from 0 through 14, representing increasing levels of detail.

### Cluster Status Commands
- **mmgetstate** - Check GPFS daemon state on nodes
- **mmlsconfig** - List cluster configuration
- **mmlscluster** - Display cluster information
- **mmlsdisk** - List disk status

## Performance Testing Tools

### nsdperf (IBM's Network Performance Tool)
IBM has several tools to test a Spectrum Scale cluster, which includes nsdperf. Tools like iperf are good for testing throughput between two nodes, but trying to use these tools on a larger configuration and coordinating the startup can be difficult.

nsdperf tests network performance, simulating GPFS NSD client/server operations. It's located in /usr/lpp/mmfs/samples/net.

### Industry-Standard Benchmarks
- **IOR** - A parallel IO benchmark testing storage systems using various interfaces and access patterns
- **mdtest** - Tests peak metadata rates of storage systems under different directory structures
- **fio** - Used to validate infrastructure before running actual performance tests

## Test Automation & Development Tools

### For CSI/Kubernetes Testing
Test automation for IBM Spectrum Scale (GPFS) CSI Operator uses the Kubernetes Python client and Pytest.

### Infrastructure Automation
- **Ansible** - IBM provides playbooks for automated installation and configuration
- **Vagrant** - IBM provides StorageScaleVagrant for development/test environments
- **Terraform** - Used for cloud provisioning, delivering Storage Scale as Terraform modules
"""

def clone_repos():
    """Clone all IBM Storage Scale repositories."""
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    
    for repo_url in REPOS:
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = REPOS_DIR / repo_name
        
        if repo_path.exists():
            print(f"Repo {repo_name} already exists, skipping...")
            continue
            
        print(f"Cloning {repo_name}...")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(repo_path)],
                check=True,
                capture_output=True
            )
            print(f"  Cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"  Failed to clone: {e}")

def extract_markdown_files(repo_path: Path) -> list[dict]:
    """Extract content from markdown files in a repository."""
    chunks = []
    
    for md_file in repo_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            if len(content.strip()) > 100:  # Skip very short files
                rel_path = md_file.relative_to(repo_path)
                chunks.append({
                    "source": f"{repo_path.name}/{rel_path}",
                    "type": "markdown",
                    "content": content[:8000]  # Limit chunk size
                })
        except Exception as e:
            print(f"  Error reading {md_file}: {e}")
    
    return chunks

def extract_yaml_configs(repo_path: Path) -> list[dict]:
    """Extract YAML configuration examples."""
    chunks = []
    
    for yaml_file in list(repo_path.rglob("*.yaml")) + list(repo_path.rglob("*.yml")):
        try:
            content = yaml_file.read_text(encoding="utf-8", errors="ignore")
            if len(content.strip()) > 50:
                rel_path = yaml_file.relative_to(repo_path)
                chunks.append({
                    "source": f"{repo_path.name}/{rel_path}",
                    "type": "yaml_config",
                    "content": content[:4000]
                })
        except Exception as e:
            pass
    
    return chunks

def extract_code_comments(repo_path: Path) -> list[dict]:
    """Extract docstrings and comments from Python/Go files."""
    chunks = []
    
    # Python files
    for py_file in repo_path.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # Extract module docstrings
            if content.startswith('"""') or content.startswith("'''"):
                end = content.find('"""', 3) if content.startswith('"""') else content.find("'''", 3)
                if end > 0:
                    docstring = content[3:end]
                    if len(docstring) > 50:
                        chunks.append({
                            "source": f"{repo_path.name}/{py_file.relative_to(repo_path)}",
                            "type": "python_docstring",
                            "content": docstring
                        })
        except Exception:
            pass
    
    return chunks

def collect_all_data():
    """Main function to collect all GPFS data."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    all_chunks = []
    
    # 1. Clone repositories
    print("=== Cloning GitHub repositories ===")
    clone_repos()
    
    # 2. Extract from repos
    print("\n=== Extracting documentation from repos ===")
    for repo_dir in REPOS_DIR.iterdir():
        if repo_dir.is_dir():
            print(f"Processing {repo_dir.name}...")
            
            md_chunks = extract_markdown_files(repo_dir)
            print(f"  Found {len(md_chunks)} markdown files")
            all_chunks.extend(md_chunks)
            
            yaml_chunks = extract_yaml_configs(repo_dir)
            print(f"  Found {len(yaml_chunks)} YAML configs")
            all_chunks.extend(yaml_chunks)
            
            code_chunks = extract_code_comments(repo_dir)
            print(f"  Found {len(code_chunks)} code docstrings")
            all_chunks.extend(code_chunks)
    
    # 3. Add GPFS knowledge base
    print("\n=== Adding GPFS diagnostic knowledge ===")
    
    # Split knowledge into sections
    sections = GPFS_KNOWLEDGE.split("##")
    for section in sections:
        if section.strip():
            all_chunks.append({
                "source": "gpfs_diagnostics_research",
                "type": "documentation",
                "content": "##" + section.strip()
            })
    
    # 4. Save extracted chunks
    output_file = OUTPUT_DIR / "gpfs_chunks.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
    
    print(f"\n=== Summary ===")
    print(f"Total chunks extracted: {len(all_chunks)}")
    print(f"Saved to: {output_file}")
    
    return all_chunks

if __name__ == "__main__":
    chunks = collect_all_data()
