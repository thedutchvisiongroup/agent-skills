# Architecture Reference

Two architecture tiers for WordPress plugins. **Pick one. No mixing.**

---

## Standard Tier

Default tier for focused plugins. Uses OOP, PSR-4, Composer autoloading, and a Hooks Loader pattern.

### Directory structure

```
my-plugin/
├── my-plugin.php              # Main plugin file (bootstrap)
├── composer.json              # Autoloading + dependencies
├── uninstall.php              # Cleanup on plugin deletion
├── languages/                 # Translation files (.pot, .po, .mo)
├── assets/
│   ├── css/
│   │   ├── admin.css
│   │   └── public.css
│   └── js/
│       ├── admin.js
│       └── public.js
├── templates/                 # PHP template files (views)
│   ├── admin/
│   └── public/
├── src/                       # PSR-4 autoloaded source (namespace root)
│   ├── Plugin.php             # Main plugin orchestrator
│   ├── Activator.php          # Activation logic
│   ├── Deactivator.php        # Deactivation logic
│   ├── Loader.php             # Hooks registration loader
│   ├── Admin/                 # Admin-facing functionality
│   │   ├── AdminPage.php
│   │   └── Settings.php
│   ├── Frontend/              # Public-facing functionality
│   │   └── Shortcodes.php
│   ├── PostTypes/             # Custom Post Types
│   │   └── BookPostType.php
│   ├── Taxonomies/            # Custom Taxonomies
│   │   └── GenreTaxonomy.php
│   ├── REST/                  # REST API controllers
│   │   └── BooksController.php
│   └── CLI/                   # WP-CLI commands
│       └── SeedCommand.php
└── tests/                     # Test files
    ├── bootstrap.php
    └── Unit/
        └── PluginTest.php
```

### Main plugin file (bootstrap)

```php
<?php
/**
 * Plugin Name:       My Plugin
 * Description:       Short description.
 * Version:           1.0.0
 * Requires at least: 6.4
 * Requires PHP:      8.1
 * Author:            Author Name
 * Text Domain:       my-plugin
 * Domain Path:       /languages
 */

defined( 'ABSPATH' ) || exit;

define( 'MY_PLUGIN_VERSION', '1.0.0' );
define( 'MY_PLUGIN_FILE', __FILE__ );
define( 'MY_PLUGIN_PATH', plugin_dir_path( __FILE__ ) );
define( 'MY_PLUGIN_URL', plugin_dir_url( __FILE__ ) );

require_once MY_PLUGIN_PATH . 'vendor/autoload.php';

use MyPlugin\Plugin;
use MyPlugin\Activator;
use MyPlugin\Deactivator;

register_activation_hook( __FILE__, [ Activator::class, 'activate' ] );
register_deactivation_hook( __FILE__, [ Deactivator::class, 'deactivate' ] );

( new Plugin() )->run();
```

### Plugin orchestrator (Standard)

```php
<?php

declare(strict_types=1);

namespace MyPlugin;

final class Plugin {

    private Loader $loader;

    public function __construct() {
        $this->loader = new Loader();
        $this->define_admin_hooks();
        $this->define_public_hooks();
    }

    private function define_admin_hooks(): void {
        $admin = new Admin\AdminPage();
        $this->loader->add_action( 'admin_menu', $admin, 'register_menu' );
        $this->loader->add_action( 'admin_enqueue_scripts', $admin, 'enqueue_assets' );
    }

    private function define_public_hooks(): void {
        $shortcodes = new Frontend\Shortcodes();
        $this->loader->add_action( 'init', $shortcodes, 'register' );
        $this->loader->add_action( 'wp_enqueue_scripts', $shortcodes, 'enqueue_assets' );
    }

    public function run(): void {
        $this->loader->run();
    }
}
```

### Hooks Loader

