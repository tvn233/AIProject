# AI Usage Transparency Report - Final_Project_T5

## Student Information
- **Name:** Hà Ngọc Bảo
- **Student ID:** 24110078
- **Role / Scope:** MCP Server, Data Models, and Unit Testing (`src/models.py`, `src/mcp/server.py`, `tests/test_mcp.py`, `data/ctxh_db.json`)

## AI Tool Assistance Overview
During the development of this project, AI was utilized as a technical assistant for:
1. **Model Design (`src/models.py`):** Structuring dataclasses with explicit type hints for MCP tool parameters.
2. **MCP Protocol Implementation (`src/mcp/server.py`):** Designing the Stdio JSON-RPC loop, enforcing absolute path resolution (`os.path.abspath`), ensuring stdout hygiene (zero `print()` usage, flushing buffers), and implementing robust exception handling (`try-except`).
3. **Unit Testing (`tests/test_mcp.py`):** Writing validation scripts to verify side effects (writing to JSON DB) and verification reads.

## Verification & Personal Ownership
All generated suggestions, protocol loops, and error-handling mechanisms were thoroughly reviewed, manually tested, and verified by the author to ensure complete ownership and correctness during academic evaluation.