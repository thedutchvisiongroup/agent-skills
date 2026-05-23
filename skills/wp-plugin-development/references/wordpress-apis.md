# WordPress APIs Reference

Core WordPress APIs for plugin development. Prefer these over raw PHP equivalents.

---

## Hooks API (Actions & Filters)

The hook system is the backbone of WordPress extensibility.

### Actions

Execute code at specific points in WordPress execution.

```php
// Register an action
add_action( 'init', [ $this, 'register_post_types' ] );
add_action( 'admin_init', [ $this, 'register_settings' ], 20 ); // Priority 20
add_action( 'save_post_product', [ $this, 'clear_cache' ], 10, 2 ); // 2 args

// Fire a custom action (for extensibility)
do_action( 'my_plugin/item_created', $item_id, $item_data );

// Remove an action
remove_action( 'init', [ $instance, 'some_method' ], 10 );
```

### Filters

Modify data passing through WordPress.

```php
// Register a filter
add_filter( 'the_content', [ $this, 'append_cta' ] );
add_filter( 'my_plugin/default_settings', [ $this, 'override_defaults' ] );

// Apply a custom filter (for extensibility)
$settings = apply_filters( 'my_plugin/settings', $default_settings );
$template = apply_filters( 'my_plugin/template_path', $default_path, $template_name );

// Remove a filter
remove_filter( 'the_content', [ $instance, 'append_cta' ], 10 );
```

### Key WordPress hooks for plugins

| Hook | Type | When it fires |
|------|------|--------------|
| `plugins_loaded` | Action | After all plugins loaded (use for initialization) |
| `init` | Action | After WordPress core loads (register CPTs, taxonomies) |
| `admin_init` | Action | Admin screens init (register settings) |
| `admin_menu` | Action | Building admin menu |
| `admin_enqueue_scripts` | Action | Enqueue admin assets |
| `wp_enqueue_scripts` | Action | Enqueue frontend assets |
| `rest_api_init` | Action | Register REST routes |
| `save_post` | Action | Post saved |
| `save_post_{post_type}` | Action | Specific post type saved |
| `wp_ajax_{action}` | Action | AJAX handler (logged-in) |
| `wp_ajax_nopriv_{action}` | Action | AJAX handler (not logged-in) |
| `activated_plugin` | Action | Plugin activated |
| `the_content` | Filter | Post content before display |
| `plugin_action_links_{file}` | Filter | Plugin action links on plugins page |

### Making your plugin extensible

```php
// Allow other plugins/themes to modify your output
public function get_items(): array {
    $items = $this->query_items();

    // Let others filter the results
    return apply_filters( 'my_plugin/items', $items );
}

// Allow others to hook into your workflow
public function create_item( array $data ): int {
    do_action( 'my_plugin/before_item_create', $data );

    $item_id = $this->insert( $data );

    do_action( 'my_plugin/after_item_create', $item_id, $data );

    return $item_id;
}
```

---

## REST API

Build custom REST endpoints for your plugin.

### Registering routes

