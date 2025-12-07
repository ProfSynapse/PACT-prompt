# Diagram Examples

This directory contains complete, production-ready examples of Mermaid diagrams for common architectural scenarios. All Mermaid code has been validated and tested for correct rendering.

## Purpose

These examples serve as:
- **Reference implementations**: Copy and adapt for similar use cases
- **Learning resources**: Study complete diagrams in context
- **Template validation**: Demonstrate proper usage of diagram templates
- **Best practices showcase**: See architectural patterns applied correctly

## Available Examples

### 1. E-Commerce Architecture (`e-commerce-architecture.md`)

**Scenario**: Complete architecture for an online retail platform

**Includes**:
- C4 Context diagram (system boundary, external integrations)
- C4 Container diagram (microservices, databases, message queues)
- C4 Component diagram (internal structure of Order Service)
- Component dependency graph (showing service dependencies)

**Use cases**:
- E-commerce platforms
- Multi-service architectures
- Payment processing integrations
- Inventory management systems

**Key patterns demonstrated**:
- Microservices architecture
- API Gateway pattern
- Event-driven communication
- Database per service pattern

---

### 2. Authentication Flow (`authentication-flow.md`)

**Scenario**: OAuth 2.0 and JWT authentication sequences

**Includes**:
- OAuth 2.0 Authorization Code flow
- JWT token authentication flow
- Social login integration (Google, GitHub)
- Token refresh sequence
- Multi-factor authentication (2FA) flow

**Use cases**:
- User authentication systems
- Single Sign-On (SSO) implementations
- API security
- Mobile app authentication

**Key patterns demonstrated**:
- OAuth 2.0 Authorization Code Grant
- JWT token-based authentication
- Refresh token rotation
- 2FA verification flow

---

## How to Use These Examples

### For Learning

1. **Read the scenario**: Understand the architectural context
2. **Study the diagrams**: Analyze element choices and relationships
3. **Review the explanations**: Learn why specific patterns were chosen
4. **Test rendering**: Copy Mermaid code to https://mermaid.live to see live rendering

### For Adaptation

1. **Identify similar scenario**: Find example closest to your use case
2. **Copy Mermaid code**: Use as starting template
3. **Modify elements**: Replace names, technologies, relationships
4. **Validate syntax**: Test in Mermaid Live Editor
5. **Customize styling**: Adjust colors, layout as needed

### For Reference

1. **Compare with your architecture**: See how patterns apply
2. **Check syntax details**: Reference correct Mermaid syntax
3. **Validate abstraction levels**: Ensure correct C4 level usage
4. **Review relationship patterns**: Learn effective labeling

## Example File Structure

Each example file follows this structure:

```markdown
# [Example Name]

## Scenario
Brief description of the architectural context

## Architecture Overview
High-level summary of the system

## Diagrams

### [Diagram Type]
[Explanation of what the diagram shows]

```mermaid
[Validated Mermaid code]
```

**Key Elements**:
- Explanation of important elements
- Technology choices and rationale

**Tips for Adaptation**:
- How to modify for similar use cases
```

## Diagram Rendering

All diagrams in these examples:
- ✅ Have been validated in Mermaid Live Editor (https://mermaid.live)
- ✅ Use correct, current Mermaid syntax
- ✅ Render correctly in GitHub, GitLab, and VSCode
- ✅ Follow C4 model conventions
- ✅ Include descriptive labels and relationships

## Testing Your Adaptations

After modifying example diagrams for your use case:

1. **Syntax Validation**:
   - Copy to Mermaid Live Editor (https://mermaid.live)
   - Verify diagram renders without errors
   - Check layout and readability

2. **Content Validation**:
   - Ensure all placeholders replaced with actual values
   - Verify relationship directions are correct
   - Confirm all referenced elements are defined

3. **Abstraction Validation**:
   - Check diagram is at correct C4 level
   - Ensure consistent abstraction (don't mix levels)
   - Validate appropriate detail for audience

4. **Documentation Integration**:
   - Embed in architecture markdown files
   - Add context and explanations around diagram
   - Link related diagrams (Context → Container → Component)

## Common Modifications

### Changing Technologies

```mermaid
%% Original
Container(api, "API", "Node.js/Express", "REST API")

%% Modified for Python
Container(api, "API", "Python/Flask", "REST API")

%% Modified for Java
Container(api, "API", "Java/Spring Boot", "REST API")
```

### Changing Database Types

```mermaid
%% Original
ContainerDb(db, "Database", "PostgreSQL", "Relational data")

%% Modified for MongoDB
ContainerDb(db, "Database", "MongoDB", "Document store")

%% Modified for DynamoDB
ContainerDb(db, "Database", "DynamoDB", "NoSQL database")
```

### Changing Cloud Providers

```mermaid
%% Original (AWS)
Container(storage, "Object Storage", "AWS S3")
ContainerQueue(queue, "Message Queue", "AWS SQS")

%% Modified for Azure
Container(storage, "Object Storage", "Azure Blob Storage")
ContainerQueue(queue, "Message Queue", "Azure Service Bus")

%% Modified for GCP
Container(storage, "Object Storage", "Google Cloud Storage")
ContainerQueue(queue, "Message Queue", "Google Pub/Sub")
```

### Adding Security Layers

```mermaid
%% Add authentication middleware
Container(authMiddleware, "Auth Middleware", "OAuth 2.0", "Token validation")

%% Add API Gateway
Container(apiGateway, "API Gateway", "Kong", "Rate limiting, auth, routing")

%% Add WAF
Container(waf, "Web Application Firewall", "AWS WAF", "DDoS protection")
```

## Extending Examples

To create new examples for this directory:

1. **Choose a clear scenario**: Focus on specific use case
2. **Include multiple diagram types**: Context, Container, Component, Sequence
3. **Add comprehensive explanations**: Why choices were made
4. **Validate all Mermaid syntax**: Test rendering thoroughly
5. **Provide adaptation tips**: Help others customize for their needs
6. **Follow existing structure**: Match format of current examples

## Related Resources

- **Templates**: See `../templates/` for base templates with placeholders
- **References**: See `../references/` for C4 patterns and syntax guides
- **SKILL.md**: See `../SKILL.md` for overall workflow guidance

## Feedback and Contributions

If you create diagrams based on these examples:
- Share feedback on clarity and usability
- Suggest additional example scenarios
- Report syntax issues or rendering problems
- Contribute new examples for common patterns

## Quick Start

**First time using these examples?**

1. Start with `e-commerce-architecture.md` to see complete C4 hierarchy
2. Study `authentication-flow.md` for sequence diagram patterns
3. Choose example closest to your use case
4. Copy and adapt Mermaid code
5. Validate in Mermaid Live Editor
6. Embed in your architecture documentation

**Need help?**
- Review template files in `../templates/` for placeholder guides
- Check `../references/c4-mermaid-patterns.md` for architectural patterns
- Consult `../references/troubleshooting.md` for common syntax issues
