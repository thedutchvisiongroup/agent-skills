# Performance Reference

Performance-critical practices for WordPress plugins. Slow plugins get uninstalled.

---

## Core principles

1. **Minimize database queries** — cache results, batch operations
2. **Load conditionally** — only enqueue assets where needed
3. **Cache expensive operations** — transients, object cache, static properties
4. **Defer non-critical work** — lazy loading, background processing, Action Scheduler
5. **Optimize queries** — proper indexing, avoid `meta_query` on large datasets

---

## Transients API

Transients store cached data with an expiration time. They integrate automatically with object caching when available.

### Basic usage

```php
// Store a transient (expires in 12 hours)
set_transient( 'my_plugin_api_data', $data, 12 * HOUR_IN_SECONDS );

// Retrieve a transient
$data = get_transient( 'my_plugin_api_data' );

if ( false === $data ) {
    // Cache miss — fetch fresh data
    $data = $this->fetch_from_api();
    set_transient( 'my_plugin_api_data', $data, 12 * HOUR_IN_SECONDS );
}

// Delete a transient
delete_transient( 'my_plugin_api_data' );
```

### Time constants

| Constant | Value |
|----------|-------|
| `MINUTE_IN_SECONDS` | 60 |
| `HOUR_IN_SECONDS` | 3600 |
| `DAY_IN_SECONDS` | 86400 |
| `WEEK_IN_SECONDS` | 604800 |
| `MONTH_IN_SECONDS` | 2592000 |
| `YEAR_IN_SECONDS` | 31536000 |

### Site transients (multisite-aware)

```php
// For data shared across a multisite network
set_site_transient( 'my_plugin_network_data', $data, DAY_IN_SECONDS );
$data = get_site_transient( 'my_plugin_network_data' );
delete_site_transient( 'my_plugin_network_data' );
```

### When to use transients

- **YES**: External API responses, computed aggregates, expensive query results
- **NO**: Frequently changing data, user-specific data (use object cache), data that must be real-time

### Cache invalidation pattern

```php
// Invalidate when related data changes
add_action( 'save_post_product', function ( int $post_id ): void {
    delete_transient( 'my_plugin_products_list' );
    delete_transient( "my_plugin_product_{$post_id}" );
} );
```

---

## Object Cache (wp_cache_*)

Object cache stores data in memory for the duration of a request. With a persistent object cache backend (Redis, Memcached), data persists across requests.

### Basic usage

```php
// Set cache
wp_cache_set( 'my_key', $data, 'my_plugin', HOUR_IN_SECONDS );

// Get cache
$data = wp_cache_get( 'my_key', 'my_plugin' );
if ( false === $data ) {
    $data = $this->compute_expensive_data();
    wp_cache_set( 'my_key', $data, 'my_plugin', HOUR_IN_SECONDS );
}

// Delete cache
wp_cache_delete( 'my_key', 'my_plugin' );

// Flush entire group (requires persistent cache that supports groups)
wp_cache_flush_group( 'my_plugin' );
```

### Transients vs Object Cache

| Feature | Transients | Object Cache |
|---------|-----------|--------------|
| Persistent without plugin | Yes (stored in `wp_options`) | No (memory only) |
| With persistent cache | Uses object cache under the hood | Direct memory storage |
| Expiration | Built-in | Built-in |
| Use case | Data that survives across requests | Request-scoped or short-lived data |
| Overhead without cache plugin | Database read/write | None (memory) |

**Rule of thumb**: Use transients for data that MUST survive across requests even without a persistent cache backend. Use `wp_cache_*` for request-scoped optimization.

---

## Conditional Asset Loading

NEVER load CSS/JS on every page. Load only where needed.

### Admin assets