```php
<?php

declare(strict_types=1);

namespace MyPlugin\REST;

use WP_REST_Controller;
use WP_REST_Request;
use WP_REST_Response;
use WP_REST_Server;
use WP_Error;

defined( 'ABSPATH' ) || exit;

final class ItemsController extends WP_REST_Controller {

    protected $namespace = 'my-plugin/v1';
    protected $rest_base = 'items';

    public function register_routes(): void {
        register_rest_route( $this->namespace, '/' . $this->rest_base, [
            [
                'methods'             => WP_REST_Server::READABLE,
                'callback'            => [ $this, 'get_items' ],
                'permission_callback' => [ $this, 'get_items_permissions_check' ],
                'args'                => $this->get_collection_params(),
            ],
            [
                'methods'             => WP_REST_Server::CREATABLE,
                'callback'            => [ $this, 'create_item' ],
                'permission_callback' => [ $this, 'create_item_permissions_check' ],
                'args'                => $this->get_endpoint_args_for_item_schema( WP_REST_Server::CREATABLE ),
            ],
            'schema' => [ $this, 'get_public_item_schema' ],
        ] );

        register_rest_route( $this->namespace, '/' . $this->rest_base . '/(?P<id>[\d]+)', [
            [
                'methods'             => WP_REST_Server::READABLE,
                'callback'            => [ $this, 'get_item' ],
                'permission_callback' => [ $this, 'get_item_permissions_check' ],
                'args'                => [
                    'id' => [
                        'validate_callback' => fn( $param ) => is_numeric( $param ),
                    ],
                ],
            ],
            [
                'methods'             => WP_REST_Server::EDITABLE,
                'callback'            => [ $this, 'update_item' ],
                'permission_callback' => [ $this, 'update_item_permissions_check' ],
            ],
            [
                'methods'             => WP_REST_Server::DELETABLE,
                'callback'            => [ $this, 'delete_item' ],
                'permission_callback' => [ $this, 'delete_item_permissions_check' ],
            ],
        ] );
    }

    public function get_items_permissions_check( WP_REST_Request $request ): bool {
        return true; // Public endpoint
    }

    public function create_item_permissions_check( WP_REST_Request $request ): bool|WP_Error {
        if ( ! current_user_can( 'edit_posts' ) ) {
            return new WP_Error(
                'rest_forbidden',
                __( 'You do not have permission to create items.', 'my-plugin' ),
                [ 'status' => 403 ]
            );
        }
        return true;
    }

    public function get_items( WP_REST_Request $request ): WP_REST_Response {
        $per_page = $request->get_param( 'per_page' ) ?? 10;
        $page     = $request->get_param( 'page' ) ?? 1;

        global $wpdb;
        $items = $wpdb->get_results(
            $wpdb->prepare(
                "SELECT * FROM {$wpdb->prefix}my_plugin_items
                 ORDER BY created_at DESC
                 LIMIT %d OFFSET %d",
                $per_page,
                ( $page - 1 ) * $per_page
            )
        );

        $total = (int) $wpdb->get_var(
            "SELECT COUNT(*) FROM {$wpdb->prefix}my_plugin_items"
        );

        $response = new WP_REST_Response( $items, 200 );
        $response->header( 'X-WP-Total', (string) $total );
        $response->header( 'X-WP-TotalPages', (string) ceil( $total / $per_page ) );

        return $response;
    }

    public function create_item( WP_REST_Request $request ): WP_REST_Response|WP_Error {
        $title  = sanitize_text_field( $request->get_param( 'title' ) );
        $status = sanitize_key( $request->get_param( 'status' ) ?? 'draft' );

        if ( empty( $title ) ) {
            return new WP_Error( 'missing_title', __( 'Title is required.', 'my-plugin' ), [ 'status' => 400 ] );
        }

        global $wpdb;
        $inserted = $wpdb->insert(
            "{$wpdb->prefix}my_plugin_items",
            [
                'title'      => $title,
                'status'     => $status,
                'author_id'  => get_current_user_id(),
                'created_at' => current_time( 'mysql' ),
            ],
            [ '%s', '%s', '%d', '%s' ]
        );

        if ( ! $inserted ) {
            return new WP_Error( 'insert_failed', __( 'Failed to create item.', 'my-plugin' ), [ 'status' => 500 ] );
        }

        $item = $wpdb->get_row(
            $wpdb->prepare(
                "SELECT * FROM {$wpdb->prefix}my_plugin_items WHERE id = %d",
                $wpdb->insert_id
            )
        );

        return new WP_REST_Response( $item, 201 );
    }

    public function get_item_schema(): array {
        return [
            '$schema'    => 'http://json-schema.org/draft-04/schema#',
            'title'      => 'my-plugin-item',
            'type'       => 'object',
            'properties' => [
                'id' => [
                    'description' => __( 'Unique identifier.', 'my-plugin' ),
                    'type'        => 'integer',
                    'context'     => [ 'view', 'edit' ],
                    'readonly'    => true,
                ],
                'title' => [
                    'description' => __( 'Item title.', 'my-plugin' ),
                    'type'        => 'string',
                    'required'    => true,
                ],
                'status' => [
                    'description' => __( 'Item status.', 'my-plugin' ),
                    'type'        => 'string',
                    'enum'        => [ 'draft', 'active', 'archived' ],
                    'default'     => 'draft',
                ],
            ],
        ];
    }
}
```

