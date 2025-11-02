#!/usr/bin/env python3
"""
qBittorrent Remote Client

A command-line interface for managing qBittorrent instances remotely via the Web API.
Provides commands for listing, adding, pausing, resuming, and deleting torrents.
"""

import sys

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text

from qbt_api import QBittorrentError, create_client_from_config

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
    except QBittorrentError as e:
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

    except QBittorrentError as e:
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

    except QBittorrentError as e:
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
    except QBittorrentError as e:
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
    except QBittorrentError as e:
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
    except QBittorrentError as e:
        console.print(f"[red]Error deleting torrents: {e}[/red]")


@cli.command("delete-by-status")
@click.argument("status")
@click.option("--delete-files", is_flag=True, help="Also delete downloaded files")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be deleted without actually deleting",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt (useful for automation)",
)
@click.pass_context
def delete_by_status(ctx, status, delete_files, dry_run, yes):
    """Delete all torrents with specified status (e.g., error, missingFiles)"""
    client = ctx.obj["client"]

    try:
        # Get all torrents and filter by status
        all_torrents = client.get_torrents()
        matching_torrents = [t for t in all_torrents if t.get("state", "").lower() == status.lower()]

        if not matching_torrents:
            console.print(f"[yellow]No torrents found with status '{status}'[/yellow]")
            return

        console.print(f"[cyan]Found {len(matching_torrents)} torrents with status '{status}':[/cyan]")

        # Show what will be deleted
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=False, max_width=50)
        table.add_column("Size", style="green", justify="right")
        table.add_column("State", style="yellow")

        for torrent in matching_torrents:
            table.add_row(
                torrent["name"][:47] + "..." if len(torrent["name"]) > 50 else torrent["name"],
                format_size(torrent["size"]),
                torrent.get("state", "unknown"),
            )

        console.print(table)

        if dry_run:
            console.print(f"\n[yellow]DRY RUN: Would delete {len(matching_torrents)} torrents[/yellow]")
            return

        # Confirm deletion
        action = "delete with files" if delete_files else "remove"
        if not yes and not click.confirm(
            f"\nAre you sure you want to {action} these {len(matching_torrents)} torrents?"
        ):
            console.print("[yellow]Operation cancelled[/yellow]")
            return

        # Delete in batches to avoid overwhelming the API
        batch_size = 50
        hashes = [t["hash"] for t in matching_torrents]
        deleted_count = 0

        for i in range(0, len(hashes), batch_size):
            batch = hashes[i : i + batch_size]
            success = client.delete_torrents(batch, delete_files=delete_files)
            if success:
                deleted_count += len(batch)
                console.print(f"[green]Deleted batch {i // batch_size + 1}: {len(batch)} torrents[/green]")
            else:
                console.print(f"[red]Failed to delete batch {i // batch_size + 1}[/red]")

        action_past = "deleted with files" if delete_files else "removed"
        console.print(
            f"\n[bold green]Successfully {action_past} {deleted_count}/{len(matching_torrents)} torrents[/bold green]"
        )

    except QBittorrentError as e:
        console.print(f"[red]Error deleting torrents by status: {e}[/red]")


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

    except QBittorrentError as e:
        console.print(f"[red]Error getting statistics: {e}[/red]")


