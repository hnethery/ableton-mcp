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
import socket
from typing import List, Optional
import importlib.metadata

# Rich imports for UX
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .server import mcp, main as server_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AbletonMCP-CLI")

# Initialize Rich console
console = Console()


def get_version() -> str:
    """Get the current version of the package."""
    try:
        return importlib.metadata.version("ableton-mcp")
    except importlib.metadata.PackageNotFoundError:
        # Fallback to reading pyproject.toml if package is not installed (dev mode)
        try:
            # Look for pyproject.toml in the parent directory
            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            pyproject_path = os.path.join(base_dir, "pyproject.toml")
            if os.path.exists(pyproject_path):
                # Simple parsing to avoid adding tomllib/toml dependency for just version
                with open(pyproject_path, "r") as f:
                    for line in f:
                        if line.strip().startswith("version ="):
                            return line.split("=")[1].strip().strip('"').strip("'")
        except Exception:
            pass
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

    # Doctor command
    subparsers.add_parser(
        "doctor", help="Check connection to Ableton Live and troubleshoot issues")

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
    version_text = Text()
    version_text.append(f"🎵 Ableton MCP v{get_version()}\n", style="bold cyan")
    version_text.append(
        "🎹 Ableton Live integration through the Model Context Protocol\n", style="italic")
    version_text.append(
        "🔗 https://github.com/itsuzef/ableton-mcp", style="blue underline")

    console.print(Panel(version_text, border_style="cyan"))


def show_info() -> None:
    """Show information about the MCP server."""
    console.print(Panel.fit(
        f"[bold]Ableton MCP[/bold] v{get_version()}\n[italic]Ableton Live integration through the Model Context Protocol[/italic]",
        border_style="cyan"
    ))

    # Get all registered functions from the MCP server
    async def get_tools():
        return await mcp.list_tools()

    try:
        tools = asyncio.run(get_tools())

        # Define categories
        categories = {
            "Session & Transport": [
                "get_session_info", "start_playback", "stop_playback",
                "set_tempo"
            ],
            "Tracks & Mixing": [
                "get_track_info", "create_midi_track", "create_return_track",
                "set_track_name", "set_track_volume", "set_send_level"
            ],
            "Clips & Notes": [
                "create_clip", "fire_clip", "stop_clip",
                "add_notes_to_clip", "set_clip_name"
            ],
            "Devices & Effects": [
                "get_device_parameters", "set_device_parameter",
                "load_instrument_or_effect", "set_eq_band",
                "set_eq_global", "apply_eq_preset"
            ],
            "Browser": [
                "get_browser_tree", "get_browser_items_at_path",
                "load_drum_kit"
            ]
        }

        # Helper to get description summary
        def get_summary(tool):
            if not tool.description:
                return ""
            # Get first line and strip
            return tool.description.strip().split('\n')[0].strip()

        # Map tools by name for easy lookup
        tool_map = {t.name: t for t in tools}

        # Track which tools we've displayed
        displayed_tools = set()

        for category, tool_names in categories.items():
            # Create a table for each category
            table = Table(box=None, show_header=False, padding=(0, 2))
            table.add_column("Tool", style="cyan bold", width=30)
            table.add_column("Description")

            has_items = False
            for name in tool_names:
                if name in tool_map:
                    tool = tool_map[name]
                    summary = get_summary(tool)
                    table.add_row(name, summary)
                    displayed_tools.add(name)
                    has_items = True

            if has_items:
                console.print()
                console.rule(f"[bold blue]📂 {category}[/bold blue]")
                console.print(table)

        # Display any remaining tools (uncategorized)
        remaining = [t for t in tools if t.name not in displayed_tools]
        if remaining:
            console.print()
            console.rule("[bold yellow]🔧 Other Tools[/bold yellow]")
            table = Table(box=None, show_header=False, padding=(0, 2))
            table.add_column("Tool", style="cyan bold", width=30)
            table.add_column("Description")

            for tool in remaining:
                summary = get_summary(tool)
                table.add_row(tool.name, summary)

            console.print(table)

    except Exception as e:
        console.print(Panel(f"❌ Error listing tools: {e}", border_style="red"))

    console.print()
    console.print(Panel(
        "💡 For more information, start the server and visit [link=http://localhost:8000/docs]http://localhost:8000/docs[/link]",
        border_style="yellow"
    ))


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


