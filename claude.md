# Claude Code Development Guide

## Purpose & Philosophy

This guide establishes sound coding practices for reviewing, refactoring, and evolving existing codebases. It balances **proven engineering principles** with **creative problem-solving** and **experimental innovation**. When working on existing programs, prioritize understanding before changing, and always consider both immediate improvements and long-term maintainability.

**Core Values:**
- Clarity over cleverness
- Simplicity over complexity
- Adaptability over rigidity
- Collaboration over isolation
- Experimentation within structure

---

## I. SOLID Principles

The SOLID principles form the foundation of maintainable object-oriented design. Apply these when refactoring classes and interfaces.

### Single Responsibility Principle (SRP)
**A class should have only one reason to change.**

- Each class should focus on a single concern or responsibility
- If you can describe a class's purpose with "and" or "or", it likely violates SRP
- Separate data access, business logic, and presentation concerns
- High cohesion within modules leads to easier testing and maintenance

**When reviewing:** Look for classes doing multiple unrelated things. Extract responsibilities into focused, purpose-driven classes.

### Open/Closed Principle (OCP)
**Software entities should be open for extension but closed for modification.**

- Design systems that can grow through extension rather than modification
- Use abstraction (interfaces, abstract classes) to enable new behavior
- Protect stable code from changes when adding features
- Leverage composition and dependency injection

**When reviewing:** If adding features requires modifying existing stable code, consider introducing abstractions or extension points.

### Liskov Substitution Principle (LSP)
**Subtypes must be substitutable for their base types without altering program correctness.**

- Derived classes should honor the contract established by base classes
- Don't strengthen preconditions or weaken postconditions in subclasses
- Avoid surprising behavior in inheritance hierarchies
- If a subtype can't properly replace its parent, reconsider the inheritance

**When reviewing:** Check if polymorphic code would break with different subtype implementations. Ensure derived classes don't violate base class contracts.

### Interface Segregation Principle (ISP)
**Clients should not be forced to depend on interfaces they don't use.**

- Create focused, client-specific interfaces rather than large, general-purpose ones
- Many small interfaces are better than one large interface
- Reduces coupling and makes systems more flexible
- Prevents "fat interfaces" that burden implementers with unused methods

**When reviewing:** Look for interfaces forcing implementations to define methods they don't need. Split into smaller, more cohesive interfaces.

### Dependency Inversion Principle (DIP)
**High-level modules should not depend on low-level modules. Both should depend on abstractions.**

- Depend on interfaces/abstractions, not concrete implementations
- Reduces coupling between components
- Enables easier testing through dependency injection
- Facilitates swapping implementations without changing consumers

**When reviewing:** Check if high-level logic directly instantiates or depends on low-level details. Introduce abstractions to invert the dependency.

---

## II. Fundamental Code Quality Principles

### DRY (Don't Repeat Yourself)
**Every piece of knowledge must have a single, unambiguous, authoritative representation.**

- Duplication isn't just about identical code—it's about duplicated intent
- When the same knowledge exists in multiple places, changes require multiple updates
- Extract common patterns into reusable functions, classes, or modules
- Use abstraction to eliminate redundancy while maintaining clarity

**Application:**
- Identify duplicated business logic and centralize it
- Create utility functions for repeated operations
- Use configuration over hard-coded values
- Balance DRY with readability—abstraction should clarify, not obscure

**When reviewing:** If you see similar code in multiple locations, ask: "Is this the same knowledge?" If yes, consolidate. If no, similar code serving different purposes may be acceptable.

### KISS (Keep It Simple, Stupid)
**Simplicity should be a key goal in design; unnecessary complexity should be avoided.**

- Simple solutions are easier to understand, test, and maintain
- Avoid over-engineering and premature optimization
- Straightforward code is less prone to bugs than clever code
- Use the simplest approach that solves the problem effectively

**Application:**
- Choose clarity over cleverness in implementation
- Avoid unnecessary abstractions and patterns
- Write code as if the next person to maintain it knows less than you
- Refactor complex logic into smaller, understandable pieces

**Important:** Simple ≠ Easy. Simple means few moving parts and low complexity. Achieving simplicity often requires significant thought and effort.

**When reviewing:** If you can't explain how code works in 30 seconds, it may be too complex. Simplify logic, improve naming, or add clarifying comments.

### YAGNI (You Aren't Gonna Need It)
**Don't implement functionality until it's actually needed.**