```php
public function enqueue_admin_assets( string $hook_suffix ): void {
    // Only load on our plugin's admin page
    if ( 'toplevel_page_my-plugin-settings' !== $hook_suffix ) {
        return;
    }

    wp_enqueue_style(
        'my-plugin-admin',
        MY_PLUGIN_URL . 'assets/css/admin.css',
        [],
        MY_PLUGIN_VERSION
    );

    wp_enqueue_script(
        'my-plugin-admin',
        MY_PLUGIN_URL . 'assets/js/admin.js',
        [ 'jquery' ],
        MY_PLUGIN_VERSION,
        true // Load in footer
    );

    wp_localize_script( 'my-plugin-admin', 'myPluginAdmin', [
        'ajaxUrl' => admin_url( 'admin-ajax.php' ),
        'nonce'   => wp_create_nonce( 'my_plugin_admin' ),
        'i18n'    => [
            'confirm' => esc_html__( 'Are you sure?', 'my-plugin' ),
        ],
    ] );
}
```

### Frontend assets (conditional)

```php
public function enqueue_public_assets(): void {
    // Only load when our shortcode is present
    global $post;
    if ( ! is_a( $post, 'WP_Post' ) || ! has_shortcode( $post->post_content, 'my_plugin' ) ) {
        return;
    }

    wp_enqueue_style(
        'my-plugin-public',
        MY_PLUGIN_URL . 'assets/css/public.css',
        [],
        MY_PLUGIN_VERSION
    );

    wp_enqueue_script(
        'my-plugin-public',
        MY_PLUGIN_URL . 'assets/js/public.js',
        [],
        MY_PLUGIN_VERSION,
        true
    );
}
```

### Script optimization attributes

```php
// Defer or async loading (WP 6.3+)
wp_enqueue_script( 'my-plugin-script', $url, [], $ver, [
    'in_footer' => true,
    'strategy'  => 'defer', // or 'async'
] );
```

---

## Database Query Optimization

### Avoid unnecessary queries

```php
// BAD: Querying inside a loop
foreach ( $post_ids as $id ) {
    $meta = get_post_meta( $id, 'my_field', true ); // N+1 queries!
}

// GOOD: Batch prime the cache
update_meta_cache( 'post', $post_ids );
foreach ( $post_ids as $id ) {
    $meta = get_post_meta( $id, 'my_field', true ); // Served from cache
}
```

### Efficient WP_Query usage

```php
// Only get what you need
$query = new WP_Query( [
    'post_type'      => 'product',
    'posts_per_page' => 10,
    'no_found_rows'  => true,      // Skip SQL_CALC_FOUND_ROWS (skip pagination count)
    'fields'         => 'ids',      // Only get IDs if you don't need full objects
    'update_post_meta_cache' => false, // Skip meta cache if not needed
    'update_post_term_cache' => false, // Skip term cache if not needed
] );
```

### Avoid meta_query on large datasets

```php
// BAD: Slow meta_query on 100k+ posts
$query = new WP_Query( [
    'meta_query' => [
        [ 'key' => 'price', 'value' => 100, 'compare' => '>=', 'type' => 'NUMERIC' ],
    ],
] );

// GOOD: Use a custom table with proper indexes for large datasets
// Or use a taxonomy for filterable attributes
```

### Direct queries with LIMIT

```php
// When WP_Query is overkill
global $wpdb;
$results = $wpdb->get_results(
    $wpdb->prepare(
        "SELECT id, title FROM {$wpdb->prefix}my_plugin_items
         WHERE status = %s
         ORDER BY created_at DESC
         LIMIT %d",
        'active',
        20
    )
);
```

---

## Lazy Loading & Deferred Initialization

### Only instantiate when needed

```php
// BAD: Always loads the heavy class
public function __construct() {
    $this->report_generator = new ReportGenerator(); // Expensive
}

// GOOD: Lazy load
private ?ReportGenerator $report_generator = null;

public function get_report_generator(): ReportGenerator {
    if ( null === $this->report_generator ) {
        $this->report_generator = new ReportGenerator();
    }
    return $this->report_generator;
}
```

### Conditional class loading

```php
// Only load admin classes in admin context
if ( is_admin() ) {
    $this->loader->add_action( 'admin_menu', $admin_page, 'register' );
}

// Only load REST controllers when REST is active
add_action( 'rest_api_init', [ $this, 'register_rest_routes' ] );

// Only load CLI commands when WP-CLI is active
if ( defined( 'WP_CLI' ) && WP_CLI ) {
    WP_CLI::add_command( 'my-plugin', CLI\MainCommand::class );
}
```