### REST API constants

| Constant | HTTP Method |
|----------|-------------|
| `WP_REST_Server::READABLE` | GET |
| `WP_REST_Server::CREATABLE` | POST |
| `WP_REST_Server::EDITABLE` | POST, PUT, PATCH |
| `WP_REST_Server::DELETABLE` | DELETE |
| `WP_REST_Server::ALLMETHODS` | All methods |

---

## Settings API

Register and manage plugin settings with built-in validation.

```php
<?php

declare(strict_types=1);

namespace MyPlugin\Admin;

defined( 'ABSPATH' ) || exit;

final class Settings {

    private const OPTION_GROUP = 'my_plugin_settings';
    private const OPTION_NAME  = 'my_plugin_options';
    private const PAGE_SLUG    = 'my-plugin-settings';

    public function register(): void {
        register_setting(
            self::OPTION_GROUP,
            self::OPTION_NAME,
            [
                'type'              => 'array',
                'sanitize_callback' => [ $this, 'sanitize_options' ],
                'default'           => $this->get_defaults(),
            ]
        );

        add_settings_section(
            'my_plugin_general',
            __( 'General Settings', 'my-plugin' ),
            [ $this, 'render_section_description' ],
            self::PAGE_SLUG
        );

        add_settings_field(
            'api_key',
            __( 'API Key', 'my-plugin' ),
            [ $this, 'render_text_field' ],
            self::PAGE_SLUG,
            'my_plugin_general',
            [
                'label_for' => 'api_key',
                'type'      => 'password',
            ]
        );

        add_settings_field(
            'enabled',
            __( 'Enable Plugin', 'my-plugin' ),
            [ $this, 'render_checkbox_field' ],
            self::PAGE_SLUG,
            'my_plugin_general',
            [
                'label_for'   => 'enabled',
                'description' => __( 'Enable or disable plugin functionality.', 'my-plugin' ),
            ]
        );
    }

    public function sanitize_options( array $input ): array {
        $sanitized = [];
        $sanitized['api_key'] = sanitize_text_field( $input['api_key'] ?? '' );
        $sanitized['enabled'] = ! empty( $input['enabled'] );
        return $sanitized;
    }

    public function get_defaults(): array {
        return [
            'api_key' => '',
            'enabled' => false,
        ];
    }

    public function render_section_description(): void {
        echo '<p>' . esc_html__( 'Configure the plugin settings below.', 'my-plugin' ) . '</p>';
    }

    public function render_text_field( array $args ): void {
        $options = get_option( self::OPTION_NAME, $this->get_defaults() );
        $value   = $options[ $args['label_for'] ] ?? '';
        $type    = $args['type'] ?? 'text';

        printf(
            '<input type="%s" id="%s" name="%s[%s]" value="%s" class="regular-text">',
            esc_attr( $type ),
            esc_attr( $args['label_for'] ),
            esc_attr( self::OPTION_NAME ),
            esc_attr( $args['label_for'] ),
            esc_attr( $value )
        );
    }

    public function render_checkbox_field( array $args ): void {
        $options = get_option( self::OPTION_NAME, $this->get_defaults() );
        $checked = ! empty( $options[ $args['label_for'] ] );

        printf(
            '<input type="checkbox" id="%s" name="%s[%s]" value="1" %s>',
            esc_attr( $args['label_for'] ),
            esc_attr( self::OPTION_NAME ),
            esc_attr( $args['label_for'] ),
            checked( $checked, true, false )
        );

        if ( ! empty( $args['description'] ) ) {
            printf( '<p class="description">%s</p>', esc_html( $args['description'] ) );
        }
    }

    public function render_page(): void {
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }

        ?>
        <div class="wrap">
            <h1><?php echo esc_html( get_admin_page_title() ); ?></h1>
            <form action="options.php" method="post">
                <?php
                settings_fields( self::OPTION_GROUP );
                do_settings_sections( self::PAGE_SLUG );
                submit_button();
                ?>
            </form>
        </div>
        <?php
    }
}
```