@cli.command()
@click.option("--refresh", "-r", type=int, help="Auto-refresh every N seconds")
@click.pass_context
def status(ctx, refresh):
    """Show comprehensive qBittorrent instance status dashboard"""
    client = ctx.obj["client"]

    def display_status():
        try:
            # Get all the data we need
            torrents = client.get_torrents()
            transfer_info = client.get_global_transfer_info()
            version = client.get_application_version()
            categories = client.get_categories()

            # Clear screen for refresh mode
            if refresh:
                console.clear()

            console.print("[bold blue]═══ qBittorrent Status Dashboard ═══[/bold blue]\n")

            # Server Information
            server_table = Table(title="🖥️  Server Information", show_header=False, box=None)
            server_table.add_column("Field", style="cyan", width=20)
            server_table.add_column("Value", style="green")

            server_table.add_row("Version", version)
            server_table.add_row("Connection", f"{client.host}:{client.port}")
            server_table.add_row("Protocol", "HTTPS" if client.base_url.startswith("https") else "HTTP")

            console.print(server_table)
            console.print()

            # Transfer Statistics
            transfer_table = Table(title="📊 Transfer Statistics", show_header=False, box=None)
            transfer_table.add_column("Metric", style="cyan", width=20)
            transfer_table.add_column("Value", style="green")

            transfer_table.add_row("Download Speed", format_speed(transfer_info["dl_info_speed"]))
            transfer_table.add_row("Upload Speed", format_speed(transfer_info["up_info_speed"]))
            transfer_table.add_row("Session Downloaded", format_size(transfer_info["dl_info_data"]))
            transfer_table.add_row("Session Uploaded", format_size(transfer_info["up_info_data"]))
            transfer_table.add_row("All-time Downloaded", format_size(transfer_info.get("alltime_dl", 0)))
            transfer_table.add_row("All-time Uploaded", format_size(transfer_info.get("alltime_ul", 0)))

            if transfer_info.get("global_ratio"):
                transfer_table.add_row("Global Ratio", f"{transfer_info['global_ratio']:.2f}")

            console.print(transfer_table)
            console.print()

            # Torrent Overview
            status_counts = {}
            total_size = 0
            active_downloads = 0
            active_uploads = 0

            for torrent in torrents:
                state = torrent.get("state", "unknown")
                status_counts[state] = status_counts.get(state, 0) + 1
                total_size += torrent.get("size", 0)

                if torrent.get("dlspeed", 0) > 0:
                    active_downloads += 1
                if torrent.get("upspeed", 0) > 0:
                    active_uploads += 1

            overview_table = Table(title="📚 Torrent Overview", show_header=False, box=None)
            overview_table.add_column("Metric", style="cyan", width=20)
            overview_table.add_column("Value", style="green")

            overview_table.add_row("Total Torrents", str(len(torrents)))
            overview_table.add_row("Total Size", format_size(total_size))
            overview_table.add_row("Active Downloads", str(active_downloads))
            overview_table.add_row("Active Uploads", str(active_uploads))
            overview_table.add_row("Categories", str(len(categories)))

            console.print(overview_table)
            console.print()

            # Status Breakdown
            if status_counts:
                status_table = Table(title="📈 Status Breakdown", show_header=True)
                status_table.add_column("Status", style="cyan")
                status_table.add_column("Count", style="green", justify="right")
                status_table.add_column("Percentage", style="yellow", justify="right")

                total_torrents = len(torrents)
                for state, count in sorted(status_counts.items()):
                    percentage = (count / total_torrents) * 100 if total_torrents > 0 else 0

                    # Color code the status
                    if state in ["downloading", "uploading"]:
                        status_style = "bold green"
                    elif state in ["error", "missingFiles"]:
                        status_style = "bold red"
                    elif state in ["pausedDL", "pausedUP"]:
                        status_style = "yellow"
                    else:
                        status_style = "white"

                    status_table.add_row(
                        Text(state, style=status_style),
                        str(count),
                        f"{percentage:.1f}%",
                    )

                console.print(status_table)
                console.print()

            # Recent Activity (Top 5 most active torrents)
            active_torrents = [t for t in torrents if t.get("dlspeed", 0) > 0 or t.get("upspeed", 0) > 0]

            if active_torrents:
                # Sort by combined speed
                active_torrents.sort(
                    key=lambda x: x.get("dlspeed", 0) + x.get("upspeed", 0),
                    reverse=True,
                )

                activity_table = Table(title="🚀 Most Active Torrents", show_header=True)
                activity_table.add_column("Name", style="cyan", max_width=40)
                activity_table.add_column("Progress", style="green", justify="right")
                activity_table.add_column("Down Speed", style="blue", justify="right")
                activity_table.add_column("Up Speed", style="magenta", justify="right")
                activity_table.add_column("ETA", style="yellow", justify="right")

                for torrent in active_torrents[:5]:  # Top 5
                    name = torrent["name"]
                    if len(name) > 37:
                        name = name[:34] + "..."

                    progress = torrent.get("progress", 0) * 100
                    dl_speed = format_speed(torrent.get("dlspeed", 0))
                    up_speed = format_speed(torrent.get("upspeed", 0))
                    eta = format_eta(torrent.get("eta", 0))

                    activity_table.add_row(
                        name,
                        f"{progress:.1f}%",
                        dl_speed if torrent.get("dlspeed", 0) > 0 else "-",
                        up_speed if torrent.get("upspeed", 0) > 0 else "-",
                        eta,
                    )

                console.print(activity_table)

            if refresh:
                console.print(f"\n[dim]Refreshing every {refresh} seconds. Press Ctrl+C to stop.[/dim]")

        except QBittorrentError as e:
            console.print(f"[red]Error getting status: {e}[/red]")
            return False
        except KeyboardInterrupt:
            console.print("\n[yellow]Status monitoring stopped.[/yellow]")
            return False

        return True

    # Display once or continuously based on refresh parameter
    if refresh:
        import time

        while True:
            if not display_status():
                break
            try:
                time.sleep(refresh)
            except KeyboardInterrupt:
                console.print("\n[yellow]Status monitoring stopped.[/yellow]")
                break
    else:
        display_status()


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
            if command.lower() == "help":
                console.print(
                    """
Available commands:
  list           - List all torrents
  stats          - Show transfer statistics
  status         - Show comprehensive status dashboard
  add <url>      - Add torrent from magnet/URL
  pause <hash>   - Pause torrent
  resume <hash>  - Resume torrent
  delete <hash>  - Delete torrent
  delete-by-status <status> - Delete all torrents with specified status
  quit           - Exit interactive mode
                """
                )
            elif command.lower() == "list":
                ctx.invoke(list)
            elif command.lower() == "stats":
                ctx.invoke(stats)
            elif command.lower() == "status":
                ctx.invoke(status, refresh=None)
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
    cli()  # pylint: disable=no-value-for-parameter


def main():
    """Entry point for console script."""
    cli()  # pylint: disable=no-value-for-parameter
