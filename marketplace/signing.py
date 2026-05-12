"""Ed25519 cryptographic signing and verification for plugin marketplace.

Replaces the non-cryptographic SHA-256 hash with proper Ed25519
public-key signatures.  Every plugin package is signed by a private key
held by the plugin author or distribution authority, and verified at
load time against a trusted public key registry.

Key generation (CLI)::

    # Generate a new key pair
    python -c "
from marketplace.signing import PluginSigner
signer = PluginSigner()
signer.generate_keypair('plugin_signing_key')
print('Generated plugin_signing_key (private) and plugin_signing_key.pub (public)')
"

Signature creation::

    python -c "
from marketplace.signing import PluginSigner
signer = PluginSigner()
signer.sign_package('/path/to/plugin_dir', 'plugin_signing_key')
print('manifest.json signature updated')
"
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


class PluginSigningError(Exception):
    """Raised when signing or verification fails."""


class PluginSigner:
    """Ed25519-based plugin signing and verification.

    Usage::

        signer = PluginSigner()
        signer.generate_keypair("plugin_key")
        signer.sign_package(plugin_dir, "plugin_key")
        signer.verify_package(plugin_dir, "plugin_key.pub")
    """

    @staticmethod
    def generate_keypair(name: str = "plugin_signing_key", key_dir: str | Path | None = None) -> tuple[Path, Path]:
        """Generate an Ed25519 key pair and write to files.

        Args:
            name: Base filename for the key pair (default: plugin_signing_key).
            key_dir: Directory to write keys.  Defaults to current directory.

        Returns:
            ``(private_key_path, public_key_path)``
        """
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        output_dir = Path(key_dir).resolve() if key_dir else Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)

        private_path = output_dir / f"{name}"
        public_path = output_dir / f"{name}.pub"

        # Write private key (PEM, not encrypted — caller must secure the file)
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        private_path.write_bytes(private_bytes)
        private_path.chmod(0o600)  # owner read/write only

        # Write public key (PEM)
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        public_path.write_bytes(public_bytes)

        return private_path, public_path

    @staticmethod
    def load_private_key(path: str | Path) -> Ed25519PrivateKey:
        """Load an Ed25519 private key from a PEM file."""
        key_path = Path(path).resolve()
        if not key_path.exists():
            raise PluginSigningError(f"Private key not found: {key_path}")
        try:
            key_bytes = key_path.read_bytes()
            private_key = serialization.load_pem_private_key(key_bytes, password=None)
            if not isinstance(private_key, Ed25519PrivateKey):
                raise PluginSigningError(f"Key at {key_path} is not an Ed25519 private key")
            return private_key
        except PluginSigningError:
            raise
        except ValueError as exc:
            raise PluginSigningError(f"Invalid private key at {key_path}: {exc}") from exc
        except Exception as exc:
            raise PluginSigningError(f"Failed to load private key: {exc}") from exc

    @staticmethod
    def load_public_key(path: str | Path) -> Ed25519PublicKey:
        """Load an Ed25519 public key from a PEM file."""
        key_path = Path(path).resolve()
        if not key_path.exists():
            raise PluginSigningError(f"Public key not found: {key_path}")
        try:
            key_bytes = key_path.read_bytes()
            public_key = serialization.load_pem_public_key(key_bytes)
            if not isinstance(public_key, Ed25519PublicKey):
                raise PluginSigningError(f"Key at {key_path} is not an Ed25519 public key")
            return public_key
        except PluginSigningError:
            raise
        except ValueError as exc:
            raise PluginSigningError(f"Invalid public key at {key_path}: {exc}") from exc
        except Exception as exc:
            raise PluginSigningError(f"Failed to load public key: {exc}") from exc

    @staticmethod
    def sign_package(package_path: str | Path, private_key_path: str | Path) -> str:
        """Sign all files in a plugin package using the given private key.

        Updates ``manifest.json`` with a ``signature`` field containing
        the base64-encoded Ed25519 signature of all file contents.

        Args:
            package_path: Path to the plugin directory.
            private_key_path: Path to the Ed25519 private key PEM file.

        Returns:
            The base64-encoded signature that was written to the manifest.
        """
        private_key = PluginSigner.load_private_key(private_key_path)
        package_dir = Path(package_path).resolve()

        if not package_dir.is_dir():
            raise PluginSigningError(f"Package path is not a directory: {package_dir}")

        manifest_path = package_dir / "manifest.json"
        if not manifest_path.exists():
            raise PluginSigningError("manifest.json not found in package")

        # Normalize manifest to canonical format (indent=2, no signature yet)
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        PluginSigner._write_manifest_canonical(package_dir, manifest_data)

        # Build canonical message from all files in canonical form
        message = PluginSigner._canonical_package_message(package_dir)
        signature = private_key.sign(message)

        import base64
        sig_b64 = base64.b64encode(signature).decode("ascii")

        # Write signature to manifest.json
        manifest_data["signature"] = sig_b64
        manifest_path.write_text(
            json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        return sig_b64

    @staticmethod
    def verify_package(package_path: str | Path, public_key_path: str | Path) -> bool:
        """Verify the Ed25519 signature of a plugin package.

        Args:
            package_path: Path to the plugin directory.
            public_key_path: Path to the Ed25519 public key PEM file.

        Returns:
            ``True`` if the signature is valid.

        Raises:
            PluginSigningError: If verification fails.
        """
        public_key = PluginSigner.load_public_key(public_key_path)
        package_dir = Path(package_path).resolve()

        if not package_dir.is_dir():
            raise PluginSigningError(f"Package path is not a directory: {package_dir}")

        manifest_path = package_dir / "manifest.json"
        if not manifest_path.exists():
            raise PluginSigningError("manifest.json not found in package")

        try:
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PluginSigningError(f"Invalid manifest.json: {exc}") from exc

        signature_b64 = manifest_data.pop("signature", None)
        if not signature_b64:
            raise PluginSigningError("No signature found in manifest.json")

        import base64
        try:
            signature = base64.b64decode(signature_b64)
        except Exception as exc:
            raise PluginSigningError(f"Invalid signature encoding: {exc}") from exc

        # Rebuild canonical message EXCLUDING the signature field
        PluginSigner._write_manifest_canonical(package_dir, manifest_data)
        message = PluginSigner._canonical_package_message(package_dir)

        try:
            public_key.verify(signature, message)
            return True
        except InvalidSignature:
            raise PluginSigningError("Plugin signature verification failed: signature does not match public key")
        except Exception as exc:
            raise PluginSigningError(f"Signature verification error: {exc}") from exc

    @staticmethod
    def _canonical_package_message(package_dir: Path) -> bytes:
        """Build a canonical message from all files in the package.

        The message is built from sorted relative paths + their file contents,
        ensuring deterministic verification regardless of filesystem order.
        """
        parts: list[bytes] = []
        for file_path in sorted(package_dir.rglob("*")):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(package_dir).as_posix()
            parts.append(rel.encode("utf-8"))
            parts.append(b"\x00")
            parts.append(file_path.read_bytes())
            parts.append(b"\x00")
        return b"".join(parts)

    @staticmethod
    def _write_manifest_canonical(
        package_dir: Path, manifest_data: dict[str, Any]
    ) -> None:
        """Write manifest data back without the signature field for canonical signing."""
        manifest_path = package_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )