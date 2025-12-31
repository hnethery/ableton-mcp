#!/usr/bin/env python3
"""
Ableton MCP CLI - Command line interface for Ableton Live integration through
the Model Context Protocol
"""

import argparse
import logging
import sys
import os
import asyncio
from typing import List, Optional
import importlib.metadata

from .server import mcp, main as server_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AbletonMCP-CLI")


def get_version() -> str:
    """Get the current version of the package."""
    try:
        return importlib.metadata.version("ableton-mcp")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="ableton-mcp",
        description="Ableton Live integration through the Model Context "
                    "Protocol",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Server command
    server_parser = subparsers.add_parser(
        "server", help="Start the MCP server")
    server_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    server_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    # Info command
    subparsers.add_parser(
        "info", help="Show information about the MCP server")

    # Version command
    subparsers.add_parser(
        "version", help="Show version information")

    # Install command for Ableton Live Remote Script
    install_parser = subparsers.add_parser(
        "install",
        help="Install the Ableton Live Remote Script"
    )
    install_parser.add_argument(
        "--ableton-path",
        type=str,
        help="Path to Ableton Live installation (optional, auto-detects)")
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Force installation even if the script already exists"
    )

    return parser.parse_args(args)


def show_version() -> None:
    """Show version information."""
    print(f"🎵 Ableton MCP v{get_version()}")
    print("🎹 Ableton Live integration through the Model Context Protocol")
    print("🔗 https://github.com/itsuzef/ableton-mcp")


def show_info() -> None:
    """Show information about the MCP server."""
    print(f"ℹ️  Ableton MCP v{get_version()}")
    print("\n📋 Available MCP functions:")

    # Get all registered functions from the MCP server
    async def get_tools():
        return await mcp.list_tools()

    try:
        tools = asyncio.run(get_tools())
        for tool in tools:
            print(f"  ✨ {tool.name}")
    except Exception as e:
        print(f"  ❌ Error listing tools: {e}")

    print("\n💡 For more information, start the server and visit "
          "http://localhost:8000/docs")


