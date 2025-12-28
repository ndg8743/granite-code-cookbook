# Prompt for Claude Code: Multi-Agent Fine-Tuning with Specialized Granite Models

I need you to create a complete multi-agent fine-tuning pipeline that scrapes my job-specific documentation, generates specialized datasets for different agent roles, and fine-tunes different IBM Granite models for each agent with distinct tool capabilities.

## My Requirements

**Job Context:** [Fill in: Your job title, company, key responsibilities]

**Data Sources to Scrape:**
- Documentation: [List URLs]
- GitHub repos: [List repos]
- APIs/Tools: [List tools]
- MCP Servers: [List MCP servers]

## Multi-Agent System

Create 5 specialized agents, each using an optimized Granite model:

### Agent 1: Documentation Assistant
- **Model**: `ibm-granite/granite-4.0-micro` (3B) - Fast Q&A
- **Tools**: mcp_context7_search, mcp_filesystem_read, mcp_web_search
- **Focus**: Documentation queries, knowledge retrieval

### Agent 2: Code Assistant  
- **Model**: `ibm-granite/granite-3b-code-base-2k` or `granite-3.3-8b-instruct` (8B)
- **Tools**: mcp_filesystem_write, mcp_github_api, execute_shell_command, mcp_python_executor
- **Focus**: Code generation, review, automation

### Agent 3: Infrastructure Assistant
- **Model**: `ibm-granite/granite-3.3-8b-instruct` (8B) - Complex workflows
- **Tools**: execute_shell_command, mcp_kubernetes_api, mcp_prometheus_query, mcp_ansible_runner
- **Focus**: Operations, troubleshooting, deployment

### Agent 4: Research Assistant
- **Model**: `ibm-granite/granite-4.0-h-micro` (3B) - Efficient analysis
- **Tools**: mcp_context7_search, mcp_sqlite_query, mcp_python_executor, mcp_web_search
- **Focus**: Research, data analysis, reports

### Agent 5: Communication Assistant
- **Model**: `ibm-granite/granite-4.0-micro` (3B) - Fast writing
- **Tools**: mcp_filesystem_write, mcp_context7_search
- **Focus**: Documentation writing, communication

## Deliverables

1. **Unified Scraping Pipeline**
   - Scrape all sources
   - Categorize content for each agent
   - Extract tool definitions

2. **Agent-Specific Dataset Generation**
   - Generate datasets for each agent
   - Include tool use examples (20-70% depending on agent)
   - Format as JSONL

3. **Fine-Tuning Scripts**
   - Individual training scripts per agent
   - Appropriate model selection per agent
   - Unified training orchestrator

4. **Agent Router & Integration**
   - Intelligent query routing
   - Multi-agent orchestration
   - Agent handoff logic

5. **Evaluation**
   - Per-agent evaluation
   - System-wide testing
   - Tool use accuracy metrics

## Dataset Format

Each agent dataset in JSONL:
```json
{
  "agent": "code|documentation|infrastructure|research|communication",
  "instruction": "Task description",
  "input": "",
  "output": "Response",
  "tools": [{"name": "tool_name", "parameters": {...}}]
}
```

## Training Config Per Agent

- **3B Models** (Documentation, Research, Communication): lora_r=8, max_length=1024-2048, tool_use=20-50%
- **8B Models** (Code, Infrastructure): lora_r=16, max_length=2048-4096, tool_use=60-70%
- All: learning_rate=2e-4, bf16=True, qLoRA 4-bit

## Agent Routing Logic

Route queries based on keywords:
- Documentation → Agent 1
- Code/script/API → Agent 2
- Deploy/cluster/infra → Agent 3
- Analyze/research/data → Agent 4
- Write/document/email → Agent 5

## Success Criteria

- Each agent: 85-95% accuracy in their domain
- Tool use: 85%+ correct invocations
- Agent routing: 90%+ correct selection
- System: Seamless multi-agent workflows

## Reference

Use `recipes/finetune-gpfs/` as template. Extend for:
- Multiple agents with different models
- Agent-specific tool sets
- Multi-agent orchestration
- Tool use training per agent

Create a complete working system with all agents, router, and evaluation.
