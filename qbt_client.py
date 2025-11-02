#!/usr/bin/env python3

import click
import sys
from rich.console import Console
from rich.table import Table
from rich.text import Text

from qbt_api import create_client_from_config


console = Console()


def format_size(bytes_size):
    """Format bytes to human readable size."""
    if bytes_size == 0:
        return "0 B"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_speed(bytes_per_sec):
    """Format bytes per second to human readable speed."""
    return f"{format_size(bytes_per_sec)}/s"


def format_eta(seconds):
    """Format ETA in seconds to human readable time."""
    if seconds == 8640000:  # qBittorrent's infinity value
        return "∞"
    if seconds <= 0:
        return "0s"

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts[:2])  # Show max 2 units


def get_state_color(state):
    """Get color for torrent state."""
    colors = {
        "downloading": "blue",
        "uploading": "green",
        "stalledDL": "yellow",
        "stalledUP": "yellow",
        "queuedDL": "cyan",
        "queuedUP": "cyan",
        "pausedDL": "red",
        "pausedUP": "red",
        "error": "bright_red",
        "missingFiles": "bright_red",
        "unknown": "white",
    }
    return colors.get(state, "white")


@click.group()
@click.option("--config", "-c", default="config.json", help="Path to configuration file")
@click.pass_context
def cli(ctx, config):
    """qBittorrent Remote Client"""
    ctx.ensure_object(dict)
    try:
        ctx.obj["client"] = create_client_from_config(config)
    except FileNotFoundError:
        console.print(f"[red]Config file not found: {config}[/red]")
        console.print("Please copy config.example.json to config.json and edit it")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        sys.exit(1)


