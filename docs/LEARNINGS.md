# REDDSTUDIO Engineering Learnings

Detailed debugging history and patterns. Read this when stuck on similar issues.

---

## 2026-02-05: TRANSFORMATION Enum Failure

**Symptom:** 500 error on `/api/generate/frameworks/generate`
```
invalid input value for enum imagetypeenum: "TRANSFORMATION"
```

**Root Cause:**
SQLAlchemy stores Python enum **member names** (uppercase) in PostgreSQL, not the values (lowercase). The migration added `'transformation'` but PostgreSQL expected `'TRANSFORMATION'`.

**Fix:**
```python
# app/db/session.py
conn.execute(text("ALTER TYPE imagetypeenum ADD VALUE IF NOT EXISTS 'TRANSFORMATION'"))
```

**Lesson:** Always use UPPERCASE when adding PostgreSQL enum values for SQLAlchemy models.

---

## 2026-02-05: Style Reference Toggle Blank Screen

**Symptom:** Clicking "Generate" with "Use Exact Style" toggle ON caused blank screen.

**Root Causes (3 issues):**

1. **Frontend:** `uploadedStyleRefPath` was only set for fresh uploads, not existing style refs
   ```typescript
   // Fix: Use originalStyleRefPath when toggle is on
   const effectiveStyleRefPath = uploadedStyleRefPath ||
     (useOriginalStyleRef && originalStyleRefPath ? originalStyleRefPath : undefined);
   ```

2. **AI Prompt:** `STYLE_REFERENCE_FRAMEWORK_PROMPT` had lazy `{{...}}` placeholders causing incomplete JSON
   ```python
   # Bad: "typography": {{...}}
   # Good: Full schema with all fields
   ```

3. **Schema:** Missing defaults in Pydantic models caused validation failures

**Lesson:** When AI returns incomplete data, fix the PROMPT first - don't add fallbacks that mask the issue.

---

## 2026-02-05: Ralph-Loop Plugin Bash Error on Windows

**Symptom:**
```
Stop hook error: 'bash' is not recognized as an internal or external command
```

**Cause:** `ralph-loop` plugin uses `.sh` scripts that require bash (not available on Windows).

**Fix:** Disable in `~/.claude/settings.json`:
```json
"enabledPlugins": {
  "ralph-loop@claude-plugins-official": false
}
```

---

## Patterns

### When Generation Fails
1. Check Railway logs first: `railway logs -s reddstudio-staging-backend --environment staging`
2. Look for: enum errors, schema validation, Gemini API errors
3. If enum: add migration in `app/db/session.py`
4. If schema: check `app/schemas/generation.py` for missing fields/defaults
5. If AI data: fix prompt in `app/prompts/ai_designer.py`

### When Frontend Breaks
1. Check browser console (F12)
2. Common: `undefined.something()` - data not loaded yet or wrong shape
3. Add optional chaining (`?.`) or normalize data before use
4. Test the actual user flow, don't assume "it should work"

### Deployment Checklist
1. Push to `develop`
2. Deploy: `railway up --service reddstudio-staging-backend --environment staging`
3. Check logs for startup errors
4. Test on staging.reddstudio.ai
5. Only then consider merging to `main` for production
