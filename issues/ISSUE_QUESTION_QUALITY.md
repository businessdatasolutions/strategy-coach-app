# Issue: Improve question quality - reduce verbosity and avoid cognitive biases

## Problem Description

The strategy coach's responses are sometimes too verbose and ask multiple questions in a single response, which can overwhelm users and reduce engagement quality. Additionally, the coach should be aware of and avoid common question biases that could lead to poor strategic decisions.

## Current Issues

1. **Excessive Verbosity**: Responses are often too long and contain unnecessary explanations
2. **Multiple Questions**: Several questions are bundled in one response, making it difficult for users to focus
3. **Potential Biases**: Questions may inadvertently introduce cognitive biases

## Proposed Improvements

### 1. Response Guidelines
- Limit responses to 2-3 concise paragraphs
- Ask only ONE primary question per response
- Use clear, simple language without jargon
- Provide context only when necessary

### 2. Common Question Biases to Avoid

**Leading Questions**
- ❌ "Don't you think your strategy should focus on innovation?"
- ✅ "What role does innovation play in your strategy?"

**Confirmation Bias**
- ❌ "Your success in X confirms that this approach works, right?"
- ✅ "What evidence supports or challenges this approach?"

**Anchoring Bias**
- ❌ "Since competitors charge $100, where would you price?"
- ✅ "How would you determine your pricing strategy?"

**Availability Heuristic**
- ❌ "Given the recent failure of Company X, how will you avoid the same?"
- ✅ "What risks do you see in your industry?"

**False Dichotomy**
- ❌ "Should you focus on growth or profitability?"
- ✅ "How do you balance different strategic priorities?"

**Assumption-Loaded Questions**
- ❌ "How will you implement digital transformation?"
- ✅ "What role might technology play in your strategy?"

**Status Quo Bias**
- ❌ "Why change what's already working?"
- ✅ "What factors would influence strategic changes?"

**Hindsight Bias**
- ❌ "It's obvious now why that strategy failed, isn't it?"
- ✅ "What can we learn from past strategic decisions?"

**Framing Effects**
- ❌ "You could lose 30% market share without action"
- ✅ "How do you assess your market position?"

**Social Desirability Bias**
- ❌ "How does your sustainable strategy help society?"
- ✅ "What factors influence your strategic choices?"

## Implementation Suggestions

### Update Prompt Templates
Modify agent prompts in `src/utils/prompts.py` to include:
- Question quality guidelines
- Bias awareness instructions
- One-question-per-response rule

### Enhance Synthesizer Logic
Update `src/agents/synthesizer.py` to:
- Limit response length
- Extract and present single focused questions
- Filter out biased language patterns

### Add Validation Layer
Consider adding a bias-checking mechanism that reviews questions before sending to users.

## Acceptance Criteria

- [ ] Responses limited to 150-200 words typically
- [ ] Only one primary question per response
- [ ] No leading or assumption-loaded questions
- [ ] Clear, unbiased language throughout
- [ ] User feedback shows improved engagement

## Priority
High - This directly impacts user experience and decision quality

## Labels
- enhancement
- UX
- ai-quality
- cognitive-bias