# Testing & Debugging Reference

Unit testing, integration testing, and debugging workflows for WordPress plugins.

---

## Testing Stack

| Tool | Purpose |
|------|---------|
| PHPUnit | Test framework |
| WP_Mock | Mock WordPress functions without loading WP |
| Brain Monkey | Alternative to WP_Mock, Mockery-based |
| WordPress Test Suite | Integration tests with real WP environment |
| PHP_CodeSniffer + WPCS | Code style and standards enforcement |
| PHPStan / Psalm | Static analysis |

---

## Project Setup

### composer.json (dev dependencies)

```json
{
  "require-dev": {
    "phpunit/phpunit": "^10.0",
    "10up/wp_mock": "^1.0",
    "brain/monkey": "^2.6",
    "phpstan/phpstan": "^1.10",
    "wp-coding-standards/wpcs": "^3.0",
    "dealerdirect/phpcodesniffer-composer-installer": "^1.0",
    "phpcompatibility/phpcompatibility-wp": "^2.1"
  },
  "scripts": {
    "test": "phpunit",
    "test:unit": "phpunit --testsuite unit",
    "test:integration": "phpunit --testsuite integration",
    "lint": "phpcs",
    "lint:fix": "phpcbf",
    "analyze": "phpstan analyse"
  }
}
```

### phpunit.xml

```xml
<?xml version="1.0"?>
<phpunit
    bootstrap="tests/bootstrap.php"
    colors="true"
    testdox="true"
>
    <testsuites>
        <testsuite name="unit">
            <directory>tests/Unit</directory>
        </testsuite>
        <testsuite name="integration">
            <directory>tests/Integration</directory>
        </testsuite>
    </testsuites>
    <source>
        <include>
            <directory suffix=".php">src</directory>
        </include>
    </source>
</phpunit>
```

### Test bootstrap (unit tests with WP_Mock)

```php
<?php
// tests/bootstrap.php

require_once dirname( __DIR__ ) . '/vendor/autoload.php';

WP_Mock::bootstrap();
```

### Test bootstrap (integration tests with WordPress)

```php
<?php
// tests/bootstrap-integration.php

$_tests_dir = getenv( 'WP_TESTS_DIR' ) ?: '/tmp/wordpress-tests-lib';

require_once $_tests_dir . '/includes/functions.php';

// Load plugin
tests_add_filter( 'muplugins_loaded', function () {
    require dirname( __DIR__ ) . '/my-plugin.php';
} );

require $_tests_dir . '/includes/bootstrap.php';
```

---

## Unit Testing with WP_Mock

Unit tests mock WordPress functions. They're fast and don't require a WordPress installation.

### Basic test class

```php
<?php

declare(strict_types=1);

namespace MyPlugin\Tests\Unit;

use MyPlugin\Admin\Settings;
use WP_Mock;
use WP_Mock\Tools\TestCase;

final class SettingsTest extends TestCase {

    private Settings $settings;

    public function setUp(): void {
        parent::setUp();
        $this->settings = new Settings();
    }

    public function tearDown(): void {
        parent::tearDown();
    }

    public function test_get_defaults_returns_expected_structure(): void {
        $defaults = $this->settings->get_defaults();

        $this->assertIsArray( $defaults );
        $this->assertArrayHasKey( 'api_key', $defaults );
        $this->assertArrayHasKey( 'enabled', $defaults );
        $this->assertSame( '', $defaults['api_key'] );
        $this->assertFalse( $defaults['enabled'] );
    }

    public function test_sanitize_options_sanitizes_api_key(): void {
        WP_Mock::userFunction( 'sanitize_text_field' )
            ->once()
            ->with( '<script>alert("xss")</script>' )
            ->andReturn( 'alertxss' );

        $result = $this->settings->sanitize_options( [
            'api_key' => '<script>alert("xss")</script>',
            'enabled' => '1',
        ] );

        $this->assertSame( 'alertxss', $result['api_key'] );
        $this->assertTrue( $result['enabled'] );
    }

    public function test_sanitize_options_handles_empty_input(): void {
        WP_Mock::userFunction( 'sanitize_text_field' )
            ->once()
            ->with( '' )
            ->andReturn( '' );

        $result = $this->settings->sanitize_options( [] );

        $this->assertSame( '', $result['api_key'] );
        $this->assertFalse( $result['enabled'] );
    }

    public function test_register_calls_settings_api(): void {
        WP_Mock::userFunction( 'register_setting' )->once();
        WP_Mock::userFunction( 'add_settings_section' )->once();
        WP_Mock::userFunction( 'add_settings_field' )->twice();

        $this->settings->register();

        $this->assertConditionsMet();
    }
}
```

### Testing hooks registration

