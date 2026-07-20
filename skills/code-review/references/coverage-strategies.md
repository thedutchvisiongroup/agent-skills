# Coverage Strategies

## Why Coverage Matters

Test coverage measures how much of your code is exercised by tests. Low coverage means untested code — and untested code is broken code waiting to happen.

**Coverage is necessary but not sufficient.** 100% coverage doesn't mean bug-free, but <80% coverage almost certainly means missing tests.

## Types of Coverage

### Line Coverage
Which lines of code are executed by tests?

```python
def calculate_discount(price, discount_percent):
    if discount_percent > 50:          # Line 1 - covered
        raise ValueError("Too high")   # Line 2 - NOT covered
    return price * (1 - discount_percent / 100)  # Line 3 - covered
```

**Gap:** Line 2 is not tested — the error case is missing.

### Branch Coverage
Which branches (if/else, switch) are exercised?

```python
def get_status(code):
    if code == 200:        # Branch 1 - covered
        return "OK"
    elif code == 404:      # Branch 2 - covered
        return "Not Found"
    else:                  # Branch 3 - NOT covered
        return "Unknown"
```

**Gap:** The else branch is not tested.

### Function Coverage
Which functions are called by tests?

```python
class UserService:
    def create_user(self, data):    # covered
        ...
    
    def delete_user(self, id):      # NOT covered
        ...
    
    def update_user(self, id, data): # covered
        ...
```

**Gap:** `delete_user` has no tests.

### Condition Coverage
Which boolean conditions are fully tested?

```python
def is_eligible(age, has_id):
    if age >= 18 and has_id:  # Both conditions need True/False testing
        return True
    return False
```

**Test needed:**
- `age >= 18` True + `has_id` True → True
- `age >= 18` True + `has_id` False → False
- `age >= 18` False + `has_id` True → False
- `age >= 18` False + `has_id` False → False

## Identifying Coverage Gaps

### 1. Run Coverage Tool

```bash
# Python
pytest --cov=src --cov-report=term-missing

# JavaScript
npm run test:coverage

# Go
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out

# Rust
cargo tarpaulin
```

### 2. Read the Report

**Terminal report:**
```
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/auth/login.py          45     12    73%   45-50, 67, 89
src/utils/parser.py        30      8    73%   23, 34-38
```

**Key columns:**
- **Stmts** — Total statements
- **Miss** — Statements not covered
- **Cover** — Percentage covered
- **Missing** — Line numbers not covered

### 3. Focus on Changed Files

When reviewing a PR, focus on coverage of CHANGED files:

```bash
# Get coverage for changed files only
git diff --name-only HEAD~1 | xargs pytest --cov
```

### 4. Identify Critical Gaps

**Priority order:**

1. **New functions without tests** — MUST add tests
2. **Modified functions without tests** — MUST add tests
3. **Error handling paths** — Should be tested
4. **Edge cases** — Should be tested
5. **Complex logic** — Should be tested

## Common Coverage Gaps

### Error Handling

```python
def connect_to_db(config):
    try:
        return create_connection(config)
    except ConnectionError:
        logger.error("Connection failed")  # NOT tested
        raise
    except TimeoutError:
        logger.error("Connection timeout")  # NOT tested
        raise
```

**What to test:**
- What happens when connection fails?
- What happens on timeout?
- Are errors properly re-raised?

### Edge Cases

```python
def process_items(items):
    if not items:  # NOT tested
        return []
    
    result = []
    for item in items:
        if item.is_valid():  # NOT tested with invalid items
            result.append(item)
    
    return result
```

**What to test:**
- Empty list input
- List with invalid items
- List with all invalid items
- List with all valid items

### Boundary Conditions

```python
def paginate(items, page, per_page):
    start = (page - 1) * per_page  # What if page is 0? -1?
    end = start + per_page          # What if beyond list?
    return items[start:end]
```

**What to test:**
- Page 0 or negative
- Page beyond total pages
- Empty items list
- per_page larger than items