def run_doctor() -> None:
    """Run diagnostics to help troubleshoot issues."""
    console.print(Panel(
        "[bold]🏥 Ableton MCP Doctor[/bold]\n"
        "Checking your environment...",
        border_style="cyan"
    ))

    # Check 1: Remote Script Installation
    console.print("[bold]1. 📂 Remote Script Installation[/bold]")

    script_path = find_ableton_script_path()
    if script_path:
        installed_path = os.path.join(script_path, "AbletonMCP_Remote_Script")
        if os.path.exists(installed_path):
            console.print(f"   [green]✅ Found at:[/green] {installed_path}")
        else:
            console.print(
                f"   [yellow]⚠️  Not found in:[/yellow] {script_path}")
            console.print(
                "      Run [bold cyan]ableton-mcp install[/bold cyan] to install it.")
    else:
        console.print(
            "   [yellow]⚠️  Could not locate Ableton Live Remote Scripts directory.[/yellow]")
        console.print(
            "      If you have Ableton Live installed, use [bold cyan]ableton-mcp install --ableton-path <path>[/bold cyan]")

    console.print()

    # Check 2: Connection
    console.print("[bold]2. 🔌 Connection to Ableton Live[/bold]")
    if check_ableton_connection():
        console.print("   [green]✅ Connected to Ableton Live![/green]")
    else:
        console.print("   [red]❌ Could not connect to Ableton Live.[/red]")
        console.print("\n   [bold]Troubleshooting:[/bold]")
        console.print("   1. Is Ableton Live running?")
        console.print(
            "   2. Is [cyan]AbletonMCP_Remote_Script[/cyan] selected in:\n      [italic]Preferences > Link/Tempo/MIDI > Control Surfaces[/italic]?")
        console.print("   3. Is the server port 9877 blocked?")
        console.print(
            "   4. Check Remote Script logs in Ableton's log folder.")

    console.print()
    console.print(
        "[dim]Note: This tool checks for common issues. For more details, run the server with --debug.[/dim]")


