# Power Automate / AppSheet Pseudocode
1. Trigger when a fault form is submitted.
2. Validate fault ID, asset and description.
3. POST the record to the governed triage endpoint.
4. Persist response fields to the action table.
5. Start an approval assigned to the responsible engineer.
6. If accepted or modified, create an approved downstream work item.
7. Record reviewer, decision, timestamp and change rationale.
8. Notify the reporter and measure completion/effectiveness.
