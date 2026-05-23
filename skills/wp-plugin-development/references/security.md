# Security Reference

Security is non-negotiable. Every plugin MUST implement these practices. No exceptions.

---

## Core principle: Defense in Depth

Never rely on a single layer of protection. Apply ALL of:
1. **Input validation** — reject invalid data at entry
2. **Input sanitization** — clean data before storage
3. **Output escaping** — escape data before display
4. **Authorization** — verify user capabilities
5. **Nonce verification** — confirm request intent
6. **Prepared statements** — prevent SQL injection

---

## Nonces (CSRF Protection)

Nonces verify that a request was intentional and originated from the expected source.

### Creating nonces

```php
// In a form
wp_nonce_field( 'my_plugin_save_settings', 'my_plugin_nonce' );

// In a URL
$url = wp_nonce_url( admin_url( 'admin.php?action=delete&id=5' ), 'my_plugin_delete_5' );

// Standalone (for AJAX/REST)
$nonce = wp_create_nonce( 'my_plugin_ajax_action' );
```

### Verifying nonces

```php
// Form submission verification
if (
    ! isset( $_POST['my_plugin_nonce'] ) ||
    ! wp_verify_nonce(
        sanitize_text_field( wp_unslash( $_POST['my_plugin_nonce'] ) ),
        'my_plugin_save_settings'
    )
) {
    wp_die( esc_html__( 'Security check failed.', 'my-plugin' ) );
}

// AJAX verification
check_ajax_referer( 'my_plugin_ajax_action', 'nonce' );

// URL verification
if ( ! wp_verify_nonce( $_GET['_wpnonce'], 'my_plugin_delete_5' ) ) {
    wp_die( esc_html__( 'Invalid request.', 'my-plugin' ) );
}
```

### Nonce rules

- ALWAYS use a unique action string per operation (include plugin prefix)
- ALWAYS sanitize the nonce value before verification
- ALWAYS use `wp_unslash()` before sanitization on superglobals
- Nonces expire after 24 hours (12-hour tick validity)
- For REST API: use `permission_callback` instead of nonces

---

## Input Sanitization

Sanitize ALL user input before saving to the database.

### Sanitization functions

| Function | Use for |
|----------|---------|
| `sanitize_text_field()` | Single-line text, general strings |
| `sanitize_textarea_field()` | Multi-line text |
| `sanitize_email()` | Email addresses |
| `sanitize_url()` | URLs |
| `sanitize_title()` | Slugs and URL-safe strings |
| `sanitize_file_name()` | File names |
| `sanitize_key()` | Lowercase alphanumeric + dashes/underscores |
| `sanitize_hex_color()` | CSS hex colors |
| `absint()` | Non-negative integers |
| `intval()` | Integers (can be negative) |
| `wp_kses()` | HTML with allowed tags |
| `wp_kses_post()` | HTML (post content allowed tags) |
| `sanitize_mime_type()` | MIME types |

### Sanitization patterns

```php
// Text field
$title = sanitize_text_field( wp_unslash( $_POST['title'] ?? '' ) );

// Integer
$count = absint( $_POST['count'] ?? 0 );

// Email
$email = sanitize_email( wp_unslash( $_POST['email'] ?? '' ) );
if ( ! is_email( $email ) ) {
    // Handle invalid email
}

// URL
$url = sanitize_url( wp_unslash( $_POST['url'] ?? '' ) );

// Array of values
$ids = array_map( 'absint', (array) ( $_POST['ids'] ?? [] ) );
$ids = array_filter( $ids ); // Remove zeros

// HTML content (limited tags)
$allowed_html = [
    'a'      => [ 'href' => [], 'title' => [] ],
    'strong' => [],
    'em'     => [],
    'p'      => [],
];
$content = wp_kses( wp_unslash( $_POST['content'] ?? '' ), $allowed_html );
```

### Validation before sanitization

