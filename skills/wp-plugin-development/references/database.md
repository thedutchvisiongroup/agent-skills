# Database Reference

Custom tables, migrations, and safe database interactions for WordPress plugins.

---

## When to use custom tables vs WordPress built-ins

| Scenario | Solution |
|----------|----------|
| Key-value settings | Options API (`get_option` / `update_option`) |
| Data attached to posts | Post Meta (`get_post_meta` / `update_post_meta`) |
| Data attached to users | User Meta (`get_user_meta` / `update_user_meta`) |
| Structured content with titles/slugs | Custom Post Type |
| High-volume structured data (logs, analytics, transactions) | **Custom table** |
| Data requiring complex queries (JOINs, aggregations) | **Custom table** |
| Data that doesn't map to post/user/term/comment paradigm | **Custom table** |

**Rule**: Use custom tables when data volume exceeds ~10k rows of meta, requires complex indexing, or has relational structure that meta tables cannot efficiently handle.

---

## Creating Custom Tables with dbDelta

### Schema class

```php
<?php

declare(strict_types=1);

namespace MyPlugin\Database;

defined( 'ABSPATH' ) || exit;

final class Schema {

    public static function create_tables(): void {
        global $wpdb;
        $charset_collate = $wpdb->get_charset_collate();

        $tables = [];

        // Items table
        $tables[] = "CREATE TABLE {$wpdb->prefix}my_plugin_items (
            id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            title varchar(255) NOT NULL DEFAULT '',
            slug varchar(255) NOT NULL DEFAULT '',
            status varchar(20) NOT NULL DEFAULT 'draft',
            author_id bigint(20) unsigned NOT NULL DEFAULT 0,
            content longtext NOT NULL DEFAULT '',
            meta_data longtext DEFAULT NULL,
            created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY status (status),
            KEY author_id (author_id),
            KEY created_at (created_at),
            UNIQUE KEY slug (slug)
        ) {$charset_collate};";

        // Logs table
        $tables[] = "CREATE TABLE {$wpdb->prefix}my_plugin_logs (
            id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            item_id bigint(20) unsigned NOT NULL DEFAULT 0,
            user_id bigint(20) unsigned NOT NULL DEFAULT 0,
            action varchar(50) NOT NULL DEFAULT '',
            details longtext DEFAULT NULL,
            ip_address varchar(45) DEFAULT NULL,
            created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            KEY item_id (item_id),
            KEY user_id (user_id),
            KEY action (action),
            KEY created_at (created_at)
        ) {$charset_collate};";

        require_once ABSPATH . 'wp-admin/includes/upgrade.php';

        foreach ( $tables as $sql ) {
            dbDelta( $sql );
        }
    }

    public static function drop_tables(): void {
        global $wpdb;
        $wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}my_plugin_logs" );
        $wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}my_plugin_items" );
    }
}
```

### dbDelta requirements

dbDelta is strict about SQL formatting. Follow these rules EXACTLY:

- Each field on its own line
- TWO spaces between field name and type definition
- Use `KEY` for indexes, not `INDEX`
- `PRIMARY KEY` must have TWO spaces before `(id)`
- No comma after the last line before closing `)`
- Must use `$wpdb->get_charset_collate()` for the charset
- Table names MUST use `$wpdb->prefix`
- Do NOT use `IF NOT EXISTS` (dbDelta handles this)

### Critical dbDelta formatting

```sql
-- CORRECT (note the spacing):
CREATE TABLE {$wpdb->prefix}my_plugin_items (
    id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
    title varchar(255) NOT NULL DEFAULT '',
    PRIMARY KEY  (id),
    KEY title (title(191))
) {$charset_collate};

-- WRONG (will fail):
CREATE TABLE IF NOT EXISTS my_plugin_items (   -- No IF NOT EXISTS, no prefix
    `id` bigint(20),                           -- No backticks
    PRIMARY KEY(id)                            -- Needs two spaces before (id)
);
```

---

## Schema Versioning (Migrations)

Track and apply schema changes across plugin updates.

