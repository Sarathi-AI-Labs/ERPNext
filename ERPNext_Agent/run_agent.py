"""ERPNext AI Agent Interactive CLI Entrypoint.

Provides an autonomous command-line interface for natural language querying,
transaction execution, live metadata inspection, and audit log analysis.
"""

import argparse
import json
import os
import sys

# Ensure root workspace is on python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ERPNext_Agent.core.master_agent import MasterERPNextAgent


def main():
	parser = argparse.ArgumentParser(description="ERPNext AI Autonomous Agent CLI")
	parser.add_argument("--prompt", "-p", type=str, help="Natural language request or instruction")
	parser.add_argument(
		"--container",
		"-c",
		type=str,
		default="frappe_docker_main-backend-1",
		help="Frappe backend Docker container name",
	)
	parser.add_argument("--site", "-s", type=str, default="frontend", help="Frappe site name")
	parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive session")

	args = parser.parse_args()

	print("=" * 60)
	print("  ERPNext AI Agent (Frappe v16 / ERPNext v16)")
	print(f"  Container: {args.container} | Site: {args.site}")
	print("=" * 60)

	agent = MasterERPNextAgent(container_name=args.container, site_name=args.site)

	from ERPNext_Agent.core.conversational_agent import ConversationalAgent

	conv_agent = ConversationalAgent(master_agent=agent)

	if args.prompt:
		print(f"\n[USER PROMPT]: {args.prompt}")
		res = conv_agent.handle_message(args.prompt, session_id="cli_single")
		print("\n[RESULT]:")
		print(res.get("message", json.dumps(res, indent=2, default=str)))
		return

	if args.interactive or not args.prompt:
		print("\nEntering interactive mode. Type 'exit' or 'quit' to stop.\n")
		session_id = "cli_session"
		while True:
			try:
				user_input = input("ERPNext-Agent> ").strip()
				if not user_input:
					continue
				if user_input.lower() in ("exit", "quit", "q"):
					print("Exiting ERPNext AI Agent. Goodbye!")
					break
				response = conv_agent.handle_message(user_input, session_id=session_id)
				msg = response.get("message")
				if msg:
					print(f"\n{msg}\n")
				else:
					print("\n" + json.dumps(response, indent=2, default=str) + "\n")
			except (KeyboardInterrupt, EOFError):
				print("\nSession terminated.")
				break


if __name__ == "__main__":
	main()
