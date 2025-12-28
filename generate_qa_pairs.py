"""
Generate Q&A pairs from GPFS documentation chunks.
Uses rule-based extraction + templates for quick demo.
"""
import json
import re
from pathlib import Path

INPUT_FILE = Path("gpfs_data/extracted/gpfs_chunks.json")
OUTPUT_FILE = Path("gpfs_dataset.jsonl")

# Pre-defined Q&A pairs based on GPFS knowledge
MANUAL_QA_PAIRS = [
    # Diagnostic commands
    {
        "question": "How do I check network connectivity in GPFS?",
        "answer": "Use the mmdiag --network command to check network connectivity and pending operations in GPFS. This displays diagnostic information about the network state on the current node."
    },
    {
        "question": "What does mmdiag --iohist show?",
        "answer": "The mmdiag --iohist command lists the last 512 I/O operations performed by GPFS on the current node. This is useful for diagnosing I/O performance issues and understanding recent file system activity."
    },
    {
        "question": "How do I collect debug data from a GPFS cluster?",
        "answer": "Use the gpfs.snap command to collect debug data. This script gathers all logs and configurations from nodes. If you suspect a deadlock, run 'gpfs.snap -deadlock' to collect additional deadlock-specific information."
    },
    {
        "question": "What is mmfsadm used for in GPFS?",
        "answer": "mmfsadm is a diagnostic tool intended for trained service personnel. It extracts data from GPFS without using locking, allowing data collection even during locking errors. Common uses include: 'mmfsadm dump waiters' to find long-lasting processes, 'mmfsadm dump all' for comprehensive debug dumps, and 'mmfsadm dump deadlock' for deadlock detection."
    },
    {
        "question": "How do I check the health of a GPFS cluster?",
        "answer": "Use the mmhealth command for health monitoring. It creates alerts based on callhome data for recent findings. You can run 'mmhealth node show' to see the health status of nodes, or 'mmhealth node show --unhealthy' to only show unhealthy nodes."
    },
    {
        "question": "How do I enable tracing in GPFS?",
        "answer": "Use the mmtracectl command to set up and enable tracing. Trace levels range from 0 to 14, with higher numbers providing more detail. Use 'mmtracectl --set' to configure tracing and 'mmfsadm showtrace' to display current trace levels."
    },
    # Cluster status
    {
        "question": "How do I check the state of GPFS daemons on nodes?",
        "answer": "Use the mmgetstate command to check the GPFS daemon state on nodes. This shows whether the GPFS daemon (mmfsd) is active, down, or in an arbitrating state on each node in the cluster."
    },
    {
        "question": "How do I list GPFS cluster configuration?",
        "answer": "Use mmlsconfig to list the cluster configuration parameters. This displays all configuration settings for the GPFS cluster including network settings, timeouts, and performance tuning parameters."
    },
    {
        "question": "How do I display GPFS cluster information?",
        "answer": "Use the mmlscluster command to display cluster information including the cluster name, cluster ID, primary and secondary configuration servers, and a list of all nodes in the cluster."
    },
    # Performance testing
    {
        "question": "How do I test network performance in a GPFS cluster?",
        "answer": "Use nsdperf, IBM's network performance tool located in /usr/lpp/mmfs/samples/net. Unlike iperf which tests between two nodes, nsdperf simulates GPFS NSD client/server operations and can coordinate tests across multiple nodes in a large cluster configuration."
    },
    {
        "question": "What tools can I use to benchmark GPFS performance?",
        "answer": "Common benchmarking tools for GPFS include: 1) IOR - a parallel IO benchmark for testing storage systems with various interfaces and access patterns, 2) mdtest - tests peak metadata rates including mkdir, stat, rmdir, creat, open, close, and unlink operations, 3) fio - validates infrastructure with configurable block sizes and I/O patterns."
    },
    # CSI/Kubernetes
    {
        "question": "How do I deploy the IBM Spectrum Scale CSI driver?",
        "answer": "Deploy the IBM Spectrum Scale CSI driver using the operator pattern. Install the CSI operator from OperatorHub or using kubectl/oc. Then create a CSIScaleOperator custom resource that specifies your cluster configuration, including the primary and GUI clusters, secret references for authentication, and node selectors for driver placement."
    },
    {
        "question": "What are the prerequisites for IBM Spectrum Scale CSI driver?",
        "answer": "Prerequisites include: 1) A running IBM Spectrum Scale cluster with GUI enabled, 2) Kubernetes 1.19+ or OpenShift 4.6+, 3) The Spectrum Scale client installed on all Kubernetes worker nodes, 4) Network connectivity between Kubernetes nodes and the Spectrum Scale cluster, 5) A Kubernetes secret containing the Scale GUI credentials."
    },
    {
        "question": "How do I create a PersistentVolumeClaim with IBM Spectrum Scale CSI?",
        "answer": "Create a StorageClass referencing the CSI driver (spectrumscale.csi.ibm.com), then create a PVC referencing that StorageClass. The CSI driver will dynamically provision a fileset on your Spectrum Scale filesystem. Example: Create a StorageClass with 'provisioner: spectrumscale.csi.ibm.com' and configure volBackendFs to specify which filesystem to use."
    },
    # Troubleshooting
    {
        "question": "How do I diagnose a GPFS deadlock?",
        "answer": "To diagnose a GPFS deadlock: 1) Run 'gpfs.snap -deadlock' to collect deadlock-specific debug data, 2) Use 'mmfsadm dump deadlock' for deadlock detection, 3) Check 'mmfsadm dump waiters' to find long-lasting processes that may be blocking others. The collected data can be analyzed by IBM support."
    },
    {
        "question": "What should I check when GPFS nodes are being expelled from the cluster?",
        "answer": "When nodes are expelled: 1) Check mmfs.log for the reason - in GPFS 6.0.0+, the log provides clearer details about expel decisions, 2) Use mmhealth to see expel reports via the postExpel callback, 3) Common causes include network issues (check with mmnetverify), lease expiration, or inter-node RPC failures."
    },
    # Cloud and automation
    {
        "question": "How do I automate IBM Storage Scale installation?",
        "answer": "IBM provides several automation options: 1) Ansible playbooks for automated installation, configuration, verification, and upgrades, 2) Terraform modules for cloud provisioning in AWS, Azure, and IBM Cloud, 3) Vagrant with StorageScaleVagrant for development/test environments. The Installation Toolkit also provides automated deployment capabilities."
    },
    {
        "question": "What is IBM Storage Scale Container Native?",
        "answer": "IBM Storage Scale Container Native provides native integration of Spectrum Scale with Kubernetes/OpenShift environments. It allows containers to directly access Spectrum Scale filesystems with enterprise features like snapshots, quotas, and data tiering. It's deployed alongside the CSI driver for complete container storage integration."
    },
    # Grafana monitoring
    {
        "question": "How do I monitor IBM Storage Scale with Grafana?",
        "answer": "Use the IBM Spectrum Scale Bridge for Grafana. This bridge collects performance metrics from your Scale cluster and exposes them to Prometheus, which Grafana can then visualize. Install the bridge, configure it to connect to your Scale cluster's performance monitoring (mmperfmon), and import the provided Grafana dashboards."
    },
    {
        "question": "What metrics are available for IBM Storage Scale monitoring?",
        "answer": "IBM Storage Scale exposes metrics through mmperfmon including: filesystem throughput (read/write MB/s), IOPS, latency, metadata operations, network statistics, disk utilization, and per-fileset metrics. These can be collected via the Grafana bridge or directly queried using mmpmon."
    },
]


