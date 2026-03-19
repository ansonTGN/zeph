# zeph-vault

`VaultProvider` trait and backends (environment variables and age-encrypted files) for Zeph secret management.

Extracted from `zeph-core` in epic #1973 (Phase 1c).

## Purpose

`zeph-vault` owns secret retrieval. It defines the `VaultProvider` trait — the interface that all secret backends implement — and ships two production backends:

- `EnvVaultProvider` — reads secrets from environment variables (zero-config, safe for CI)
- `AgeVaultProvider` — decrypts secrets from an age-encrypted JSON file (`secrets.age`) on disk

Secrets are always held as `Zeroizing<String>`, which overwrites the memory containing the plaintext value when the variable is dropped.

## Key Types

| Type | Description |
|------|-------------|
| `VaultProvider` | Async trait: `get_secret(key) -> Result<Option<String>>` and `list_keys() -> Vec<String>` |
| `EnvVaultProvider` | Reads secrets from environment variables by name |
| `AgeVaultProvider` | Decrypts an age-encrypted JSON secrets file; supports read, write, init |
| `ArcAgeVaultProvider` | `VaultProvider` wrapper around `Arc<RwLock<AgeVaultProvider>>` for shared mutable access |
| `AgeVaultError` | Typed error enum covering key read/parse, vault read, decryption, JSON, encryption, and write failures |
| `MockVaultProvider` | `BTreeMap`-backed provider for tests (enabled by `mock` feature) |

## `VaultProvider` Trait

```rust
pub trait VaultProvider: Send + Sync {
    fn get_secret(
        &self,
        key: &str,
    ) -> Pin<Box<dyn Future<Output = Result<Option<String>, VaultError>> + Send + '_>>;

    fn list_keys(&self) -> Vec<String> {
        Vec::new()
    }
}
```

`get_secret` returns `Ok(None)` when the key does not exist. `Err(VaultError)` signals a backend failure (I/O, decryption, network, etc.).

## Age Vault Backend

The age vault stores secrets as a JSON object encrypted with [age](https://age-encryption.org/) using an x25519 keypair.

### File layout

```
~/.config/zeph/
├── vault-key.txt   # age x25519 identity (mode 0600)
└── secrets.age     # age-encrypted JSON: { "KEY": "value", ... }
```

### Initialize a new vault

```bash
zeph vault init
```

This generates a new keypair, writes `vault-key.txt` with mode `0600`, and creates an empty `secrets.age`.

### Manage secrets

```bash
zeph vault set ZEPH_CLAUDE_API_KEY sk-ant-...
zeph vault get ZEPH_CLAUDE_API_KEY
zeph vault list
zeph vault remove ZEPH_CLAUDE_API_KEY
```

### Config

```toml
[vault]
backend = "age"
key_file  = "~/.config/zeph/vault-key.txt"
vault_file = "~/.config/zeph/secrets.age"
```

## Environment Variable Backend

The `EnvVaultProvider` reads secrets directly from the process environment. This is the default when `vault.backend = "env"` or when no vault is configured.

`list_keys()` returns all environment variables with the `ZEPH_SECRET_` prefix.

```toml
[vault]
backend = "env"
```

```bash
export ZEPH_CLAUDE_API_KEY=sk-ant-...
```

## Feature Flags

| Feature | Default | Description |
|---------|---------|-------------|
| `mock` | off | Enables `MockVaultProvider` for use in tests |

## Security Properties

- Secret values are stored in `Zeroizing<String>` — plaintext is overwritten on drop
- `AgeVaultProvider::Debug` implementation prints only the count of secrets, never their values
- The age key file is created with mode `0600` on Unix (Windows: standard file write, no ACL restrictions — tracked as TODO)
- `AgeVaultProvider::save()` uses atomic write (write to `.age.tmp`, then rename) to prevent partial writes
- `ArcAgeVaultProvider::list_keys()` uses `block_in_place` to avoid `blocking_read()` panics inside async contexts

## Integration with zeph-core

`zeph-core`'s `AppBuilder` constructs the vault backend from `VaultConfig` during bootstrap and passes it to `resolve_secrets()`, which populates `ResolvedSecrets` before the agent loop starts.

```rust
// zeph-core bootstrap (simplified)
let vault: Box<dyn VaultProvider> = match config.vault.backend {
    VaultBackend::Age => Box::new(AgeVaultProvider::new(&key_path, &vault_path)?),
    VaultBackend::Env => Box::new(EnvVaultProvider),
};
let secrets = resolve_secrets(&config, vault.as_ref()).await?;
```

## Common Use Cases

### Using the env backend for local development

```bash
export ZEPH_CLAUDE_API_KEY=sk-ant-...
cargo run -- --config config.toml
```

### Using the age backend (production)

```bash
zeph vault init
zeph vault set ZEPH_CLAUDE_API_KEY sk-ant-...
# config.toml: vault.backend = "age"
cargo run -- --config config.toml
```

### Writing a custom vault backend

```rust
use zeph_vault::VaultProvider;
use zeph_common::secret::VaultError;
use std::pin::Pin;
use std::future::Future;

struct MyVault;

impl VaultProvider for MyVault {
    fn get_secret(
        &self,
        key: &str,
    ) -> Pin<Box<dyn Future<Output = Result<Option<String>, VaultError>> + Send + '_>> {
        let key = key.to_owned();
        Box::pin(async move {
            // Fetch from your backend
            Ok(Some("secret".into()))
        })
    }
}
```

## Source Code

[`crates/zeph-vault/`](https://github.com/bug-ops/zeph/tree/main/crates/zeph-vault)
