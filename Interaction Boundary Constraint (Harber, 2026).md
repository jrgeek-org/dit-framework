Interaction Boundary Constraint

## Abstract

This paper defines a constraint on the evaluation of system interactions.

Systems increasingly produce interactions that appear complete and actionable at the point of encounter. These interactions are evaluated based on their content, structure, and presented outcomes.

Evaluation beyond appearance requires that the composition producing an interaction be present at the interaction boundary. Where composition is not present, evaluation is limited to what is presented at the boundary and cannot be extended to claims about consistency, attribution, or reliability across interactions.

This condition applies independent of system design, correctness, or performance. It defines the limits of what can be known from the interaction itself.

# Decisioning - Domain

## Baseline Condition

Systems produce outputs in response to inputs.  
The participant encounters the output. The interaction appears complete.

## Current Evaluation Model

The evaluation model applied to decisioning systems is centered on the output as presented. Practitioners assess whether the output is correct, relevant, and aligned with expectations.

Correctness is defined at the level of the output.  
Performance is measured through accuracy and consistency across similar observable inputs.  
Confidence accrues through outputs that repeatedly align with expectations under similar observable inputs.

The assessment is real. It is applied to what is presented.  
The composition producing the output is not present at the interaction boundary.

## Constraint

Evaluation beyond appearance requires composition to be present at the interaction boundary.

- The ability to reconstruct or determine composition after the output does not satisfy this condition
- The output does not establish what produced it

## Consequences

- Consistency of outputs does not establish stability of composition
- Confidence based on prior outputs cannot be tied to the composition producing the current output
- Attribution cannot be established at the interaction boundary

## Impact (Decisioning - Domain)

Outputs can be assessed. Their content can be evaluated.

The assessments remain.  
Their scope contracts.

# Agentic - Domain

## Baseline Condition

Systems produce actions in response to inputs.  
The participant encounters the effects of those actions. The interaction appears complete.

## Current Evaluation Model

The evaluation model applied to agentic systems is centered on the effects as presented. Practitioners assess whether the action produced the intended outcome.

Correctness is defined at the level of the presented effect.  
Performance is measured through success of the action and consistency across similar observable inputs.  
Confidence accrues through repeated actions that produce expected outcomes.

The assessment is real. It is applied to what is presented.  
The action has occurred, and the composition producing it is not present at the interaction boundary.

## Constraint

Evaluation beyond appearance requires composition to be present at the interaction boundary.

- The action has already occurred at the point of evaluation
- The composition producing the action is not present at the interaction boundary
- Observation of an action increases what can be evaluated. It does not make composition present at the interaction boundary

## Consequences

- Causality cannot be established at the interaction boundary
- Consistency of outcomes does not establish stability of composition
- Attribution cannot be established at the interaction boundary

# Example 1 - Credit and Lending Decisions

## Scenario

A credit application is submitted. The system processes the application, reaches a decision, and issues a notification. The decision is decline. The applicant has been informed.

By the time any participant engages with the outcome, the action is complete and the window has closed.

## Current Evaluation

The outcome is evaluated based on what is present:

- the application as submitted
- the decision as recorded
- the notification as sent

The action is complete. Evaluation begins where it ended.

## What Is Not Present at the Interaction Boundary

At the point of evaluation, it is not possible to determine whether the conditions that produced this decision are consistent with those that produced prior decisions.

The decision is recorded. The outcome is observable. But it is not possible to determine whether:

- the composition present at this interaction is consistent with the composition present at prior decisions
- the basis on which prior decisions were reached is comparable to the basis of this one

The outcome is visible.  
The composition producing the action is not present at the interaction boundary.

## Constraint Applied

The evaluation applies to the action taken by the system, not the composition producing the action.

The assessment is real.  
But the evaluation cannot determine whether the composition producing the action is stable across interactions.

## Limit

- The system may produce consistent outputs whether or not the composition producing them is stable
- It may also produce identical outputs from different underlying compositions
- These conditions cannot be distinguished at the point of evaluation

Stability is required for evaluation to extend beyond presented outputs to claims across interactions. Where composition is not present at the interaction boundary, that stability cannot be established.

## Conclusion

The decision can be evaluated.  
The outcome can be measured.

The system that produced it cannot be evaluated beyond what is observable at the interaction boundary.

# Example 2 - Infrastructure and Resource Allocation

## Scenario

A resource allocation is required. The system processes current conditions, makes a determination, and reallocates capacity.

By the time any participant engages with the state of the environment, the reallocation has occurred and downstream dependencies have adjusted to it.

The action is complete. What is present is the resulting state.

## Current Evaluation

The outcome is evaluated based on what is present:

- the allocation as recorded
- the state of the environment as it now exists
- the downstream adjustments as presented

The action is complete. Evaluation begins where it ended.

## What Is Not Present at the Interaction Boundary

At the point of evaluation, it is not possible to determine whether the conditions that produced this allocation are consistent with those that produced prior allocations.

The allocation is recorded. The outcome is observable. But it is not possible to determine whether:

- the composition present at this interaction is consistent with the composition present at prior allocations
- the basis on which prior allocations were reached is comparable to the basis of this one

The outcome is visible.  
The composition producing the action is not present at the interaction boundary.

## Constraint Applied

The evaluation applies to the action taken by the system, not the composition producing the action.

The assessment is real.  
But the evaluation cannot determine whether the composition producing the action is stable across interactions.

## Limit

- The system may produce consistent allocations whether or not the composition producing them is stable
- It may also reach identical allocations from different underlying compositions
- These conditions cannot be distinguished at the point of evaluation

Stability is required for evaluation to extend beyond presented outputs to claims across interactions. Where composition is not present at the interaction boundary, that stability cannot be established.

## Conclusion

The allocation can be evaluated.  
The outcome can be measured.

The system that produced it cannot be evaluated beyond what is observable at the interaction boundary.

## Impact (Agentic - Domain)

Outcomes can be assessed. Results can be measured. These assessments are real. They carry meaning within the scope of what is observable after the action has occurred.

What changes is the scope of the claims evaluation can support.

- Claims about system reliability are claims about what a system will produce under conditions that have not yet occurred
- Claims about consistency are claims about whether the composition producing a prior outcome is the composition producing this one
- Claims about attribution are claims about what produced the result

Without composition at the interaction boundary, none of these claims are grounded in knowledge of what acted. They are grounded in inference over presented effects.

The assessments remain.  
Their scope contracts.

# MCP - Domain

## Baseline Condition

Systems operate across multiple components that contribute to a single interaction.

A single interaction may involve:

- the model
- the MCP client layer
- one or more MCP servers
- the systems those servers connect to

The interaction reflects the participation of these components.  
The interaction appears complete.

## Current Evaluation Model

The evaluation model applied to MCP-based systems is centered on the interaction as presented. Practitioners assess whether the interaction is relevant, accurate, and complete.

Correctness is defined at the level of the interaction.  
Performance is measured through interaction quality and consistency across similar observable inputs.  
Confidence accrues through repeated interactions that produce similar results under similar observable inputs.

The assessment is real. It is applied to what is presented.  
The composition producing the interaction is not present at the interaction boundary.

## Constraint

Evaluation beyond appearance requires composition to be present at the interaction boundary.

- Composition in MCP-based systems is distributed across independently operated participating components
- At the interaction boundary, what is present is the interaction as presented
- The ability to reconstruct or determine composition after the interaction does not satisfy this condition
- Internal observability, telemetry, protocol configuration, or representations of component participation may support operation, monitoring, or audit
- They do not satisfy the condition

The composition producing the interaction is not present at the interaction boundary.

## Consequences

- Consistency does not establish stability of composition
- Confidence cannot be tied to composition
- Attribution cannot be established at the interaction boundary

