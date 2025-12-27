"""
Command-line interface for Terraria Pyramid Detector.

This module provides a Click-based CLI for all generation modes.
"""

import click
import sys

from ..core import (
    WorldConfig,
    WorldGenerationParams,
    GenerationOrchestrator,
    create_strategy,
)
from ..platform import get_platform_adapter, get_platform_name


# Custom validators for Click
def validate_size(ctx, param, value):
    """Validate world size parameter."""
    try:
        return WorldConfig.validate_size(value)
    except ValueError as e:
        raise click.BadParameter(str(e))


def validate_difficulty(ctx, param, value):
    """Validate difficulty parameter."""
    try:
        return WorldConfig.validate_difficulty(value)
    except ValueError as e:
        raise click.BadParameter(str(e))


def validate_evil(ctx, param, value):
    """Validate evil type parameter."""
    try:
        return WorldConfig.validate_evil(value)
    except ValueError as e:
        raise click.BadParameter(str(e))


def validate_count(ctx, param, value):
    """Validate world count parameter."""
    try:
        return WorldConfig.validate_count(value)
    except ValueError as e:
        raise click.BadParameter(str(e))


def validate_pyramid_target(ctx, param, value):
    """Validate pyramid target parameter."""
    try:
        return WorldConfig.validate_pyramid_target(value)
    except ValueError as e:
        raise click.BadParameter(str(e))


def validate_max_attempts(ctx, param, value):
    """Validate max attempts parameter."""
    try:
        return WorldConfig.validate_max_attempts(value)
    except ValueError as e:
        raise click.BadParameter(str(e))


@click.group()
@click.version_option(version='1.0.0', prog_name='pyramid-detector')
def cli():
    """
    Terraria Pyramid Detector - Automatically generate and detect pyramid worlds.

    Use --help with any command to see detailed options.

    Examples:

        \b
        # Generate 10 medium worlds, keep all
        pyramid-detector auto-find --size 2 --count 10

        \b
        # Find 5 pyramid worlds (small, crimson)
        pyramid-detector find-pyramids --size 1 --evil 3 --target 5

        \b
        # Generate 3 worlds without detection
        pyramid-detector generate --count 3
    """
    # Display platform info
    platform_name = get_platform_name()
    click.echo(f"Platform: {platform_name}\n", err=True)


@cli.command(name='auto-find')
@click.option(
    '--size', '-s',
    type=int,
    default=WorldConfig.DEFAULT_SIZE,
    callback=validate_size,
    help='World size (1=Small, 2=Medium, 3=Large)'
)
@click.option(
    '--difficulty', '-d',
    type=int,
    default=WorldConfig.DEFAULT_DIFFICULTY,
    callback=validate_difficulty,
    help='Difficulty (1=Normal, 2=Expert, 3=Master)'
)
@click.option(
    '--evil', '-e',
    type=int,
    default=WorldConfig.DEFAULT_EVIL,
    callback=validate_evil,
    help='Evil type (1=Random, 2=Corruption, 3=Crimson)'
)
@click.option(
    '--count', '-c',
    type=int,
    default=WorldConfig.DEFAULT_COUNT,
    callback=validate_count,
    help='Number of worlds to generate'
)
@click.option(
    '--delete/--no-delete',
    default=False,
    help='Delete worlds without pyramids'
)
def auto_find(size, difficulty, evil, count, delete):
    """
    Generate a fixed number of worlds and detect pyramids.

    This mode generates exactly COUNT worlds, optionally deleting
    worlds without pyramids based on the --delete flag.

    Examples:

        \b
        # Generate 10 medium worlds, keep all
        pyramid-detector auto-find --count 10

        \b
        # Generate 5 large worlds, delete non-pyramid
        pyramid-detector auto-find --size 3 --count 5 --delete
    """
    try:
        # Create platform adapter
        platform = get_platform_adapter()

        # Create orchestrator
        orchestrator = GenerationOrchestrator(
            platform=platform,
            progress_callback=click.echo
        )

        # Create base parameters (name will be generated per-world)
        base_params = WorldGenerationParams(
            size=size,
            difficulty=difficulty,
            evil=evil,
            world_name="temp"  # Will be replaced
        )

        # Create strategy
        delete_mode = 1 if delete else 0
        strategy = create_strategy(
            'fixed',
            total_count=count,
            delete_mode=delete_mode
        )

        # Execute
        results, stats = orchestrator.execute_strategy(base_params, strategy)

        # Exit with appropriate code
        sys.exit(0)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='find-pyramids')
@click.option(
    '--size', '-s',
    type=int,
    default=WorldConfig.DEFAULT_SIZE,
    callback=validate_size,
    help='World size (1=Small, 2=Medium, 3=Large)'
)
@click.option(
    '--difficulty', '-d',
    type=int,
    default=WorldConfig.DEFAULT_DIFFICULTY,
    callback=validate_difficulty,
    help='Difficulty (1=Normal, 2=Expert, 3=Master)'
)
@click.option(
    '--evil', '-e',
    type=int,
    default=WorldConfig.DEFAULT_EVIL,
    callback=validate_evil,
    help='Evil type (1=Random, 2=Corruption, 3=Crimson)'
)
@click.option(
    '--target', '-t',
    type=int,
    default=WorldConfig.DEFAULT_PYRAMID_TARGET,
    callback=validate_pyramid_target,
    help='Number of pyramid worlds to find'
)
@click.option(
    '--max-attempts', '-m',
    type=int,
    default=WorldConfig.DEFAULT_MAX_ATTEMPTS,
    callback=validate_max_attempts,
    help='Maximum worlds to generate before giving up'
)
def find_pyramids(size, difficulty, evil, target, max_attempts):
    """
    Generate worlds until finding a target number with pyramids.

    This mode continues generating worlds until TARGET pyramid worlds
    are found, or MAX_ATTEMPTS is reached. Non-pyramid worlds are
    automatically deleted.

    Examples:

        \b
        # Find 3 pyramid worlds (up to 50 attempts)
        pyramid-detector find-pyramids --target 3 --max-attempts 50

        \b
        # Find 1 large crimson pyramid world
        pyramid-detector find-pyramids --size 3 --evil 3 --target 1
    """
    try:
        # Create platform adapter
        platform = get_platform_adapter()

        # Create orchestrator
        orchestrator = GenerationOrchestrator(
            platform=platform,
            progress_callback=click.echo
        )

        # Create base parameters
        base_params = WorldGenerationParams(
            size=size,
            difficulty=difficulty,
            evil=evil,
            world_name="temp"  # Will be replaced
        )

        # Create strategy
        strategy = create_strategy(
            'target',
            pyramid_target=target,
            max_attempts=max_attempts
        )

        # Execute
        results, stats = orchestrator.execute_strategy(base_params, strategy)

        # Exit with appropriate code
        if stats.pyramids_found >= target:
            sys.exit(0)  # Success
        else:
            sys.exit(2)  # Partial success (didn't reach target)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name='generate')
@click.option(
    '--size', '-s',
    type=int,
    default=WorldConfig.DEFAULT_SIZE,
    callback=validate_size,
    help='World size (1=Small, 2=Medium, 3=Large)'
)
@click.option(
    '--difficulty', '-d',
    type=int,
    default=WorldConfig.DEFAULT_DIFFICULTY,
    callback=validate_difficulty,
    help='Difficulty (1=Normal, 2=Expert, 3=Master)'
)
@click.option(
    '--evil', '-e',
    type=int,
    default=WorldConfig.DEFAULT_EVIL,
    callback=validate_evil,
    help='Evil type (1=Random, 2=Corruption, 3=Crimson)'
)
@click.option(
    '--count', '-c',
    type=int,
    default=WorldConfig.DEFAULT_COUNT,
    callback=validate_count,
    help='Number of worlds to generate'
)
def generate(size, difficulty, evil, count):
    """
    Generate worlds without pyramid detection.

    This is the basic world generation mode without pyramid
    detection or deletion. Equivalent to tWorldGen.

    Examples:

        \b
        # Generate 5 medium worlds
        pyramid-detector generate --count 5

        \b
        # Generate 3 small expert crimson worlds
        pyramid-detector generate --size 1 --difficulty 2 --evil 3 --count 3
    """
    try:
        # Create platform adapter
        platform = get_platform_adapter()

        # Create orchestrator
        orchestrator = GenerationOrchestrator(
            platform=platform,
            progress_callback=click.echo
        )

        # Create base parameters
        base_params = WorldGenerationParams(
            size=size,
            difficulty=difficulty,
            evil=evil,
            world_name="temp"  # Will be replaced
        )

        # Create strategy (basic mode, no detection)
        strategy = create_strategy(
            'basic',
            total_count=count
        )

        # Execute
        results, stats = orchestrator.execute_strategy(base_params, strategy)

        # Exit
        sys.exit(0)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
