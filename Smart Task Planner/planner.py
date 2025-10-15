"""
Smart Task Planner - Ollama Integration
Generates actionable task plans from goal descriptions using local Ollama LLM.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import ollama


class TaskPlanner:
    """Generates structured task plans using Ollama's chat method."""
    
    def __init__(self, model: str = "llama3:latest", temperature: float = 0.3):
        """
        Initialize the task planner.
        
        Args:
            model: Ollama model name (default: llama3.1:8b)
            temperature: Generation temperature for consistency (0.0-1.0)
        """
        self.model = model
        self.temperature = temperature
        
    def generate_plan(
        self, 
        goal: str, 
        deadline: Optional[str] = None,
        constraints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a task plan from a goal using Ollama.
        
        Args:
            goal: The goal to plan for (e.g., "Launch a product in 2 weeks")
            deadline: Optional deadline or timebox (e.g., "2 weeks", "2025-10-30")
            constraints: Optional list of constraints (e.g., ["team of 2", "no paid ads"])
            
        Returns:
            Dictionary containing tasks, dependencies, timeline, and reasoning
        """
        # Build the prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(goal, deadline, constraints)
        
        # Call Ollama chat
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": self.temperature,
                    "num_predict": 2000,
                },
                format="json"
            )
            
            # Extract and parse the response
            content = response['message']['content']
            plan_data = json.loads(content)
            
            # Validate and enhance the plan
            validated_plan = self._validate_and_enhance(plan_data, goal, deadline)
            
            return validated_plan
            
        except json.JSONDecodeError as e:
            return {
                "error": "Failed to parse LLM response as JSON",
                "details": str(e),
                "raw_response": content if 'content' in locals() else None
            }
        except Exception as e:
            return {
                "error": "Failed to generate plan",
                "details": str(e)
            }
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM."""
        return """You are a project planning assistant. Your job is to break down goals into actionable tasks.

You MUST respond with ONLY a valid JSON object. No explanation, no markdown, just pure JSON.

The JSON must have this exact structure:
{
  "tasks": [
    {
      "id": "T1",
      "title": "Task title",
      "description": "What needs to be done",
      "estimateDays": 2
    }
  ],
  "dependencies": [
    {
      "from": "T1",
      "to": "T2"
    }
  ],
  "assumptions": ["Assumption 1", "Assumption 2"],
  "risks": [
    {
      "title": "Risk description",
      "severity": "high|medium|low",
      "mitigation": "How to address it"
    }
  ],
  "reasoning": "Brief explanation of the plan structure"
}

Rules:
- Task IDs must be unique (T1, T2, T3, etc.)
- Dependencies reference task IDs that exist
- Estimates are in days (can be fractional like 0.5)
- Keep reasoning brief (1-2 sentences)
- Be realistic with estimates
- No cycles in dependencies"""

    def _build_user_prompt(
        self, 
        goal: str, 
        deadline: Optional[str], 
        constraints: Optional[List[str]]
    ) -> str:
        """Build the user prompt with goal and context."""
        prompt = f"Goal: {goal}\n"
        
        if deadline:
            prompt += f"Deadline/Timebox: {deadline}\n"
        
        if constraints:
            prompt += f"Constraints: {', '.join(constraints)}\n"
        
        prompt += "\nBreak this down into actionable tasks with dependencies and timelines."
        
        return prompt
    
    def _validate_and_enhance(
        self, 
        plan_data: Dict[str, Any], 
        goal: str,
        deadline: Optional[str]
    ) -> Dict[str, Any]:
        """Validate the plan structure and add metadata."""
        
        # Ensure required fields exist
        if "tasks" not in plan_data:
            plan_data["tasks"] = []
        if "dependencies" not in plan_data:
            plan_data["dependencies"] = []
        if "assumptions" not in plan_data:
            plan_data["assumptions"] = []
        if "risks" not in plan_data:
            plan_data["risks"] = []
        if "reasoning" not in plan_data:
            plan_data["reasoning"] = "Plan generated automatically"
        
        # Add metadata
        plan_data["meta"] = {
            "goal": goal,
            "deadline": deadline,
            "generatedAt": datetime.now().isoformat(),
            "model": self.model
        }
        
        # Validate dependencies
        task_ids = {task["id"] for task in plan_data["tasks"]}
        valid_deps = []
        for dep in plan_data["dependencies"]:
            if dep["from"] in task_ids and dep["to"] in task_ids:
                valid_deps.append(dep)
        plan_data["dependencies"] = valid_deps
        
        # Check for cycles (simple detection)
        has_cycle = self._detect_cycle(plan_data["tasks"], plan_data["dependencies"])
        plan_data["meta"]["hasCycle"] = has_cycle
        
        return plan_data
    
    def _detect_cycle(self, tasks: List[Dict], dependencies: List[Dict]) -> bool:
        """Simple cycle detection in dependency graph."""
        # Build adjacency list
        graph = {task["id"]: [] for task in tasks}
        for dep in dependencies:
            graph[dep["from"]].append(dep["to"])
        
        # DFS-based cycle detection
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle_util(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in graph:
            if task_id not in visited:
                if has_cycle_util(task_id):
                    return True
        
        return False


def format_plan_output(plan: Dict[str, Any]) -> str:
    """Format the plan for readable console output."""
    if "error" in plan:
        return f"❌ Error: {plan['error']}\nDetails: {plan.get('details', 'N/A')}"
    
    output = []
    output.append("=" * 80)
    output.append("📋 SMART TASK PLAN")
    output.append("=" * 80)
    
    meta = plan.get("meta", {})
    output.append(f"\n🎯 Goal: {meta.get('goal', 'N/A')}")
    if meta.get("deadline"):
        output.append(f"⏰ Deadline: {meta['deadline']}")
    output.append(f"🤖 Model: {meta.get('model', 'N/A')}")
    output.append(f"📅 Generated: {meta.get('generatedAt', 'N/A')}")
    
    if meta.get("hasCycle"):
        output.append("\n⚠️  WARNING: Dependency cycle detected!")
    
    output.append("\n" + "─" * 80)
    output.append("📝 TASKS")
    output.append("─" * 80)
    
    for task in plan.get("tasks", []):
        output.append(f"\n[{task['id']}] {task['title']}")
        output.append(f"    📖 {task.get('description', 'No description')}")
        output.append(f"    ⏱️  Estimate: {task.get('estimateDays', 'N/A')} days")
    
    if plan.get("dependencies"):
        output.append("\n" + "─" * 80)
        output.append("🔗 DEPENDENCIES")
        output.append("─" * 80)
        for dep in plan["dependencies"]:
            output.append(f"  {dep['from']} → {dep['to']}")
    
    if plan.get("assumptions"):
        output.append("\n" + "─" * 80)
        output.append("💭 ASSUMPTIONS")
        output.append("─" * 80)
        for assumption in plan["assumptions"]:
            output.append(f"  • {assumption}")
    
    if plan.get("risks"):
        output.append("\n" + "─" * 80)
        output.append("⚠️  RISKS")
        output.append("─" * 80)
        for risk in plan["risks"]:
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                risk.get("severity", "medium"), "⚪"
            )
            output.append(f"  {severity_icon} {risk['title']} ({risk.get('severity', 'N/A')})")
            output.append(f"     Mitigation: {risk.get('mitigation', 'None specified')}")
    
    if plan.get("reasoning"):
        output.append("\n" + "─" * 80)
        output.append("💡 REASONING")
        output.append("─" * 80)
        output.append(f"  {plan['reasoning']}")
    
    output.append("\n" + "=" * 80)
    
    return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    print("🚀 Smart Task Planner - Ollama Edition\n")
    
    planner = TaskPlanner(model="llama3:latest")
    
    # Example goal
    goal = "Launch a product in 2 weeks"
    print(f"Planning for: {goal}\n")
    
    plan = planner.generate_plan(
        goal=goal,
        deadline="2 weeks",
        constraints=["team of 2", "limited budget"]
    )
    
    print(format_plan_output(plan))
    
    # Save to JSON
    with open("plan_output.json", "w") as f:
        json.dump(plan, f, indent=2)
    print("\n💾 Full plan saved to plan_output.json")
