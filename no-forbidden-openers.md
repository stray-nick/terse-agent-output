---
description: Enforce the Runway output style. Abort mid-stream when a response opens with forbidden preamble or closes with forbidden filler.
condition: ["(?i)^(great question|sure!?|certainly|of course!?|let me (explain|show|start|break|walk|look|check|see|think|understand)|i'll (explain|start|show|walk|break|help|go ahead)|i'm going to|looking at your|to answer your question|happy to help|i'd be happy to|absolutely[,!?]|perfect[,!?]|good question|hope this helps|let me know if|feel free to|don't hesitate to)"]
interruptMode: always
scope: text
---

You opened or closed with a forbidden phrase from the Runway output style.

Forbidden openers: "Great question", "Good question", "Let me...", "I'll...", "I'm going to...", "Sure!", "Certainly", "Of course", "Happy to help", "I'd be happy to", "Absolutely", "Perfect", "Looking at your...", "To answer your question".

Forbidden closers: "Hope this helps", "Let me know if you need anything else", "Feel free to ask", "Don't hesitate to".

Rewrite the response. Start with the answer or the next action. Stop when the answer is complete. No preamble, no recap, no closer.
