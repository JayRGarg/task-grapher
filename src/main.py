from src.node import Node
from src.gui import Gui
import logging

def main():
    
    logging.basicConfig(level=logging.DEBUG)
    node_p: Node = Node("Morning Routine")
    node_c1: Node = Node("Brush My Teeth")
    node_c2: Node = Node("Wash My Face")
    node_gc1: Node = Node("Apply PREMIUM Face Wash")
    node_gc2: Node = Node("Scrubba Dub Dub")
    _ = node_p.add_child(node_c1)
    _ = node_p.add_child(node_c2)
    _ = node_c2.add_child(node_gc1)
    _ = node_c2.add_child(node_gc2)
    graphics = Gui(node_p)
    # graphics.draw_node(graphics._canvas, node_p, 200, 200)
    # graphics.draw_branch_and_child(graphics._canvas, node_p, node_c1, -50, 50)
    # graphics.draw_branch_and_child(graphics._canvas, node_p, node_c2, 50, 50)
    # graphics.draw_branch_and_child(graphics._canvas, node_c2, node_gc1, -50, 50)
    # graphics.draw_branch_and_child(graphics._canvas, node_c2, node_gc2, 50, 50)
    graphics.calculate_node_positions()
    graphics.draw_tree(graphics._canvas)

    graphics.run()

    return