```php
public function test_plugin_registers_init_hook(): void {
    WP_Mock::expectActionAdded( 'init', [ $this->post_type, 'register' ] );

    $this->loader->add_action( 'init', $this->post_type, 'register' );
    $this->loader->run();

    $this->assertConditionsMet();
}

public function test_plugin_registers_filter(): void {
    WP_Mock::expectFilterAdded( 'the_content', [ $this->shortcode, 'filter_content' ] );

    $this->loader->add_filter( 'the_content', $this->shortcode, 'filter_content' );
    $this->loader->run();

    $this->assertConditionsMet();
}
```

### Mocking WordPress functions

```php
// Mock get_option
WP_Mock::userFunction( 'get_option' )
    ->with( 'my_plugin_settings', [] )
    ->andReturn( [ 'api_key' => 'test-key', 'enabled' => true ] );

// Mock current_user_can
WP_Mock::userFunction( 'current_user_can' )
    ->with( 'manage_options' )
    ->andReturn( true );

// Mock wp_verify_nonce
WP_Mock::userFunction( 'wp_verify_nonce' )
    ->once()
    ->andReturn( 1 );

// Mock a filter application
WP_Mock::onFilter( 'my_plugin/settings' )
    ->with( $default_settings )
    ->reply( $modified_settings );
```

---

## Integration Testing with WordPress Test Suite

Integration tests run against a real WordPress installation.

```php
<?php

declare(strict_types=1);

namespace MyPlugin\Tests\Integration;

use WP_UnitTestCase;

final class BookPostTypeTest extends WP_UnitTestCase {

    public function test_post_type_is_registered(): void {
        $this->assertTrue( post_type_exists( 'my_plugin_book' ) );
    }

    public function test_post_type_supports_expected_features(): void {
        $supports = get_all_post_type_supports( 'my_plugin_book' );

        $this->assertTrue( $supports['title'] );
        $this->assertTrue( $supports['editor'] );
        $this->assertTrue( $supports['thumbnail'] );
    }

    public function test_can_create_book(): void {
        $post_id = $this->factory->post->create( [
            'post_type'  => 'my_plugin_book',
            'post_title' => 'Test Book',
        ] );

        $this->assertGreaterThan( 0, $post_id );
        $this->assertSame( 'Test Book', get_the_title( $post_id ) );
    }

    public function test_taxonomy_is_registered(): void {
        $this->assertTrue( taxonomy_exists( 'my_plugin_genre' ) );
    }

    public function test_meta_saves_correctly(): void {
        $post_id = $this->factory->post->create( [ 'post_type' => 'my_plugin_book' ] );

        update_post_meta( $post_id, '_my_plugin_isbn', '978-0-13-468599-1' );

        $this->assertSame( '978-0-13-468599-1', get_post_meta( $post_id, '_my_plugin_isbn', true ) );
    }
}
```

### REST API integration tests

```php
<?php

declare(strict_types=1);

namespace MyPlugin\Tests\Integration;

use WP_REST_Request;
use WP_UnitTestCase;

final class ItemsControllerTest extends WP_UnitTestCase {

    public function setUp(): void {
        parent::setUp();
        // Ensure REST routes are registered
        do_action( 'rest_api_init' );
    }

    public function test_get_items_returns_200(): void {
        $request  = new WP_REST_Request( 'GET', '/my-plugin/v1/items' );
        $response = rest_get_server()->dispatch( $request );

        $this->assertSame( 200, $response->get_status() );
    }

    public function test_create_item_requires_authentication(): void {
        $request = new WP_REST_Request( 'POST', '/my-plugin/v1/items' );
        $request->set_body_params( [ 'title' => 'New Item' ] );
        $response = rest_get_server()->dispatch( $request );

        $this->assertSame( 403, $response->get_status() );
    }

    public function test_create_item_succeeds_for_authorized_user(): void {
        $user_id = $this->factory->user->create( [ 'role' => 'editor' ] );
        wp_set_current_user( $user_id );

        $request = new WP_REST_Request( 'POST', '/my-plugin/v1/items' );
        $request->set_body_params( [ 'title' => 'New Item' ] );
        $response = rest_get_server()->dispatch( $request );

        $this->assertSame( 201, $response->get_status() );
        $this->assertSame( 'New Item', $response->get_data()->title );
    }

    public function test_create_item_validates_required_fields(): void {
        $user_id = $this->factory->user->create( [ 'role' => 'editor' ] );
        wp_set_current_user( $user_id );

        $request = new WP_REST_Request( 'POST', '/my-plugin/v1/items' );
        $request->set_body_params( [] ); // Missing title
        $response = rest_get_server()->dispatch( $request );

        $this->assertSame( 400, $response->get_status() );
    }
}
```

---

## Static Analysis (PHPStan)

### phpstan.neon

```neon
parameters:
    level: 8
    paths:
        - src
    scanDirectories:
        - vendor
    ignoreErrors:
        - '#Function [a-z_]+ not found#' # WordPress functions
    bootstrapFiles:
        - tests/phpstan-bootstrap.php
```

### PHPStan bootstrap for WordPress stubs

```php
<?php
// tests/phpstan-bootstrap.php

define( 'ABSPATH', '/tmp/' );
define( 'WPINC', 'wp-includes' );
```

