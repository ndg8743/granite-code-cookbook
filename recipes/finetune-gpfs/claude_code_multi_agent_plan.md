# Claude Code Prompt: Multi-Agent Fine-Tuning Pipeline with Specialized Granite Models

## Objective

Create a comprehensive multi-agent fine-tuning pipeline that:
1. Scrapes job-specific documentation, APIs, and knowledge bases
2. Generates specialized datasets for different agent roles
3. Fine-tunes different IBM Granite models for specialized agents with distinct tool capabilities
4. Integrates all agents into a unified system

## Context

I work as [YOUR JOB TITLE] at [COMPANY/ORGANIZATION]. My role involves:
- [Key responsibility 1, e.g., "Managing IBM Storage Scale clusters"]
- [Key responsibility 2, e.g., "Troubleshooting Kubernetes deployments"]
- [Key responsibility 3, e.g., "Writing automation scripts"]
- [Key responsibility 4, e.g., "Code review and development"]

I need a multi-agent system where each agent is specialized for different tasks, using optimized Granite models and specific tool sets.

## Multi-Agent Architecture

Based on [IBM Granite model collection](https://huggingface.co/ibm-granite/collections), we'll use different models for different agents:

### Agent 1: Documentation & Knowledge Assistant
**Model**: `ibm-granite/granite-4.0-micro` (3B) or `ibm-granite/granite-3.3-2b-instruct` (3B)
- **Purpose**: Fast, efficient Q&A about documentation and knowledge base
- **Use Case**: Quick lookups, documentation queries, knowledge retrieval
- **Tools**:
  - `mcp_context7_search` - Library documentation search
  - `mcp_filesystem_read` - Read documentation files
  - `mcp_web_search` - Search external docs
  - `mcp_sqlite_query` - Query knowledge base databases
- **Training Focus**: Q&A accuracy, documentation comprehension, fast responses

### Agent 2: Code & Development Assistant
**Model**: `ibm-granite/granite-3b-code-base-2k` or `ibm-granite/granite-3.3-8b-instruct` (8B)
- **Purpose**: Code generation, review, debugging, automation
- **Use Case**: Script writing, code review, API integration, automation
- **Tools**:
  - `mcp_filesystem_write` - Write code files
  - `mcp_github_api` - GitHub operations
  - `execute_shell_command` - Run scripts and commands
  - `mcp_python_executor` - Execute Python code
  - `mcp_git_operations` - Git commands
- **Training Focus**: Code quality, syntax correctness, best practices, tool orchestration

### Agent 3: Infrastructure & Operations Assistant
**Model**: `ibm-granite/granite-3.3-8b-instruct` (8B)
- **Purpose**: Infrastructure management, troubleshooting, operations
- **Use Case**: Cluster management, monitoring, troubleshooting, deployment
- **Tools**:
  - `execute_shell_command` - CLI tool execution
  - `mcp_kubernetes_api` - K8s operations
  - `mcp_prometheus_query` - Metrics and monitoring
  - `mcp_ansible_runner` - Configuration management
  - `mcp_terraform_apply` - Infrastructure as code
- **Training Focus**: Operational procedures, troubleshooting workflows, multi-step operations

### Agent 4: Research & Analysis Assistant
**Model**: `ibm-granite/granite-4.0-h-micro` (3B) or `ibm-granite/granite-3.3-2b-instruct` (3B)
- **Purpose**: Research, analysis, data processing
- **Use Case**: Data analysis, research queries, report generation
- **Tools**:
  - `mcp_context7_search` - Research and documentation
  - `mcp_sqlite_query` - Data queries
  - `mcp_python_executor` - Data analysis scripts
  - `mcp_web_search` - External research
  - `mcp_filesystem_read` - Read data files
- **Training Focus**: Research accuracy, data interpretation, analytical reasoning

### Agent 5: Communication & Documentation Writer
**Model**: `ibm-granite/granite-4.0-micro` (3B)
- **Purpose**: Writing, documentation, communication
- **Use Case**: Documentation writing, email drafting, report generation
- **Tools**:
  - `mcp_filesystem_write` - Write documents
  - `mcp_context7_search` - Reference lookup
  - `mcp_web_search` - Fact checking
- **Training Focus**: Writing quality, clarity, proper formatting

## Data Sources to Scrape

### Primary Sources
1. **Internal Documentation**
   - Confluence/Wiki pages: [URLs or search terms]
   - Internal knowledge bases: [URLs]
   - Runbooks and playbooks: [Locations]
   - Code repositories: [GitHub orgs/repos]

2. **External Documentation**
   - Product documentation: [URLs]
   - API documentation: [OpenAPI/Swagger specs]
   - GitHub repositories: [List of repos]
   - Technical blogs and guides: [URLs]

3. **Codebases**
   - Internal tools: [Repository paths]
   - Scripts and automation: [Locations]
   - Configuration examples: [Paths]
   - Infrastructure as code: [Terraform/Ansible repos]

4. **Tools and APIs**
   - MCP servers: [List MCP server names/descriptions]
   - REST APIs: [Endpoints or OpenAPI specs]
   - CLI tools: [Tool names and their documentation]
   - Kubernetes: [Cluster configs]
   - Monitoring tools: [Prometheus/Grafana configs]

### Specific URLs/Repos to Scrape
```
# Add your specific sources here:
- Documentation: [URLs]
- GitHub: [org/repo1, org/repo2, ...]
- APIs: [OpenAPI specs]
- Internal wiki: [URL]
```

## Dataset Requirements by Agent

### Agent 1: Documentation Assistant Dataset
**Format**: Q&A pairs with documentation references
```json
{
  "agent": "documentation",
  "instruction": "How do I configure Storage Scale cluster?",
  "input": "",
  "output": "To configure a Storage Scale cluster, use the mmcrcluster command...",
  "tools": [
    {"name": "mcp_context7_search", "parameters": {"query": "Storage Scale cluster configuration", "library": "storage-scale"}}
  ],
  "references": ["docs/storage-scale/cluster-setup.md"]
}
```

### Agent 2: Code Assistant Dataset
**Format**: Code generation with tool use
```json
{
  "agent": "code",
  "instruction": "Create a Python script to check cluster health",
  "input": "",
  "output": "I'll create a Python script that uses the mmhealth command to check cluster health.",
  "tools": [
    {"name": "mcp_filesystem_write", "parameters": {"path": "check_cluster.py", "content": "import subprocess\n\ndef check_cluster():\n    result = subprocess.run(['mmhealth', 'node', 'show'], capture_output=True, text=True)\n    return result.stdout\n"}},
    {"name": "execute_shell_command", "parameters": {"command": "python check_cluster.py"}}
  ],
  "code_examples": ["examples/cluster_health.py"]
}
```

### Agent 3: Infrastructure Assistant Dataset
**Format**: Multi-step operational procedures
```json
{
  "agent": "infrastructure",
  "instruction": "Deploy a new Storage Scale cluster with 5 nodes",
  "input": "",
  "output": "I'll deploy the cluster step by step: 1) Prepare nodes, 2) Install GPFS, 3) Create cluster, 4) Add nodes, 5) Verify.",
  "tools": [
    {"name": "execute_shell_command", "parameters": {"command": "mmcrcluster -C mycluster -N node1:manager-quorum,node2:manager-quorum,node3:manager-quorum"}},
    {"name": "mcp_ansible_runner", "parameters": {"playbook": "deploy-cluster.yml", "inventory": "nodes.ini"}},
    {"name": "execute_shell_command", "parameters": {"command": "mmlscluster"}}
  ],
  "workflow_steps": ["prepare", "install", "create", "add_nodes", "verify"]
}
```

### Agent 4: Research Assistant Dataset
**Format**: Research queries with data analysis
```json
{
  "agent": "research",
  "instruction": "Analyze cluster performance trends over the last month",
  "input": "",
  "output": "I'll query the monitoring database and analyze performance metrics.",
  "tools": [
    {"name": "mcp_prometheus_query", "parameters": {"query": "rate(cluster_io_ops[1h])", "range": "30d"}},
    {"name": "mcp_python_executor", "parameters": {"code": "import pandas as pd\n# analysis code"}},
    {"name": "mcp_filesystem_write", "parameters": {"path": "analysis_report.md", "content": "# Performance Analysis\n..."}}
  ]
}
```

### Agent 5: Communication Assistant Dataset
**Format**: Writing tasks with references
```json
{
  "agent": "communication",
  "instruction": "Write a runbook for cluster troubleshooting",
  "input": "",
  "output": "I'll create a comprehensive troubleshooting runbook.",
  "tools": [
    {"name": "mcp_context7_search", "parameters": {"query": "cluster troubleshooting procedures", "library": "operations"}},
    {"name": "mcp_filesystem_write", "parameters": {"path": "runbook.md", "content": "# Troubleshooting Runbook\n..."}}
  ]
}
```

## Fine-tuning Configuration by Agent

### Agent 1: Documentation (Granite 4.0-micro or 3.3-2b)
```python
agent1_config = {
    "model": "ibm-granite/granite-4.0-micro",  # or granite-3.3-2b-instruct
    "learning_rate": 2e-4,
    "max_steps": 500,  # Smaller dataset
    "max_length": 1024,  # Shorter for quick responses
    "lora_r": 8,  # Smaller for 3B model
    "lora_alpha": 16,
    "target_modules": ["q_proj", "v_proj"],
    "tool_use_percentage": 20%  # Light tool use
}
```

### Agent 2: Code (Granite 3b-code or 3.3-8b)
```python
agent2_config = {
    "model": "ibm-granite/granite-3b-code-base-2k",  # or granite-3.3-8b-instruct
    "learning_rate": 1.5e-4,
    "max_steps": 1500,  # More steps for code quality
    "max_length": 4096,  # Longer for code generation
    "lora_r": 16,
    "lora_alpha": 32,
    "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
    "tool_use_percentage": 60%  # Heavy tool use
}
```

### Agent 3: Infrastructure (Granite 3.3-8b)
```python
agent3_config = {
    "model": "ibm-granite/granite-3.3-8b-instruct",
    "learning_rate": 2e-4,
    "max_steps": 2000,  # Most complex workflows
    "max_length": 2048,
    "lora_r": 16,
    "lora_alpha": 32,
    "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
    "tool_use_percentage": 70%  # Very heavy tool use
}
```

### Agent 4: Research (Granite 4.0-h-micro or 3.3-2b)
```python
agent4_config = {
    "model": "ibm-granite/granite-4.0-h-micro",  # or granite-3.3-2b-instruct
    "learning_rate": 2e-4,
    "max_steps": 800,
    "max_length": 2048,  # Longer for analysis
    "lora_r": 8,
    "lora_alpha": 16,
    "target_modules": ["q_proj", "v_proj"],
    "tool_use_percentage": 50%  # Moderate tool use
}
```

### Agent 5: Communication (Granite 4.0-micro)
```python
agent5_config = {
    "model": "ibm-granite/granite-4.0-micro",
    "learning_rate": 2e-4,
    "max_steps": 600,
    "max_length": 2048,  # Longer for documents
    "lora_r": 8,
    "lora_alpha": 16,
    "target_modules": ["q_proj", "v_proj"],
    "tool_use_percentage": 30%  # Light tool use
}
```

## Implementation Pipeline

### Phase 1: Data Collection (Unified)
1. **Scrape All Sources**
   - `scrape_documentation.py` - Web/documentation scraper
   - `scrape_github.py` - GitHub repo extractor
   - `scrape_apis.py` - API documentation parser
   - `extract_mcp_tools.py` - MCP tool schema extractor
   - `extract_code_examples.py` - Code example extractor

2. **Categorize Content**
   - `categorize_content.py` - Route content to appropriate agent datasets
   - Documentation → Agent 1
   - Code → Agent 2
   - Operations/Infra → Agent 3
   - Research/Analysis → Agent 4
   - Writing/Docs → Agent 5

### Phase 2: Dataset Generation (Per Agent)
1. **Agent-Specific Generators**
   - `generate_doc_agent_dataset.py` - Agent 1 dataset
   - `generate_code_agent_dataset.py` - Agent 2 dataset
   - `generate_infra_agent_dataset.py` - Agent 3 dataset
   - `generate_research_agent_dataset.py` - Agent 4 dataset
   - `generate_comm_agent_dataset.py` - Agent 5 dataset

2. **Tool Example Generation**
   - For each agent, generate tool use examples specific to their tools
   - Include multi-tool workflows
   - Add error handling scenarios
   - Create tool chaining examples

3. **Quality Control**
   - `validate_datasets.py` - Validate all agent datasets
   - `check_tool_examples.py` - Verify tool examples are correct
   - `balance_datasets.py` - Balance dataset sizes

### Phase 3: Fine-Tuning (Parallel)
1. **Training Scripts**
   - `train_agent1_documentation.py` - Train documentation agent
   - `train_agent2_code.py` - Train code agent
   - `train_agent3_infrastructure.py` - Train infrastructure agent
   - `train_agent4_research.py` - Train research agent
   - `train_agent5_communication.py` - Train communication agent

2. **Unified Training Orchestrator**
   - `train_all_agents.py` - Train all agents in parallel or sequence
   - Monitor training progress for all agents
   - Collect metrics and results

### Phase 4: Integration & Evaluation
1. **Agent Router**
   - `agent_router.py` - Route queries to appropriate agent
   - `multi_agent_orchestrator.py` - Coordinate multiple agents
   - `agent_handoff.py` - Hand off tasks between agents

2. **Evaluation**
   - `evaluate_all_agents.py` - Evaluate each agent
   - `test_agent_integration.py` - Test multi-agent workflows
   - `benchmark_tool_use.py` - Benchmark tool calling accuracy

## Expected Outputs

### Data Collection
- `scraped_data/` - All scraped content organized by source
- `tool_definitions.json` - All tool schemas (MCP + custom)
- `content_categories.json` - Content categorization mapping

### Datasets (Per Agent)
- `datasets/agent1_documentation.jsonl`
- `datasets/agent2_code.jsonl`
- `datasets/agent3_infrastructure.jsonl`
- `datasets/agent4_research.jsonl`
- `datasets/agent5_communication.jsonl`

### Trained Models
- `models/agent1_documentation/` - Fine-tuned documentation agent
- `models/agent2_code/` - Fine-tuned code agent
- `models/agent3_infrastructure/` - Fine-tuned infrastructure agent
- `models/agent4_research/` - Fine-tuned research agent
- `models/agent5_communication/` - Fine-tuned communication agent

### Integration
- `agent_router.py` - Main routing logic
- `multi_agent_system.py` - Unified agent system
- `config/agent_config.yaml` - Agent configuration

## Agent Selection Logic

```python
def route_to_agent(query, context):
    """Route query to appropriate agent based on intent."""
    
    # Analyze query intent
    if "how to" in query.lower() or "documentation" in query.lower():
        return "agent1_documentation"
    
    elif any(keyword in query.lower() for keyword in ["code", "script", "function", "api", "github"]):
        return "agent2_code"
    
    elif any(keyword in query.lower() for keyword in ["deploy", "cluster", "kubernetes", "infrastructure", "troubleshoot"]):
        return "agent3_infrastructure"
    
    elif any(keyword in query.lower() for keyword in ["analyze", "research", "data", "metrics", "report"]):
        return "agent4_research"
    
    elif any(keyword in query.lower() for keyword in ["write", "document", "email", "report", "draft"]):
        return "agent5_communication"
    
    else:
        return "agent1_documentation"  # Default
```

## Success Criteria

### Per Agent
- **Agent 1 (Documentation)**: 95%+ accuracy on documentation Q&A, <2s response time
- **Agent 2 (Code)**: 90%+ code correctness, proper tool use, syntax validation
- **Agent 3 (Infrastructure)**: 85%+ successful multi-step workflows, correct tool chaining
- **Agent 4 (Research)**: Accurate data analysis, proper tool orchestration
- **Agent 5 (Communication)**: High-quality writing, proper formatting

### System-Wide
- Correct agent selection 90%+ of the time
- Seamless agent handoffs for complex tasks
- Unified response formatting
- Tool use accuracy 85%+ across all agents

## Additional Requirements

- **Model Selection**: Choose appropriate Granite model size based on:
  - Task complexity (simple Q&A → 3B, complex workflows → 8B)
  - Response time requirements (fast → 3B, quality → 8B)
  - Available GPU memory
  - Tool use complexity

- **Tool Integration**: Each agent must:
  - Understand its specific tool set
  - Handle tool errors gracefully
  - Chain tools correctly
  - Validate tool outputs

- **Agent Coordination**: System must:
  - Route queries intelligently
  - Support multi-agent collaboration
  - Handle agent handoffs
  - Maintain conversation context

## Reference Implementation

Use the GPFS fine-tuning recipe in `recipes/finetune-gpfs/` as a template, but extend it for:
- Multiple specialized agents
- Different Granite models per agent
- Agent-specific tool sets
- Multi-agent orchestration
- Tool use training for each agent

## Notes

- Start with 2-3 agents (Documentation, Code, Infrastructure) for initial testing
- Use smaller models (3B) for faster iteration
- Scale up to 8B models for complex agents once validated
- Granite 4.0 models are newest but may have less community support
- Granite 3.3 models are stable and well-tested
- Code models (`granite-3b-code-*`) are optimized for code tasks

---

**Please create:**
1. A unified scraping pipeline that categorizes content for different agents
2. Agent-specific dataset generation scripts
3. Fine-tuning scripts for each agent with appropriate Granite models
4. An agent router and multi-agent orchestration system
5. Evaluation scripts for each agent and the integrated system

The system should allow me to query any agent individually or use the router for automatic agent selection.