- Avoid building features "just in case" or for hypothetical future needs
- Focus on current requirements and iterate based on real needs
- Reduces code complexity and maintenance burden
- Supports agile, iterative development

**Application:**
- Implement only what's required for current user stories/tasks
- Resist the temptation to add "nice to have" features
- Trust that you can add functionality later when truly needed
- Keep the codebase lean and focused

**When reviewing:** Question any code that isn't serving a current, concrete need. If it's speculative, consider removing it until it's actually required.

---

## III. Clean Code Principles (Robert C. Martin)

Clean Code emphasizes craftsmanship—writing code that reads like well-written prose and clearly communicates intent.

### Meaningful Names
**Names should reveal intent without requiring additional explanation.**

- Use intention-revealing names: `getUserAccountBalance()` not `getData()`
- Make names searchable: `DAYS_PER_WEEK` not `7`
- Avoid mental mapping: explicit names beat abbreviations
- Use problem-domain or solution-domain terminology consistently
- Classes should be nouns; methods should be verbs

### Functions
**Functions should be small and do one thing well.**

- Functions should do one thing at one level of abstraction
- Keep functions short—ideally under 20 lines, definitely under 50
- Extract complex logic into well-named helper functions
- Minimize function arguments (0-2 ideal, 3 acceptable, 4+ requires refactoring)
- Avoid side effects—functions should not surprise the caller
- Command-Query Separation: functions either change state OR return information, not both

### Comments
**Good code mostly documents itself; comments explain the "why," not the "what."**

- Prefer expressive code over explanatory comments
- Use comments to explain intent, rationale, or consequences
- Avoid obvious comments that just restate code
- Remove commented-out code (version control preserves history)
- TODOs are acceptable but should be tracked and resolved

### Error Handling
**Use exceptions rather than return codes; provide meaningful context.**

- Use exceptions for exceptional conditions
- Write try-catch-finally blocks first when handling errors
- Provide context with exceptions (what failed and why)
- Don't return or pass null—use Optional/Maybe or empty collections
- Define exception classes based on caller needs, not implementation details

### Formatting
**Consistent formatting aids readability and reduces cognitive load.**

- Vertical formatting: related concepts close together, blank lines separate sections
- Keep files focused and reasonably sized
- Horizontal formatting: avoid long lines, use whitespace for clarity
- Team should agree on and enforce formatting rules (use automated formatters)

### Objects and Data Structures
**Hide internal structure; expose operations.**