---

## Background Processing with Action Scheduler

Action Scheduler is a **mandatory peer dependency** for all plugins built with this skill. It is a scalable, traceable job queue for background processing — battle-tested by WooCommerce processing millions of tasks monthly.

**NEVER use WP-Cron (`wp_schedule_event`, `wp_cron`, `cron_schedules`).** Always use Action Scheduler instead.

### Why Action Scheduler over WP-Cron

| Feature | WP-Cron | Action Scheduler |
|---------|---------|------------------|
| Execution trigger | Page load (unreliable) | WP-Cron + async loopback (reliable) |
| Logging/traceability | None | Full history, status tracking, admin UI |
| Failure handling | Silent failure | Logged failures, retry support |
| Concurrency | No protection | Claimed batches, prevents duplicates |
| Custom intervals | Requires `cron_schedules` filter | Direct seconds parameter |
| Unique scheduling | Manual `wp_next_scheduled` check | Built-in `$unique` parameter |
| Scalability | Degrades at scale | Handles 10,000+/hour sustained |
| Admin visibility | Requires plugin | Built-in scheduled actions UI |
| Grouping | Not supported | Groups for organized management |
| Priority | Not supported | Priority levels (0-255) |

### Composer dependency

Action Scheduler MUST be declared in `composer.json`:

```json
{
  "require": {
    "woocommerce/action-scheduler": "^3.9"
  }
}
```

Then load it in the main plugin file:

```php
require_once MY_PLUGIN_PATH . 'vendor/woocommerce/action-scheduler/action-scheduler.php';
```

### API initialization

Action Scheduler initializes on the `init` hook at priority `1`. API functions (`as_*`) are safe to call after `action_scheduler_init` fires or during/after `init` at priority `>= 1`.

```php
// Safe: hook into action_scheduler_init
add_action( 'action_scheduler_init', [ $this, 'schedule_actions' ] );

// Safe: check if initialized
if ( ActionScheduler::is_initialized() ) {
    // Call as_* functions
}
```

### Schedule a recurring action

```php
// Schedule on plugin activation
public static function activate(): void {
    if ( ! as_has_scheduled_action( 'my_plugin_daily_cleanup', [], 'my-plugin' ) ) {
        as_schedule_recurring_action(
            time(),
            DAY_IN_SECONDS,
            'my_plugin_daily_cleanup',
            [],
            'my-plugin',  // Group
            true           // Unique
        );
    }
}

// Handle the action
add_action( 'my_plugin_daily_cleanup', [ $this, 'run_cleanup' ] );

public function run_cleanup(): void {
    global $wpdb;
    $wpdb->query(
        $wpdb->prepare(
            "DELETE FROM {$wpdb->prefix}my_plugin_logs WHERE created_at < %s",
            gmdate( 'Y-m-d H:i:s', strtotime( '-30 days' ) )
        )
    );
    delete_transient( 'my_plugin_log_count' );
}

// Cancel on deactivation
public static function deactivate(): void {
    as_unschedule_all_actions( 'my_plugin_daily_cleanup', [], 'my-plugin' );
}
```

### Ensure recurring actions stay scheduled

Recurring actions can be lost during updates or database issues. Use the `action_scheduler_ensure_recurring_actions` hook:

```php
add_action( 'init', function (): void {
    if ( function_exists( 'as_supports' ) && as_supports( 'ensure_recurring_actions_hook' ) ) {
        add_action(
            'action_scheduler_ensure_recurring_actions',
            'my_plugin_ensure_recurring_actions'
        );
    } elseif ( is_admin() ) {
        my_plugin_ensure_recurring_actions();
    }
} );

function my_plugin_ensure_recurring_actions(): void {
    if ( ! as_has_scheduled_action( 'my_plugin_daily_cleanup', [], 'my-plugin' ) ) {
        as_schedule_recurring_action(
            time(),
            DAY_IN_SECONDS,
            'my_plugin_daily_cleanup',
            [],
            'my-plugin',
            true
        );
    }
}
```

