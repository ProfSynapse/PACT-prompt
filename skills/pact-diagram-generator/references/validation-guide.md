# Diagram Validation Guide

Complete guide for validating Mermaid diagrams generated using pact-diagram-generator skill.

## Overview

Validation ensures generated Mermaid diagrams are:
1. **Syntactically valid**: No parsing errors, renders correctly
2. **Semantically accurate**: Represents architectural specification correctly
3. **Platform compatible**: Works in target environments (GitHub, GitLab, VSCode)

**Validation Workflow**:
1. Syntax validation (Mermaid Live Editor)
2. Semantic validation (compare to spec)
3. Platform validation (test in target environment)
4. Visual validation (diagram is readable and clear)

## Syntax Validation

### Method 1: Mermaid Live Editor (Recommended)

**URL**: https://mermaid.live

**Steps**:
1. Copy generated Mermaid diagram code
2. Paste into Mermaid Live Editor
3. Observe rendering in real-time
4. Check for syntax errors in editor panel
5. Verify diagram renders without errors

**Advantages**:
- Real-time feedback
- Immediate error messages
- Official Mermaid parser
- Export capabilities (PNG, SVG, URL)

**Example Workflow**:
```markdown
1. Generate diagram using template
2. Copy full diagram code (including ```mermaid fences)
3. Navigate to https://mermaid.live
4. Clear editor, paste diagram code
5. Verify no red error messages
6. Visually inspect rendered diagram
7. If errors: fix syntax, repeat
8. If valid: proceed to semantic validation
```

### Method 2: GitHub Markdown Preview

**Steps**:
1. Create temporary branch in your repository
2. Add diagram to markdown file in branch
3. Push to GitHub
4. View file in GitHub web interface
5. Check if diagram renders correctly

**Advantages**:
- Tests actual deployment environment
- Verifies GitHub Mermaid version compatibility
- Ensures no GitHub-specific rendering issues

**Limitations**:
- Slower feedback loop
- Requires git repository
- May lag behind latest Mermaid version

### Method 3: VSCode Markdown Preview

**Prerequisites**:
- Install VSCode extension: "Markdown Preview Mermaid Support" or "Mermaid Editor"

**Steps**:
1. Open markdown file with diagram in VSCode
2. Open preview pane (Cmd/Ctrl + Shift + V)
3. Verify diagram renders in preview

**Advantages**:
- Local validation
- No internet required
- Fast iteration

**Limitations**:
- Extension version may differ from deployment platform
- May not catch platform-specific issues

### Method 4: Mermaid CLI (Advanced)

**Installation**:
```bash
npm install -g @mermaid-js/mermaid-cli
```

**Usage**:
```bash
# Save diagram to file
echo 'your-mermaid-code' > diagram.mmd

# Validate and generate image
mmdc -i diagram.mmd -o diagram.png