"""

def main():

    logging.basicConfig(level=logging.DEBUG)
    # Root Task
    project_management: Node = Node("Manage Software Development Project")

    # Level 1
    initiation: Node = Node("Project Initiation Phase")
    planning: Node = Node("Project Planning Phase")
    execution: Node = Node("Project Execution Phase")
    monitoring_control: Node = Node("Project Monitoring and Control")
    closure: Node = Node("Project Closure Phase")

    _ = project_management.add_child(initiation)
    _ = project_management.add_child(planning)
    _ = project_management.add_child(execution)
    _ = project_management.add_child(monitoring_control)
    _ = project_management.add_child(closure)

    # Level 2 - Initiation
    define_scope: Node = Node("Define Project Scope")
    identify_stakeholders: Node = Node("Identify Key Stakeholders")
    develop_charter: Node = Node("Develop Project Charter")
    feasibility_study: Node = Node("Conduct Feasibility Study")

    _ = initiation.add_child(define_scope)
    _ = initiation.add_child(identify_stakeholders)
    _ = initiation.add_child(develop_charter)
    _ = initiation.add_child(feasibility_study)

    # Level 2 - Planning
    create_wbs: Node = Node("Create Work Breakdown Structure")
    define_tasks: Node = Node("Define Individual Tasks")
    estimate_durations: Node = Node("Estimate Task Durations")
    allocate_resources: Node = Node("Allocate Resources to Tasks")
    develop_schedule: Node = Node("Develop Project Schedule")
    budget_planning: Node = Node("Develop Project Budget")
    risk_assessment: Node = Node("Conduct Risk Assessment")
    communication_plan: Node = Node("Develop Communication Plan")

    _ = planning.add_child(create_wbs)
    _ = planning.add_child(define_tasks)
    _ = planning.add_child(estimate_durations)
    _ = planning.add_child(allocate_resources)
    _ = planning.add_child(develop_schedule)
    _ = planning.add_child(budget_planning)
    _ = planning.add_child(risk_assessment)
    _ = planning.add_child(communication_plan)

    # Level 2 - Execution
    manage_team: Node = Node("Manage Development Team")
    code_development: Node = Node("Perform Code Development")
    testing: Node = Node("Conduct Software Testing")
    integrate_modules: Node = Node("Integrate Software Modules")
    client_communication: Node = Node("Communicate with Client")
    resolve_issues: Node = Node("Resolve Project Issues")

    _ = execution.add_child(manage_team)
    _ = execution.add_child(code_development)
    _ = execution.add_child(testing)
    _ = execution.add_child(integrate_modules)
    _ = execution.add_child(client_communication)
    _ = execution.add_child(resolve_issues)

    # Level 2 - Monitoring and Control
    track_progress: Node = Node("Track Project Progress")
    monitor_budget: Node = Node("Monitor Project Budget")
    manage_changes: Node = Node("Manage Change Requests")
    report_status: Node = Node("Report Project Status")
    conduct_meetings: Node = Node("Conduct Project Meetings")

    _ = monitoring_control.add_child(track_progress)
    _ = monitoring_control.add_child(monitor_budget)
    _ = monitoring_control.add_child(manage_changes)
    _ = monitoring_control.add_child(report_status)
    _ = monitoring_control.add_child(conduct_meetings)

    # Level 2 - Closure
    final_report: Node = Node("Prepare Final Project Report")
    client_signoff: Node = Node("Obtain Client Sign-off")
    lessons_learned: Node = Node("Document Lessons Learned")
    release_resources: Node = Node("Release Project Resources")

    _ = closure.add_child(final_report)
    _ = closure.add_child(client_signoff)
    _ = closure.add_child(lessons_learned)
    _ = closure.add_child(release_resources)

    # Level 3 - Planning Subtasks
    task_breakdown_1: Node = Node("Break Down Feature Requirements")
    task_breakdown_2: Node = Node("Outline Database Schema")
    ui_design: Node = Node("Create User Interface Mockups")
    api_specification: Node = Node("Define API Specifications")
    unit_testing_plan: Node = Node("Plan Unit Testing Strategy")
    integration_testing_plan: Node = Node("Plan Integration Testing")
    server_setup: Node = Node("Plan Server Infrastructure")
    front_end_framework: Node = Node("Select Front-end Framework")
    back_end_framework: Node = Node("Select Back-end Framework")
    third_party_integration: Node = Node("Identify Third-party Integrations")

    _ = define_tasks.add_child(task_breakdown_1)
    _ = define_tasks.add_child(task_breakdown_2)
    _ = define_tasks.add_child(ui_design)
    _ = define_tasks.add_child(api_specification)
    _ = define_tasks.add_child(unit_testing_plan)
    _ = define_tasks.add_child(integration_testing_plan)
    _ = allocate_resources.add_child(server_setup)
    _ = allocate_resources.add_child(front_end_framework)
    _ = allocate_resources.add_child(back_end_framework)
    _ = allocate_resources.add_child(third_party_integration)

    # Level 3 - Execution Subtasks
    develop_user_authentication: Node = Node("Develop User Authentication Module")
    develop_data_models: Node = Node("Develop Data Models")
    implement_api_endpoints: Node = Node("Implement API Endpoints")
    write_unit_tests: Node = Node("Write Unit Tests")
    perform_ui_testing: Node = Node("Perform User Interface Testing")
    database_setup_exec: Node = Node("Set Up Database Environment")
    deploy_to_staging: Node = Node("Deploy Application to Staging")
    address_bugs: Node = Node("Address Identified Bugs")
    conduct_code_reviews: Node = Node("Conduct Code Reviews")
    prepare_release_notes: Node = Node("Prepare Release Notes")

    _ = code_development.add_child(develop_user_authentication)
    _ = code_development.add_child(develop_data_models)
    _ = code_development.add_child(implement_api_endpoints)
    _ = testing.add_child(write_unit_tests)
    _ = testing.add_child(perform_ui_testing)
    _ = integrate_modules.add_child(database_setup_exec)
    _ = integrate_modules.add_child(deploy_to_staging)
    _ = resolve_issues.add_child(address_bugs)
    _ = manage_team.add_child(conduct_code_reviews)
    _ = client_communication.add_child(prepare_release_notes)

    # Level 3 - Monitoring and Control Subtasks
    track_story_points: Node = Node("Track Story Point Completion")
    review_burn_down_chart: Node = Node("Review Project Burn-down Chart")
    analyze_cost_variance: Node = Node("Analyze Project Cost Variance")
    process_change_requests: Node = Node("Process Incoming Change Requests")
    prepare_weekly_report: Node = Node("Prepare Weekly Progress Report")
    schedule_daily_standups: Node = Node("Schedule Daily Stand-up Meetings")

    _ = track_progress.add_child(track_story_points)
    _ = monitor_budget.add_child(analyze_cost_variance)
    _ = manage_changes.add_child(process_change_requests)
    _ = report_status.add_child(prepare_weekly_report)
    _ = conduct_meetings.add_child(schedule_daily_standups)
    _ = track_progress.add_child(review_burn_down_chart)

    # Level 3 - Closure Subtasks
    gather_feedback: Node = Node("Gather Stakeholder Feedback")
    archive_project_files: Node = Node("Archive All Project-Related Files")
    conduct_post_mortem: Node = Node("Conduct Post-mortem Analysis")
    invoice_client: Node = Node("Issue Final Project Invoice")

    _ = final_report.add_child(gather_feedback)
    _ = release_resources.add_child(archive_project_files)
    _ = lessons_learned.add_child(conduct_post_mortem)
    _ = client_signoff.add_child(invoice_client)

    # Create and run the GUI with the manually created tree
    gui = Gui(project_management)
    gui.calculate_node_positions()
    gui.draw_tree(gui._canvas)
    gui.run()
"""

if __name__ == "__main__":
    main()
