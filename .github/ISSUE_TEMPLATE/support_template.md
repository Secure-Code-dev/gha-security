---
name: Support request
about: Get help with using our GitHub Actions
title: '[SUPPORT] '
labels: ['question', 'support']
assignees: ''
---

## Support Request Type
**What type of help do you need?**
- [ ] Configuration help
- [ ] Usage questions
- [ ] Integration guidance
- [ ] Troubleshooting
- [ ] Best practices
- [ ] Documentation clarification
- [ ] Other: [please specify]

## Question/Issue
**What do you need help with?**
A clear and concise description of your question or the issue you're experiencing.

## What You've Tried
**What have you already attempted?**
- [ ] Read the documentation
- [ ] Searched existing issues
- [ ] Tried different configuration options
- [ ] Looked at example workflows
- [ ] Other: [please describe]

## Current Setup
**Environment Information:**
- OS/Runner: [e.g. ubuntu-latest, windows-latest, macos-latest]
- Action Version: [e.g. v2.1.0]
- Repository Type: [e.g. public, private]

## Current Configuration
**Your current workflow configuration:**
```yaml
# Paste your current workflow configuration here
name: Your Workflow
on: [push]
jobs:
  security-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: securecode-llc/secure-analyzer@v2
        with:
          # Your current configuration
```

## Expected Outcome
**What are you trying to achieve?**
Describe what you want your workflow to do or what result you're expecting.

## Documentation Reference
**Which documentation did you reference?**
- [ ] README.md
- [ ] Action marketplace page
- [ ] Example workflows
- [ ] Other documentation: [please specify]
- [ ] No documentation found for my use case

## Error Messages (if any)
```
Paste any error messages or unexpected output here
```

## Additional Context
**Is there anything else that might help us assist you?**
- Project type or programming language
- Specific security requirements
- Integration with other tools
- Timeline or urgency
- Team size or organizational context

## Checklist
- [ ] I have searched existing issues for similar questions
- [ ] I have provided my current configuration
- [ ] I have described what I'm trying to achieve
- [ ] I have included any relevant error messages