```php
// Validate type + sanitize
$status = sanitize_text_field( wp_unslash( $_POST['status'] ?? '' ) );
if ( ! in_array( $status, [ 'draft', 'published', 'archived' ], true ) ) {
    $status = 'draft'; // Default to safe value
}

// Validate range
$per_page = absint( $_POST['per_page'] ?? 10 );
$per_page = min( max( $per_page, 1 ), 100 ); // Clamp between 1 and 100
```

---

## Output Escaping

Escape ALL output. No exceptions. Even data you saved yourself.

### Escaping functions

| Function | Use for |
|----------|---------|
| `esc_html()` | Output inside HTML tags |
| `esc_attr()` | Output in HTML attributes |
| `esc_url()` | Output in `href`, `src`, URL contexts |
| `esc_js()` | Output in inline JavaScript (avoid this pattern) |
| `esc_textarea()` | Output inside `<textarea>` tags |
| `wp_kses()` | Allow specific HTML tags |
| `wp_kses_post()` | Allow post-content HTML |

### Late escaping pattern

ALWAYS escape at the point of output, not earlier:

```php
// CORRECT: Escape at output
<h1><?php echo esc_html( $title ); ?></h1>
<a href="<?php echo esc_url( $link ); ?>"><?php echo esc_html( $text ); ?></a>
<input type="text" value="<?php echo esc_attr( $value ); ?>">
<textarea><?php echo esc_textarea( $content ); ?></textarea>

// WRONG: Escaping at save time, not at output
// $title = esc_html( $input ); // Don't do this on save
// update_option( 'title', $title ); // Stores escaped data
```

### Translation + escaping

```php
// Escaped translation functions (preferred)
esc_html_e( 'Settings saved.', 'my-plugin' );
echo esc_html__( 'Total items:', 'my-plugin' );
printf( esc_html__( 'Found %d results.', 'my-plugin' ), intval( $count ) );

// With HTML
echo wp_kses_post(
    sprintf(
        __( 'Visit <a href="%s">our website</a>.', 'my-plugin' ),
        esc_url( $url )
    )
);
```

---

## Capability Checks (Authorization)

ALWAYS verify the user has permission before executing privileged actions.

### Common capabilities

| Capability | Who has it | Use for |
|-----------|-----------|---------|
| `manage_options` | Administrators | Plugin settings, global config |
| `edit_posts` | Editors, Authors, Contributors | Content-related actions |
| `publish_posts` | Editors, Authors | Publishing content |
| `delete_posts` | Editors, Authors | Deleting content |
| `upload_files` | Authors and above | Media uploads |
| `manage_categories` | Editors and above | Taxonomy management |
| `install_plugins` | Super Admins (Multisite) | Plugin management |

### Implementation pattern

```php
// Admin page registration
function my_plugin_admin_menu(): void {
    add_menu_page(
        __( 'My Plugin', 'my-plugin' ),
        __( 'My Plugin', 'my-plugin' ),
        'manage_options',     // Capability required
        'my-plugin-settings',
        [ $this, 'render_page' ]
    );
}

// Before processing actions
function my_plugin_handle_save(): void {
    // 1. Check capability
    if ( ! current_user_can( 'manage_options' ) ) {
        wp_die( esc_html__( 'Unauthorized access.', 'my-plugin' ) );
    }

    // 2. Verify nonce
    check_admin_referer( 'my_plugin_save', 'my_plugin_nonce' );

    // 3. Sanitize and save
    $value = sanitize_text_field( wp_unslash( $_POST['setting'] ?? '' ) );
    update_option( 'my_plugin_setting', $value );
}

// Custom capabilities (for CPTs)
function my_plugin_register_post_type(): void {
    register_post_type( 'my_plugin_item', [
        'capability_type' => 'my_plugin_item',
        'map_meta_cap'    => true,
        // ... other args
    ] );
}
```

### REST API authorization

```php
register_rest_route( 'my-plugin/v1', '/settings', [
    'methods'             => WP_REST_Server::EDITABLE,
    'callback'            => [ $this, 'update_settings' ],
    'permission_callback' => function () {
        return current_user_can( 'manage_options' );
    },
] );
```

---

## Database Security (SQL Injection Prevention)