def find_ableton_script_path() -> Optional[str]:
    """
    Attempt to find the Ableton Live Remote Scripts directory.
    Returns None if not found.
    """
    possible_paths = []

    # macOS paths
    if sys.platform == "darwin":
        home = os.path.expanduser("~")
        possible_paths.extend([
            f"{home}/Music/Ableton/Live 11 Suite/Resources/MIDI Remote Scripts",
            f"{home}/Music/Ableton/Live 10 Suite/Resources/MIDI Remote Scripts",
            f"{home}/Music/Ableton/Live 11/Resources/MIDI Remote Scripts",
            f"{home}/Music/Ableton/Live 10/Resources/MIDI Remote Scripts",
            "/Applications/Ableton Live 11 Suite.app/Contents/App-Resources/"
            "MIDI Remote Scripts",
            "/Applications/Ableton Live 10 Suite.app/Contents/App-Resources/"
            "MIDI Remote Scripts",
            "/Applications/Ableton Live 11.app/Contents/App-Resources/"
            "MIDI Remote Scripts",
            "/Applications/Ableton Live 10.app/Contents/App-Resources/"
            "MIDI Remote Scripts",
        ])

    # Windows paths
    elif sys.platform == "win32":
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get(
            "ProgramFiles(x86)", "C:\\Program Files (x86)")
        possible_paths.extend([
            f"{program_files}\\Ableton\\Live 11 Suite\\Resources\\"
            "MIDI Remote Scripts",
            f"{program_files}\\Ableton\\Live 10 Suite\\Resources\\"
            "MIDI Remote Scripts",
            f"{program_files}\\Ableton\\Live 11\\Resources\\"
            "MIDI Remote Scripts",
            f"{program_files}\\Ableton\\Live 10\\Resources\\"
            "MIDI Remote Scripts",
            f"{program_files_x86}\\Ableton\\Live 11 Suite\\Resources\\"
            "MIDI Remote Scripts",
            f"{program_files_x86}\\Ableton\\Live 10 Suite\\Resources\\"
            "MIDI Remote Scripts",
            f"{program_files_x86}\\Ableton\\Live 11\\Resources\\"
            "MIDI Remote Scripts",
            f"{program_files_x86}\\Ableton\\Live 10\\Resources\\"
            "MIDI Remote Scripts",
        ])

    # Linux paths
    elif sys.platform == "linux":
        home = os.path.expanduser("~")
        possible_paths.extend([
            f"{home}/.config/ableton/Live 11 Suite/Resources/"
            "MIDI Remote Scripts",
            f"{home}/.config/ableton/Live 10 Suite/Resources/"
            "MIDI Remote Scripts",
            f"{home}/.config/ableton/Live 11/Resources/"
            "MIDI Remote Scripts",
            f"{home}/.config/ableton/Live 10/Resources/"
            "MIDI Remote Scripts",
        ])

    # Check if any of the paths exist
    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def install_remote_script(
        ableton_path: Optional[str] = None, force: bool = False) -> None:
    """Install the Ableton Live Remote Script."""
    print("📦 Installing Ableton Live Remote Script...")

    # Determine the source path (where the Remote Script files are in our
    # package)
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_path = os.path.join(package_dir, "AbletonMCP_Remote_Script")

    if not os.path.exists(source_path):
        print(
            f"❌ Error: Remote Script source directory not found at "
            f"{source_path}")
        sys.exit(1)

    # Determine the target path (where to install in Ableton)
    target_base_path = ableton_path
    if not target_base_path:
        print("🔍 Searching for Ableton Live Remote Scripts directory...")
        target_base_path = find_ableton_script_path()
        if not target_base_path:
            print(
                "❌ Error: Could not find Ableton Live Remote Scripts "
                "directory.")
            print("Please specify the path using --ableton-path")
            sys.exit(1)
        print(f"📂 Found Ableton Live directory: {target_base_path}")

    target_path = os.path.join(
        target_base_path, "AbletonMCP_Remote_Script")

    # Check if the script is already installed
    if os.path.exists(target_path) and not force:
        print(f"⚠️  Remote Script is already installed at {target_path}")
        print("Use --force to reinstall")
        return

    # Create the target directory if it doesn't exist
    os.makedirs(target_path, exist_ok=True)

    # Copy all files from source to target
    import shutil
    file_count = 0
    try:
        for item in os.listdir(source_path):
            source_item = os.path.join(source_path, item)
            target_item = os.path.join(target_path, item)

            if os.path.isfile(source_item):
                shutil.copy2(source_item, target_item)
                file_count += 1
            elif os.path.isdir(source_item):
                shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                file_count += 1
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        sys.exit(1)

    print(f"✅ Copied {file_count} files to {target_path}")

    print("\n✨ Installation Successful!")
    print("\n⚠️  NEXT STEPS:")
    print("  1. Restart Ableton Live.")
    print("  2. Open Preferences > Link/Tempo/MIDI.")
    print("  3. Select 'AbletonMCP_Remote_Script' in the Control Surface "
          "list.")


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    if args.command == "server":
        # Configure logging level
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Start the server
        print(
            f"🚀 Starting Ableton MCP server v{
                get_version()} on http://{
                args.host}:{
                args.port}")
        print("🛑 Press Ctrl+C to stop the server")

        # Set environment variables for the server
        os.environ["MCP_HOST"] = args.host
        os.environ["MCP_PORT"] = str(args.port)

        # Run the server
        server_main()

    elif args.command == "version":
        show_version()

    elif args.command == "info":
        show_info()

    elif args.command == "install":
        install_remote_script(args.ableton_path, args.force)

    else:
        # If no command is provided, show help
        parse_args(["--help"])


if __name__ == "__main__":
    main()
