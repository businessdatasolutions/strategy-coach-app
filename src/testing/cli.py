#!/usr/bin/env python3
"""
Command Line Interface for Testing Agent System
Provides easy access to testing agent functionality.
"""

import asyncio
import click
import sys
import json
from pathlib import Path
from typing import Optional

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.testing.business_case import business_case_library
from src.testing.journey_simulator import run_journey_test, run_multiple_journey_tests
from src.testing.journey_recorder import run_recorded_test


@click.group()
def cli():
    """Testing Agent CLI for Strategic Coaching Journey Simulation."""
    pass


@cli.command()
def list_cases():
    """List available business cases."""
    cases = business_case_library.list_cases()
    
    click.echo("Available Business Cases:")
    click.echo("=" * 40)
    
    for case_name in cases:
        case = business_case_library.get_case(case_name)
        click.echo(f"📋 {case_name}")
        click.echo(f"   Company: {case.company_profile.name}")
        click.echo(f"   Industry: {case.company_profile.industry.value}")
        click.echo(f"   Stage: {case.company_profile.stage.value}")
        click.echo(f"   Persona: {case.persona_type.value}")
        click.echo(f"   Revenue: {case.company_profile.revenue}")
        click.echo()


@cli.command()
@click.argument('business_case')
@click.option('--output-dir', type=click.Path(), help='Output directory for results')
def run_journey(business_case: str, output_dir: Optional[str]):
    """Run a single journey test for specified business case."""
    
    async def _run():
        try:
            click.echo(f"🚀 Starting journey simulation for: {business_case}")
            
            output_path = Path(output_dir) if output_dir else Path("tests/evaluation/results")
            result = await run_journey_test(business_case, output_path)
            
            click.echo("\n📊 Journey Results:")
            click.echo("=" * 40)
            click.echo(f"Success: {'✅' if result.success else '❌'} {result.success}")
            click.echo(f"Exchanges: {result.total_exchanges}")
            click.echo(f"Phases Completed: {', '.join(result.phases_completed)}")
            click.echo(f"Final Completeness: {result.final_completeness}%")
            click.echo(f"Duration: {result.journey_duration:.1f}s")
            
            if result.errors:
                click.echo(f"\n⚠️  Errors ({len(result.errors)}):")
                for error in result.errors:
                    click.echo(f"   • {error}")
            
            # Performance metrics
            metrics = result.performance_metrics
            if metrics:
                click.echo(f"\n📈 Performance Metrics:")
                click.echo(f"   Avg User Response: {metrics.get('avg_user_response_length', 0):.0f} chars")
                click.echo(f"   Avg AI Response: {metrics.get('avg_ai_response_length', 0):.0f} chars") 
                click.echo(f"   Exchanges/min: {metrics.get('exchanges_per_minute', 0):.1f}")
                click.echo(f"   Completeness/min: {metrics.get('completeness_per_minute', 0):.1f}%")
            
        except Exception as e:
            click.echo(f"❌ Journey simulation failed: {e}")
            return False
        
        return result.success
    
    success = asyncio.run(_run())
    sys.exit(0 if success else 1)


@cli.command()
@click.argument('business_case')
@click.option('--output-dir', type=click.Path(), help='Output directory for recordings')
def run_recorded_journey(business_case: str, output_dir: Optional[str]):
    """Run a journey with full recording and visual documentation."""
    
    async def _run():
        try:
            click.echo(f"📸 Starting recorded journey for: {business_case}")
            
            result, html_report = await run_recorded_test(business_case)
            
            click.echo("\n📊 Recorded Journey Results:")
            click.echo("=" * 40)
            click.echo(f"Success: {'✅' if result.success else '❌'} {result.success}")
            click.echo(f"Session ID: {result.session_id}")
            click.echo(f"HTML Report: {html_report}")
            click.echo(f"Total Exchanges: {result.total_exchanges}")
            click.echo(f"Final Completeness: {result.final_completeness}%")
            
            if html_report.exists():
                click.echo(f"\n📋 Open report: file://{html_report.absolute()}")
            
        except Exception as e:
            click.echo(f"❌ Recorded journey failed: {e}")
            return False
        
        return result.success
    
    success = asyncio.run(_run())
    sys.exit(0 if success else 1)


@cli.command()
@click.option('--cases', multiple=True, help='Specific cases to test (default: all)')
@click.option('--output-dir', type=click.Path(), help='Output directory for results')
def run_regression_suite(cases: tuple, output_dir: Optional[str]):
    """Run regression test suite across multiple business cases."""
    
    async def _run():
        try:
            if cases:
                test_cases = list(cases)
            else:
                test_cases = business_case_library.list_cases()
            
            click.echo(f"🧪 Running regression test suite for {len(test_cases)} cases")
            
            output_path = Path(output_dir) if output_dir else Path("tests/evaluation/regression")
            results = await run_multiple_journey_tests(test_cases, output_path)
            
            # Analyze results
            total_tests = len(results)
            successful_tests = sum(1 for r in results if r.success)
            success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            
            click.echo("\n📊 Regression Test Results:")
            click.echo("=" * 40)
            click.echo(f"Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
            
            for result in results:
                status = "✅" if result.success else "❌"
                click.echo(f"{status} {result.business_case_name}: {result.final_completeness}% complete")
            
            return success_rate >= 80
            
        except Exception as e:
            click.echo(f"❌ Regression suite failed: {e}")
            return False
    
    success = asyncio.run(_run())
    sys.exit(0 if success else 1)


@cli.command()
def validate_system():
    """Run comprehensive system validation tests."""
    
    click.echo("🔍 Running comprehensive testing agent validation...")
    
    # Import and run validation
    sys.path.append(str(Path(__file__).parent.parent.parent / "tests" / "testing"))
    
    try:
        from test_testing_agent_validation import run_comprehensive_validation
        success = asyncio.run(run_comprehensive_validation())
        
        if success:
            click.echo("\n🎉 Testing Agent system validation PASSED!")
        else:
            click.echo("\n⚠️  Testing Agent system validation FAILED!")
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument('business_case')
def inspect_case(business_case: str):
    """Inspect details of a specific business case."""
    
    case = business_case_library.get_case(business_case)
    if not case:
        click.echo(f"❌ Business case '{business_case}' not found")
        available = business_case_library.list_cases()
        click.echo(f"Available cases: {', '.join(available)}")
        sys.exit(1)
    
    # Display case details
    click.echo(f"📋 Business Case: {business_case}")
    click.echo("=" * 40)
    
    click.echo(f"Company: {case.company_profile.name}")
    click.echo(f"Industry: {case.company_profile.industry.value}")
    click.echo(f"Stage: {case.company_profile.stage.value}")
    click.echo(f"Size: {case.company_profile.size}")
    click.echo(f"Revenue: {case.company_profile.revenue}")
    click.echo(f"Founded: {case.company_profile.founded}")
    
    click.echo(f"\nMission: {case.strategic_context.mission}")
    
    click.echo(f"\nKey Challenges:")
    for challenge in case.strategic_context.current_challenges:
        click.echo(f"  • {challenge}")
    
    click.echo(f"\nStrategic Questions:")
    for question in case.strategic_goals.strategic_questions:
        click.echo(f"  • {question}")
    
    click.echo(f"\nPersona: {case.persona_type.value}")
    click.echo(f"Communication Style: {case.persona_characteristics.communication_style}")
    click.echo(f"Decision Making: {case.persona_characteristics.decision_making}")


if __name__ == "__main__":
    cli()