```php
<?php

declare(strict_types=1);

namespace MyPlugin\Database;

defined( 'ABSPATH' ) || exit;

final class Migrator {

    private const DB_VERSION_OPTION = 'my_plugin_db_version';
    private const CURRENT_VERSION   = '1.2.0';

    public function run(): void {
        $installed_version = get_option( self::DB_VERSION_OPTION, '0.0.0' );

        if ( version_compare( $installed_version, self::CURRENT_VERSION, '>=' ) ) {
            return; // Already up to date
        }

        if ( version_compare( $installed_version, '1.0.0', '<' ) ) {
            $this->migrate_to_1_0_0();
        }

        if ( version_compare( $installed_version, '1.1.0', '<' ) ) {
            $this->migrate_to_1_1_0();
        }

        if ( version_compare( $installed_version, '1.2.0', '<' ) ) {
            $this->migrate_to_1_2_0();
        }

        update_option( self::DB_VERSION_OPTION, self::CURRENT_VERSION );
    }

    private function migrate_to_1_0_0(): void {
        Schema::create_tables();
    }

    private function migrate_to_1_1_0(): void {
        global $wpdb;

        // Add a new column
        $column_exists = $wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                 WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s",
                DB_NAME,
                "{$wpdb->prefix}my_plugin_items",
                'priority'
            )
        );

        if ( ! $column_exists ) {
            $wpdb->query(
                "ALTER TABLE {$wpdb->prefix}my_plugin_items
                 ADD COLUMN priority tinyint(3) unsigned NOT NULL DEFAULT 0 AFTER status"
            );

            $wpdb->query(
                "ALTER TABLE {$wpdb->prefix}my_plugin_items
                 ADD KEY priority (priority)"
            );
        }
    }

    private function migrate_to_1_2_0(): void {
        global $wpdb;

        // Add a new table
        $charset_collate = $wpdb->get_charset_collate();

        $sql = "CREATE TABLE {$wpdb->prefix}my_plugin_settings_history (
            id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
            setting_key varchar(100) NOT NULL DEFAULT '',
            old_value longtext DEFAULT NULL,
            new_value longtext DEFAULT NULL,
            changed_by bigint(20) unsigned NOT NULL DEFAULT 0,
            changed_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY  (id),
            KEY setting_key (setting_key),
            KEY changed_at (changed_at)
        ) {$charset_collate};";

        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
        dbDelta( $sql );
    }
}
```

### Running migrations

Call the migrator on every admin page load (it short-circuits if version matches):

```php
// In the plugin orchestrator or activation hook
add_action( 'plugins_loaded', function (): void {
    ( new \MyPlugin\Database\Migrator() )->run();
} );

// Also run on activation (for fresh installs)
register_activation_hook( __FILE__, function (): void {
    ( new \MyPlugin\Database\Migrator() )->run();
} );
```

---

## Query Patterns

### Repository pattern

