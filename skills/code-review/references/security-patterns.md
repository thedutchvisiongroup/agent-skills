# Security Review Checklist

## Input Validation

**All user input MUST be validated:**

- [ ] **Type checking** — Input is the expected type (string, number, etc.)
- [ ] **Length limits** — Strings and arrays have maximum lengths
- [ ] **Format validation** — Emails, URLs, phone numbers match expected format
- [ ] **Range validation** — Numbers are within acceptable bounds
- [ ] **Whitelist validation** — Values match allowed set where applicable
- [ ] **Sanitization** — HTML/script tags stripped if displayed

**Common mistakes:**
```javascript
// WRONG: No validation
app.post('/api/user', (req, res) => {
  const { name, email } = req.body;
  createUser(name, email);
});

// CORRECT: Validate everything
app.post('/api/user', (req, res) => {
  const { name, email } = req.body;
  
  if (!name || typeof name !== 'string' || name.length > 100) {
    return res.status(400).json({ error: 'Invalid name' });
  }
  
  if (!email || !isValidEmail(email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  
  createUser(sanitize(name), email.toLowerCase());
});
```

## SQL Injection

**ALWAYS use parameterized queries:**

```python
# WRONG: String concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"

# WRONG: Format string
query = "SELECT * FROM users WHERE id = '%s'" % user_id

# CORRECT: Parameterized query
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

```javascript
// WRONG: String concatenation
const query = `SELECT * FROM users WHERE email = '${email}'`;

// CORRECT: Parameterized
const query = 'SELECT * FROM users WHERE email = ?';
connection.execute(query, [email]);
```

**Check for:**
- [ ] All SQL uses parameterized queries
- [ ] No string concatenation in SQL
- [ ] No format strings in SQL
- [ ] ORM queries are parameterized (not raw SQL)

## Cross-Site Scripting (XSS)

**ALWAYS escape output:**

```javascript
// WRONG: Direct HTML injection
element.innerHTML = userInput;

// CORRECT: Text content
element.textContent = userInput;

// CORRECT: Escaped HTML
element.innerHTML = escapeHtml(userInput);
```

```python
# WRONG: Unescaped template
html = f"<div>{user_input}</div>"

# CORRECT: Auto-escaping template
html = render_template("page.html", content=user_input)

# CORRECT: Manual escaping
from markupsafe import escape
html = f"<div>{escape(user_input)}</div>"
```

**Check for:**
- [ ] All user input is escaped before display
- [ ] Templates use auto-escaping
- [ ] No `innerHTML` with user input
- [ ] No `dangerouslySetInnerHTML` with user input
- [ ] JSON responses are properly encoded

## Authentication

**Verify auth is properly implemented:**

- [ ] **All endpoints require auth** — No unprotected routes
- [ ] **Auth is verified server-side** — Not just client-side
- [ ] **Tokens are validated** — JWT signature, expiration, issuer
- [ ] **Sessions are secure** — HttpOnly, Secure, SameSite flags
- [ ] **Passwords are hashed** — bcrypt, scrypt, or Argon2
- [ ] **No password in logs** — Passwords never logged

```python
# WRONG: Auth check missing
@app.route('/api/admin/users')
def get_users():
    return get_all_users()

# CORRECT: Auth required
@app.route('/api/admin/users')
@login_required
@admin_required
def get_users():
    return get_all_users()
```

## Authorization

**Verify permissions are checked:**

- [ ] **Ownership verified** — User can only access their own resources
- [ ] **Role checks present** — Admin actions require admin role
- [ ] **Permissions checked server-side** — Not just UI hiding
- [ ] **No IDOR vulnerabilities** — Can't guess other users' IDs

```python
# WRONG: No ownership check
@app.route('/api/documents/<doc_id>')
def get_document(doc_id):
    return Document.query.get(doc_id)

# CORRECT: Ownership verified
@app.route('/api/documents/<doc_id>')
@login_required
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != current_user.id:
        abort(403)
    return doc
```

## Secrets Management

**No hardcoded secrets:**

- [ ] **No API keys in code** — Use environment variables
- [ ] **No passwords in code** — Use secrets manager
- [ ] **No tokens in code** — Use environment variables
- [ ] **No secrets in logs** — Mask sensitive values
- [ ] **No secrets in version control** — Use .gitignore

```python
# WRONG: Hardcoded secret
API_KEY = "sk-1234567890abcdef"

# CORRECT: Environment variable
API_KEY = os.environ["API_KEY"]

# WRONG: Logging secret
logger.info(f"Using API key: {API_KEY}")

# CORRECT: Masked
logger.info("Using API key: ****")
```

## Sensitive Data

**Protect sensitive data:**

- [ ] **PII is encrypted at rest** — Database encryption
- [ ] **PII is encrypted in transit** — HTTPS only
- [ ] **PII is masked in logs** — No raw PII in logs
- [ ] **PII is masked in errors** — No PII in error messages
- [ ] **Data is minimized** — Only collect what's needed
- [ ] **Data retention enforced** — Delete when no longer needed

```python
# WRONG: PII in logs
logger.info(f"User {user.email} logged in from {ip}")

# CORRECT: Masked
logger.info(f"User {user.id} logged in from {ip[:8]}.xxx")

# WRONG: PII in error
raise ValueError(f"User {email} not found")

# CORRECT: Generic error
raise ValueError("User not found")
```

## Dependency Security

**Check dependencies:**

- [ ] **No known vulnerabilities** — Run `npm audit`, `pip audit`, etc.
- [ ] **Dependencies are pinned** — Use exact versions
- [ ] **Lock file is committed** — package-lock.json, poetry.lock
- [ ] **Unused dependencies removed** — Smaller attack surface

```bash
# Check for vulnerabilities
npm audit
pip audit
cargo audit
```

## Error Handling

**Secure error handling:**

- [ ] **No stack traces in production** — Generic error messages
- [ ] **No internal details exposed** — No file paths, SQL, etc.
- [ ] **Errors are logged securely** — No sensitive data in logs
- [ ] **Error pages are generic** — No system information

```python
# WRONG: Detailed error in production
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({
        "error": str(e),
        "traceback": traceback.format_exc()
    }), 500

# CORRECT: Generic in production
@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"Unhandled error: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500
```

## Rate Limiting

**Protect against abuse:**

- [ ] **API endpoints are rate limited** — Prevent brute force
- [ ] **Login attempts are limited** — Prevent credential stuffing
- [ ] **Password reset is limited** — Prevent enumeration
- [ ] **Expensive operations are limited** — Prevent DoS

```python
# WRONG: No rate limiting
@app.route('/api/login', methods=['POST'])
def login():
    ...

# CORRECT: Rate limited
@limiter.limit("5 per minute")
@app.route('/api/login', methods=['POST'])
def login():
    ...
```

## Review Procedure

For each file, check:

1. **Input validation** — All user input validated?
2. **SQL injection** — Parameterized queries?
3. **XSS** — Output escaped?
4. **Auth** — Authentication required?
5. **AuthZ** — Authorization checked?
6. **Secrets** — No hardcoded secrets?
7. **Sensitive data** — PII protected?
8. **Dependencies** — No known vulnerabilities?
9. **Error handling** — Secure error messages?
10. **Rate limiting** — Protected against abuse?
