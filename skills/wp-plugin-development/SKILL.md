---
name: wp-plugin-development
description: Builds scalable, production-ready WordPress plugins using modern OOP PHP. Use when the task involves creating, extending, reviewing, or debugging a WordPress plugin — including hooks, REST API endpoints, custom database tables, admin pages, WP-CLI commands, security hardening, or performance optimization. Covers both Standard and Enterprise architecture tiers.
---

# WordPress Plugin Development

Skill for building **production-ready WordPress plugins** with modern PHP (8.1+).

**Trigger when the task involves:**
- Creating a new WordPress plugin from scratch
- Adding features to an existing plugin (CPTs, taxonomies, meta boxes, settings)
- Building REST API endpoints for a plugin
- Creating WP-CLI commands
- Plugin security review or hardening
- Performance optimization of plugin code
- Database schema design (custom tables, migrations)
- Writing or reviewing plugin unit/integration tests

**Do not use for:**
- Gutenberg block development (React/JSX, @wordpress/scripts)
- Theme development (templates, template hierarchy, theme.json)
- WordPress core contribution or core modification
- Generic PHP development unrelated to WordPress
- WordPress site administration (installing plugins, configuring settings via UI)

---

## MANDATORY: Architecture Tier Selection

**There are exactly TWO tiers. No mix and match. No hybrid. Pick one.**

Before writing ANY plugin code, you MUST determine which tier applies. If the user has not specified a tier, you MUST ask:

> "This skill supports two architecture tiers for WordPress plugins:
>
> **Standard** — OOP with Hooks Loader, PSR-4 autoloading, Composer, namespaced classes. Best for plugins with a focused feature set (settings pages, CPTs, REST endpoints, admin tools).
>
> **Enterprise** — Adds a Service Container, Dependency Injection, modular architecture, and support for background processing/queues. Best for large plugins with multiple independent feature modules.
>
> Which tier should I use?"

### Tier decision rules

| Signal | Tier |
|--------|------|
| Single feature set (e.g., one CPT + admin page + REST endpoint) | **Standard** |
| Multiple independent modules (e.g., analytics + reporting + integrations + API) | **Enterprise** |
| User says "simple" or "small" | **Standard** |
| User says "scalable", "modular", "large-scale", or "enterprise" | **Enterprise** |
| Unclear | **ASK the user** |

**NEVER combine elements from both tiers.** Standard plugins do NOT use a Service Container. Enterprise plugins ALWAYS use one.

---

## Reference files

Detailed guidance, code examples, and patterns for each domain:

- **Architecture**: See [references/architecture.md](references/architecture.md) — Tier structures, directory layouts, bootstrapping, PSR-4, DI, Service Container, Hooks Loader
- **Security**: See [references/security.md](references/security.md) — Nonces, sanitization, escaping, capabilities, prepared statements, CSRF/XSS/SQLi prevention
- **Performance**: See [references/performance.md](references/performance.md) — Transients, object caching, conditional script loading, lazy loading, query optimization, Action Scheduler
- **WP-CLI**: See [references/wp-cli.md](references/wp-cli.md) — Custom commands, arguments, progress bars, batch processing, output formatting
- **WordPress APIs**: See [references/wordpress-apis.md](references/wordpress-apis.md) — REST API, Settings API, Options API, Hooks (actions/filters), Custom Post Types, Taxonomies, Meta Boxes
- **Database**: See [references/database.md](references/database.md) — Custom tables, dbDelta, migrations, $wpdb, prepared statements, schema versioning
- **Testing**: See [references/testing.md](references/testing.md) — PHPUnit, WP_Mock, Brain Monkey, integration tests, debugging workflows

---

## MANDATORY: Action Scheduler Dependency

**Action Scheduler is a REQUIRED peer dependency for EVERY plugin built with this skill.**

NEVER use WP-Cron (`wp_schedule_event`, `wp_cron`, `cron_schedules` filter). ALWAYS use Action Scheduler for all scheduled, recurring, and background tasks.

Every plugin's `composer.json` MUST include:

```json
{
  "require": {
    "woocommerce/action-scheduler": "^3.9"
  }
}
```

See [references/performance.md](references/performance.md) for the full Action Scheduler API reference and usage patterns.

---

## Operating principles

- Assume **WordPress latest** and **PHP 8.1+** unless stated otherwise.
- Assume required companion plugins (e.g., ACF, WooCommerce) are latest versions when referenced.
- **Action Scheduler** is ALWAYS available as a Composer dependency. NEVER fall back to WP-Cron.
- Prefer **WordPress core functions** over raw PHP equivalents (e.g., `wp_remote_get()` over `curl`).
- Prefer **WordPress coding standards** (WPCS) for formatting and naming.
- Use **snake_case** for functions/hooks, **PascalCase** for class names, **UPPER_CASE** for constants.
- Prefix ALL global functions, hooks, constants, and option names with the plugin slug.
- NEVER use `extract()`, `eval()`, `serialize()`/`unserialize()` on untrusted data.
- ALWAYS escape output. ALWAYS sanitize input. ALWAYS use nonces for form submissions.
- ALWAYS use `$wpdb->prepare()` for dynamic queries.
- Do not invent WordPress functions or hooks that do not exist.
- If a detail is missing, mark it as **UNSPECIFIED** and ask (max 5 targeted questions).

---

## Required workflow

### 1. Determine tier

See [MANDATORY: Architecture Tier Selection](#mandatory-architecture-tier-selection) above. Do NOT proceed without a confirmed tier.

### 2. Gather context

Before writing code, determine:
- Plugin name and slug
- Architecture tier (Standard or Enterprise)
- Core features and responsibilities
- Required WordPress APIs (REST, Settings, CPT, etc.)
- Database needs (options only, or custom tables?)
- WP-CLI commands needed?
- External API integrations?
- Multisite compatibility needed?
- Internationalization (i18n) requirements?

If details are missing, state them as **UNSPECIFIED** and ALWAYS ask targeted questions (max 5). NEVER provide default values or make assumptions.

### 3. Produce output

**Standard build format:**
1. Summary (tier, features, assumptions, UNSPECIFIED details)
2. Directory structure
3. Composer configuration (composer.json with PSR-4 autoload)
4. Main plugin file (header, bootstrap)
5. Core classes (implementation)
6. Hooks registration
7. Security measures applied
8. Tests (3–6 concrete test cases)
9. Pitfalls and considerations

**Standard review format:**
1. What the code does → 2. Security issues → 3. Performance issues → 4. Architecture violations → 5. Suggested fixes

**Standard debugging format:**
1. Likely cause → 2. How to verify → 3. Minimal fix → 4. Root cause fix → 5. Regression tests

---

## Key conventions

### Plugin header

```php
<?php
/**
 * Plugin Name:       My Plugin Name
 * Plugin URI:        https://example.com/my-plugin
 * Description:       Short description of the plugin.
 * Version:           1.0.0
 * Requires at least: 6.4
 * Requires PHP:      8.1
 * Author:            Author Name
 * Author URI:        https://example.com
 * License:           GPL v2 or later
 * License URI:       https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain:       my-plugin
 * Domain Path:       /languages
 */
```

### Direct access prevention

Every PHP file MUST include:

```php
defined( 'ABSPATH' ) || exit;
```

### Naming conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Plugin slug | `kebab-case` | `my-awesome-plugin` |
| PHP namespace | `PascalCase` | `MyAwesomePlugin` |
| Function prefix | `snake_case` with slug | `my_awesome_plugin_init()` |
| Hook prefix | `snake_case` with slug | `my_awesome_plugin/settings/saved` |
| Constants | `UPPER_CASE` with prefix | `MY_AWESOME_PLUGIN_VERSION` |
| Option names | `snake_case` with prefix | `my_awesome_plugin_settings` |
| Database tables | `snake_case` with wpdb prefix | `{$wpdb->prefix}my_awesome_plugin_logs` |

### Composer.json (minimum)

```json
{
  "name": "vendor/my-awesome-plugin",
  "description": "Plugin description",
  "type": "wordpress-plugin",
  "require": {
    "php": ">=8.1",
    "woocommerce/action-scheduler": "^3.9"
  },
  "autoload": {
    "psr-4": {
      "MyAwesomePlugin\\": "src/"
    }
  }
}
```

---

## Error-handling rules

- **Never guess WordPress APIs** — say UNSPECIFIED, avoid fake function/hook names
- **Never skip security** — every form needs a nonce, every output needs escaping, every DB query needs preparation
- **Never mix tiers** — Standard stays Standard, Enterprise stays Enterprise
- **Never bypass capability checks** — always verify `current_user_can()` before privileged actions
- **Never use deprecated functions** — use current WordPress APIs only
- **Never hardcode paths** — use `plugin_dir_path()`, `plugin_dir_url()`, `plugins_url()`

---

## Response quality rules

- Prefer complete, runnable code over disconnected fragments.
- Prefer WordPress-native solutions over third-party packages where equivalent.
- Keep namespaces, imports, and file paths explicit.
- Architecture advice: explain trade-offs, then recommend one approach.
- Always include `composer.json` when creating a new plugin.
- Always show the full directory structure when scaffolding.
- Include activation/deactivation hooks when database schema or rewrite rules are involved.
- Provide uninstall cleanup (options, tables, transients) for production plugins.

---

## When this Skill is active

Behave like a **WordPress plugin architecture specialist**: enforce the selected tier's structure, generate secure and performant code, protect against common vulnerabilities, follow WordPress coding standards, and provide implementation-ready output with tests and security considerations for every substantial task.