---

## Custom Post Types

```php
<?php

declare(strict_types=1);

namespace MyPlugin\PostTypes;

defined( 'ABSPATH' ) || exit;

final class BookPostType {

    public const POST_TYPE = 'my_plugin_book';

    public function register(): void {
        register_post_type( self::POST_TYPE, [
            'labels'             => $this->get_labels(),
            'public'             => true,
            'publicly_queryable' => true,
            'show_ui'            => true,
            'show_in_menu'       => true,
            'show_in_rest'       => true, // Enables Gutenberg & REST API
            'query_var'          => true,
            'rewrite'            => [ 'slug' => 'books' ],
            'capability_type'    => 'post',
            'has_archive'        => true,
            'hierarchical'       => false,
            'menu_position'      => 20,
            'menu_icon'          => 'dashicons-book',
            'supports'           => [ 'title', 'editor', 'thumbnail', 'excerpt', 'custom-fields' ],
        ] );
    }

    private function get_labels(): array {
        return [
            'name'               => _x( 'Books', 'post type general name', 'my-plugin' ),
            'singular_name'      => _x( 'Book', 'post type singular name', 'my-plugin' ),
            'menu_name'          => _x( 'Books', 'admin menu', 'my-plugin' ),
            'add_new'            => _x( 'Add New', 'book', 'my-plugin' ),
            'add_new_item'       => __( 'Add New Book', 'my-plugin' ),
            'new_item'           => __( 'New Book', 'my-plugin' ),
            'edit_item'          => __( 'Edit Book', 'my-plugin' ),
            'view_item'          => __( 'View Book', 'my-plugin' ),
            'all_items'          => __( 'All Books', 'my-plugin' ),
            'search_items'       => __( 'Search Books', 'my-plugin' ),
            'not_found'          => __( 'No books found.', 'my-plugin' ),
            'not_found_in_trash' => __( 'No books found in Trash.', 'my-plugin' ),
        ];
    }
}
```

---

## Custom Taxonomies

```php
<?php

declare(strict_types=1);

namespace MyPlugin\Taxonomies;

defined( 'ABSPATH' ) || exit;

final class GenreTaxonomy {

    public const TAXONOMY = 'my_plugin_genre';

    public function register(): void {
        register_taxonomy( self::TAXONOMY, [ BookPostType::POST_TYPE ], [
            'labels'            => $this->get_labels(),
            'hierarchical'      => true,
            'public'            => true,
            'show_ui'           => true,
            'show_admin_column' => true,
            'show_in_rest'      => true,
            'query_var'         => true,
            'rewrite'           => [ 'slug' => 'genre' ],
        ] );
    }

    private function get_labels(): array {
        return [
            'name'              => _x( 'Genres', 'taxonomy general name', 'my-plugin' ),
            'singular_name'     => _x( 'Genre', 'taxonomy singular name', 'my-plugin' ),
            'search_items'      => __( 'Search Genres', 'my-plugin' ),
            'all_items'         => __( 'All Genres', 'my-plugin' ),
            'parent_item'       => __( 'Parent Genre', 'my-plugin' ),
            'parent_item_colon' => __( 'Parent Genre:', 'my-plugin' ),
            'edit_item'         => __( 'Edit Genre', 'my-plugin' ),
            'update_item'       => __( 'Update Genre', 'my-plugin' ),
            'add_new_item'      => __( 'Add New Genre', 'my-plugin' ),
            'new_item_name'     => __( 'New Genre Name', 'my-plugin' ),
            'menu_name'         => __( 'Genres', 'my-plugin' ),
        ];
    }
}
```