ALWAYS use `$wpdb->prepare()` for any query containing dynamic values.

```php
global $wpdb;

// SELECT with prepare
$results = $wpdb->get_results(
    $wpdb->prepare(
        "SELECT * FROM {$wpdb->prefix}my_plugin_logs WHERE user_id = %d AND status = %s",
        $user_id,
        $status
    )
);

// INSERT with prepare
$wpdb->insert(
    "{$wpdb->prefix}my_plugin_logs",
    [
        'user_id'    => $user_id,
        'action'     => $action,
        'created_at' => current_time( 'mysql' ),
    ],
    [ '%d', '%s', '%s' ]
);

// UPDATE with prepare
$wpdb->update(
    "{$wpdb->prefix}my_plugin_logs",
    [ 'status' => 'completed' ],
    [ 'id' => $log_id ],
    [ '%s' ],
    [ '%d' ]
);

// DELETE with prepare
$wpdb->delete(
    "{$wpdb->prefix}my_plugin_logs",
    [ 'id' => $log_id ],
    [ '%d' ]
);
```

### Format specifiers for $wpdb->prepare()

| Specifier | Type |
|-----------|------|
| `%d` | Integer |
| `%f` | Float |
| `%s` | String |

### NEVER do this

```php
// NEVER: Direct variable interpolation
$wpdb->query( "DELETE FROM {$wpdb->prefix}logs WHERE id = {$id}" ); // SQL INJECTION!

// NEVER: User input in query without prepare
$wpdb->get_results( "SELECT * FROM {$wpdb->prefix}logs WHERE status = '$status'" ); // SQL INJECTION!
```

---

## File Upload Security

```php
function my_plugin_handle_upload(): void {
    // 1. Verify nonce and capability
    check_admin_referer( 'my_plugin_upload', 'my_plugin_nonce' );
    if ( ! current_user_can( 'upload_files' ) ) {
        wp_die( 'Unauthorized' );
    }

    // 2. Validate file type
    $allowed_types = [ 'image/jpeg', 'image/png', 'image/webp' ];
    $file_type = wp_check_filetype( $_FILES['my_file']['name'] );
    if ( ! in_array( $file_type['type'], $allowed_types, true ) ) {
        wp_die( 'Invalid file type.' );
    }

    // 3. Use WordPress upload handling
    require_once ABSPATH . 'wp-admin/includes/file.php';
    $upload = wp_handle_upload( $_FILES['my_file'], [ 'test_form' => false ] );

    if ( isset( $upload['error'] ) ) {
        wp_die( esc_html( $upload['error'] ) );
    }

    // 4. Create attachment
    $attachment_id = wp_insert_attachment( [
        'post_mime_type' => $upload['type'],
        'post_title'     => sanitize_file_name( $_FILES['my_file']['name'] ),
        'post_status'    => 'inherit',
    ], $upload['file'] );

    require_once ABSPATH . 'wp-admin/includes/image.php';
    wp_update_attachment_metadata(
        $attachment_id,
        wp_generate_attachment_metadata( $attachment_id, $upload['file'] )
    );
}
```

---

## Direct File Access Prevention

Every PHP file in the plugin (except the main file with plugin header) MUST have:

```php
<?php

defined( 'ABSPATH' ) || exit;
```

---

## Security checklist

Before shipping any plugin:

- [ ] All forms have nonce fields
- [ ] All form handlers verify nonces
- [ ] All user input is sanitized before storage
- [ ] All output is escaped at the point of display
- [ ] All privileged actions check `current_user_can()`
- [ ] All database queries use `$wpdb->prepare()` for dynamic values
- [ ] All files prevent direct access (`defined( 'ABSPATH' ) || exit`)
- [ ] No use of `eval()`, `extract()`, or `unserialize()` on user data
- [ ] File uploads validate MIME types
- [ ] REST endpoints have `permission_callback` defined
- [ ] AJAX handlers verify nonces and capabilities
- [ ] Options are not storing unescaped HTML
- [ ] Action Scheduler callbacks validate input arguments