@cli.command("list")
@click.option(
    "--filter",
    "-f",
    "filter_type",
    default="all",
    help="Filter torrents (all, downloading, seeding, completed, paused)",
)
@click.option(
    "--sort",
    "-s",
    default="name",
    help="Sort field (name, size, progress, dlspeed, upspeed, priority, eta, ratio)",
)
@click.option("--reverse", "-r", is_flag=True, help="Reverse sort order")
@click.pass_context
def list_torrents(ctx, filter_type, sort, reverse):
    """List torrents"""
    client = ctx.obj["client"]

    try:
        torrents = client.get_torrents(filter_type=filter_type, sort=sort, reverse=reverse)

        if not torrents:
            console.print("[yellow]No torrents found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=False, max_width=40)
        table.add_column("Size", justify="right")
        table.add_column("Progress", justify="right")
        table.add_column("State", justify="center")
        table.add_column("Down Speed", justify="right")
        table.add_column("Up Speed", justify="right")
        table.add_column("ETA", justify="right")
        table.add_column("Ratio", justify="right")

        for torrent in torrents:
            progress = f"{torrent['progress'] * 100:.1f}%"
            state_color = get_state_color(torrent["state"])

            table.add_row(
                torrent["name"],
                format_size(torrent["size"]),
                progress,
                Text(torrent["state"], style=state_color),
                format_speed(torrent["dlspeed"]),
                format_speed(torrent["upspeed"]),
                format_eta(torrent["eta"]),
                f"{torrent['ratio']:.2f}",
            )

        console.print(table)
        console.print(f"\n[bold]Total: {len(torrents)} torrents[/bold]")

    except Exception as e:
        console.print(f"[red]Error listing torrents: {e}[/red]")


@cli.command()
@click.argument("source")
@click.option("--path", "-p", help="Download path")
@click.option("--category", "-cat", help="Category")
@click.option("--paused", is_flag=True, help="Add in paused state")
@click.pass_context
def add(ctx, source, path, category, paused):
    """Add torrent from magnet link, URL, or file"""
    client = ctx.obj["client"]

    try:
        if source.startswith(("magnet:", "http://", "https://")):
            success = client.add_torrent_url(source, save_path=path or "", category=category or "", paused=paused)
        else:
            success = client.add_torrent_file(source, save_path=path or "", category=category or "", paused=paused)

        if success:
            console.print("[green]Torrent added successfully[/green]")
        else:
            console.print("[red]Failed to add torrent[/red]")

    except Exception as e:
        console.print(f"[red]Error adding torrent: {e}[/red]")


@cli.command()
@click.argument("hashes", nargs=-1, required=True)
@click.pass_context
def pause(ctx, hashes):
    """Pause torrents by hash"""
    client = ctx.obj["client"]

    try:
        success = client.pause_torrents(list(hashes))
        if success:
            console.print(f"[green]Paused {len(hashes)} torrent(s)[/green]")
        else:
            console.print("[red]Failed to pause torrents[/red]")
    except Exception as e:
        console.print(f"[red]Error pausing torrents: {e}[/red]")


@cli.command()
@click.argument("hashes", nargs=-1, required=True)
@click.pass_context
def resume(ctx, hashes):
    """Resume torrents by hash"""
    client = ctx.obj["client"]

    try:
        success = client.resume_torrents(list(hashes))
        if success:
            console.print(f"[green]Resumed {len(hashes)} torrent(s)[/green]")
        else:
            console.print("[red]Failed to resume torrents[/red]")
    except Exception as e:
        console.print(f"[red]Error resuming torrents: {e}[/red]")


@cli.command()
@click.argument("hashes", nargs=-1, required=True)
@click.option("--delete-files", is_flag=True, help="Also delete downloaded files")
@click.confirmation_option(prompt="Are you sure you want to delete the torrent(s)?")
@click.pass_context
def delete(ctx, hashes, delete_files):
    """Delete torrents by hash"""
    client = ctx.obj["client"]

    try:
        success = client.delete_torrents(list(hashes), delete_files=delete_files)
        if success:
            action = "deleted with files" if delete_files else "removed"
            console.print(f"[green]{len(hashes)} torrent(s) {action}[/green]")
        else:
            console.print("[red]Failed to delete torrents[/red]")
    except Exception as e:
        console.print(f"[red]Error deleting torrents: {e}[/red]")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show global transfer statistics"""
    client = ctx.obj["client"]

    try:
        info = client.get_global_transfer_info()
        version = client.get_application_version()

        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("qBittorrent Version", version)
        table.add_row("Download Speed", format_speed(info["dl_info_speed"]))
        table.add_row("Upload Speed", format_speed(info["up_info_speed"]))
        table.add_row("Downloaded (Session)", format_size(info["dl_info_data"]))
        table.add_row("Uploaded (Session)", format_size(info["up_info_data"]))
        table.add_row("Global Ratio", f"{info.get('global_ratio', 'N/A')}")
        table.add_row("All-time Download", format_size(info.get("alltime_dl", 0)))
        table.add_row("All-time Upload", format_size(info.get("alltime_ul", 0)))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error getting statistics: {e}[/red]")


@cli.command()
@click.pass_context
def interactive(ctx):
    """Interactive mode"""
    # client = ctx.obj["client"]  # Available if needed for interactive commands

    console.print("[bold blue]qBittorrent Interactive Mode[/bold blue]")
    console.print("Type 'help' for available commands or 'quit' to exit")

    while True:
        try:
            command = console.input("\n[bold cyan]qbt>[/bold cyan] ").strip()

            if command.lower() in ["quit", "exit", "q"]:
                break
            elif command.lower() == "help":
                console.print(
                    """
Available commands:
  list           - List all torrents
  stats          - Show transfer statistics
  add <url>      - Add torrent from magnet/URL
  pause <hash>   - Pause torrent
  resume <hash>  - Resume torrent
  delete <hash>  - Delete torrent
  quit           - Exit interactive mode
                """
                )
            elif command.lower() == "list":
                ctx.invoke(list)
            elif command.lower() == "stats":
                ctx.invoke(stats)
            elif command.startswith("add "):
                url = command[4:].strip()
                ctx.invoke(add, source=url)
            elif command.startswith(("pause ", "resume ", "delete ")):
                parts = command.split()
                action = parts[0]
                hash_val = parts[1] if len(parts) > 1 else ""
                if hash_val:
                    if action == "pause":
                        ctx.invoke(pause, hashes=[hash_val])
                    elif action == "resume":
                        ctx.invoke(resume, hashes=[hash_val])
                    elif action == "delete":
                        ctx.invoke(delete, hashes=[hash_val])
                else:
                    console.print(f"[red]Usage: {action} <hash>[/red]")
            elif command:
                console.print(f"[red]Unknown command: {command}[/red]")
                console.print("Type 'help' for available commands")

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit[/yellow]")
        except EOFError:
            break


if __name__ == "__main__":
    cli()


def main():
    """Entry point for console script."""
    cli()
