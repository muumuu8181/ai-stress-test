# AI Stress Test

Testing how many high-quality components can be built in 1 week using Jules + Codex CR pipeline.

## Structure

```
components/
  001-component-name/   # Each directory = 1 complete, working component
  002-component-name/
  ...
```

## Quality Standards

Every component must include:
- Comprehensive test suite (unit + integration + edge cases)
- Type hints/annotations on all public APIs
- Clear README with usage examples
- No external dependencies unless explicitly specified in the Issue

## Pipeline

1. Issue (with `jules` label) → Jules creates PR
2. Codex CR reviews PR
3. Claude transfers feedback if needed
4. Jules fixes issues
5. Auto-merge (if no destructive changes)

## Metrics

- Components completed
- Average test count per component
- Bug rate (Codex CR findings / component)
- Time from Issue creation to merge