---

## Meta Boxes

```php
<?php

declare(strict_types=1);

namespace MyPlugin\Admin;

defined( 'ABSPATH' ) || exit;

final class BookMetaBox {

    private const NONCE_ACTION = 'my_plugin_book_meta';
    private const NONCE_NAME   = 'my_plugin_book_meta_nonce';
    private const META_KEY     = '_my_plugin_isbn';

    public function register(): void {
        add_meta_box(
            'my_plugin_book_details',
            __( 'Book Details', 'my-plugin' ),
            [ $this, 'render' ],
            \MyPlugin\PostTypes\BookPostType::POST_TYPE,
            'side',
            'high'
        );
    }

    public function render( \WP_Post $post ): void {
        $isbn = get_post_meta( $post->ID, self::META_KEY, true );
        wp_nonce_field( self::NONCE_ACTION, self::NONCE_NAME );
        ?>
        <p>
            <label for="my_plugin_isbn"><?php esc_html_e( 'ISBN:', 'my-plugin' ); ?></label>
            <input type="text" id="my_plugin_isbn" name="my_plugin_isbn"
                   value="<?php echo esc_attr( $isbn ); ?>" class="widefat">
        </p>
        <?php
    }

    public function save( int $post_id ): void {
        // Verify nonce
        if (
            ! isset( $_POST[ self::NONCE_NAME ] ) ||
            ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST[ self::NONCE_NAME ] ) ), self::NONCE_ACTION )
        ) {
            return;
        }

        // Check autosave
        if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
            return;
        }

        // Check permissions
        if ( ! current_user_can( 'edit_post', $post_id ) ) {
            return;
        }

        // Sanitize and save
        if ( isset( $_POST['my_plugin_isbn'] ) ) {
            $isbn = sanitize_text_field( wp_unslash( $_POST['my_plugin_isbn'] ) );
            update_post_meta( $post_id, self::META_KEY, $isbn );
        }
    }
}
```

---

## Options API

```php
// Store a single value
update_option( 'my_plugin_version', '1.0.0' );
$version = get_option( 'my_plugin_version', '0.0.0' ); // With default

// Store an array
update_option( 'my_plugin_settings', [
    'api_key' => 'abc123',
    'enabled' => true,
] );
$settings = get_option( 'my_plugin_settings', [] );

// Delete an option
delete_option( 'my_plugin_settings' );

// Autoload control (set false for rarely-used options)
add_option( 'my_plugin_large_data', $data, '', false ); // No autoload
```

---

## AJAX API

```php
// Register AJAX handlers
add_action( 'wp_ajax_my_plugin_save', [ $this, 'ajax_save' ] );        // Logged-in
add_action( 'wp_ajax_nopriv_my_plugin_save', [ $this, 'ajax_save' ] ); // Not logged-in

public function ajax_save(): void {
    // Verify nonce
    check_ajax_referer( 'my_plugin_nonce', 'nonce' );

    // Check capability
    if ( ! current_user_can( 'edit_posts' ) ) {
        wp_send_json_error( [ 'message' => 'Unauthorized' ], 403 );
    }

    // Process request
    $title = sanitize_text_field( wp_unslash( $_POST['title'] ?? '' ) );

    if ( empty( $title ) ) {
        wp_send_json_error( [ 'message' => 'Title is required.' ], 400 );
    }

    // Save and respond
    $result = $this->save_item( $title );
    wp_send_json_success( [ 'id' => $result ] );
}
```

---

## Internationalization (i18n)

```php
// Simple string
__( 'Settings', 'my-plugin' )

// Echo directly
_e( 'Save Changes', 'my-plugin' );

// With context
_x( 'Post', 'verb', 'my-plugin' );

// Plurals
sprintf(
    _n( '%d item', '%d items', $count, 'my-plugin' ),
    $count
);

// Load text domain (in init or plugins_loaded)
load_plugin_textdomain( 'my-plugin', false, dirname( plugin_basename( __FILE__ ) ) . '/languages' );
```