Install WordPress stubs:
```json
{
  "require-dev": {
    "php-stubs/wordpress-stubs": "^6.4"
  }
}
```

---

## Code Standards (PHPCS)

### .phpcs.xml

```xml
<?xml version="1.0"?>
<ruleset name="My Plugin">
    <description>WordPress Coding Standards for My Plugin</description>

    <file>src</file>
    <file>my-plugin.php</file>

    <arg name="extensions" value="php"/>
    <arg name="colors"/>
    <arg value="sp"/>

    <rule ref="WordPress">
        <!-- Allow PSR-4 file naming -->
        <exclude name="WordPress.Files.FileName"/>
        <!-- Allow short array syntax -->
        <exclude name="Universal.Arrays.DisallowShortArraySyntax"/>
    </rule>

    <rule ref="WordPress.WP.I18n">
        <properties>
            <property name="text_domain" type="array">
                <element value="my-plugin"/>
            </property>
        </properties>
    </rule>

    <!-- Minimum PHP version -->
    <config name="minimum_wp_version" value="6.4"/>
    <config name="testVersion" value="8.1-"/>
</ruleset>
```

---

## Debugging Workflows

### WordPress debug constants (wp-config.php)

```php
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );       // Log to wp-content/debug.log
define( 'WP_DEBUG_DISPLAY', false );  // Don't show errors on screen
define( 'SCRIPT_DEBUG', true );       // Use unminified core scripts
define( 'SAVEQUERIES', true );        // Log all DB queries
```

### Logging in plugin code

```php
// Simple logging (writes to wp-content/debug.log when WP_DEBUG_LOG is true)
if ( defined( 'WP_DEBUG' ) && WP_DEBUG ) {
    error_log( 'My Plugin: ' . print_r( $data, true ) );
}

// Structured logging class
final class Logger {

    public function info( string $message, array $context = [] ): void {
        $this->log( 'INFO', $message, $context );
    }

    public function error( string $message, array $context = [] ): void {
        $this->log( 'ERROR', $message, $context );
    }

    public function debug( string $message, array $context = [] ): void {
        if ( ! defined( 'WP_DEBUG' ) || ! WP_DEBUG ) {
            return;
        }
        $this->log( 'DEBUG', $message, $context );
    }

    private function log( string $level, string $message, array $context ): void {
        $entry = sprintf(
            '[%s] [%s] [My Plugin] %s %s',
            current_time( 'Y-m-d H:i:s' ),
            $level,
            $message,
            $context ? wp_json_encode( $context ) : ''
        );
        error_log( $entry );
    }
}
```

### Query debugging

```php
// Log slow queries
add_filter( 'query', function ( string $query ): string {
    if ( defined( 'SAVEQUERIES' ) && SAVEQUERIES ) {
        global $wpdb;
        // Queries are stored in $wpdb->queries after page load
    }
    return $query;
} );

// Inspect all queries (use in debug/dev only)
add_action( 'shutdown', function (): void {
    if ( ! defined( 'SAVEQUERIES' ) || ! SAVEQUERIES ) {
        return;
    }
    global $wpdb;
    $slow_queries = array_filter( $wpdb->queries, fn( $q ) => $q[1] > 0.05 );
    if ( $slow_queries ) {
        error_log( 'Slow queries: ' . print_r( $slow_queries, true ) );
    }
} );
```

### Hook debugging

```php
// Debug which hooks fire
add_action( 'all', function ( string $hook ): void {
    if ( str_starts_with( $hook, 'my_plugin/' ) ) {
        error_log( "Hook fired: {$hook}" );
    }
} );
```

---

## Test Writing Guidelines

- Test the **public API** of your classes, not private internals
- One assertion concept per test method (test ONE behavior)
- Use descriptive test method names: `test_{method}_{scenario}_{expected_result}`
- Test both happy path AND edge cases
- Test security: unauthorized access, invalid nonces, bad input
- Mock external dependencies (APIs, file system) in unit tests
- Use factories (`$this->factory->post->create()`) in integration tests
- Clean up after tests (WordPress test suite handles this automatically)
- Run tests in CI/CD pipeline on every push

---

## Common test scenarios for plugins

| What to test | Type | How |
|-------------|------|-----|
| Sanitization logic | Unit | Pass malicious strings, verify output |
| Settings defaults | Unit | Call getter, assert structure |
| Hook registration | Unit | Assert hooks are registered with WP_Mock |
| CPT registration | Integration | Verify `post_type_exists()` |
| REST permission checks | Integration | Request without auth, expect 403 |
| REST validation | Integration | Send bad data, expect 400 |
| Meta box save | Integration | Simulate POST, verify meta saved |
| Activation creates tables | Integration | Activate plugin, check table exists |
| Uninstall removes data | Integration | Run uninstall, verify cleanup |
| Cache invalidation | Unit/Integration | Change data, verify cache cleared |
