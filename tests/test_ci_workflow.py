"""
Tests for the GitHub Actions workflow file.
"""

import pytest
import os
import yaml

def test_workflow_file_exists():
    """Test that the GitHub Actions workflow file exists."""
    workflow_path = os.path.join(".github", "workflows", "ci.yml")
    assert os.path.exists(workflow_path), "GitHub Actions workflow file not found"

def test_workflow_file_content():
    """Test that the GitHub Actions workflow file has the required content."""
    workflow_path = os.path.join(".github", "workflows", "ci.yml")
    
    # Read the file content directly
    with open(workflow_path, "r") as f:
        file_content = f.read()
        print(f"Raw file content:\n{file_content}")
    
    # Parse the YAML
    with open(workflow_path, "r") as f:
        workflow = yaml.safe_load(f)
    
    # Print the workflow for debugging
    print(f"Workflow keys: {list(workflow.keys())}")
    
    # Check basic structure
    assert "name" in workflow, "Workflow name not found"
    
    # The 'on' key might be parsed differently due to being a Python keyword
    # Try both 'on' and True as keys
    on_key = "on" if "on" in workflow else True
    assert on_key in workflow, "Workflow triggers not found"
    
    assert "jobs" in workflow, "Workflow jobs not found"
    
    # Check triggers
    triggers = workflow[on_key]
    assert "push" in triggers, "Push trigger not found"
    assert "pull_request" in triggers, "Pull request trigger not found"
    
    # Check jobs
    jobs = workflow["jobs"]
    assert "test" in jobs, "Test job not found"
    
    # Check test job
    test_job = jobs["test"]
    assert "runs-on" in test_job, "Test job runner not found"
    assert "steps" in test_job, "Test job steps not found"
    
    # Check Python version
    assert "strategy" in test_job, "Test job strategy not found"
    assert "matrix" in test_job["strategy"], "Test job matrix not found"
    assert "python-version" in test_job["strategy"]["matrix"], "Python version matrix not found"
    
    python_versions = test_job["strategy"]["matrix"]["python-version"]
    print(f"Python versions in matrix: {python_versions}")
    assert isinstance(python_versions, list), "Python versions should be a list"
    assert len(python_versions) > 0, "No Python versions specified"
    
    # Check that no Python version is 3.1
    for i, version in enumerate(python_versions):
        version_str = str(version)
        print(f"Checking version {i}: {version} (type: {type(version)})")
        assert version_str != "3.1", f"Python version 3.1 is specified, which is not supported"
        
    # Check for essential steps
    steps = test_job["steps"]
    step_names = [step.get("name", "") for step in steps if isinstance(step, dict) and "name" in step]
    
    essential_steps = [
        "Set up Python",
        "Install dependencies",
        "Test with pytest"
    ]
    
    for step in essential_steps:
        assert any(step in name for name in step_names), f"Essential step '{step}' not found" 