# Example 1 - Enterprise Workflow

## Scenario

A participant submits a request to update a customer record. The system processes the request, retrieves the relevant data, applies the update, and returns a confirmation.

The record has been updated. The confirmation is present.  
The interaction appears complete.

## Current Evaluation

The interaction is evaluated based on what is present:

- the request as submitted
- the confirmation
- the updated record

Evaluation applies to what is presented.

## What Is Not Present at the Interaction Boundary

At the point of evaluation, it is not possible to determine whether the components that produced this interaction are consistent with the components that produced prior interactions.

The confirmation is present. The record reflects the update. But it is not possible to determine whether:

- the composition present at this interaction is consistent with the composition present at prior interactions
- the components that participated in retrieving and updating the record are the components that participated previously
- the conditions under which prior interactions were produced are comparable to those of this one

The interaction is visible.  
The composition producing the interaction is not present at the interaction boundary.

## Constraint Applied

The evaluation applies to the interaction presented, not the composition producing the interaction.

The assessment is real.  
The record was updated. The confirmation was returned.

But the evaluation cannot determine whether the composition producing this interaction is consistent with the composition producing prior interactions.

## Limit

- The system may produce consistent interactions whether or not the composition producing them is consistent
- It may also produce identical interactions from different underlying compositions
- These conditions cannot be distinguished at the interaction boundary

Stability is required for evaluation to extend beyond presented interactions to claims across interactions. Where composition is not present at the interaction boundary, that stability cannot be established.

## Conclusion

The interaction can be evaluated. Its effects can be assessed.

The composition producing the interaction cannot be evaluated beyond what is present at the interaction boundary.

# Example 2 - Multi-Server Interaction

## Scenario

A participant submits a request that requires retrieving external data and generating a response. The system processes the request, routes it through multiple services, retrieves the relevant data, applies additional processing, and returns a response.

The response is present.  
The interaction appears complete.

## Current Evaluation

The interaction is evaluated based on what is present:

- the request as submitted
- the response
- the information contained in the response

Evaluation applies to what is presented.

## What Is Not Present at the Interaction Boundary

At the point of evaluation, it is not possible to determine which components participated in producing this interaction or how those components contributed to it.

The response is present. The information appears complete. But it is not possible to determine whether:

- the composition present at this interaction is consistent with the composition present at prior interactions
- the components that retrieved and processed the data are the components that participated previously
- the contribution of each participating component is identifiable within the interaction

The interaction is visible.  
The composition producing the interaction is not present at the interaction boundary.

## Constraint Applied

The evaluation applies to the interaction presented, not the composition producing the interaction.

The assessment is real.  
The response was returned. The information can be assessed.

But the evaluation cannot determine which components participated in producing the interaction or whether the composition is consistent across interactions.

## Limit

- The system may produce consistent interactions whether or not the composition producing them is consistent
- It may also produce identical interactions from different underlying compositions
- These conditions cannot be distinguished at the interaction boundary

Stability is required for evaluation to extend beyond presented interactions to claims across interactions. Where composition is not present at the interaction boundary, that stability cannot be established.

## Conclusion

The interaction can be evaluated. Its effects can be assessed.

The composition producing the interaction cannot be evaluated beyond what is present at the interaction boundary.

## Impact (MCP - Domain)

Interactions can be assessed. Their content can be evaluated. These assessments are real. They carry meaning within the scope of what is observable at the interaction boundary.

What changes is the scope of the claims evaluation can support.

- Claims about system reliability are claims about what a system will produce under conditions that have not yet occurred
- Claims about consistency are claims about whether the composition producing a prior interaction is the composition producing this one
- Claims about attribution are claims about which components participated in producing the interaction

Without composition present at the interaction boundary, none of these claims are grounded in knowledge of what participated. They are grounded in inference over presented interactions.

The assessments remain.  
Their scope contracts.