def extract_qa_from_readme(content: str, source: str) -> list[dict]:
    """Extract Q&A pairs from README files based on headers and content."""
    qa_pairs = []
    
    # Find headers and their content
    sections = re.split(r'\n##?\s+', content)
    
    for section in sections[1:]:  # Skip content before first header
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        header = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        
        if len(body) < 50 or len(body) > 2000:
            continue
            
        # Generate question from header
        header_lower = header.lower()
        
        if 'install' in header_lower or 'setup' in header_lower or 'deploy' in header_lower:
            question = f"How do I {header.lower().replace('installation', 'install').replace('deployment', 'deploy')}?"
        elif 'configur' in header_lower:
            question = f"How do I configure {header.replace('Configuration', '').replace('Configuring', '').strip()}?"
        elif 'prerequisite' in header_lower or 'requirement' in header_lower:
            question = f"What are the {header.lower()}?"
        elif 'troubleshoot' in header_lower:
            question = f"How do I troubleshoot {header.replace('Troubleshooting', '').strip()}?"
        elif 'usage' in header_lower or 'example' in header_lower:
            question = f"How do I use {source.split('/')[0].replace('ibm-spectrum-scale-', '')}?"
        else:
            continue
        
        # Clean up the answer
        answer = body[:1500]  # Limit answer length
        answer = re.sub(r'\n{3,}', '\n\n', answer)  # Remove excessive newlines
        
        qa_pairs.append({
            "question": question,
            "answer": answer
        })
    
    return qa_pairs