### Async/Concurrent Code

```python
async def fetch_all(urls):
    tasks = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks)
```

**What to test:**
- What if one fetch fails?
- What if all fail?
- What if tasks take too long?
- What if URLs list is empty?

## Coverage Thresholds

### Recommended Thresholds

| Component | Minimum | Target |
|-----------|---------|--------|
| Core business logic | 90% | 95%+ |
| API endpoints | 80% | 90%+ |
| Utility functions | 85% | 95%+ |
| Configuration | 70% | 80%+ |
| Error handling | 80% | 90%+ |

### Enforcing Thresholds

**Python (pytest):**
```ini
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov-fail-under=80"
```

**JavaScript (Jest):**
```json
// jest.config.js
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

**Go:**
```bash
# Fail if coverage < 80%
go test -coverprofile=coverage.out ./...
coverage=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
if (( $(echo "$coverage < 80" | bc -l) )); then
  echo "Coverage $coverage% is below 80%"
  exit 1
fi
```

## Asking About Gaps

When you find coverage gaps, ASK the user:

### Template Questions

```
Coverage Gap Found:
- File: src/auth/login.py
- Lines: 45-50 (error handling for invalid credentials)
- Current coverage: 73%

Questions:
1. Is this gap intentional? (e.g., covered by integration tests elsewhere)
2. Should I add unit tests for these lines?
3. Is there a reason these paths can't be tested?
```

### When NOT to Ask

- Gap is in auto-generated code
- Gap is in third-party code
- Gap is in configuration-only code
- Gap is explicitly marked with `# pragma: no cover`

### When to Ask

- Gap is in business logic
- Gap is in error handling
- Gap is in new code
- Gap is in modified code
- Gap is unexplained

## Improving Coverage

### 1. Add Tests for Missing Lines

```python
# If line 45-50 is not covered:
def test_invalid_credentials():
    with pytest.raises(AuthError, match="Invalid credentials"):
        login("user", "wrong_password")
```

### 2. Add Tests for Missing Branches

```python
# If else branch is not covered:
def test_unknown_status_code():
    assert get_status(500) == "Unknown"
```

### 3. Add Tests for Missing Functions

```python
# If delete_user is not covered:
def test_delete_user():
    user = create_user({"name": "test"})
    delete_user(user.id)
    assert get_user(user.id) is None
```

### 4. Mock External Dependencies

```python
# If error path requires external failure:
@patch('src.auth.login.verify_password', side_effect=ConnectionError)
def test_login_db_error(mock_verify):
    with pytest.raises(AuthError):
        login("user", "password")
```

## Coverage Anti-Patterns

### Testing for Coverage, Not Behavior

```python
# WRONG: Testing to hit lines, not behavior
def test_process():
    process(None)  # Just to hit the null check
    process([])    # Just to hit the empty check
    process([1])   # Just to hit the normal path

# CORRECT: Testing behavior
def test_process_handles_empty_input():
    assert process([]) == []

def test_process_raises_on_null():
    with pytest.raises(ValueError):
        process(None)
```

### Over-Mocking

```python
# WRONG: Mocking everything, testing nothing
@patch('src.service.db')
@patch('src.service.cache')
@patch('src.service.logger')
def test_create_user(mock_logger, mock_cache, mock_db):
    # This test proves nothing
    create_user({"name": "test"})
```

### Ignoring Coverage Reports

```python
# WRONG: Running coverage but not reading it
pytest --cov=src

# CORRECT: Analyzing and acting on coverage
pytest --cov=src --cov-report=term-missing
# Then: add tests for missing lines
```

## Coverage Checklist

For each review:

- [ ] Run coverage tool
- [ ] Read coverage report
- [ ] Identify gaps in changed files
- [ ] Prioritize gaps (errors > branches > lines)
- [ ] Ask user about each gap
- [ ] Verify gaps are addressed
- [ ] Confirm coverage meets threshold