```php
<?php

declare(strict_types=1);

namespace MyPlugin;

final class Loader {

    /** @var array<int, array{hook: string, component: object, callback: string, priority: int, accepted_args: int}> */
    private array $actions = [];

    /** @var array<int, array{hook: string, component: object, callback: string, priority: int, accepted_args: int}> */
    private array $filters = [];

    public function add_action(
        string $hook,
        object $component,
        string $callback,
        int $priority = 10,
        int $accepted_args = 1
    ): void {
        $this->actions[] = compact( 'hook', 'component', 'callback', 'priority', 'accepted_args' );
    }

    public function add_filter(
        string $hook,
        object $component,
        string $callback,
        int $priority = 10,
        int $accepted_args = 1
    ): void {
        $this->filters[] = compact( 'hook', 'component', 'callback', 'priority', 'accepted_args' );
    }

    public function run(): void {
        foreach ( $this->filters as $hook ) {
            add_filter(
                $hook['hook'],
                [ $hook['component'], $hook['callback'] ],
                $hook['priority'],
                $hook['accepted_args']
            );
        }

        foreach ( $this->actions as $hook ) {
            add_action(
                $hook['hook'],
                [ $hook['component'], $hook['callback'] ],
                $hook['priority'],
                $hook['accepted_args']
            );
        }
    }
}
```

### Activator / Deactivator

```php
<?php

declare(strict_types=1);

namespace MyPlugin;

final class Activator {

    public static function activate(): void {
        // Create custom tables, set default options, flush rewrite rules
        flush_rewrite_rules();
    }
}
```

```php
<?php

declare(strict_types=1);

namespace MyPlugin;

final class Deactivator {

    public static function deactivate(): void {
        // Clean up scheduled events, flush rewrite rules
        flush_rewrite_rules();
    }
}
```

### Uninstall file

```php
<?php
// uninstall.php

defined( 'WP_UNINSTALL_PLUGIN' ) || exit;

// Delete options
delete_option( 'my_plugin_settings' );

// Drop custom tables
global $wpdb;
$wpdb->query( "DROP TABLE IF EXISTS {$wpdb->prefix}my_plugin_logs" );

// Clear transients
delete_transient( 'my_plugin_cache' );

// Cancel all scheduled Action Scheduler actions
as_unschedule_all_actions( '', [], 'my-plugin' );
```

---

## Enterprise Tier

For large plugins with multiple independent feature modules. Adds Service Container and Dependency Injection.

### Directory structure

```
my-enterprise-plugin/
├── my-enterprise-plugin.php    # Bootstrap
├── composer.json
├── uninstall.php
├── config/
│   └── services.php            # Service definitions
├── languages/
├── assets/
│   ├── css/
│   └── js/
├── templates/
│   ├── admin/
│   └── public/
├── src/
│   ├── Plugin.php              # Application kernel
│   ├── Container.php           # Service Container
│   ├── ServiceProvider.php     # Base service provider (abstract)
│   ├── Activator.php
│   ├── Deactivator.php
│   ├── Contracts/              # Interfaces
│   │   ├── Registrable.php     # Interface for classes that register hooks
│   │   ├── HasActivation.php   # Interface for activation logic
│   │   └── CacheDriver.php     # Example interface
│   ├── Modules/                # Feature modules (independent units)
│   │   ├── Analytics/
│   │   │   ├── AnalyticsServiceProvider.php
│   │   │   ├── AnalyticsTracker.php
│   │   │   └── REST/
│   │   │       └── AnalyticsController.php
│   │   ├── Reporting/
│   │   │   ├── ReportingServiceProvider.php
│   │   │   ├── ReportGenerator.php
│   │   │   └── Admin/
│   │   │       └── ReportsPage.php
│   │   └── Integrations/
│   │       ├── IntegrationsServiceProvider.php
│   │       └── Webhooks/
│   │           └── WebhookHandler.php
│   ├── Core/                   # Shared infrastructure
│   │   ├── Cache.php
│   │   ├── Logger.php
│   │   └── Queue/
│   │       ├── Job.php
│   │       └── Dispatcher.php
│   └── CLI/
│       └── MainCommand.php
└── tests/
    ├── bootstrap.php
    ├── Unit/
    └── Integration/
```

### Service Container

```php
<?php

declare(strict_types=1);

namespace MyEnterprisePlugin;

use InvalidArgumentException;

final class Container {

    /** @var array<string, callable> */
    private array $bindings = [];

    /** @var array<string, object> */
    private array $instances = [];

    public function bind( string $abstract, callable $factory ): void {
        $this->bindings[ $abstract ] = $factory;
    }

    public function singleton( string $abstract, callable $factory ): void {
        $this->bindings[ $abstract ] = function () use ( $abstract, $factory ) {
            if ( ! isset( $this->instances[ $abstract ] ) ) {
                $this->instances[ $abstract ] = $factory( $this );
            }
            return $this->instances[ $abstract ];
        };
    }

    public function get( string $abstract ): mixed {
        if ( isset( $this->instances[ $abstract ] ) ) {
            return $this->instances[ $abstract ];
        }

        if ( ! isset( $this->bindings[ $abstract ] ) ) {
            throw new InvalidArgumentException( "No binding found for: {$abstract}" );
        }

        return ( $this->bindings[ $abstract ] )( $this );
    }

    public function has( string $abstract ): bool {
        return isset( $this->bindings[ $abstract ] ) || isset( $this->instances[ $abstract ] );
    }
}
```

