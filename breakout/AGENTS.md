# Instructions for the Coding Agent

## 1. Read the Specification First

- Read `SPEC.md` before writing or modifying code.
- Treat `SPEC.md` as the source of truth for the game's required behavior.
- If a requirement is ambiguous, choose a simple, reasonable interpretation. Ask for clarification only if the ambiguity prevents implementation.

## 2. Licensing and Originality

- Read the `LICENSE` file before creating or modifying code.
- All code created for this project must be compatible with the license specified in `LICENSE`.
- Prefer original implementations written for this project.
- Do not copy code from websites, repositories, or other projects unless its license permits use under the project's license and all required notices are preserved.
- Do not introduce third-party libraries, assets, fonts, images, or other resources unless their licenses permit the intended use and any required attribution or notices are included.
- Do not claim that code is license-compatible unless you have sufficient information to support that conclusion.
- If you are unsure whether existing code or a resource is compatible with the project license, explain the uncertainty and ask for clarification rather than silently including it.
- Preserve the `LICENSE` file. Do not change the project's license without explicit authorization.

## 3. Keep the Implementation Simple

- Use only HTML, CSS, and JavaScript.
- Do not introduce external libraries, frameworks, build tools, or dependencies.
- Create or modify the files needed to implement the game.
- Prefer straightforward, readable code over clever or unnecessarily complex solutions.
- Do not add features that are not requested in `SPEC.md`.

## 4. Write Readable Code

- Use descriptive names for variables and functions.
- Organize the code into logical sections and functions.
- Add comments to explain important logic, non-obvious decisions, and game behavior.
- Avoid comments that merely repeat what the code already says.
- Keep the implementation understandable to a student learning programming.

## 5. Implement Incrementally

- Inspect the existing project before making changes.
- For a new implementation, create the files needed to satisfy the specification.
- For an existing implementation, preserve working behavior unless a requirement explicitly calls for a change.
- When requirements change, identify the affected parts of the implementation before modifying them.
- Avoid rewriting unrelated code when a smaller change will work.

## 6. Verify the Implementation

- Check the implementation against the requirements in `SPEC.md`.
- Run available checks when practical.
- Do not claim that the game or a test has been run unless you actually ran it.
- Explain any tests that could not be performed.
- Provide clear instructions for opening and playing the game in a browser.
- Identify any known problems or incomplete requirements honestly.

## 7. Explain Changes

After implementing the game or making a change, summarize:

- Which files were created or modified.
- What behavior was implemented or changed.
- How the result can be tested manually.
- Any assumptions, limitations, or known issues.

Keep explanations concise and appropriate for a student learning software development.
