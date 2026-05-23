# WP-CLI Reference

Integrating plugins with WP-CLI for command-line management, data operations, and automation.

---

## Registering Commands

### Basic command registration

```php
if ( defined( 'WP_CLI' ) && WP_CLI ) {
    WP_CLI::add_command( 'my-plugin', \MyPlugin\CLI\MainCommand::class );
}
```

Place this in your plugin bootstrap (main plugin file) or in the ServiceProvider boot method (Enterprise tier).

### Command class structure

```php
<?php

declare(strict_types=1);

namespace MyPlugin\CLI;

use WP_CLI;
use WP_CLI\ExitException;

defined( 'ABSPATH' ) || exit;

/**
 * Manages My Plugin operations from the command line.
 */
final class MainCommand {

    /**
     * Imports data from a CSV file.
     *
     * ## OPTIONS
     *
     * <file>
     * : Path to the CSV file to import.
     *
     * [--dry-run]
     * : Preview changes without writing to database.
     *
     * [--batch-size=<number>]
     * : Number of records per batch. Default: 100.
     *
     * ## EXAMPLES
     *
     *     wp my-plugin import /path/to/data.csv
     *     wp my-plugin import /path/to/data.csv --dry-run
     *     wp my-plugin import /path/to/data.csv --batch-size=50
     *
     * @when after_wp_load
     */
    public function import( array $args, array $assoc_args ): void {
        $file       = $args[0];
        $dry_run    = WP_CLI\Utils\get_flag_value( $assoc_args, 'dry-run', false );
        $batch_size = (int) ( $assoc_args['batch-size'] ?? 100 );

        if ( ! file_exists( $file ) ) {
            WP_CLI::error( "File not found: {$file}" );
        }

        if ( $dry_run ) {
            WP_CLI::log( 'Running in dry-run mode. No changes will be made.' );
        }

        $this->process_csv( $file, $batch_size, $dry_run );
    }

    /**
     * Clears all cached data.
     *
     * ## EXAMPLES
     *
     *     wp my-plugin flush-cache
     *
     * @when after_wp_load
     */
    public function flush_cache( array $args, array $assoc_args ): void {
        delete_transient( 'my_plugin_data_cache' );
        wp_cache_flush_group( 'my_plugin' );
        WP_CLI::success( 'Cache cleared successfully.' );
    }

    /**
     * Shows plugin status and statistics.
     *
     * ## OPTIONS
     *
     * [--format=<format>]
     * : Output format. Default: table.
     * ---
     * default: table
     * options:
     *   - table
     *   - json
     *   - csv
     *   - yaml
     * ---
     *
     * ## EXAMPLES
     *
     *     wp my-plugin status
     *     wp my-plugin status --format=json
     *
     * @when after_wp_load
     */
    public function status( array $args, array $assoc_args ): void {
        global $wpdb;

        $format = $assoc_args['format'] ?? 'table';

        $count = (int) $wpdb->get_var(
            "SELECT COUNT(*) FROM {$wpdb->prefix}my_plugin_items"
        );

        $items = [
            [
                'metric' => 'Total Items',
                'value'  => $count,
            ],
            [
                'metric' => 'Version',
                'value'  => MY_PLUGIN_VERSION,
            ],
            [
                'metric' => 'Cache Status',
                'value'  => false !== get_transient( 'my_plugin_data_cache' ) ? 'Active' : 'Empty',
            ],
        ];

        WP_CLI\Utils\format_items( $format, $items, [ 'metric', 'value' ] );
    }

    private function process_csv( string $file, int $batch_size, bool $dry_run ): void {
        $handle = fopen( $file, 'r' );
        if ( false === $handle ) {
            WP_CLI::error( "Unable to open file: {$file}" );
        }

        $headers = fgetcsv( $handle );
        $total   = 0;
        $success = 0;
        $errors  = 0;

        // Count total lines for progress bar
        $line_count = 0;
        while ( fgetcsv( $handle ) ) {
            $line_count++;
        }
        rewind( $handle );
        fgetcsv( $handle ); // Skip header again

        $progress = WP_CLI\Utils\make_progress_bar( 'Importing', $line_count );

        while ( ( $row = fgetcsv( $handle ) ) !== false ) {
            $total++;
            $data = array_combine( $headers, $row );

            if ( ! $dry_run ) {
                $result = $this->insert_record( $data );
                if ( $result ) {
                    $success++;
                } else {
                    $errors++;
                }
            } else {
                $success++;
            }

            $progress->tick();
        }

        $progress->finish();
        fclose( $handle );

        WP_CLI::log( '' );
        WP_CLI::log( "Processed: {$total}" );
        WP_CLI::log( "Success: {$success}" );
        WP_CLI::log( "Errors: {$errors}" );

        if ( $dry_run ) {
            WP_CLI::warning( 'Dry run complete. No records were modified.' );
        } else {
            WP_CLI::success( "Import complete. {$success} records imported." );
        }
    }

    private function insert_record( array $data ): bool {
        global $wpdb;
        return (bool) $wpdb->insert(
            "{$wpdb->prefix}my_plugin_items",
            [
                'title'      => sanitize_text_field( $data['title'] ?? '' ),
                'status'     => sanitize_key( $data['status'] ?? 'draft' ),
                'created_at' => current_time( 'mysql' ),
            ],
            [ '%s', '%s', '%s' ]
        );
    }
}
```