### Service Provider (abstract)

```php
<?php

declare(strict_types=1);

namespace MyEnterprisePlugin;

abstract class ServiceProvider {

    public function __construct(
        protected readonly Container $container
    ) {}

    /**
     * Register bindings into the container.
     */
    abstract public function register(): void;

    /**
     * Boot services (called after all providers are registered).
     * Hook into WordPress here.
     */
    abstract public function boot(): void;
}
```

### Module Service Provider example

```php
<?php

declare(strict_types=1);

namespace MyEnterprisePlugin\Modules\Analytics;

use MyEnterprisePlugin\Container;
use MyEnterprisePlugin\ServiceProvider;

final class AnalyticsServiceProvider extends ServiceProvider {

    public function register(): void {
        $this->container->singleton(
            AnalyticsTracker::class,
            fn( Container $c ) => new AnalyticsTracker(
                $c->get( \MyEnterprisePlugin\Core\Logger::class )
            )
        );
    }

    public function boot(): void {
        $tracker = $this->container->get( AnalyticsTracker::class );
        add_action( 'wp_footer', [ $tracker, 'inject_tracking_script' ] );
        add_action( 'rest_api_init', [ $this, 'register_routes' ] );
    }

    public function register_routes(): void {
        $controller = new REST\AnalyticsController(
            $this->container->get( AnalyticsTracker::class )
        );
        $controller->register_routes();
    }
}
```

### Enterprise Plugin Kernel

```php
<?php

declare(strict_types=1);

namespace MyEnterprisePlugin;

final class Plugin {

    private Container $container;

    /** @var array<int, ServiceProvider> */
    private array $providers = [];

    /** @var array<int, class-string<ServiceProvider>> */
    private const PROVIDERS = [
        Modules\Analytics\AnalyticsServiceProvider::class,
        Modules\Reporting\ReportingServiceProvider::class,
        Modules\Integrations\IntegrationsServiceProvider::class,
    ];

    public function __construct() {
        $this->container = new Container();
        $this->register_core_services();
    }

    private function register_core_services(): void {
        $this->container->singleton(
            Core\Logger::class,
            fn() => new Core\Logger()
        );

        $this->container->singleton(
            Core\Cache::class,
            fn() => new Core\Cache()
        );
    }

    public function run(): void {
        // Register all providers
        foreach ( self::PROVIDERS as $provider_class ) {
            $provider = new $provider_class( $this->container );
            $provider->register();
            $this->providers[] = $provider;
        }

        // Boot all providers (hooks are registered here)
        foreach ( $this->providers as $provider ) {
            $provider->boot();
        }
    }

    public function container(): Container {
        return $this->container;
    }
}
```

### Registrable interface (Enterprise)

```php
<?php

declare(strict_types=1);

namespace MyEnterprisePlugin\Contracts;

interface Registrable {
    /**
     * Register hooks with WordPress.
     */
    public function register(): void;
}
```

---

## Key architectural rules

| Rule | Standard | Enterprise |
|------|----------|-----------|
| Autoloading | PSR-4 via Composer | PSR-4 via Composer |
| Hook registration | Loader class | ServiceProvider::boot() |
| Dependency management | Constructor parameters | Container + DI |
| Module organization | Flat src/ directories | src/Modules/ with providers |
| Shared services | Direct instantiation | Container singletons |
| Interfaces | Optional | Required for core contracts |
| Config | Constants + options | config/ directory + Container |

---

## Anti-patterns (both tiers)

- **God class**: A single class handling admin, frontend, REST, and CLI. Split by responsibility.
- **Static abuse**: Overusing static methods prevents testing. Use instance methods.
- **Global state**: Avoid global variables. Pass dependencies explicitly.
- **Hook spaghetti**: Registering hooks in 15 different files. Centralize via Loader (Standard) or ServiceProvider (Enterprise).
- **Tight coupling**: Classes directly instantiating their dependencies. Use constructor injection.
- **Namespace pollution**: Putting everything in the root namespace. Use meaningful sub-namespaces.
