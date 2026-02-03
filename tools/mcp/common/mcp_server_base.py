#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


JSONDict = Dict[str, Any]


@dataclass(frozen=True)
class MCPEnvSpec:
    required: Tuple[str, ...] = ("OPENAI_API_KEY",)
    optional: Tuple[str, ...] = ()
    allow_dotenv: bool = True


@dataclass(frozen=True)
class MCPPathsSpec:
    # We support both layouts:
    # 1) MCP/config/local_paths.json
    # 2) MCP/tools/mcp/config/local_paths.json
    local_paths_filename: str = "local_paths.json"
    example_paths_filename: str = "local_paths.example.json"


@dataclass(frozen=True)
class MCPServerSpec:
    name: str = "mcp-server"
    default_host: str = "127.0.0.1"
    default_port: int = 3001
    env: MCPEnvSpec = MCPEnvSpec()
    paths: MCPPathsSpec = MCPPathsSpec()


class MCPBaseError(RuntimeError):
    pass


class MCPServerBase:
    """
    Hardened base for MCP/RAG servers:
    - optional .env loading (never required)
    - required env validation
    - portable machine-local path config
    - safe logging (never prints secrets)
    - minimal CLI and lifecycle hooks
    """

    def __init__(self, spec: MCPServerSpec):
        self.spec = spec
        self.repo_root = self._resolve_repo_root()
        self.paths_cfg = self._load_local_paths_config()
        self.env = self._load_and_validate_env()

    # =====================
    # OVERRIDE THESE
    # =====================

    def run(self, host: str, port: int) -> None:
        raise NotImplementedError("Subclass must implement run(host, port)")

    def shutdown(self) -> None:
        return

    # =====================
    # ENTRY POINT
    # =====================

    def main(self, argv: Optional[Sequence[str]] = None) -> None:
        args = self._parse_args(argv)

        self._log("info", f"Starting {self.spec.name}")
        self._log("info", f"Host: {args.host}")
        self._log("info", f"Port: {args.port}")
        self._log("info", f"Repo root: {self.repo_root}")
        self._log("info", f"Local paths loaded: {bool(self.paths_cfg)}")
        self._log("info", f"Secrets loaded: {self._secrets_loaded_summary()}")

        try:
            self.run(args.host, args.port)
        except KeyboardInterrupt:
            self._log("warn", "Shutdown requested (Ctrl+C)")
            self.shutdown()
            self._log("info", "Shutdown complete")
        except Exception as e:
            self._log("error", f"Unhandled exception: {type(e).__name__}: {e}")
            raise

    # =====================
    # ENV
    # =====================

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.env.get(key, default)

    def require_env(self, key: str) -> str:
        val = self.env.get(key)
        if not val:
            raise MCPBaseError(f"Required env var missing: {key}")
        return val

    def _load_and_validate_env(self) -> JSONDict:
        if self.spec.env.allow_dotenv and load_dotenv is not None:
            load_dotenv(override=False)

        env: JSONDict = {}
        missing = []

        for k in self.spec.env.required:
            v = os.environ.get(k)
            if not v:
                missing.append(k)
            else:
                env[k] = v

        for k in self.spec.env.optional:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v

        if missing:
            self._fatal(
                "Missing required environment variables: "
                + ", ".join(missing)
                + "\nSet them in your shell or a local .env file (never commit secrets)."
            )

        return env

    def _secrets_loaded_summary(self) -> str:
        parts = []
        for k in self.spec.env.required:
            parts.append(f"{k}=YES")
        for k in self.spec.env.optional:
            parts.append(f"{k}={'YES' if (k in self.env and self.env[k]) else 'NO'}")
        return ", ".join(parts) if parts else "none"

    # =====================
    # PATH CONFIG
    # =====================

    def get_paths_cfg(self) -> JSONDict:
        return dict(self.paths_cfg)

    def _resolve_repo_root(self) -> Path:
        # File is: MCP/tools/mcp/common/mcp_server_base.py
        # parents: common(0), mcp(1), tools(2), MCP(3)
        return Path(__file__).resolve().parents[3]

    def _possible_local_paths_files(self) -> Tuple[Path, Path]:
        # Support both:
        # MCP/config/local_paths.json
        # MCP/tools/mcp/config/local_paths.json
        a = self.repo_root / "config" / self.spec.paths.local_paths_filename
        b = self.repo_root / "tools" / "mcp" / "config" / self.spec.paths.local_paths_filename
        return a, b

    def _load_local_paths_config(self) -> JSONDict:
        for cfg_path in self._possible_local_paths_files():
            if cfg_path.exists():
                try:
                    data = json.loads(cfg_path.read_text(encoding="utf-8"))
                    if not isinstance(data, dict):
                        self._fatal("local_paths.json must contain a JSON object")
                    return data
                except Exception as e:
                    self._fatal(f"Failed to parse {cfg_path}: {e}")
        return {}

    # =====================
    # LOGGING
    # =====================

    def _log(self, level: str, msg: str) -> None:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        out = sys.stderr if level in ("warn", "error") else sys.stdout
        print(f"[{self.spec.name}][{level.upper()}][{ts}] {msg}", file=out, flush=True)

    def _fatal(self, msg: str) -> None:
        self._log("error", msg)
        raise SystemExit(1)

    # =====================
    # CLI
    # =====================

    def _parse_args(self, argv: Optional[Sequence[str]]) -> argparse.Namespace:
        p = argparse.ArgumentParser(prog=self.spec.name)
        p.add_argument("--host", default=self.spec.default_host)
        p.add_argument("--port", type=int, default=self.spec.default_port)
        return p.parse_args(list(argv) if argv is not None else None)