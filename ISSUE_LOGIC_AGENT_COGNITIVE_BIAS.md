# Issue: Enhance Logic Agent with Kahneman's Cognitive Bias Recognition

## Problem Description
The Logic Agent currently lacks sufficient context and framework to effectively recognize and address cognitive biases in strategic reasoning. While it validates logical arguments, it doesn't have the depth of psychological insight needed to identify common thinking errors that affect strategic decision-making.

## Current Behavior
- Logic Agent focuses primarily on deductive reasoning validation
- Limited ability to identify cognitive biases in user's strategic thinking
- No systematic framework for bias detection and mitigation
- Misses opportunities to challenge assumptions rooted in psychological biases

## Expected Behavior
- Logic Agent should recognize common cognitive biases from Kahneman's framework
- Proactively identify when strategic decisions might be affected by:
  - Anchoring bias
  - Availability heuristic
  - Confirmation bias
  - Overconfidence bias
  - Loss aversion
  - Planning fallacy
  - Hindsight bias
  - Framing effects
- Provide specific guidance to counteract identified biases
- Use System 1 vs System 2 thinking framework to improve decision quality

## Resource Available
- **Daniel Kahneman - Thinking, Fast and Slow.pdf** has been added to `agents/strategy-logic-agent-docs/`
- This comprehensive resource contains:
  - Detailed explanations of cognitive biases
  - System 1 (fast, intuitive) vs System 2 (slow, deliberate) thinking
  - Real-world examples of biases in business decisions
  - Strategies for bias mitigation

## Implementation Requirements

### 1. Content Extraction from Kahneman's Work
Extract and synthesize key concepts:
- **Two Systems Framework**
  - System 1: Automatic, fast, intuitive, emotional
  - System 2: Deliberate, slow, logical, calculating
  
- **Key Cognitive Biases for Strategic Thinking**
  - **Anchoring**: Over-reliance on first piece of information
  - **Availability Heuristic**: Overweighting easily recalled examples
  - **Confirmation Bias**: Seeking information that confirms existing beliefs
  - **Planning Fallacy**: Underestimating time and resources needed
  - **Overconfidence**: Excessive confidence in own judgments
  - **Loss Aversion**: Weighing losses more heavily than gains
  - **Sunk Cost Fallacy**: Continuing due to past investments
  - **Halo Effect**: One positive trait influences overall judgment

### 2. Enhanced Logic Agent Prompts
Update the Logic Agent's system prompts to include:

```python
COGNITIVE_BIAS_CONTEXT = """
You are equipped with Daniel Kahneman's framework for identifying cognitive biases.
When evaluating strategic arguments, check for these common biases:

1. ANCHORING BIAS: Is the strategy overly influenced by initial information?
   - Question: "What if we started with different assumptions?"
   
2. AVAILABILITY HEURISTIC: Are recent/memorable events overweighted?
   - Question: "Are we basing this on systematic data or memorable anecdotes?"
   
3. CONFIRMATION BIAS: Is contradictory evidence being ignored?
   - Question: "What evidence would convince us we're wrong?"
   
4. PLANNING FALLACY: Are timelines and resources realistic?
   - Question: "What similar projects took longer than expected?"
   
5. OVERCONFIDENCE: Is uncertainty being underestimated?
   - Question: "What's our confidence interval, not just point estimate?"

For each identified bias, provide:
- Specific evidence of the bias
- Potential impact on strategy
- Debiasing technique to apply
"""
```

### 3. Bias Detection Logic
Implement systematic bias checking:

```python
def detect_cognitive_biases(strategic_argument):
    biases_detected = []
    
    # Check for anchoring
    if contains_absolute_statements(argument):
        biases_detected.append({
            "bias": "Anchoring",
            "evidence": "Strong attachment to initial assumptions",
            "mitigation": "Consider alternative starting points"
        })
    
    # Check for availability heuristic
    if relies_on_anecdotes(argument):
        biases_detected.append({
            "bias": "Availability Heuristic",
            "evidence": "Overreliance on easily recalled examples",
            "mitigation": "Seek systematic data, not just memorable cases"
        })
    
    # Check for planning fallacy
    if contains_optimistic_timelines(argument):
        biases_detected.append({
            "bias": "Planning Fallacy",
            "evidence": "Timelines seem optimistic without buffers",
            "mitigation": "Use reference class forecasting"
        })
    
    return biases_detected
```

### 4. Integration with Existing Logic Framework
- Maintain current deductive logic validation
- Add cognitive bias layer as complementary analysis
- Provide both logical and psychological assessment
- Synthesize findings into actionable recommendations

## Acceptance Criteria
- [ ] Logic Agent successfully identifies at least 8 major cognitive biases
- [ ] Each bias detection includes specific evidence from user's input
- [ ] Debiasing techniques are provided for each identified bias
- [ ] System 1 vs System 2 framework is used to guide thinking
- [ ] Integration doesn't disrupt existing logical validation
- [ ] Responses balance logical rigor with psychological insight
- [ ] User receives actionable guidance to improve decision quality

## Testing Scenarios
1. **Anchoring Test**: Present strategy heavily based on competitor's approach
2. **Availability Test**: Strategy based on recent market event
3. **Confirmation Bias Test**: Strategy ignoring contradictory market data
4. **Planning Fallacy Test**: Aggressive timeline for complex implementation
5. **Overconfidence Test**: Strategy with no risk mitigation
6. **Loss Aversion Test**: Strategy avoiding necessary changes due to sunk costs

## Implementation Priority
**High Priority** - This enhancement significantly improves the quality of strategic reasoning by addressing the psychological factors that often derail logical thinking.

## Related Files
- `src/agents/logic_agent.py` - Main Logic Agent implementation
- `src/utils/prompts.py` - Prompt templates
- `agents/strategy-logic-agent-docs/Daniel Kahneman-Thinking, Fast and Slow.pdf` - Source material
- `tests/agents/test_logic_agent.py` - Test cases for bias detection

## Expected Outcomes
- More robust strategic decisions by identifying hidden biases
- Users become aware of their cognitive blind spots
- Strategies are tested against both logical and psychological frameworks
- Improved decision quality through systematic bias mitigation
- Educational value as users learn about cognitive biases

---
**Date Reported**: 2025-08-14  
**Reported By**: User Request  
**Status**: Open  
**Priority**: High  
**Category**: Agent Enhancement - Cognitive Psychology Integration