def extract_qa_from_yaml(content: str, source: str) -> list[dict]:
    """Generate Q&A about YAML configuration examples."""
    qa_pairs = []
    
    # Check if it's a meaningful configuration file
    if 'kind:' in content and ('Spectrum' in content or 'CSI' in content or 'Scale' in content):
        kind_match = re.search(r'kind:\s*(\w+)', content)
        if kind_match:
            kind = kind_match.group(1)
            
            question = f"Can you show an example {kind} configuration for IBM Spectrum Scale?"
            answer = f"Here's an example {kind} configuration:\n\n```yaml\n{content[:1200]}\n```"
            
            qa_pairs.append({
                "question": question,
                "answer": answer
            })
    
    return qa_pairs


def generate_dataset():
    """Generate the complete Q&A dataset."""
    
    # Load extracted chunks
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    all_qa_pairs = []
    
    # Add manual Q&A pairs first (highest quality)
    all_qa_pairs.extend(MANUAL_QA_PAIRS)
    print(f"Added {len(MANUAL_QA_PAIRS)} manual Q&A pairs")
    
    # Extract from markdown files
    md_count = 0
    for chunk in chunks:
        if chunk['type'] == 'markdown':
            pairs = extract_qa_from_readme(chunk['content'], chunk['source'])
            all_qa_pairs.extend(pairs)
            md_count += len(pairs)
    print(f"Extracted {md_count} Q&A pairs from markdown")
    
    # Extract from YAML configs (limit to avoid too many similar examples)
    yaml_count = 0
    for chunk in chunks[:50]:  # Limit YAML examples
        if chunk['type'] == 'yaml_config':
            pairs = extract_qa_from_yaml(chunk['content'], chunk['source'])
            all_qa_pairs.extend(pairs)
            yaml_count += len(pairs)
    print(f"Extracted {yaml_count} Q&A pairs from YAML configs")
    
    # Remove duplicates based on question similarity
    seen_questions = set()
    unique_pairs = []
    for pair in all_qa_pairs:
        q_key = pair['question'].lower()[:50]
        if q_key not in seen_questions:
            seen_questions.add(q_key)
            unique_pairs.append(pair)
    
    print(f"\nTotal unique Q&A pairs: {len(unique_pairs)}")
    
    # Save as JSONL
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for pair in unique_pairs:
            f.write(json.dumps(pair) + '\n')
    
    print(f"Saved to: {OUTPUT_FILE}")
    
    # Show some examples
    print("\n=== Sample Q&A pairs ===")
    for pair in unique_pairs[:3]:
        print(f"\nQ: {pair['question']}")
        print(f"A: {pair['answer'][:200]}...")
    
    return unique_pairs


if __name__ == "__main__":
    generate_dataset()
