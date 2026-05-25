"""Kubernetes security checker tool for MCP server."""

import subprocess
import json
from mcp.types import ToolAnnotations
from core.server import mcp


@mcp.tool(
    annotations=ToolAnnotations(
        title="Check Privileged Pods",
        readOnlyHint=True,
    ),
)
def check_privileged_pods(namespace: str = "") -> str:
    """Check for pods running in privileged mode across the cluster.

    Args:
        namespace: Specific namespace to check. Empty string means all namespaces.

    Returns:
        List of privileged pods or confirmation that none were found.
    """
    cmd = ["kubectl", "get", "pods", "-o", "json"]
    if namespace:
        cmd.extend(["-n", namespace])
    else:
        cmd.append("-A")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        pods = json.loads(result.stdout)
        privileged = []

        for pod in pods.get("items", []):
            pod_name = pod["metadata"]["name"]
            ns = pod["metadata"]["namespace"]
            for container in pod["spec"].get("containers", []):
                sc = container.get("securityContext", {})
                if sc.get("privileged", False):
                    privileged.append(f"{ns}/{pod_name} (container: {container['name']})")

        if privileged:
            return f"Found {len(privileged)} privileged containers:\n" + "\n".join(privileged)
        return "No privileged containers found."
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="Check Default ServiceAccounts",
        readOnlyHint=True,
    ),
)
def check_default_serviceaccounts(namespace: str = "") -> str:
    """Check for pods using the default ServiceAccount.

    Args:
        namespace: Specific namespace to check. Empty string means all namespaces.

    Returns:
        List of pods using default SA or confirmation that none were found.
    """
    cmd = ["kubectl", "get", "pods", "-o", "json"]
    if namespace:
        cmd.extend(["-n", namespace])
    else:
        cmd.append("-A")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        pods = json.loads(result.stdout)
        using_default = []

        for pod in pods.get("items", []):
            sa = pod["spec"].get("serviceAccountName", "default")
            if sa == "default":
                name = pod["metadata"]["name"]
                ns = pod["metadata"]["namespace"]
                using_default.append(f"{ns}/{name}")

        if using_default:
            return f"Found {len(using_default)} pods using default ServiceAccount:\n" + "\n".join(using_default)
        return "No pods using default ServiceAccount."
    except Exception as e:
        return f"Error: {str(e)}"