def install_remote_script(
        ableton_path: Optional[str] = None, force: bool = False) -> None:
    """Install the Ableton Live Remote Script."""
    console.print("[bold]📦 Installing Ableton Live Remote Script...[/bold]")

    # Determine the source path (where the Remote Script files are in our
    # package)
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_path = os.path.join(package_dir, "AbletonMCP_Remote_Script")

    if not os.path.exists(source_path):
        console.print(
            f"[bold red]❌ Error: Remote Script source directory not found at "
            f"{source_path}[/bold red]")
        sys.exit(1)

    # Determine the target path (where to install in Ableton)
    target_base_path = ableton_path
    if not target_base_path:
        with console.status("[bold cyan]🔍 Searching for Ableton Live Remote Scripts directory...[/bold cyan]", spinner="dots"):
            target_base_path = find_ableton_script_path()

        if not target_base_path:
            console.print(
                "[bold red]❌ Could not automatically find Ableton Live Remote Scripts directory.[/bold red]")

            # Show examples based on OS
            example_path = ""
            if sys.platform == "darwin":
                example_path = "/Applications/Ableton Live 11 Suite.app/Contents/App-Resources/MIDI Remote Scripts"
            elif sys.platform == "win32":
                example_path = "C:\\Program Files\\Ableton\\Live 11 Suite\\Resources\\MIDI Remote Scripts"
            else:
                example_path = "/path/to/ableton/MIDI Remote Scripts"

            console.print(f"[dim]Example: {example_path}[/dim]")

            # Interactive prompt
            target_base_path = Prompt.ask(
                "[bold yellow]Please enter the full path to 'MIDI Remote Scripts'[/bold yellow]")

            # Validate input
            if not target_base_path or not os.path.exists(target_base_path):
                console.print(
                    f"[bold red]❌ Path not found: {target_base_path}[/bold red]")
                sys.exit(1)

        console.print(
            f"📂 Using Ableton Live directory: [cyan]{target_base_path}[/cyan]")

    target_path = os.path.join(
        target_base_path, "AbletonMCP_Remote_Script")

    # Check if the script is already installed
    if os.path.exists(target_path) and not force:
        console.print(
            f"[yellow]⚠️  Remote Script is already installed at {target_path}[/yellow]")
        console.print("Use --force to reinstall")
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
        console.print(f"[bold red]❌ Error during installation: {e}[/bold red]")
        sys.exit(1)

    console.print(
        f"[green]✅ Copied {file_count} files to {target_path}[/green]")

    steps = [
        "Restart Ableton Live.",
        "Open Preferences > Link/Tempo/MIDI.",
        "Select [bold cyan]'AbletonMCP_Remote_Script'[/bold cyan] in the Control Surface list."
    ]

    steps_text = Text()
    for i, step in enumerate(steps, 1):
        steps_text.append_text(Text.from_markup(f"{i}. {step}\n"))

    console.print(Panel(
        steps_text,
        title="[bold green]✨ Installation Successful![/bold green]",
        border_style="green",
        subtitle="[bold yellow]⚠️  NEXT STEPS[/bold yellow]"
    ))


def check_ableton_connection(host: str = "127.0.0.1", port: int = 9877) -> bool:
    """Check if Ableton Live Remote Script is reachable."""
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    if args.command == "server":
        # Configure logging level
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Start the server
        console.print(Panel(
            f"🚀 Starting [bold]Ableton MCP server[/bold] v{get_version()}\n"
            f"📡 Listening on [link=http://{args.host}:{args.port}]http://{args.host}:{args.port}[/link]\n\n"
            "🛑 Press [bold red]Ctrl+C[/bold red] to stop the server",
            border_style="green",
            title="Server Starting"
        ))

        # Check Ableton connection
        with console.status("[bold yellow]🔌 Checking connection to Ableton Live...[/bold yellow]"):
            is_connected = check_ableton_connection()

        if is_connected:
            console.print("[green]✅ Ableton Live detected![/green]")
        else:
            warning_msg = (
                "[yellow bold]⚠️  Ableton Live not detected on port 9877.[/yellow bold]\n\n"
                "[dim]The server will start, but commands will fail until connected.[/dim]\n\n"
                "[bold]Troubleshooting Checklist:[/bold]\n"
                "1. Is Ableton Live running?\n"
                "2. Is [cyan]AbletonMCP_Remote_Script[/cyan] selected in:\n"
                "   [italic]Preferences > Link/Tempo/MIDI > Control Surfaces[/italic]?\n"
                "3. Check Remote Script logs if issues persist.\n\n"
                "Run [bold cyan]ableton-mcp doctor[/bold cyan] for more checks."
            )

            console.print(Panel(
                warning_msg,
                border_style="yellow",
                title="Connection Warning"
            ))
            console.print()

        # Set environment variables for the server
        os.environ["MCP_HOST"] = args.host
        os.environ["MCP_PORT"] = str(args.port)

        # Run the server
        server_main()

    elif args.command == "version":
        show_version()

    elif args.command == "info":
        show_info()

    elif args.command == "doctor":
        run_doctor()

    elif args.command == "install":
        install_remote_script(args.ableton_path, args.force)

    else:
        # If no command is provided, show help
        parse_args(["--help"])


if __name__ == "__main__":
    main()