```php
<?php

declare(strict_types=1);

namespace MyPlugin\Database;

defined( 'ABSPATH' ) || exit;

final class ItemRepository {

    private string $table;

    public function __construct() {
        global $wpdb;
        $this->table = "{$wpdb->prefix}my_plugin_items";
    }

    public function find( int $id ): ?object {
        global $wpdb;
        return $wpdb->get_row(
            $wpdb->prepare( "SELECT * FROM {$this->table} WHERE id = %d", $id )
        );
    }

    public function find_by_status( string $status, int $limit = 20, int $offset = 0 ): array {
        global $wpdb;
        return $wpdb->get_results(
            $wpdb->prepare(
                "SELECT * FROM {$this->table}
                 WHERE status = %s
                 ORDER BY created_at DESC
                 LIMIT %d OFFSET %d",
                $status,
                $limit,
                $offset
            )
        );
    }

    public function count_by_status( string $status ): int {
        global $wpdb;
        return (int) $wpdb->get_var(
            $wpdb->prepare(
                "SELECT COUNT(*) FROM {$this->table} WHERE status = %s",
                $status
            )
        );
    }

    public function create( array $data ): int {
        global $wpdb;
        $wpdb->insert(
            $this->table,
            [
                'title'      => $data['title'],
                'slug'       => sanitize_title( $data['title'] ),
                'status'     => $data['status'] ?? 'draft',
                'author_id'  => $data['author_id'] ?? get_current_user_id(),
                'content'    => $data['content'] ?? '',
                'created_at' => current_time( 'mysql' ),
            ],
            [ '%s', '%s', '%s', '%d', '%s', '%s' ]
        );

        return (int) $wpdb->insert_id;
    }

    public function update( int $id, array $data ): bool {
        global $wpdb;
        $fields  = [];
        $formats = [];

        $allowed = [ 'title', 'slug', 'status', 'content', 'priority' ];
        foreach ( $allowed as $field ) {
            if ( array_key_exists( $field, $data ) ) {
                $fields[ $field ] = $data[ $field ];
                $formats[]        = is_int( $data[ $field ] ) ? '%d' : '%s';
            }
        }

        if ( empty( $fields ) ) {
            return false;
        }

        return (bool) $wpdb->update(
            $this->table,
            $fields,
            [ 'id' => $id ],
            $formats,
            [ '%d' ]
        );
    }

    public function delete( int $id ): bool {
        global $wpdb;
        return (bool) $wpdb->delete(
            $this->table,
            [ 'id' => $id ],
            [ '%d' ]
        );
    }

    public function search( string $query, int $limit = 20 ): array {
        global $wpdb;
        $like = '%' . $wpdb->esc_like( $query ) . '%';
        return $wpdb->get_results(
            $wpdb->prepare(
                "SELECT * FROM {$this->table}
                 WHERE title LIKE %s OR content LIKE %s
                 ORDER BY created_at DESC
                 LIMIT %d",
                $like,
                $like,
                $limit
            )
        );
    }
}
```

---

## Important $wpdb methods

| Method | Returns | Use for |
|--------|---------|---------|
| `$wpdb->get_results( $sql )` | Array of row objects | Multiple rows |
| `$wpdb->get_row( $sql )` | Single row object or null | One row |
| `$wpdb->get_var( $sql )` | Single value or null | COUNT, MAX, etc. |
| `$wpdb->get_col( $sql )` | Array of single column values | List of IDs |
| `$wpdb->insert( $table, $data, $format )` | Rows affected (int/false) | INSERT |
| `$wpdb->update( $table, $data, $where, $format, $where_format )` | Rows affected (int/false) | UPDATE |
| `$wpdb->delete( $table, $where, $format )` | Rows affected (int/false) | DELETE |
| `$wpdb->query( $sql )` | Rows affected (int/false) | Raw queries |
| `$wpdb->prepare( $sql, ...$args )` | Prepared SQL string | Parameter binding |

---

## Performance considerations for custom tables

- ALWAYS add indexes for columns used in WHERE, ORDER BY, or JOIN
- Use appropriate column types (don't use TEXT for 50-char strings)
- Add composite indexes for common query patterns
- Consider partitioning for tables exceeding millions of rows
- Use `$wpdb->get_var()` for COUNT queries (don't fetch all rows to count)
- Batch INSERT/UPDATE operations (don't run 1000 individual queries)
- Use transactions for atomic operations:

```php
global $wpdb;
$wpdb->query( 'START TRANSACTION' );

try {
    $wpdb->insert( /* ... */ );
    $wpdb->insert( /* ... */ );
    $wpdb->query( 'COMMIT' );
} catch ( \Exception $e ) {
    $wpdb->query( 'ROLLBACK' );
    throw $e;
}
```

---

## Cleanup on uninstall

ALWAYS clean up custom tables when the plugin is deleted:

```php
// uninstall.php
defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

global $wpdb;

// Drop tables in correct order (foreign key constraints)
$wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}my_plugin_logs" );
$wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}my_plugin_items" );
$wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}my_plugin_settings_history" );

// Remove options
delete_option( 'my_plugin_db_version' );
delete_option( 'my_plugin_settings' );

// Remove user meta (if applicable)
$wpdb->query( "DELETE FROM {$wpdb->usermeta} WHERE meta_key LIKE 'my_plugin_%'" );

// Remove transients
$wpdb->query(
    "DELETE FROM {$wpdb->options}
     WHERE option_name LIKE '_transient_my_plugin_%'
     OR option_name LIKE '_transient_timeout_my_plugin_%'"
);
```