---

## WP-CLI Output Methods

| Method | Use for |
|--------|---------|
| `WP_CLI::log( $msg )` | Informational output (stdout) |
| `WP_CLI::success( $msg )` | Success message (green) |
| `WP_CLI::warning( $msg )` | Warning message (yellow, non-fatal) |
| `WP_CLI::error( $msg )` | Error message (red, exits with code 1) |
| `WP_CLI::error( $msg, false )` | Error without exiting |
| `WP_CLI::debug( $msg )` | Debug output (only with `--debug` flag) |
| `WP_CLI::line( $msg )` | Raw output (no formatting) |
| `WP_CLI::halt( $code )` | Exit with specific code |

---

## Progress Bars

```php
$items = get_items_to_process();
$progress = WP_CLI\Utils\make_progress_bar( 'Processing items', count( $items ) );

foreach ( $items as $item ) {
    // Process item...
    $progress->tick();
}

$progress->finish();
```

---

## Formatted Output

### Table format

```php
$items = [
    [ 'id' => 1, 'name' => 'Item A', 'status' => 'active' ],
    [ 'id' => 2, 'name' => 'Item B', 'status' => 'draft' ],
];

WP_CLI\Utils\format_items(
    $assoc_args['format'] ?? 'table',
    $items,
    [ 'id', 'name', 'status' ]
);
```

### Supported formats

- `table` — ASCII table (default)
- `json` — JSON array
- `csv` — Comma-separated values
- `yaml` — YAML format
- `ids` — Space-separated IDs
- `count` — Just the count

---

## Subcommands

Organize related commands under a namespace:

```php
// Register parent command
WP_CLI::add_command( 'my-plugin', MainCommand::class );

// Register subcommands as separate classes
WP_CLI::add_command( 'my-plugin import', ImportCommand::class );
WP_CLI::add_command( 'my-plugin export', ExportCommand::class );
WP_CLI::add_command( 'my-plugin migrate', MigrateCommand::class );
```

---

## Confirmation Prompts

```php
public function reset( array $args, array $assoc_args ): void {
    WP_CLI::confirm( 'This will delete ALL plugin data. Are you sure?' );

    // Only reaches here if user confirms
    $this->delete_all_data();
    WP_CLI::success( 'All data has been reset.' );
}

// Skip confirmation with --yes flag
public function reset( array $args, array $assoc_args ): void {
    WP_CLI::confirm(
        'This will delete ALL plugin data. Are you sure?',
        $assoc_args
    );
    // --yes flag auto-confirms
}
```

---

## Long-running Operations

### Memory management

```php
public function migrate( array $args, array $assoc_args ): void {
    global $wpdb;

    $batch_size = 100;
    $offset     = 0;

    // Disable autocommit for batch performance
    $wpdb->query( 'SET autocommit = 0' );

    do {
        $items = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT * FROM {$wpdb->prefix}my_plugin_old_table LIMIT %d OFFSET %d",
                $batch_size,
                $offset
            )
        );

        foreach ( $items as $item ) {
            $this->migrate_item( $item );
        }

        $wpdb->query( 'COMMIT' );

        // Free memory
        WP_CLI::debug( "Processed batch at offset {$offset}" );
        $offset += $batch_size;

        // Prevent timeout
        if ( function_exists( 'wp_cache_flush' ) ) {
            wp_cache_flush();
        }
    } while ( ! empty( $items ) );

    $wpdb->query( 'SET autocommit = 1' );
    WP_CLI::success( "Migration complete. Processed {$offset} records." );
}
```

### Disabling hooks for bulk operations

```php
// Remove hooks that fire on every post save during bulk import
remove_action( 'save_post', 'my_plugin_update_cache' );

foreach ( $items as $item ) {
    wp_insert_post( $item );
}

// Re-add hooks
add_action( 'save_post', 'my_plugin_update_cache' );

// Rebuild cache once
my_plugin_rebuild_full_cache();
```

---

## Best Practices

- ALWAYS use `@when after_wp_load` for commands that need WordPress loaded
- ALWAYS include `## OPTIONS` and `## EXAMPLES` in PHPDoc for discoverability
- ALWAYS validate input before processing
- ALWAYS support `--format` for data output commands
- ALWAYS include `--dry-run` for destructive operations
- Use progress bars for operations with > 10 items
- Free memory periodically in long-running operations (`wp_cache_flush()`)
- Use `WP_CLI::confirm()` for irreversible actions
- Support `--yes` flag to skip confirmation in scripts
- Handle interrupts gracefully (store progress, allow resume)