- Objects hide data and expose operations (methods)
- Data structures expose data and have minimal operations
- Avoid hybrid structures that are neither clear objects nor clear data structures
- The Law of Demeter: objects should only talk to immediate friends, not strangers
  - `object.getA().getB().doSomething()` violates this (train wreck)
  - Better: `object.doSomething()` (tell, don't ask)

### Testing
**Tests are as important as production code.**

- Write tests first when possible (TDD: Test-Driven Development)
- Tests should be F.I.R.S.T.:
  - **Fast**: Run quickly
  - **Independent**: No interdependencies between tests
  - **Repeatable**: Same result every time
  - **Self-validating**: Pass or fail, no manual checking
  - **Timely**: Written just before production code
- One assert per test concept (not necessarily one assert call)
- Clean tests follow the same principles as clean code

---

## IV. Domain-Driven Design (DDD) Principles

DDD provides patterns for modeling complex business domains and keeping code aligned with business reality. Particularly valuable when working on business-critical or domain-heavy applications.

### Ubiquitous Language
**Create a shared language between developers and domain experts.**

- Use business terminology in code (classes, methods, variables)
- The code should read like the business speaks
- Avoid technical jargon in domain models
- When the language evolves, refactor code to match
- Continuously refine the model through conversation with domain experts

### Model-Driven Design
**The code IS the model; the model IS the code.**

- Domain model should drive the software design
- Changes to the model should directly translate to code changes
- Keep the model and implementation tightly synchronized
- Use domain objects to encapsulate business logic
- Iterate on the model as you gain deeper domain insight

### Building Blocks

#### Entities
- Objects with a distinct identity that persists over time
- Identity matters more than attributes
- Examples: User, Order, Product
- Implement equals/hashCode based on ID, not attributes

#### Value Objects
- Objects defined by their attributes, not identity
- Immutable by design
- Examples: Money, DateRange, Address
- No concept of "same instance"—equality based on values

#### Aggregates
- Cluster of entities and value objects treated as a unit
- One entity is the aggregate root; external references only through the root
- Enforce invariants and business rules within the aggregate
- Aggregate boundaries define transactional consistency boundaries

#### Services
- Operations that don't naturally belong to entities or value objects
- Stateless operations that represent domain activities
- Named using verbs from the ubiquitous language
- Examples: PaymentProcessor, ShippingCalculator

#### Repositories
- Provide collection-like access to aggregates
- Abstract away data access concerns from domain logic
- Query and retrieve aggregates by identity or criteria
- Only repositories for aggregate roots

#### Factories
- Encapsulate complex creation logic for entities and aggregates
- Ensure objects are created in valid states
- Use when construction requires significant logic or invariant enforcement

### Strategic Design

#### Bounded Contexts
- Explicit boundaries within which a model applies
- Different contexts may have different models for the same concept
- Reduces complexity by limiting model scope
- Clear boundaries enable teams to work independently

#### Context Mapping
- Define relationships between bounded contexts
- Patterns: Partnership, Shared Kernel, Customer/Supplier, Conformist, Anti-Corruption Layer
- Makes integration points and translation needs explicit

### DDD and Refactoring
**Refactor toward deeper insight as you learn more about the domain.**

- Domain understanding evolves throughout the project
- Refactor not just code structure, but the model itself
- Breakthrough insights often come late in development
- Continuous refactoring keeps the model aligned with reality

---

## V. Balancing Principles: Pragmatism & Creativity

### When Principles Conflict
Coding principles are guidelines, not absolute laws. They sometimes conflict, and judgment is required.

**Common Tensions:**
- **DRY vs. KISS**: Excessive abstraction can make code complex. Sometimes small duplication is clearer.
- **YAGNI vs. OCP**: Designing for extension can feel speculative. Balance current needs with reasonable extensibility.
- **Clean Code vs. Performance**: Readable code is usually fast enough. Optimize only when profiling reveals actual bottlenecks.

**Resolution Strategy:**
1. Understand the trade-offs involved
2. Prioritize based on the specific context
3. Document decisions when deviating from principles
4. Revisit decisions as circumstances change

### Encouraging Creativity & Experimentation

**Refactoring as Creative Problem-Solving:**
- View legacy code as a puzzle to solve, not a burden to carry
- Explore multiple solutions before committing to one
- Use small, reversible experiments to test approaches
- Celebrate elegant solutions that simplify complex problems

**Safe Experimentation:**
- Use feature flags to deploy experimental code safely
- Create spike branches to explore risky changes
- Write tests before refactoring to ensure behavior preservation
- Pair program to combine creative exploration with critical review

**Innovation Within Structure:**
- Principles provide guardrails, not cages
- Feel free to break rules when you understand why they exist
- Document intentional deviations with rationale
- Share learnings with the team to evolve collective understanding

---

## VI. Practical Application: Code Review Checklist

When reviewing or refactoring existing code, use this systematic approach:

### Architecture & Design
- [ ] Does the code follow SOLID principles appropriately?
- [ ] Are concerns properly separated (domain, UI, data access)?
- [ ] Is the dependency direction correct (high-level → abstractions ← low-level)?
- [ ] Are bounded contexts and module boundaries clear?

### Code Quality
- [ ] Are names meaningful and intention-revealing?
- [ ] Are functions small and focused on doing one thing?
- [ ] Is duplication eliminated without sacrificing clarity (DRY)?
- [ ] Is the code as simple as possible (KISS)?
- [ ] Does the code serve current needs without speculation (YAGNI)?

### Domain Modeling (if applicable)
- [ ] Does code use ubiquitous language from the business domain?
- [ ] Are entities, value objects, and aggregates properly distinguished?
- [ ] Are invariants and business rules enforced?
- [ ] Is the domain logic isolated from infrastructure concerns?

### Maintainability
- [ ] Can someone unfamiliar with the code understand it quickly?
- [ ] Are error conditions handled gracefully with meaningful messages?
- [ ] Is the code testable with clear, independent tests?
- [ ] Are dependencies injected rather than hard-coded?

### Performance & Scalability
- [ ] Are there obvious performance issues or bottlenecks?
- [ ] Is data fetched efficiently (avoiding N+1 queries, etc.)?
- [ ] Are resources (connections, files, memory) properly managed?

---

## VII. Working with Legacy Code

When revising programs already in development, follow these strategies:

### Understanding Before Changing
1. **Read the code** as you would read a book—understand the narrative
2. **Map dependencies** to see how components interact
3. **Identify seams** where changes can be made safely
4. **Write characterization tests** to capture current behavior

### Incremental Improvement
- **The Boy Scout Rule**: Leave code cleaner than you found it
- Make small, focused changes rather than massive rewrites
- Refactor in small steps with tests confirming each step
- Prioritize high-value, high-impact improvements

### Dealing with Technical Debt
- **Acknowledge debt explicitly** rather than ignoring it
- **Document decisions** that create debt and plans to address it
- **Allocate time** for regular refactoring and cleanup
- **Balance** new features with technical health

### Refactoring Patterns
- **Extract Method**: Break large functions into smaller, named pieces
- **Extract Class**: Separate distinct responsibilities into different classes
- **Introduce Parameter Object**: Group related parameters into objects
- **Replace Conditional with Polymorphism**: Use OCP instead of switch/if chains
- **Introduce Dependency Injection**: Replace direct instantiation with abstraction

---

## VIII. Communication & Collaboration

### Code as Communication
- Code is read far more often than it's written
- Write code for humans first, computers second
- Use formatting and structure to guide readers through the logic
- Optimize for the next developer (who might be you in 6 months)

### Team Practices
- **Pair programming**: Combine creative exploration with real-time review
- **Code reviews**: Share knowledge, catch issues, maintain standards
- **Continuous integration**: Keep code integrated and tested frequently
- **Retrospectives**: Reflect on what works and continuously improve

### Documentation Strategy
- **Code documents itself** through clear names and structure
- **Comments explain why**, not what or how
- **README files** provide context and getting-started information
- **Architecture Decision Records (ADRs)** capture significant choices
- **Living documentation** evolves with the code

---

## IX. Continuous Learning & Improvement

### Expand Your Toolkit
- Study design patterns (Gang of Four, enterprise patterns)
- Explore functional programming concepts (immutability, pure functions)
- Learn about concurrency and parallel processing
- Understand your language's idioms and best practices

### Practice Deliberately
- Participate in code katas to practice techniques
- Contribute to open-source projects to see diverse approaches
- Refactor personal projects to experiment without pressure
- Teach others to deepen your own understanding

### Stay Pragmatic
- Principles are tools, not dogma
- Context matters—adapt practices to your situation
- Measure impact, not adherence to rules
- Balance idealism with delivery requirements

---

## X. Summary: Key Takeaways

1. **SOLID principles** create flexible, maintainable object-oriented designs
2. **DRY, KISS, YAGNI** keep code focused, simple, and free of unnecessary complexity
3. **Clean Code** emphasizes craftsmanship—code that reads like prose
4. **Domain-Driven Design** aligns code with business reality in complex domains
5. **Balance** principles pragmatically based on context
6. **Refactor continuously** with small, tested improvements
7. **Communicate through code** using meaningful names and clear structure
8. **Experiment safely** within the structure provided by principles
9. **Learn from the domain** and let insights drive model evolution
10. **Collaborate actively** through reviews, pairing, and shared language

---

## Resources for Further Learning

### Books
- *Clean Code* by Robert C. Martin
- *Domain-Driven Design* by Eric Evans
- *Refactoring* by Martin Fowler
- *Design Patterns* by Gang of Four
- *The Pragmatic Programmer* by Hunt & Thomas

### Online Communities
- Stack Overflow for Q&A
- GitHub for open-source examples
- Dev.to and Medium for articles
- Reddit (r/programming, r/softwaredevelopment)

### Practice Platforms
- LeetCode, HackerRank for algorithms
- Exercism for language-specific practice
- Code katas for deliberate practice

---

## Closing Thoughts

Great code emerges from the intersection of **discipline** and **creativity**. Principles provide the discipline—guardrails that prevent common pitfalls and ensure quality. Creativity flourishes within these guardrails, finding elegant solutions to complex problems.

When working on existing programs:
- **Understand before you change**
- **Test before you refactor**
- **Improve incrementally**
- **Communicate clearly**
- **Experiment boldly**

Remember: The goal isn't perfect code, but code that's clear, maintainable, and valuable to users. Every revision is an opportunity to make the codebase a little better, a little clearer, a little more aligned with business needs.

**Code with intention. Refactor with purpose. Innovate with structure.**