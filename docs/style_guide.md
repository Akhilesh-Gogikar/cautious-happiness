# Documentation Style Guide

## Purpose / Context
This guide establishes the standards for all documentation within the **Alpha Insights Platform** repository. The goal is maintain a professional, cohesive, and "Institutional" tone consistent with the product's vision.

## 1. Tone and Voice
- **Professional & Technical**: Use clear, concise language. Avoid slang or overly casual phrasing.
- **Institutional Authority**: The voice should sound like a tier-1 financial institution or research lab.
- **Direct**: Use active voice where possible. "The system processes data" rather than "Data is processed by the system".

## 2. Terminology
Ensure consistent usage of these terms:

| Term | Definition |
|------|------------|
| **Alpha Insights Platform** | The overall product name (formerly Hedge Fund Dashboard). |
| **OpenForecaster** | The specific AI model used for predictions. |
| **Critic** | The verification agent that cross-references facts. |
| **Intelligence Mirror** | The competitive intelligence feature. |
| **Polymarket** | The prediction market platform integrated. |
| **Data Noir** | The visual design language (used in UI contexts, less in technical docs). |

## 3. Formatting Standards

### Headers
- Use `#` H1 for the document title (Title Case).
- Use `##` H2 for major sections (Title Case).
- Use `###` H3 for subsections (Sentence Case).

### Code Blocks
- **Mandatory**: Always specify the language for syntax highlighting (e.g., \`\`\`bash, \`\`\`python).
- **Comments**: Include comments in code snippets where helpful.

### Links
- Use descriptive link text. Avoid "click here".
- Format: `[Link Text](path/to/file)` or `[Link Text](https://url.com)`.

### Lists
- Use `-` for unordered lists.
- Use `1.` for ordered lists.

## 4. Agentic Standards (For AI Contributors)

### Docstrings
When writing Python code, follow Google Style but add an "Agent Note" if logic is obscure.
```python
def verify_claim(claim: str) -> bool:
    """Verifies a claim against the whitelist.
    
    Args:
        claim: The string to verify.
    
    Agent Note: This function calls the Gemini API and costs money. Do not loop.
    """
```

### Mermaid Diagrams
- Use `graph TD` (Top-Down) for most flows.
- Keep node labels concise.
- Use subgraphs to group logical components.

## 5. File Structure
- `README.md`: High-level overview, quick start, installation.
- `docs/AGENTS.md`: Instruction manual for AI Agents.
- `docs/ARCHITECTURE.md`: Deep dive into system internals.
- `docs/backend.md`: Specifics for FastAPI service.
- `docs/frontend.md`: Specifics for Next.js service.
- `docs/style_guide.md`: This file.