# If command succeeds, syntax is valid
```

**Advantages**:
- Automatable
- Can integrate into CI/CD
- Programmatic validation

**Limitations**:
- Requires Node.js installation
- Command-line only
- More setup complexity

## Syntax Validation Checklist

Before moving to semantic validation, verify:

**General Syntax**:
- [ ] Diagram starts with diagram type keyword (`C4Context`, `sequenceDiagram`, `erDiagram`)
- [ ] All blocks properly closed (matching `end` statements)
- [ ] No unclosed parentheses, braces, or quotes
- [ ] Proper line breaks (no missing newlines between statements)

**C4 Diagrams**:
- [ ] All aliases defined before use in `Rel()` statements
- [ ] System boundary has matching braces `{ }`
- [ ] Element types correct (`Person`, `System`, `Container`, etc.)
- [ ] All `Rel()` statements have from, to, and label parameters

**Sequence Diagrams**:
- [ ] All participants referenced in messages are declared
- [ ] Arrow syntax valid (`->>`, `-->>`, etc.)
- [ ] All `alt`, `opt`, `loop`, `par` blocks have matching `end`
- [ ] Activation/deactivation markers balanced (`+` and `-`)

**ER Diagrams**:
- [ ] Entity names are valid identifiers (no spaces)
- [ ] Cardinality syntax correct (`||--o{`, etc.)
- [ ] All entities referenced in relationships are defined
- [ ] Attribute blocks have matching braces `{ }`
- [ ] Data types are valid

## Semantic Validation

Semantic validation ensures the diagram accurately represents the architectural specification.

### Completeness Check

**C4 Context Diagrams**:
- [ ] System name matches specification
- [ ] All actors from spec are represented
- [ ] All external systems from spec are included
- [ ] All documented integrations have relationship lines
- [ ] Relationship directions match spec (from → to)

**C4 Container Diagrams**:
- [ ] All deployable units from spec are included
- [ ] Technology stack matches architectural decisions
- [ ] All inter-container communication is shown
- [ ] System boundary includes all internal containers
- [ ] External systems correctly placed outside boundary

**Sequence Diagrams**:
- [ ] All participants from API flow are included
- [ ] Steps match documented sequence in spec
- [ ] Request/response pairs are complete
- [ ] Conditional flows match business logic
- [ ] Error handling paths are documented

**ER Diagrams**:
- [ ] All entities from schema are included
- [ ] All attributes match schema definition
- [ ] Primary keys correctly marked
- [ ] Foreign keys correctly marked
- [ ] Cardinality matches business rules

### Accuracy Check

Compare diagram elements to specification:

**Naming Accuracy**:
- [ ] Entity/system names match spec exactly
- [ ] Relationship labels match documented interactions
- [ ] Technology names are correct and specific
- [ ] Attribute names match schema definitions

**Relationship Accuracy**:
- [ ] One-to-many relationships correctly represented
- [ ] Many-to-many uses junction tables (ER diagrams)
- [ ] API flow sequence matches endpoint documentation
- [ ] Container communication protocols are accurate

**Description Accuracy**:
- [ ] Element descriptions match spec purpose
- [ ] Technology versions match decisions document
- [ ] Attribute types match schema DDL
- [ ] Relationship semantics are correct

### Consistency Check

Verify diagram consistency with other documentation:

**Cross-Diagram Consistency**:
- [ ] C4 Context actors appear in sequence diagrams
- [ ] C4 Container elements match sequence diagram participants
- [ ] ER entities referenced in container database elements
- [ ] External systems consistent across diagrams

**Specification Consistency**:
- [ ] Technology choices match architecture decisions doc
- [ ] API flows match endpoint specifications
- [ ] Database schema matches migration files
- [ ] System boundaries match deployment architecture

## Platform Validation

### GitHub Validation

**Test in GitHub**:
1. Create branch with diagram
2. Push to GitHub
3. View in web interface
4. Check rendering in:
   - File view (README.md, docs/)
   - Pull request description
   - Issue comment
   - Wiki pages

**GitHub-Specific Issues**:
- [ ] Verify Mermaid code fence syntax: ` ```mermaid `
- [ ] Check for GitHub-specific rendering bugs
- [ ] Ensure diagram complexity within limits
- [ ] Test on mobile view (GitHub app)

**Common GitHub Issues**:
- Very large diagrams may not render
- Some styling may be stripped
- Mermaid version may lag behind latest

### GitLab Validation

**Similar to GitHub**:
1. Create merge request with diagram
2. View in GitLab web interface
3. Verify rendering in markdown files

**GitLab Considerations**:
- Native Mermaid support
- Similar limitations to GitHub
- May have different version than GitHub

### Documentation Site Validation

**Docusaurus**:
- Requires `@docusaurus/theme-mermaid` plugin
- Test in local dev server
- Verify in production build

**MkDocs**:
- Requires `pymdown-extensions` plugin
- Configure in `mkdocs.yml`
- Test with `mkdocs serve`

**VuePress**:
- Requires `vuepress-plugin-mermaidjs`
- Test in development mode
- Verify in production build

## Visual Validation

Beyond syntax and semantics, ensure diagram is visually effective.

### Readability Check

- [ ] Text is legible (not too small)
- [ ] Diagram fits reasonably on screen (not too wide/tall)
- [ ] Relationship lines don't obscure labels
- [ ] Element spacing is adequate
- [ ] No overlapping elements

### Clarity Check

- [ ] Diagram purpose is immediately clear
- [ ] Relationship directions are obvious
- [ ] Labels are descriptive, not cryptic
- [ ] Groupings make sense (system boundaries, etc.)
- [ ] No unnecessary complexity

### Accessibility Check

- [ ] Labels use plain language
- [ ] Acronyms are explained (in diagram or legend)
- [ ] Color is not the only differentiator
- [ ] Diagram has descriptive title
- [ ] Legend provided if needed

## Common Validation Errors

### Syntax Errors

**Error: Undefined participant**
```
Error: Participant 'API' not defined
```
**Fix**: Declare participant before use
```mermaid
participant API
User->>API: Request
```

**Error: Unclosed block**
```
Error: Expected 'end' but reached end of file
```
**Fix**: Close all control flow blocks
```mermaid
alt Success
  API-->>User: 200 OK
end  # Must close
```

**Error: Invalid cardinality**
```
Error: Parse error on line X
```
**Fix**: Use valid ER cardinality syntax
```mermaid
User ||--o{ Post : "creates"  # Correct
```

**Error: Missing relationship parameter**
```
Error: Expected 3 parameters, got 2
```
**Fix**: Provide all required parameters
```mermaid
Rel(user, system, "Uses")  # All 3 params
```

### Semantic Errors

**Error: Wrong cardinality**
- Diagram shows one-to-one, spec says one-to-many
- **Fix**: Correct cardinality to match business rules

**Error: Missing entity**
- Spec mentions "Comments" table, not in diagram
- **Fix**: Add missing entity and relationships

**Error: Incorrect sequence**
- API flow steps out of order
- **Fix**: Reorder steps to match specification

**Error: Wrong technology**
- Diagram says "MySQL", spec says "PostgreSQL"
- **Fix**: Update technology to match architecture decisions

### Platform Errors

**Error: Diagram renders locally but not on GitHub**
- Possible cause: GitHub Mermaid version incompatibility
- **Fix**: Simplify diagram, avoid bleeding-edge features

**Error: Diagram renders on GitHub but not in docs site**
- Possible cause: Missing Mermaid plugin
- **Fix**: Install and configure Mermaid plugin for docs framework

## Validation Workflow Example

**Complete validation process**:

```markdown
## Step 1: Generate Diagram
1. Read architectural spec
2. Select appropriate template
3. Fill template with spec data
4. Generate Mermaid code

## Step 2: Syntax Validation
1. Copy diagram code
2. Paste into https://mermaid.live
3. Verify no syntax errors
4. Fix any errors, repeat until valid

## Step 3: Semantic Validation
1. Compare diagram to spec side-by-side
2. Verify all elements present
3. Check relationship accuracy
4. Confirm naming consistency
5. Fix any inaccuracies

## Step 4: Platform Validation
1. Embed diagram in markdown file
2. Push to GitHub (or target platform)
3. View in web interface
4. Verify rendering
5. Test on mobile if relevant

## Step 5: Visual Validation
1. Review diagram clarity
2. Check readability on different screen sizes
3. Ensure labels are descriptive
4. Verify no overlapping elements
5. Add legend if needed

## Step 6: Documentation
1. Add diagram to architecture doc
2. Provide context paragraph before diagram
3. Explain key elements after diagram
4. Link to related diagrams
5. Commit and push
```

## Automated Validation (Advanced)

### CI/CD Integration

**GitHub Actions Example**:
```yaml
name: Validate Mermaid Diagrams

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Mermaid CLI
        run: npm install -g @mermaid-js/mermaid-cli
      - name: Validate diagrams
        run: |
          find docs -name "*.md" -exec mmdc -i {} -o /tmp/output.png \;
```

**Benefits**:
- Automatic syntax validation on PR
- Catches errors before merge
- Ensures all diagrams remain valid

### Pre-commit Hook

**Example hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Find all mermaid code blocks
# Validate syntax with mmdc
# Reject commit if validation fails
```

## Validation Tools Reference

| Tool | Type | Best For | Setup Required |
|------|------|----------|----------------|
| **Mermaid Live Editor** | Web | Quick syntax checks | None |
| **GitHub Preview** | Platform | End-to-end validation | Git repo |
| **VSCode Extension** | Local | Rapid iteration | Extension install |
| **Mermaid CLI** | CLI | Automation, CI/CD | Node.js install |
| **Browser DevTools** | Debug | Troubleshooting | Browser only |

## Troubleshooting Validation Issues

**Issue: Diagram valid in Live Editor but not GitHub**
- Check GitHub Mermaid version compatibility
- Simplify diagram (reduce complexity)
- Remove advanced features
- Test with minimal example

**Issue: Diagram breaks on specific platform**
- Consult platform Mermaid documentation
- Check required plugins installed
- Verify platform configuration
- Use fallback ASCII diagram

**Issue: Diagram too large to render**
- Split into multiple smaller diagrams
- Reduce number of elements
- Simplify relationships
- Use layered approach (context → container → component)

**Issue: Syntax seems correct but won't validate**
- Check for invisible characters (copy/paste issues)
- Verify line endings (CRLF vs LF)
- Escape special characters in strings
- Test minimal version to isolate issue

## Best Practices for Validation

**1. Validate Early and Often**
- Test syntax after each section
- Don't wait until diagram is complete
- Catch errors when context is fresh

**2. Use Multiple Validation Methods**
- Mermaid Live Editor for syntax
- GitHub preview for platform compatibility
- Side-by-side spec comparison for semantics

**3. Keep Validation Checklist**
- Use template validation checklists
- Document custom validation criteria
- Share checklist with team

**4. Test in Target Environment**
- Always validate where diagram will be deployed
- Don't assume local validation equals production
- Test on multiple devices/browsers if public-facing

**5. Document Validation Issues**
- Keep log of common errors
- Share fixes with team
- Update templates to prevent repeat issues

## Related References

- Mermaid syntax: See `mermaid-syntax-guide.md`
- Common errors and fixes: See `troubleshooting.md`
- Template examples: See `templates/` directory
