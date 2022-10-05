# What is it for?
This software is for those, who happened to use both Telegram and Evernote a lot, just like me.
It's a Telegram bot, that saves any message as a note in Evernote.

# Running
Example
```
uvicorn --host localhost --port 8000 app:app
```

# Auto Format Before Committing
```bash
cat > .git/hooks/pre-commit<< EOF
#!/usr/bin/env bash
exec make fmt
EOF
chmod +x .git/hooks/pre-commit
```

# Commit labels
Commit messages have several tags, which I put in the beginning of a message.
- `ft` - new functionality, feature
- `fix` - bug fix
- `docs` - documentation
- `ref` - refactoring, should not include new functionality
- `mntn` - maintenance, technical backlog, something related only to the code or operations; should not include new functionality
- `test` - tests
