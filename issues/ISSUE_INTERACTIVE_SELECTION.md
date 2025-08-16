# Issue: Add Interactive Selection for Multiple Choice Questions

## Problem Description

When the strategy coach presents a list of statements or options (e.g., "Which of these resonates with you?"), users currently have to type their responses. This creates friction and makes it difficult to select multiple items efficiently. Users should be able to point and click to select options interactively.

## Current Behavior

**Example scenario:**
```
Coach: "Here are several strategic approaches. Please indicate which ones resonate most with your vision:
1. Customer-centric innovation
2. Operational excellence
3. Market disruption
4. Partnership ecosystem
5. Sustainability leadership
6. Digital transformation
7. Geographic expansion
8. Premium positioning"

User: (Has to type) "I choose 1, 3, and 6"
```

## Desired Behavior

The UI should display clickable options when the coach presents multiple choices, allowing users to:
- Click to select/deselect options
- See visual feedback for selected items
- Submit all selections with one action
- Clear selections if needed

## Proposed Solution

### 1. Backend Changes

#### API Response Structure
Add a new field to `ConversationMessageResponse` in `src/api/main.py`:
```python
class ConversationMessageResponse(BaseModel):
    response: str
    current_phase: str
    current_agent: Optional[str]
    completeness_percentage: float
    questions: List[str]
    recommendations: List[str]
    session_id: str
    # NEW: Interactive elements
    interactive_elements: Optional[Dict[str, Any]] = None
```

#### Interactive Element Format
```json
{
  "type": "multi_select",
  "prompt": "Which approaches resonate with your vision?",
  "options": [
    {"id": "1", "text": "Customer-centric innovation", "category": "strategy"},
    {"id": "2", "text": "Operational excellence", "category": "operations"},
    {"id": "3", "text": "Market disruption", "category": "strategy"}
  ],
  "min_selections": 1,
  "max_selections": 3,
  "allow_other": true
}
```

### 2. Frontend Implementation

#### Update `web/index.html` to handle interactive elements:

```javascript
// Add to Alpine.js data
interactiveMode: false,
selectedOptions: [],
currentInteractive: null,

// Method to handle interactive elements
handleInteractiveElement(element) {
    this.interactiveMode = true;
    this.currentInteractive = element;
    this.selectedOptions = [];
},

// Toggle option selection
toggleOption(optionId) {
    const index = this.selectedOptions.indexOf(optionId);
    if (index > -1) {
        this.selectedOptions.splice(index, 1);
    } else {
        if (this.selectedOptions.length < this.currentInteractive.max_selections) {
            this.selectedOptions.push(optionId);
        }
    }
},

// Submit selections
submitSelections() {
    const selectedTexts = this.selectedOptions.map(id => 
        this.currentInteractive.options.find(opt => opt.id === id).text
    );
    const message = `I select: ${selectedTexts.join(', ')}`;
    this.sendMessage(message);
    this.interactiveMode = false;
    this.currentInteractive = null;
}
```

#### HTML Template for Interactive Selection:
```html
<!-- Interactive Selection Panel -->
<div x-show="interactiveMode" x-cloak 
     class="bg-blue-50 border-2 border-blue-200 rounded-xl p-6 mb-4">
    <h3 class="font-semibold text-gray-800 mb-4" x-text="currentInteractive?.prompt"></h3>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        <template x-for="option in currentInteractive?.options" :key="option.id">
            <div @click="toggleOption(option.id)"
                 :class="selectedOptions.includes(option.id) 
                     ? 'bg-blue-100 border-blue-500 shadow-md' 
                     : 'bg-white border-gray-300 hover:border-blue-400'"
                 class="border-2 rounded-lg p-4 cursor-pointer transition-all duration-200">
                
                <div class="flex items-start">
                    <div class="flex-shrink-0 mr-3">
                        <div :class="selectedOptions.includes(option.id) 
                                ? 'bg-blue-500 border-blue-500' 
                                : 'bg-white border-gray-400'"
                             class="w-5 h-5 rounded border-2 flex items-center justify-center">
                            <svg x-show="selectedOptions.includes(option.id)" 
                                 class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" 
                                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
                                      clip-rule="evenodd"></path>
                            </svg>
                        </div>
                    </div>
                    <div class="flex-grow">
                        <p class="text-gray-800 font-medium" x-text="option.text"></p>
                        <p x-show="option.category" 
                           class="text-xs text-gray-500 mt-1" 
                           x-text="'Category: ' + option.category"></p>
                    </div>
                </div>
            </div>
        </template>
    </div>
    
    <div class="flex justify-between items-center">
        <p class="text-sm text-gray-600">
            <span x-text="selectedOptions.length"></span> of 
            <span x-text="currentInteractive?.max_selections"></span> selected
        </p>
        <div class="space-x-2">
            <button @click="selectedOptions = []" 
                    class="px-4 py-2 text-gray-600 hover:text-gray-800">
                Clear
            </button>
            <button @click="submitSelections()" 
                    :disabled="selectedOptions.length < (currentInteractive?.min_selections || 1)"
                    class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                           disabled:bg-gray-300 disabled:cursor-not-allowed">
                Submit Selection
            </button>
        </div>
    </div>
</div>
```

### 3. Agent Updates

Update agents to return interactive elements when appropriate:

```python
# In src/agents/why_agent.py or other agents
def generate_interactive_beliefs_selection(self):
    return {
        "type": "multi_select",
        "prompt": "Which of these belief statements resonate with your organization?",
        "options": [
            {"id": "1", "text": "People are our greatest asset", "category": "human"},
            {"id": "2", "text": "Innovation drives growth", "category": "strategy"},
            {"id": "3", "text": "Customer success is our success", "category": "customer"},
            # ... more options
        ],
        "min_selections": 2,
        "max_selections": 5
    }
```

## Use Cases

1. **Purpose Discovery (WHY Agent)**
   - Select core beliefs
   - Choose values that resonate
   - Pick inspiring examples

2. **Strategy Formulation (HOW Agent)**
   - Select strategic approaches
   - Choose relevant analogies
   - Pick implementation methods

3. **Implementation Planning (WHAT Agent)**
   - Select stakeholder groups
   - Choose priority initiatives
   - Pick resource allocation options

## Benefits

1. **Improved UX**: Point-and-click is more intuitive than typing
2. **Reduced Errors**: No typos or format issues
3. **Visual Feedback**: Users see their selections clearly
4. **Faster Interaction**: Multiple selections in one action
5. **Better Data**: Structured responses for better analysis

## Acceptance Criteria

- [ ] Interactive selection UI renders when coach provides options
- [ ] Users can click to select/deselect options
- [ ] Visual feedback shows selected state
- [ ] Selections respect min/max constraints
- [ ] Submit button sends structured response
- [ ] Mobile-responsive touch interactions work
- [ ] Keyboard navigation supported (accessibility)
- [ ] Selected options are clearly communicated back to the coach

## Technical Considerations

- Ensure backward compatibility with text-based responses
- Consider adding single-select radio buttons for exclusive choices
- Add support for "Other" option with text input
- Consider adding drag-and-drop for ranking/prioritization
- Store structured selection data for analytics

## Priority
High - This significantly improves user experience and data quality

## Labels
- enhancement
- UX
- frontend
- interactive-ui
- accessibility