### Schedule a single (one-time) action

```php
// Run once in 1 hour
$action_id = as_schedule_single_action(
    time() + HOUR_IN_SECONDS,
    'my_plugin_send_report',
    [ 'report_id' => 42 ],
    'my-plugin'
);

// Handle the action
add_action( 'my_plugin_send_report', function ( int $report_id ): void {
    // Generate and send report...
}, 10, 1 );
```

### Enqueue async action (run ASAP in background)

```php
// Offload heavy work immediately without blocking the request
as_enqueue_async_action(
    'my_plugin_process_upload',
    [ 'file_id' => $attachment_id ],
    'my-plugin',
    true  // Unique — prevents duplicate processing
);
```

### Schedule with cron expression

```php
// For complex schedules (e.g., every weekday at 9 AM)
as_schedule_cron_action(
    time(),
    '0 9 * * 1-5',  // Standard cron expression
    'my_plugin_weekday_report',
    [],
    'my-plugin',
    true
);
```

### Check and cancel actions

```php
// Check if an action is scheduled
if ( as_has_scheduled_action( 'my_plugin_sync', [ 'source' => 'api' ], 'my-plugin' ) ) {
    // Already scheduled
}

// Cancel next occurrence
$cancelled_id = as_unschedule_action( 'my_plugin_sync', [ 'source' => 'api' ], 'my-plugin' );

// Cancel ALL occurrences (use on deactivation)
as_unschedule_all_actions( 'my_plugin_sync', [], 'my-plugin' );
```

### Batch processing pattern

```php
public function process_batch(): void {
    $batch_size = 50;

    global $wpdb;
    $items = $wpdb->get_results(
        $wpdb->prepare(
            "SELECT * FROM {$wpdb->prefix}my_plugin_queue
             WHERE processed = 0
             ORDER BY id ASC
             LIMIT %d",
            $batch_size
        )
    );

    if ( empty( $items ) ) {
        return; // No more items — Action Scheduler handles recurring schedule
    }

    foreach ( $items as $item ) {
        $this->process_item( $item );
    }
}

// For one-off bulk operations, schedule individual items:
public function schedule_bulk_import( array $item_ids ): void {
    foreach ( $item_ids as $id ) {
        as_enqueue_async_action(
            'my_plugin_import_single_item',
            [ 'item_id' => $id ],
            'my-plugin-import',
            true // Unique per item
        );
    }
}
```

### Action Scheduler API quick reference

| Function | Purpose |
|----------|---------|
| `as_enqueue_async_action()` | Run once, as soon as possible (background) |
| `as_schedule_single_action()` | Run once at a specific future timestamp |
| `as_schedule_recurring_action()` | Run repeatedly at interval (in seconds) |
| `as_schedule_cron_action()` | Run on cron expression schedule |
| `as_has_scheduled_action()` | Check if action is pending/in-progress |
| `as_unschedule_action()` | Cancel next occurrence |
| `as_unschedule_all_actions()` | Cancel all occurrences |
| `as_next_scheduled_action()` | Get timestamp of next occurrence |
| `as_get_scheduled_actions()` | Query scheduled actions |

---

## Autoloading Best Practices

```json
{
  "autoload": {
    "psr-4": {
      "MyPlugin\\": "src/"
    }
  },
  "config": {
    "optimize-autoloader": true
  }
}
```

Run `composer dump-autoload --optimize` for production. This generates a classmap for faster lookups.

---

## Performance checklist

- [ ] Assets only loaded on pages where needed
- [ ] No queries inside loops (N+1 problem)
- [ ] Expensive computations cached (transients or object cache)
- [ ] WP_Query uses `no_found_rows` when pagination count is unnecessary
- [ ] Long-running operations deferred to Action Scheduler (never WP-Cron)
- [ ] Autoloader optimized for production
- [ ] Scripts loaded with `defer` or `async` strategy where possible
- [ ] Large datasets use custom tables with proper indexes (not post meta)
- [ ] Cache invalidated when underlying data changes
- [ ] Admin-only code wrapped in `is_admin()` checks
